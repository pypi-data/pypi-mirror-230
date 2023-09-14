from pydantic import Field

from .base_model import BaseModel
from .fragments import NamespaceUpdate


class UpdateWindowNamespace(BaseModel):
    window_namespace_update: "UpdateWindowNamespaceWindowNamespaceUpdate" = Field(
        alias="windowNamespaceUpdate"
    )


class UpdateWindowNamespaceWindowNamespaceUpdate(NamespaceUpdate):
    pass


UpdateWindowNamespace.update_forward_refs()
UpdateWindowNamespaceWindowNamespaceUpdate.update_forward_refs()
