from pydantic import Field

from .base_model import BaseModel
from .fragments import DestinationCreation


class CreateGcpBigQueryDestination(BaseModel):
    gcp_big_query_destination_create: "CreateGcpBigQueryDestinationGcpBigQueryDestinationCreate" = Field(
        alias="gcpBigQueryDestinationCreate"
    )


class CreateGcpBigQueryDestinationGcpBigQueryDestinationCreate(DestinationCreation):
    pass


CreateGcpBigQueryDestination.update_forward_refs()
CreateGcpBigQueryDestinationGcpBigQueryDestinationCreate.update_forward_refs()
