from pydantic import Field

from .base_model import BaseModel
from .fragments import WindowCreation


class CreateFileWindow(BaseModel):
    file_window_create: "CreateFileWindowFileWindowCreate" = Field(
        alias="fileWindowCreate"
    )


class CreateFileWindowFileWindowCreate(WindowCreation):
    pass


CreateFileWindow.update_forward_refs()
CreateFileWindowFileWindowCreate.update_forward_refs()
