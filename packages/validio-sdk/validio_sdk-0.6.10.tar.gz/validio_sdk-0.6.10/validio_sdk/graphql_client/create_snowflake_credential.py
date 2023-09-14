from pydantic import Field

from .base_model import BaseModel
from .fragments import CredentialCreation


class CreateSnowflakeCredential(BaseModel):
    snowflake_credential_create: "CreateSnowflakeCredentialSnowflakeCredentialCreate" = Field(
        alias="snowflakeCredentialCreate"
    )


class CreateSnowflakeCredentialSnowflakeCredentialCreate(CredentialCreation):
    pass


CreateSnowflakeCredential.update_forward_refs()
CreateSnowflakeCredentialSnowflakeCredentialCreate.update_forward_refs()
