from pydantic import Field

from .base_model import BaseModel
from .fragments import DestinationCreation


class CreateSnowflakeDestination(BaseModel):
    snowflake_destination_create: "CreateSnowflakeDestinationSnowflakeDestinationCreate" = Field(
        alias="snowflakeDestinationCreate"
    )


class CreateSnowflakeDestinationSnowflakeDestinationCreate(DestinationCreation):
    pass


CreateSnowflakeDestination.update_forward_refs()
CreateSnowflakeDestinationSnowflakeDestinationCreate.update_forward_refs()
