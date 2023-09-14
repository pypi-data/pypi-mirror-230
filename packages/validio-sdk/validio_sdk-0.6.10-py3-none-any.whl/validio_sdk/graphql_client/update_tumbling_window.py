from pydantic import Field

from .base_model import BaseModel
from .fragments import WindowUpdate


class UpdateTumblingWindow(BaseModel):
    tumbling_window_update: "UpdateTumblingWindowTumblingWindowUpdate" = Field(
        alias="tumblingWindowUpdate"
    )


class UpdateTumblingWindowTumblingWindowUpdate(WindowUpdate):
    pass


UpdateTumblingWindow.update_forward_refs()
UpdateTumblingWindowTumblingWindowUpdate.update_forward_refs()
