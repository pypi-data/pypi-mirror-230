from pydantic import Field

from .base_model import BaseModel
from .fragments import CredentialCreation


class CreateGcpCredential(BaseModel):
    gcp_credential_create: "CreateGcpCredentialGcpCredentialCreate" = Field(
        alias="gcpCredentialCreate"
    )


class CreateGcpCredentialGcpCredentialCreate(CredentialCreation):
    pass


CreateGcpCredential.update_forward_refs()
CreateGcpCredentialGcpCredentialCreate.update_forward_refs()
