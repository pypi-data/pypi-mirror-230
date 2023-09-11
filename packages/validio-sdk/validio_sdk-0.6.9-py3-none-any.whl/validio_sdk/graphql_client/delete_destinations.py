from typing import List

from pydantic import Field

from .base_model import BaseModel
from .fragments import ErrorDetails


class DeleteDestinations(BaseModel):
    destinations_delete: "DeleteDestinationsDestinationsDelete" = Field(
        alias="destinationsDelete"
    )


class DeleteDestinationsDestinationsDelete(BaseModel):
    errors: List["DeleteDestinationsDestinationsDeleteErrors"]


class DeleteDestinationsDestinationsDeleteErrors(ErrorDetails):
    pass


DeleteDestinations.update_forward_refs()
DeleteDestinationsDestinationsDelete.update_forward_refs()
DeleteDestinationsDestinationsDeleteErrors.update_forward_refs()
