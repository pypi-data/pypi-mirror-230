from typing import List

from pydantic import Field

from .base_model import BaseModel
from .fragments import ErrorDetails


class DeleteDestination(BaseModel):
    destinations_delete: "DeleteDestinationDestinationsDelete" = Field(
        alias="destinationsDelete"
    )


class DeleteDestinationDestinationsDelete(BaseModel):
    errors: List["DeleteDestinationDestinationsDeleteErrors"]


class DeleteDestinationDestinationsDeleteErrors(ErrorDetails):
    pass


DeleteDestination.update_forward_refs()
DeleteDestinationDestinationsDelete.update_forward_refs()
DeleteDestinationDestinationsDeleteErrors.update_forward_refs()
