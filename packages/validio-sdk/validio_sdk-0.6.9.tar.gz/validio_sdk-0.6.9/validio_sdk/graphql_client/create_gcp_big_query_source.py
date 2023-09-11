from pydantic import Field

from .base_model import BaseModel
from .fragments import SourceCreation


class CreateGcpBigQuerySource(BaseModel):
    gcp_big_query_source_create: "CreateGcpBigQuerySourceGcpBigQuerySourceCreate" = (
        Field(alias="gcpBigQuerySourceCreate")
    )


class CreateGcpBigQuerySourceGcpBigQuerySourceCreate(SourceCreation):
    pass


CreateGcpBigQuerySource.update_forward_refs()
CreateGcpBigQuerySourceGcpBigQuerySourceCreate.update_forward_refs()
