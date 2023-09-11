from typing import List

from pydantic import Field

from .base_model import BaseModel
from .fragments import ErrorDetails


class ResetSource(BaseModel):
    source_reset: "ResetSourceSourceReset" = Field(alias="sourceReset")


class ResetSourceSourceReset(BaseModel):
    errors: List["ResetSourceSourceResetErrors"]


class ResetSourceSourceResetErrors(ErrorDetails):
    pass


ResetSource.update_forward_refs()
ResetSourceSourceReset.update_forward_refs()
ResetSourceSourceResetErrors.update_forward_refs()
