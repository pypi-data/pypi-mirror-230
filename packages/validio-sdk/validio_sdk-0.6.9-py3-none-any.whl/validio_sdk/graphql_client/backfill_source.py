from typing import List, Optional

from pydantic import Field

from .base_model import BaseModel
from .enums import SourceState
from .fragments import ErrorDetails


class BackfillSource(BaseModel):
    source_backfill: "BackfillSourceSourceBackfill" = Field(alias="sourceBackfill")


class BackfillSourceSourceBackfill(BaseModel):
    errors: List["BackfillSourceSourceBackfillErrors"]
    state: Optional[SourceState]


class BackfillSourceSourceBackfillErrors(ErrorDetails):
    pass


BackfillSource.update_forward_refs()
BackfillSourceSourceBackfill.update_forward_refs()
BackfillSourceSourceBackfillErrors.update_forward_refs()
