from pydantic import Field

from .base_model import BaseModel
from .fragments import WindowCreation


class CreateSessionizedWindow(BaseModel):
    sessionized_window_create: "CreateSessionizedWindowSessionizedWindowCreate" = Field(
        alias="sessionizedWindowCreate"
    )


class CreateSessionizedWindowSessionizedWindowCreate(WindowCreation):
    pass


CreateSessionizedWindow.update_forward_refs()
CreateSessionizedWindowSessionizedWindowCreate.update_forward_refs()
