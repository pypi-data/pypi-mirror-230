from pydantic import Field

from .base_model import BaseModel
from .fragments import CredentialUpdate


class UpdateSnowflakeCredential(BaseModel):
    snowflake_credential_update: "UpdateSnowflakeCredentialSnowflakeCredentialUpdate" = Field(
        alias="snowflakeCredentialUpdate"
    )


class UpdateSnowflakeCredentialSnowflakeCredentialUpdate(CredentialUpdate):
    pass


UpdateSnowflakeCredential.update_forward_refs()
UpdateSnowflakeCredentialSnowflakeCredentialUpdate.update_forward_refs()
