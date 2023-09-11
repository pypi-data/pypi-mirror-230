from typing import List

from pydantic import Field

from .base_model import BaseModel
from .fragments import ErrorDetails


class DeleteSources(BaseModel):
    sources_delete: "DeleteSourcesSourcesDelete" = Field(alias="sourcesDelete")


class DeleteSourcesSourcesDelete(BaseModel):
    errors: List["DeleteSourcesSourcesDeleteErrors"]


class DeleteSourcesSourcesDeleteErrors(ErrorDetails):
    pass


DeleteSources.update_forward_refs()
DeleteSourcesSourcesDelete.update_forward_refs()
DeleteSourcesSourcesDeleteErrors.update_forward_refs()
