from pydantic import Field

from .base_model import BaseModel
from .fragments import WindowUpdate


class UpdateSessionizedWindow(BaseModel):
    sessionized_window_update: "UpdateSessionizedWindowSessionizedWindowUpdate" = Field(
        alias="sessionizedWindowUpdate"
    )


class UpdateSessionizedWindowSessionizedWindowUpdate(WindowUpdate):
    pass


UpdateSessionizedWindow.update_forward_refs()
UpdateSessionizedWindowSessionizedWindowUpdate.update_forward_refs()
