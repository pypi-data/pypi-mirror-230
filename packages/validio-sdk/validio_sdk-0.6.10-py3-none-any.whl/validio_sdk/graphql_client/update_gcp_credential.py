from pydantic import Field

from .base_model import BaseModel
from .fragments import CredentialUpdate


class UpdateGcpCredential(BaseModel):
    gcp_credential_update: "UpdateGcpCredentialGcpCredentialUpdate" = Field(
        alias="gcpCredentialUpdate"
    )


class UpdateGcpCredentialGcpCredentialUpdate(CredentialUpdate):
    pass


UpdateGcpCredential.update_forward_refs()
UpdateGcpCredentialGcpCredentialUpdate.update_forward_refs()
