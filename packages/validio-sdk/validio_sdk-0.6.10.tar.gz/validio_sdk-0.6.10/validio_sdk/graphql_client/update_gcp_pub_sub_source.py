from pydantic import Field

from .base_model import BaseModel
from .fragments import SourceUpdate


class UpdateGcpPubSubSource(BaseModel):
    gcp_pub_sub_source_update: "UpdateGcpPubSubSourceGcpPubSubSourceUpdate" = Field(
        alias="gcpPubSubSourceUpdate"
    )


class UpdateGcpPubSubSourceGcpPubSubSourceUpdate(SourceUpdate):
    pass


UpdateGcpPubSubSource.update_forward_refs()
UpdateGcpPubSubSourceGcpPubSubSourceUpdate.update_forward_refs()
