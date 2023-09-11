from pydantic import Field

from .base_model import BaseModel
from .fragments import NamespaceUpdate


class UpdateDestinationNamespace(BaseModel):
    destination_namespace_update: "UpdateDestinationNamespaceDestinationNamespaceUpdate" = Field(
        alias="destinationNamespaceUpdate"
    )


class UpdateDestinationNamespaceDestinationNamespaceUpdate(NamespaceUpdate):
    pass


UpdateDestinationNamespace.update_forward_refs()
UpdateDestinationNamespaceDestinationNamespaceUpdate.update_forward_refs()
