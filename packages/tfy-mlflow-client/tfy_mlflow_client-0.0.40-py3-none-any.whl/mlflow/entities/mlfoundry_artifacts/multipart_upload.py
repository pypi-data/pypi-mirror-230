import enum
from typing import List, Optional

from pydantic import BaseModel

from mlflow.entities.signed_url import SignedURL
from mlflow.protos import mlfoundry_artifacts_pb2 as mlfa_pb2


@enum.unique
class MultiPartUploadStorageProvider(str, enum.Enum):
    S3_COMPATIBLE = "S3_COMPATIBLE"
    AZURE_BLOB = "AZURE_BLOB"


class MultiPartUpload(BaseModel):
    class Config:
        allow_mutation = False

    storage_provider: MultiPartUploadStorageProvider
    part_signed_urls: List[SignedURL]
    s3_compatible_upload_id: Optional[str] = None
    azure_blob_block_ids: Optional[List[str]] = None
    finalize_signed_url: SignedURL

    @classmethod
    def from_proto(cls, message: mlfa_pb2.MultiPartUpload) -> "MultiPartUpload":
        message = message.multipart_upload
        return cls(
            storage_provider=message.storage_provider,
            part_signed_urls=[SignedURL.from_proto(su) for su in message.part_signed_urls],
            s3_compatible_upload_id=message.s3_compatible_upload_id or None,
            azure_blob_block_ids=[block_id for block_id in message.azure_blob_block_ids],
            finalize_signed_url=SignedURL.from_proto(message.finalize_signed_url),
        )

    def to_proto(self) -> mlfa_pb2.MultiPartUpload:
        mpu_proto = mlfa_pb2.MultiPartUpload(
            s3_compatible_upload_id=self.s3_compatible_upload_id or "",
            storage_provider=self.storage_provider.value,
            finalize_signed_url=self.finalize_signed_url.to_proto(),
        )
        mpu_proto.part_signed_urls.extend(
            signed_url.to_proto() for signed_url in self.part_signed_urls
        )
        mpu_proto.azure_blob_block_ids.extend(
            block_id for block_id in (self.azure_blob_block_ids or [])
        )
        return mpu_proto
