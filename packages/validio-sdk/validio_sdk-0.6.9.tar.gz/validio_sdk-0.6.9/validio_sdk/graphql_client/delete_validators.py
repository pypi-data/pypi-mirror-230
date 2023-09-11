from typing import List

from pydantic import Field

from .base_model import BaseModel
from .fragments import ErrorDetails


class DeleteValidators(BaseModel):
    validators_delete: "DeleteValidatorsValidatorsDelete" = Field(
        alias="validatorsDelete"
    )


class DeleteValidatorsValidatorsDelete(BaseModel):
    errors: List["DeleteValidatorsValidatorsDeleteErrors"]


class DeleteValidatorsValidatorsDeleteErrors(ErrorDetails):
    pass


DeleteValidators.update_forward_refs()
DeleteValidatorsValidatorsDelete.update_forward_refs()
DeleteValidatorsValidatorsDeleteErrors.update_forward_refs()
