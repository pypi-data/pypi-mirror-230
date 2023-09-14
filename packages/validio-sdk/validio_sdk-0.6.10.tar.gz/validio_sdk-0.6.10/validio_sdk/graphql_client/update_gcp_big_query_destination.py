from pydantic import Field

from .base_model import BaseModel
from .fragments import DestinationUpdate


class UpdateGcpBigQueryDestination(BaseModel):
    gcp_big_query_destination_update: "UpdateGcpBigQueryDestinationGcpBigQueryDestinationUpdate" = Field(
        alias="gcpBigQueryDestinationUpdate"
    )


class UpdateGcpBigQueryDestinationGcpBigQueryDestinationUpdate(DestinationUpdate):
    pass


UpdateGcpBigQueryDestination.update_forward_refs()
UpdateGcpBigQueryDestinationGcpBigQueryDestinationUpdate.update_forward_refs()
