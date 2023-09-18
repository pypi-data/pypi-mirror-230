import base64
import logging
import os
import posixpath
import re
import time
import urllib.parse
import uuid
from datetime import datetime, timedelta
from typing import Optional

from mlflow.entities import (
    FileInfo,
    MultiPartUpload,
    MultiPartUploadStorageProvider,
    SignedURL,
)
from mlflow.entities.storage_integration import AzureBlobCredentials
from mlflow.exceptions import MlflowException
from mlflow.store.artifact.artifact_repo import (
    DEFAULT_PRESIGNED_URL_EXPIRY_TIME,
    ArtifactRepository,
)
from mlflow.store.entities import PagedList

logger = logging.getLogger(__name__)


class AzureBlobArtifactRepository(ArtifactRepository):
    """
    Stores artifacts on Azure Blob Storage.

    This repository is used with URIs of the form
    ``wasbs://<container-name>@<ystorage-account-name>.blob.core.windows.net/<path>``,
    following the same URI scheme as Hadoop on Azure blob storage. It requires either that:
    - Azure storage connection string is in the env var ``AZURE_STORAGE_CONNECTION_STRING``
    - Azure storage access key is in the env var ``AZURE_STORAGE_ACCESS_KEY``
    - DefaultAzureCredential is configured
    """

    def __init__(
        self,
        artifact_uri,
        storage_integration_id: str,
        credentials: AzureBlobCredentials = None,
        client=None,
    ):
        super().__init__(artifact_uri)
        from azure.storage.blob import BlobServiceClient

        # Allow override for testing
        if client:
            self.client = client
            return

        (_, account, _, api_uri_suffix) = AzureBlobArtifactRepository.parse_wasbs_uri(artifact_uri)

        if credentials and credentials.connectionString:
            self.client = BlobServiceClient.from_connection_string(
                conn_str=credentials.connectionString
            )
        elif "AZURE_STORAGE_CONNECTION_STRING" in os.environ:
            self.client = BlobServiceClient.from_connection_string(
                conn_str=os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
            )
        elif "AZURE_STORAGE_ACCESS_KEY" in os.environ:
            account_url = "https://{account}.{api_uri_suffix}".format(
                account=account, api_uri_suffix=api_uri_suffix
            )
            self.client = BlobServiceClient(
                account_url=account_url, credential=os.environ.get("AZURE_STORAGE_ACCESS_KEY")
            )
        else:
            try:
                from azure.identity import DefaultAzureCredential
            except ImportError as exc:
                raise ImportError(
                    "Using DefaultAzureCredential requires the azure-identity package. "
                    "Please install it via: pip install azure-identity"
                ) from exc

            account_url = "https://{account}.{api_uri_suffix}".format(
                account=account, api_uri_suffix=api_uri_suffix
            )
            self.client = BlobServiceClient(
                account_url=account_url, credential=DefaultAzureCredential()
            )

    @staticmethod
    def parse_wasbs_uri(uri):
        """Parse a wasbs:// URI, returning (container, storage_account, path, api_uri_suffix)."""
        parsed = urllib.parse.urlparse(uri)
        if parsed.scheme != "wasbs":
            raise Exception("Not a WASBS URI: %s" % uri)

        match = re.match(
            r"([^@]+)@([^.]+)\.(blob\.core\.(windows\.net|chinacloudapi\.cn))", parsed.netloc
        )

        if match is None:
            raise Exception(
                "WASBS URI must be of the form "
                "<container>@<account>.blob.core.windows.net"
                " or <container>@<account>.blob.core.chinacloudapi.cn"
            )
        container = match.group(1)
        storage_account = match.group(2)
        api_uri_suffix = match.group(3)
        path = parsed.path
        if path.startswith("/"):
            path = path[1:]
        return container, storage_account, path, api_uri_suffix

    def log_artifact(self, local_file, artifact_path=None):
        (container, _, dest_path, _) = self.parse_wasbs_uri(self.artifact_uri)
        container_client = self.client.get_container_client(container)
        if artifact_path:
            dest_path = posixpath.join(dest_path, artifact_path)
        dest_path = posixpath.join(dest_path, os.path.basename(local_file))
        with open(local_file, "rb") as file:
            container_client.upload_blob(dest_path, file, overwrite=True)

    def log_artifacts(self, local_dir, artifact_path=None):
        (container, _, dest_path, _) = self.parse_wasbs_uri(self.artifact_uri)
        container_client = self.client.get_container_client(container)
        if artifact_path:
            dest_path = posixpath.join(dest_path, artifact_path)
        local_dir = os.path.abspath(local_dir)
        for root, _, filenames in os.walk(local_dir):
            upload_path = dest_path
            if root != local_dir:
                rel_path = os.path.relpath(root, local_dir)
                upload_path = posixpath.join(dest_path, rel_path)
            for f in filenames:
                remote_file_path = posixpath.join(upload_path, f)
                local_file_path = os.path.join(root, f)
                with open(local_file_path, "rb") as file:
                    container_client.upload_blob(remote_file_path, file, overwrite=True)

    def list_artifacts(
        self, path, max_results: Optional[int] = None, page_token: Optional[str] = None
    ) -> PagedList[FileInfo]:
        # Newer versions of `azure-storage-blob` (>= 12.4.0) provide a public
        # `azure.storage.blob.BlobPrefix` object to signify that a blob is a directory,
        # while older versions only expose this API internally as
        # `azure.storage.blob._models.BlobPrefix`
        try:
            from azure.storage.blob import BlobPrefix, BlobProperties
        except ImportError:
            from azure.storage.blob._models import BlobPrefix, BlobProperties
        from azure.core.paging import PageIterator

        (container, _, artifact_path, _) = self.parse_wasbs_uri(self.artifact_uri)
        dest_path = artifact_path
        if path:
            dest_path = posixpath.join(dest_path, path)
        prefix = dest_path if dest_path.endswith("/") else dest_path + "/"
        container_client = self.client.get_container_client(container)
        page_iterator: PageIterator[BlobProperties] = container_client.walk_blobs(  # type: ignore
            name_starts_with=prefix,
            results_per_page=max_results,
        ).by_page(continuation_token=page_token)
        infos, next_page_token = [], None
        # TODO (chiragjn): Extract total items to return in PagedList
        for page in page_iterator:
            for blob in page:
                if not blob.name.startswith(artifact_path):
                    raise MlflowException(
                        "The name of the listed Azure blob does not begin with the specified"
                        " artifact path. Artifact path: {artifact_path}. Blob name:"
                        " {blob_name}".format(artifact_path=artifact_path, blob_name=blob.name)
                    )
                if isinstance(blob, BlobPrefix):  # This is a prefix for items in a subdirectory
                    subdir_rel_path = posixpath.relpath(path=blob.name, start=artifact_path)
                    if subdir_rel_path.endswith("/"):
                        subdir_rel_path = subdir_rel_path[:-1]
                    infos.append(FileInfo(path=subdir_rel_path, is_dir=True, file_size=None))
                else:
                    file_rel_path = posixpath.relpath(path=blob.name, start=artifact_path)
                    # signed_url = self._get_signed_uri(
                    #     container=container,
                    #     blob_name=blob.name,
                    #     read_only=True,
                    #     expires_in=DEFAULT_PRESIGNED_URL_EXPIRY_TIME,
                    # )
                    infos.append(
                        FileInfo(
                            path=file_rel_path, is_dir=False, file_size=blob.size, signed_url=None
                        )
                    )
            if max_results is not None:
                # max_results None means list all
                next_page_token = page_iterator.continuation_token
                break
        # The list_artifacts API expects us to return an empty list if the path references a single file.
        rel_path = posixpath.relpath(path=dest_path, start=artifact_path)
        if (len(infos) == 1) and not infos[0].is_dir and (infos[0].path == rel_path):
            return PagedList([], token=None)
        return PagedList(sorted(infos, key=lambda f: f.path), token=next_page_token)

    def _download_file(self, remote_file_path, local_path):
        (container, _, remote_root_path, _) = self.parse_wasbs_uri(self.artifact_uri)
        container_client = self.client.get_container_client(container)
        remote_full_path = posixpath.join(remote_root_path, remote_file_path)
        with open(local_path, "wb") as file:
            container_client.download_blob(remote_full_path).readinto(file)

    def get_artifact_contents(self, remote_path: str) -> bytes:
        (container, _, remote_root_path, _) = self.parse_wasbs_uri(self.artifact_uri)
        container_client = self.client.get_container_client(container)
        remote_full_path = posixpath.join(remote_root_path, remote_path)
        return container_client.download_blob(remote_full_path).readall()

    def delete_artifacts(self, artifact_path=None):
        (container, _, remote_root_path, _) = self.parse_wasbs_uri(self.artifact_uri)
        container_client = self.client.get_container_client(container)
        if artifact_path:
            remote_root_path = posixpath.join(remote_root_path, artifact_path)
        results = container_client.walk_blobs(name_starts_with=remote_root_path, delimiter="")
        for r in results:
            container_client.delete_blob(r.name)

    def _get_signed_uri(
        self,
        container: str,
        blob_name: str,
        read_only: bool,
        expires_in: int = DEFAULT_PRESIGNED_URL_EXPIRY_TIME,
    ) -> str:
        from azure.storage.blob import BlobSasPermissions, generate_blob_sas

        expiry_time = datetime.utcnow() + timedelta(seconds=expires_in)
        permission = BlobSasPermissions(
            read=True, write=not read_only, create=not read_only, object=blob_name
        )
        sas_token = generate_blob_sas(
            account_name=self.client.credential.account_name,
            container_name=container,
            blob_name=blob_name,
            account_key=self.client.credential.account_key,
            permission=permission,
            expiry=expiry_time,
        )
        return f"https://{self.client.credential.account_name}.blob.core.windows.net/{container}/{blob_name}?{sas_token}"

    def get_read_signed_uri(
        self, artifact_path: str, expires_in: int = DEFAULT_PRESIGNED_URL_EXPIRY_TIME
    ) -> str:
        if not artifact_path:
            raise MlflowException("artifact_path must be not an empty string")
        (container, _, remote_root_path, _) = self.parse_wasbs_uri(self.artifact_uri)
        blob_name = posixpath.join(remote_root_path, artifact_path)
        return self._get_signed_uri(
            container=container, blob_name=blob_name, read_only=True, expires_in=expires_in
        )

    def get_write_signed_uri(
        self, artifact_path: str, expires_in: int = DEFAULT_PRESIGNED_URL_EXPIRY_TIME
    ) -> str:
        if not artifact_path:
            raise MlflowException("artifact_path must be not an empty string")
        (container, _, remote_root_path, _) = self.parse_wasbs_uri(self.artifact_uri)
        blob_name = posixpath.join(remote_root_path, artifact_path)
        return self._get_signed_uri(
            container=container, blob_name=blob_name, read_only=False, expires_in=expires_in
        )

    def create_multipart_upload(
        self,
        artifact_path: str,
        num_parts: int,
        parts_signed_url_expires_in: int = 3 * 60 * 60,
        finalization_signed_url_expires_in: int = 24 * 60 * 60,
    ) -> MultiPartUpload:
        from azure.storage.blob import BlobSasPermissions, generate_blob_sas

        (container, _, remote_root_path, _) = self.parse_wasbs_uri(self.artifact_uri)
        blob_name = posixpath.join(remote_root_path, artifact_path)
        expiry_time = datetime.utcnow() + timedelta(seconds=parts_signed_url_expires_in)

        permission = BlobSasPermissions(read=True, write=True, create=True, object=blob_name)

        # Time taken to create signed uri with 500 parts: 0.008549950000002582
        # Time taken to create signed uri with 1000 parts: 0.015885018999995282
        # Time taken to create signed uri with 10000 parts: 0.20251266500000042
        start_time = time.monotonic()
        sas_token_for_parts = generate_blob_sas(
            account_name=self.client.credential.account_name,
            container_name=container,
            blob_name=blob_name,
            account_key=self.client.credential.account_key,
            permission=permission,
            expiry=expiry_time,
        )

        blob_block_ids = []
        part_signed_urls = []
        for _ in range(num_parts):
            block_id = base64.b64encode(uuid.uuid4().hex.encode()).decode("utf-8")
            blob_block_ids.append(block_id)
            part_signed_urls.append(
                SignedURL(
                    url=f"https://{self.client.credential.account_name}.blob.core.windows.net/{container}/{blob_name}?{sas_token_for_parts}&comp=block&blockid={block_id}",
                    path=artifact_path,
                )
            )
        end_time = time.monotonic()
        logger.debug(
            "Time taken to create signed uri with %d parts: %d seconds.",
            num_parts,
            end_time - start_time,
        )
        sas_token_for_finalization = generate_blob_sas(
            account_name=self.client.credential.account_name,
            container_name=container,
            blob_name=blob_name,
            account_key=self.client.credential.account_key,
            permission=permission,
            expiry=datetime.utcnow() + timedelta(seconds=finalization_signed_url_expires_in),
        )

        return MultiPartUpload(
            storage_provider=MultiPartUploadStorageProvider.AZURE_BLOB,
            part_signed_urls=part_signed_urls,
            finalize_signed_url=SignedURL(
                url=f"https://{self.client.credential.account_name}.blob.core.windows.net/{container}/{blob_name}?{sas_token_for_finalization}&comp=blocklist",
                path=artifact_path,
            ),
            azure_blob_block_ids=blob_block_ids,
        )
