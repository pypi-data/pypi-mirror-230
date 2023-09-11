from pydantic import Field

from .base_model import BaseModel
from .fragments import NamespaceUpdate


class UpdateCredentialNamespace(BaseModel):
    credential_namespace_update: "UpdateCredentialNamespaceCredentialNamespaceUpdate" = Field(
        alias="credentialNamespaceUpdate"
    )


class UpdateCredentialNamespaceCredentialNamespaceUpdate(NamespaceUpdate):
    pass


UpdateCredentialNamespace.update_forward_refs()
UpdateCredentialNamespaceCredentialNamespaceUpdate.update_forward_refs()
