from pydantic import Field

from .base_model import BaseModel
from .fragments import SourceUpdate


class UpdateSnowflakeSource(BaseModel):
    snowflake_source_update: "UpdateSnowflakeSourceSnowflakeSourceUpdate" = Field(
        alias="snowflakeSourceUpdate"
    )


class UpdateSnowflakeSourceSnowflakeSourceUpdate(SourceUpdate):
    pass


UpdateSnowflakeSource.update_forward_refs()
UpdateSnowflakeSourceSnowflakeSourceUpdate.update_forward_refs()
