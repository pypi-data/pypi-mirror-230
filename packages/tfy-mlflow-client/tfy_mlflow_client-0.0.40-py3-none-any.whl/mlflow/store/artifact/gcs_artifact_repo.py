import json
import logging
import os
import posixpath
import tempfile
import time
import urllib.parse
from datetime import datetime
from functools import lru_cache
from typing import Optional

import requests

from mlflow.entities import (
    FileInfo,
    MultiPartUpload,
    MultiPartUploadStorageProvider,
    SignedURL,
)
from mlflow.entities.storage_integration import GCSCredentials
from mlflow.exceptions import MlflowException
from mlflow.protos.databricks_pb2 import UNAUTHORIZED
from mlflow.store.artifact.artifact_repo import (
    DEFAULT_PRESIGNED_URL_EXPIRY_TIME,
    ArtifactRepository,
)
from mlflow.store.entities import PagedList
from mlflow.utils.file_utils import relative_path_to_artifact_path

logger = logging.getLogger(__name__)

_REQUIRED_SCOPES = (
    "https://www.googleapis.com/auth/devstorage.full_control",
    "https://www.googleapis.com/auth/devstorage.read_only",
    "https://www.googleapis.com/auth/devstorage.read_write",
    "https://www.googleapis.com/auth/cloud-platform",
)

_MAX_CACHE_SECONDS = 300


# noinspection PyUnusedLocal
@lru_cache(maxsize=64)
def _cached_get_client(
    timestamp, storage_integration_id, gcloud_credentials_file_contents: Optional[str] = None
):  # pylint: disable=unused-argument
    """Returns a GCS Storage client, caching to avoid any extra network calls."""
    from google import auth
    from google.cloud import storage

    if gcloud_credentials_file_contents:
        with tempfile.NamedTemporaryFile(mode="w") as tmp:
            tmp.file.write(gcloud_credentials_file_contents)
            tmp.file.close()
            credentials, _ = auth.load_credentials_from_file(tmp.name, scopes=_REQUIRED_SCOPES)
    else:
        credentials, _ = auth.default(scopes=_REQUIRED_SCOPES)

    return storage.Client(credentials=credentials)


def _can_sign_locally(gcloud_credentials):
    from google.auth.credentials import Signing

    return isinstance(gcloud_credentials, Signing)


class GCSArtifactRepository(ArtifactRepository):
    """
    Stores artifacts on Google Cloud Storage.

    Assumes the google credentials are available in the environment,
    see https://google-cloud.readthedocs.io/en/latest/core/auth.html.
    """

    def __init__(
        self,
        artifact_uri,
        credentials: GCSCredentials = None,
        storage_integration_id=None,
    ):
        self._credentials = credentials
        self._gcloud_credentials_file_contents = None
        if self._credentials and self._credentials.keyFileContent:
            self._gcloud_credentials_file_contents = json.dumps(self._credentials.keyFileContent)
        self._storage_integration_id = storage_integration_id
        super().__init__(artifact_uri)

    @staticmethod
    def parse_gcs_uri(uri):
        """Parse an GCS URI, returning (bucket, path)"""
        parsed = urllib.parse.urlparse(uri)
        if parsed.scheme != "gs":
            raise Exception("Not a GCS URI: %s" % uri)
        path = parsed.path
        if path.startswith("/"):
            path = path[1:]
        return parsed.netloc, path

    def _get_client(self):
        from google.auth.transport import requests

        timestamp = int(datetime.utcnow().timestamp() / _MAX_CACHE_SECONDS)
        try:
            storage_client = _cached_get_client(
                timestamp=timestamp,
                storage_integration_id=self._storage_integration_id,
                gcloud_credentials_file_contents=self._gcloud_credentials_file_contents,
            )
        except Exception:
            logger.exception("Failed to initialize GCS Client.")
            raise MlflowException(
                message=(
                    "Could not initialize GCS client. "
                    "Please make sure that you have configured the "
                    "permissions of storage integration correctly. "
                ),
                error_code=UNAUTHORIZED,
            )
        # A hacky solution from https://stackoverflow.com/a/64245028/3697191
        credentials = storage_client._credentials
        if not credentials.valid:
            credentials.refresh(requests.Request())
            if not credentials.valid:
                raise Exception("Failed to fetch valid credentials to Google Cloud Storage")
        return storage_client

    def _get_bucket(self, bucket, client=None):
        client = client or self._get_client()
        return client.bucket(bucket)

    def log_artifact(self, local_file, artifact_path=None):
        (bucket, dest_path) = self.parse_gcs_uri(self.artifact_uri)
        if artifact_path:
            dest_path = posixpath.join(dest_path, artifact_path)
        dest_path = posixpath.join(dest_path, os.path.basename(local_file))

        gcs_bucket = self._get_bucket(bucket)
        blob = gcs_bucket.blob(dest_path)
        blob.upload_from_filename(local_file)

    def log_artifacts(self, local_dir, artifact_path=None):
        (bucket, dest_path) = self.parse_gcs_uri(self.artifact_uri)
        if artifact_path:
            dest_path = posixpath.join(dest_path, artifact_path)
        gcs_bucket = self._get_bucket(bucket)

        local_dir = os.path.abspath(local_dir)
        for root, _, filenames in os.walk(local_dir):
            upload_path = dest_path
            if root != local_dir:
                rel_path = os.path.relpath(root, local_dir)
                rel_path = relative_path_to_artifact_path(rel_path)
                upload_path = posixpath.join(dest_path, rel_path)
            for f in filenames:
                path = posixpath.join(upload_path, f)
                gcs_bucket.blob(path).upload_from_filename(os.path.join(root, f))

    def list_artifacts(
        self, path=None, max_results: Optional[int] = None, page_token: Optional[str] = None
    ) -> PagedList[FileInfo]:
        (bucket, artifact_path) = self.parse_gcs_uri(self.artifact_uri)
        dest_path = artifact_path
        if path:
            dest_path = posixpath.join(dest_path, path)
        prefix = dest_path if dest_path.endswith("/") else dest_path + "/"
        client = self._get_client()
        page_iterator = client.list_blobs(
            bucket_or_name=bucket,
            prefix=prefix,
            delimiter="/",
            page_size=max_results,
            page_token=page_token,
        )
        infos, next_page_token = [], None
        # TODO (chiragjn): Extract total items to return in PagedList
        for page in page_iterator.pages:
            for prefix in page.prefixes:
                subdir_rel_path = posixpath.relpath(prefix, artifact_path)
                if subdir_rel_path.endswith("/"):
                    subdir_rel_path = subdir_rel_path[:-1]
                infos.append(FileInfo(path=subdir_rel_path, is_dir=True, file_size=None))
            for blob in page:
                file_rel_path = posixpath.relpath(blob.name, artifact_path)
                # signed_url = self._get_signed_uri(
                #     method="GET",
                #     bucket=bucket,
                #     blob_path=blob.name,
                #     expires_in=DEFAULT_PRESIGNED_URL_EXPIRY_TIME
                # )
                infos.append(
                    FileInfo(path=file_rel_path, is_dir=False, file_size=blob.size, signed_url=None)
                )
            if max_results is not None:
                next_page_token = page_iterator.next_page_token
                break
        # The list_artifacts API expects us to return an empty list if the path references a single file.
        rel_path = posixpath.relpath(path=dest_path, start=artifact_path)
        if (len(infos) == 1) and not infos[0].is_dir and (infos[0].path == rel_path):
            return PagedList([], token=None)
        return PagedList(sorted(infos, key=lambda f: f.path), token=next_page_token)

    def _download_file(self, remote_file_path, local_path):
        (bucket, remote_root_path) = self.parse_gcs_uri(self.artifact_uri)
        remote_full_path = posixpath.join(remote_root_path, remote_file_path)
        gcs_bucket = self._get_bucket(bucket)
        gcs_bucket.blob(remote_full_path).download_to_filename(local_path)

    def get_artifact_contents(self, remote_path: str):
        (bucket, remote_root_path) = self.parse_gcs_uri(self.artifact_uri)
        remote_full_path = posixpath.join(remote_root_path, remote_path)
        gcs_bucket = self._get_bucket(bucket)
        # TODO (nikp1172) download_as_bytes will not work for large files,
        #   use https://cloud.google.com/python/docs/reference/storage/latest/google.cloud.storage.blob.Blob#google_cloud_storage_blob_Blob_open
        return gcs_bucket.blob(remote_full_path).download_as_bytes()

    @staticmethod
    def _verify_listed_object_contains_artifact_path_prefix(listed_object_path, artifact_path):
        if not listed_object_path.startswith(artifact_path):
            raise MlflowException(
                f"The path of the listed GCS object does not begin with the specified artifact path. "
                f"Artifact path: {artifact_path}. Object path: {listed_object_path}."
            )

    def delete_artifacts(self, artifact_path=None):
        # TODO (chiragjn): This is not the most efficient way to bulk delete things, we need to async this
        (bucket, dest_path) = self.parse_gcs_uri(self.artifact_uri)
        if artifact_path:
            dest_path = posixpath.join(dest_path, artifact_path)

        gcs_bucket = self._get_bucket(bucket)
        blobs = gcs_bucket.list_blobs(prefix=dest_path)
        for blob in blobs:
            self._verify_listed_object_contains_artifact_path_prefix(
                listed_object_path=blob.name, artifact_path=dest_path
            )
            blob.delete()

    def _get_signed_uri(
        self,
        method: str,
        bucket: str,
        blob_path: str,
        expires_in: int = DEFAULT_PRESIGNED_URL_EXPIRY_TIME,
        client=None,
    ) -> str:
        client = client or self._get_client()
        gcs_bucket = self._get_bucket(bucket, client=client)
        blob = gcs_bucket.blob(blob_path)
        kwargs = {}
        if not _can_sign_locally(client._credentials):
            # If we do not have a private key, call Google's IAM service to sign the blob
            kwargs = {
                "service_account_email": client._credentials.service_account_email,
                "access_token": client._credentials.token,
            }

        url = blob.generate_signed_url(
            version="v4",
            expiration=expires_in,
            method=method,
            **kwargs,
        )
        return url

    def get_read_signed_uri(
        self, artifact_path: str, expires_in: int = DEFAULT_PRESIGNED_URL_EXPIRY_TIME
    ) -> str:
        """
        Generates a v4 signed URL for downloading a blob.
        """
        (bucket, dest_path) = self.parse_gcs_uri(self.artifact_uri)
        blob_path = posixpath.join(dest_path, artifact_path)
        return self._get_signed_uri(
            method="GET", bucket=bucket, blob_path=blob_path, expires_in=expires_in
        )

    def get_write_signed_uri(
        self, artifact_path: str, expires_in: int = DEFAULT_PRESIGNED_URL_EXPIRY_TIME
    ) -> str:
        """
        Generates a v4 signed URL for uploading a blob.
        """
        (bucket, dest_path) = self.parse_gcs_uri(self.artifact_uri)
        blob_path = posixpath.join(dest_path, artifact_path)
        return self._get_signed_uri(
            method="PUT", bucket=bucket, blob_path=blob_path, expires_in=expires_in
        )

    def create_multipart_upload(
        self,
        artifact_path: str,
        num_parts: int,
        parts_signed_url_expires_in: int = 3 * 60 * 60,
        finalization_signed_url_expires_in: int = 24 * 60 * 60,
    ) -> MultiPartUpload:
        import xmltodict

        (bucket, dest_path) = self.parse_gcs_uri(self.artifact_uri)
        client = self._get_client()
        gcs_bucket = self._get_bucket(bucket, client=client)
        blob_path = posixpath.join(dest_path, artifact_path)
        blob = gcs_bucket.blob(blob_path)

        kwargs = {}
        if not _can_sign_locally(client._credentials):
            # If we do not have a private key, call Google's IAM service to sign the blob
            kwargs = {
                "service_account_email": client._credentials.service_account_email,
                "access_token": client._credentials.token,
            }

        create_multipart_upload_url = blob.generate_signed_url(
            version="v4",
            expiration=120,
            method="POST",
            query_parameters={"uploads": ""},
            **kwargs,
        )
        response = requests.post(create_multipart_upload_url)
        response.raise_for_status()
        try:
            response_dict = xmltodict.parse(response.text)
            upload_id = response_dict["InitiateMultipartUploadResult"]["UploadId"]
        except Exception as ex:
            logger.exception(
                "Failed to get upload id for multipart upload" "bucket=%s, path=%s, response=%s",
                gcs_bucket,
                blob_path,
                response.text,
            )
            raise ex

        # Time taken to create signed uri with 500 parts: 0.530260138 seconds.
        # Time taken to create signed uri with 1000 parts: 2.987320241000006 seconds
        # Time taken to create signed uri with 10000 parts: 11.295842703000005 seconds.

        start_time = time.monotonic()
        part_signed_urls = [
            SignedURL(
                path=artifact_path,
                url=blob.generate_signed_url(
                    version="v4",
                    expiration=parts_signed_url_expires_in,
                    method="PUT",
                    query_parameters={
                        "uploadId": upload_id,
                        "partNumber": part_num,
                    },
                    **kwargs,
                ),
            )
            for part_num in range(1, num_parts + 1)
        ]
        end_time = time.monotonic()
        logger.debug(
            "Time taken to create signed uri with %d parts: %d seconds.",
            num_parts,
            end_time - start_time,
        )

        finalize_signed_url = SignedURL(
            path=artifact_path,
            url=blob.generate_signed_url(
                version="v4",
                expiration=finalization_signed_url_expires_in,
                method="POST",
                query_parameters={
                    "uploadId": upload_id,
                },
                **kwargs,
            ),
        )

        return MultiPartUpload(
            storage_provider=MultiPartUploadStorageProvider.S3_COMPATIBLE,
            s3_compatible_upload_id=upload_id,
            part_signed_urls=part_signed_urls,
            finalize_signed_url=finalize_signed_url,
        )
