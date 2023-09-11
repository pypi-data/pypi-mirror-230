from typing import List

from pydantic import Field

from .base_model import BaseModel
from .fragments import ErrorDetails


class DeleteWindows(BaseModel):
    windows_delete: "DeleteWindowsWindowsDelete" = Field(alias="windowsDelete")


class DeleteWindowsWindowsDelete(BaseModel):
    errors: List["DeleteWindowsWindowsDeleteErrors"]


class DeleteWindowsWindowsDeleteErrors(ErrorDetails):
    pass


DeleteWindows.update_forward_refs()
DeleteWindowsWindowsDelete.update_forward_refs()
DeleteWindowsWindowsDeleteErrors.update_forward_refs()
