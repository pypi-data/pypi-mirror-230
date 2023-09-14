from pydantic import Field

from .base_model import BaseModel
from .fragments import DestinationUpdate


class UpdateSnowflakeDestination(BaseModel):
    snowflake_destination_update: "UpdateSnowflakeDestinationSnowflakeDestinationUpdate" = Field(
        alias="snowflakeDestinationUpdate"
    )


class UpdateSnowflakeDestinationSnowflakeDestinationUpdate(DestinationUpdate):
    pass


UpdateSnowflakeDestination.update_forward_refs()
UpdateSnowflakeDestinationSnowflakeDestinationUpdate.update_forward_refs()
