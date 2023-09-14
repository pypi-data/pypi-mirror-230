from pydantic import Field

from .base_model import BaseModel
from .fragments import NamespaceUpdate


class UpdateIdentityProviderNamespace(BaseModel):
    identity_provider_namespace_update: "UpdateIdentityProviderNamespaceIdentityProviderNamespaceUpdate" = Field(
        alias="identityProviderNamespaceUpdate"
    )


class UpdateIdentityProviderNamespaceIdentityProviderNamespaceUpdate(NamespaceUpdate):
    pass


UpdateIdentityProviderNamespace.update_forward_refs()
UpdateIdentityProviderNamespaceIdentityProviderNamespaceUpdate.update_forward_refs()
