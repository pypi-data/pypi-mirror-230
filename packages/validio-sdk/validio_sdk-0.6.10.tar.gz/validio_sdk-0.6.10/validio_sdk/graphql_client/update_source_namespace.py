from pydantic import Field

from .base_model import BaseModel
from .fragments import NamespaceUpdate


class UpdateSourceNamespace(BaseModel):
    source_namespace_update: "UpdateSourceNamespaceSourceNamespaceUpdate" = Field(
        alias="sourceNamespaceUpdate"
    )


class UpdateSourceNamespaceSourceNamespaceUpdate(NamespaceUpdate):
    pass


UpdateSourceNamespace.update_forward_refs()
UpdateSourceNamespaceSourceNamespaceUpdate.update_forward_refs()
