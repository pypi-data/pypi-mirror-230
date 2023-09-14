from typing import List, Optional

from pydantic import Field

from .base_model import BaseModel
from .enums import SourceState
from .fragments import ErrorDetails


class StartSource(BaseModel):
    source_start: "StartSourceSourceStart" = Field(alias="sourceStart")


class StartSourceSourceStart(BaseModel):
    errors: List["StartSourceSourceStartErrors"]
    state: Optional[SourceState]


class StartSourceSourceStartErrors(ErrorDetails):
    pass


StartSource.update_forward_refs()
StartSourceSourceStart.update_forward_refs()
StartSourceSourceStartErrors.update_forward_refs()
