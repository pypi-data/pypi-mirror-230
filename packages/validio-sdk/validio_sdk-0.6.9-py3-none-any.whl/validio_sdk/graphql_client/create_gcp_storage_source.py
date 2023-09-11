from pydantic import Field

from .base_model import BaseModel
from .fragments import SourceCreation


class CreateGcpStorageSource(BaseModel):
    gcp_storage_source_create: "CreateGcpStorageSourceGcpStorageSourceCreate" = Field(
        alias="gcpStorageSourceCreate"
    )


class CreateGcpStorageSourceGcpStorageSourceCreate(SourceCreation):
    pass


CreateGcpStorageSource.update_forward_refs()
CreateGcpStorageSourceGcpStorageSourceCreate.update_forward_refs()
