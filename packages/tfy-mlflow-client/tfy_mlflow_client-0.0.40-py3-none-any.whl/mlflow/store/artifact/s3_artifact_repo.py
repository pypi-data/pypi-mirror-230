import logging
import os
import posixpath
import time
import urllib.parse
from datetime import datetime
from functools import lru_cache
from mimetypes import guess_type
from typing import Any, Dict, Optional

from mlflow import data
from mlflow.entities import (
    FileInfo,
    MultiPartUpload,
    MultiPartUploadStorageProvider,
    SignedURL,
)
from mlflow.entities.storage_integration import AWSS3Credentials
from mlflow.exceptions import MlflowException
from mlflow.protos.databricks_pb2 import INTERNAL_ERROR, PERMISSION_DENIED, UNAUTHORIZED
from mlflow.store.artifact.artifact_repo import (
    DEFAULT_PRESIGNED_URL_EXPIRY_TIME,
    ArtifactRepository,
)
from mlflow.store.entities.paged_list import PagedList
from mlflow.utils.file_utils import relative_path_to_artifact_path

logger = logging.getLogger(__name__)


_MAX_CACHE_SECONDS = 300


def _get_utcnow_timestamp():
    return datetime.utcnow().timestamp()


@lru_cache(maxsize=64)
def _cached_get_s3_client(
    signature_version,
    timestamp,
    storage_integration_id,
    aws_access_key_id=None,
    aws_secret_access_key=None,
    aws_region=None,
):  # pylint: disable=unused-argument
    """Returns a boto3 client, caching to avoid extra boto3 verify calls.

    This method is outside of the S3ArtifactRepository as it is
    agnostic and could be used by other instances.

    `maxsize` set to avoid excessive memory consmption in the case
    a user has dynamic endpoints (intentionally or as a bug).

    Some of the boto3 endpoint urls, in very edge cases, might expire
    after twelve hours as that is the current expiration time. To ensure
    we throw an error on verification instead of using an expired endpoint
    we utilise the `timestamp` parameter to invalidate cache.
    """
    import boto3
    from botocore.client import Config

    # Making it possible to access public S3 buckets
    # Workaround for https://github.com/boto/botocore/issues/2442
    if signature_version.lower() == "unsigned":
        from botocore import UNSIGNED

        signature_version = UNSIGNED
    params = {}
    config_fields = {}
    if aws_secret_access_key and aws_access_key_id:
        params["aws_access_key_id"] = aws_access_key_id
        params["aws_secret_access_key"] = aws_secret_access_key
        if aws_region:
            config_fields["region_name"] = aws_region
    return boto3.client(
        "s3",
        config=Config(signature_version=signature_version, **config_fields),
        **params,
    )


class S3ArtifactRepository(ArtifactRepository):
    """Stores artifacts on Amazon S3."""

    def __init__(
        self,
        artifact_uri: str,
        credentials: AWSS3Credentials = None,
        storage_integration_id: str = None,
    ):
        self._storage_integration_id = storage_integration_id
        self._credentials = credentials
        super().__init__(artifact_uri)

    @staticmethod
    def parse_s3_uri(uri):
        """Parse an S3 URI, returning (bucket, path)"""
        parsed = urllib.parse.urlparse(uri)
        if parsed.scheme != "s3":
            raise Exception("Not an S3 URI: %s" % uri)
        path = parsed.path
        if path.startswith("/"):
            path = path[1:]
        return parsed.netloc, path

    @staticmethod
    def get_s3_file_upload_extra_args():
        import json

        s3_file_upload_extra_args = os.environ.get("MLFLOW_S3_UPLOAD_EXTRA_ARGS")
        if s3_file_upload_extra_args:
            return json.loads(s3_file_upload_extra_args)
        else:
            return None

    def _get_s3_client(self):
        signature_version = "s3v4"
        # Invalidate cache every `_MAX_CACHE_SECONDS`
        timestamp = int(_get_utcnow_timestamp() / _MAX_CACHE_SECONDS)
        params = {}

        if self._credentials:
            params["aws_access_key_id"] = self._credentials.awsAccessKeyId
            params["aws_secret_access_key"] = self._credentials.awsSecretAccessKey
            params["aws_region"] = self._credentials.region

        try:
            return _cached_get_s3_client(
                signature_version=signature_version,
                timestamp=timestamp,
                storage_integration_id=self._storage_integration_id,
                **params,
            )
        except Exception:
            logger.exception("Failed to initialize S3 Client")
            raise MlflowException(
                message=(
                    "Could not initialize S3 client. "
                    "Please make sure that you have configured"
                    "permissions of storage integration correctly. "
                ),
                error_code=UNAUTHORIZED,
            )

    def _upload_file(self, s3_client, local_file, bucket, key):
        extra_args = dict()
        guessed_type, guessed_encoding = guess_type(local_file)
        if guessed_type is not None:
            extra_args["ContentType"] = guessed_type
        if guessed_encoding is not None:
            extra_args["ContentEncoding"] = guessed_encoding
        environ_extra_args = self.get_s3_file_upload_extra_args()
        if environ_extra_args is not None:
            extra_args.update(environ_extra_args)
        s3_client.upload_file(Filename=local_file, Bucket=bucket, Key=key, ExtraArgs=extra_args)

    def log_artifact(self, local_file, artifact_path=None):
        (bucket, dest_path) = data.parse_s3_uri(self.artifact_uri)
        if artifact_path:
            dest_path = posixpath.join(dest_path, artifact_path)
        dest_path = posixpath.join(dest_path, os.path.basename(local_file))
        self._upload_file(
            s3_client=self._get_s3_client(), local_file=local_file, bucket=bucket, key=dest_path
        )

    def log_artifacts(self, local_dir, artifact_path=None):
        (bucket, dest_path) = data.parse_s3_uri(self.artifact_uri)
        if artifact_path:
            dest_path = posixpath.join(dest_path, artifact_path)
        s3_client = self._get_s3_client()
        local_dir = os.path.abspath(local_dir)
        for root, _, filenames in os.walk(local_dir):
            upload_path = dest_path
            if root != local_dir:
                rel_path = os.path.relpath(root, local_dir)
                rel_path = relative_path_to_artifact_path(rel_path)
                upload_path = posixpath.join(dest_path, rel_path)
            for f in filenames:
                self._upload_file(
                    s3_client=s3_client,
                    local_file=os.path.join(root, f),
                    bucket=bucket,
                    key=posixpath.join(upload_path, f),
                )

    def list_artifacts(
        self, path=None, max_results: Optional[int] = None, page_token: Optional[str] = None
    ):
        (bucket, artifact_path) = data.parse_s3_uri(self.artifact_uri)
        dest_path = artifact_path
        if path:
            dest_path = posixpath.join(dest_path, path)
        prefix = (dest_path.rstrip("/") + "/") if dest_path else ""
        s3_client = self._get_s3_client()
        paginator = s3_client.get_paginator("list_objects_v2")
        list_objects_v2_kwargs = {}
        if page_token:
            list_objects_v2_kwargs["ContinuationToken"] = page_token
        page_iterator = paginator.paginate(
            Bucket=bucket,
            Prefix=prefix,
            Delimiter="/",
            PaginationConfig={"PageSize": max_results},
            **list_objects_v2_kwargs,
        )
        infos, next_page_token = [], None
        # TODO (chiragjn): Extract total items to return in PagedList
        for page in page_iterator:
            # Subdirectories will be listed as "common prefixes" due to the way we made the request
            for obj in page.get("CommonPrefixes", []):
                subdir_path = obj.get("Prefix")
                self._verify_listed_object_contains_artifact_path_prefix(
                    listed_object_path=subdir_path, artifact_path=artifact_path
                )
                subdir_rel_path = posixpath.relpath(path=subdir_path, start=artifact_path)
                if subdir_rel_path.endswith("/"):
                    subdir_rel_path = subdir_rel_path[:-1]
                infos.append(FileInfo(path=subdir_rel_path, is_dir=True, file_size=None))
            # Objects listed directly will be files
            for obj in page.get("Contents", []):
                file_path = obj.get("Key")
                self._verify_listed_object_contains_artifact_path_prefix(
                    listed_object_path=file_path, artifact_path=artifact_path
                )
                file_rel_path = posixpath.relpath(path=file_path, start=artifact_path)
                file_size = int(obj.get("Size"))
                # signed_url = self._get_signed_uri(
                #     operation_name="get_object",
                #     bucket=bucket,
                #     key=file_path,
                #     expires_in=DEFAULT_PRESIGNED_URL_EXPIRY_TIME,
                #     s3_client=s3_client,
                # )
                infos.append(
                    FileInfo(path=file_rel_path, is_dir=False, file_size=file_size, signed_url=None)
                )
            if max_results is not None:
                if page.get("IsTruncated"):
                    next_continuation_token = page.get("NextContinuationToken")
                    if next_continuation_token:
                        next_page_token = next_continuation_token
                    else:
                        raise MlflowException(
                            "Got `IsTruncated` True from `list_objects_v2` call but got a null `NextContinuationToken`",
                            error_code=INTERNAL_ERROR,
                        )
                else:
                    next_page_token = None
                break
        # The list_artifacts API expects us to return an empty list if the path references a single file.
        rel_path = posixpath.relpath(path=dest_path, start=artifact_path)
        if (len(infos) == 1) and not infos[0].is_dir and (infos[0].path == rel_path):
            return PagedList([], token=None)
        return PagedList(sorted(infos, key=lambda f: f.path), token=next_page_token)

    @staticmethod
    def _verify_listed_object_contains_artifact_path_prefix(listed_object_path, artifact_path):
        if not listed_object_path.startswith(artifact_path):
            raise MlflowException(
                "The path of the listed S3 object does not begin with the specified"
                " artifact path. Artifact path: {artifact_path}. Object path:"
                " {object_path}.".format(
                    artifact_path=artifact_path, object_path=listed_object_path
                )
            )

    def _download_file(self, remote_file_path, local_path):
        (bucket, s3_root_path) = data.parse_s3_uri(self.artifact_uri)
        s3_full_path = posixpath.join(s3_root_path, remote_file_path)
        s3_client = self._get_s3_client()
        s3_client.download_file(bucket, s3_full_path, local_path)

    def get_artifact_contents(self, remote_path: str):
        (bucket, s3_root_path) = data.parse_s3_uri(self.artifact_uri)
        s3_full_path = posixpath.join(s3_root_path, remote_path)
        s3_client = self._get_s3_client()
        response = s3_client.get_object(Bucket=bucket, Key=s3_full_path)
        return response["Body"].read()

    def delete_artifacts(self, artifact_path=None):
        # TODO (chiragjn): This is not the most efficient way to bulk delete things, we need to async this
        #       Futhermore `list_objects` may not return everything above a certain number of files
        (bucket, dest_path) = data.parse_s3_uri(self.artifact_uri)
        if artifact_path:
            dest_path = posixpath.join(dest_path, artifact_path)

        s3_client = self._get_s3_client()
        list_objects = s3_client.list_objects(Bucket=bucket, Prefix=dest_path).get("Contents", [])
        for to_delete_obj in list_objects:
            file_path = to_delete_obj.get("Key")
            self._verify_listed_object_contains_artifact_path_prefix(
                listed_object_path=file_path, artifact_path=dest_path
            )
            s3_client.delete_object(Bucket=bucket, Key=file_path)

    def _strip_artifact_uri(self, artifact_path: str):
        if artifact_path.startswith("s3://"):
            if artifact_path.startswith(self.artifact_uri):
                artifact_path = artifact_path[len(self.artifact_uri) :]
            else:
                raise MlflowException(
                    f"Not authorized to access the uri: {artifact_path}",
                    error_code=PERMISSION_DENIED,
                )
        return artifact_path.lstrip("/")

    def _get_signed_uri(
        self,
        operation_name: str,
        bucket: str,
        key: str,
        expires_in: int = DEFAULT_PRESIGNED_URL_EXPIRY_TIME,
        s3_client=None,
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> str:
        s3_client = s3_client or self._get_s3_client()
        extra_params = extra_params or {}
        return s3_client.generate_presigned_url(
            operation_name,
            Params={"Bucket": bucket, "Key": key, **extra_params},
            ExpiresIn=expires_in,
        )

    def get_read_signed_uri(
        self, artifact_path: str, expires_in: int = DEFAULT_PRESIGNED_URL_EXPIRY_TIME
    ) -> str:
        if not artifact_path:
            raise MlflowException("artifact_path must be not an empty string")
        # TODO: this is needed till client prepends artifact_uri
        artifact_path = self._strip_artifact_uri(artifact_path=artifact_path)
        (bucket, s3_root_path) = data.parse_s3_uri(self.artifact_uri)
        key = posixpath.join(s3_root_path, artifact_path)
        return self._get_signed_uri(
            operation_name="get_object", bucket=bucket, key=key, expires_in=expires_in
        )

    def get_write_signed_uri(
        self, artifact_path: str, expires_in: int = DEFAULT_PRESIGNED_URL_EXPIRY_TIME
    ) -> str:
        if not artifact_path:
            raise MlflowException("artifact_path must be not an empty string")
        # TODO: this is needed till client prepends artifact_uri
        artifact_path = self._strip_artifact_uri(artifact_path=artifact_path)
        (bucket, s3_root_path) = data.parse_s3_uri(self.artifact_uri)
        key = posixpath.join(s3_root_path, artifact_path)
        return self._get_signed_uri(
            operation_name="put_object", bucket=bucket, key=key, expires_in=expires_in
        )

    def create_multipart_upload(
        self,
        artifact_path: str,
        num_parts: int,
        parts_signed_url_expires_in: int = 3 * 60 * 60,
        finalization_signed_url_expires_in: int = 24 * 60 * 60,
    ) -> MultiPartUpload:
        artifact_path = self._strip_artifact_uri(artifact_path=artifact_path)
        (bucket, s3_root_path) = data.parse_s3_uri(self.artifact_uri)
        key = posixpath.join(s3_root_path, artifact_path)

        s3_client = self._get_s3_client()

        response = s3_client.create_multipart_upload(Bucket=bucket, Key=key)
        upload_id = response["UploadId"]

        # Time taken to create signed uri with 500 parts: 0.28769380000000044 seconds.
        # Time taken to create signed uri with 1000 parts: 0.8583922919999978 seconds.
        # Time taken to create signed uri with 10000 parts: 5.419726211000004 seconds.
        start_time = time.monotonic()
        part_signed_urls = [
            SignedURL(
                path=artifact_path,
                url=s3_client.generate_presigned_url(
                    "upload_part",
                    ExpiresIn=parts_signed_url_expires_in,
                    Params={
                        "Bucket": bucket,
                        "Key": key,
                        "UploadId": upload_id,
                        "PartNumber": part_num,
                    },
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
            url=s3_client.generate_presigned_url(
                "complete_multipart_upload",
                ExpiresIn=finalization_signed_url_expires_in,
                Params={
                    "Bucket": bucket,
                    "Key": key,
                    "UploadId": upload_id,
                },
            ),
        )

        return MultiPartUpload(
            storage_provider=MultiPartUploadStorageProvider.S3_COMPATIBLE,
            s3_compatible_upload_id=upload_id,
            part_signed_urls=part_signed_urls,
            finalize_signed_url=finalize_signed_url,
        )
