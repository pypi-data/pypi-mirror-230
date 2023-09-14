from pydantic import Field

from .base_model import BaseModel
from .fragments import SourceCreation


class CreateSnowflakeSource(BaseModel):
    snowflake_source_create: "CreateSnowflakeSourceSnowflakeSourceCreate" = Field(
        alias="snowflakeSourceCreate"
    )


class CreateSnowflakeSourceSnowflakeSourceCreate(SourceCreation):
    pass


CreateSnowflakeSource.update_forward_refs()
CreateSnowflakeSourceSnowflakeSourceCreate.update_forward_refs()
