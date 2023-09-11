from pydantic import Field

from .base_model import BaseModel
from .fragments import WindowCreation


class CreateFixedBatchWindow(BaseModel):
    fixed_batch_window_create: "CreateFixedBatchWindowFixedBatchWindowCreate" = Field(
        alias="fixedBatchWindowCreate"
    )


class CreateFixedBatchWindowFixedBatchWindowCreate(WindowCreation):
    pass


CreateFixedBatchWindow.update_forward_refs()
CreateFixedBatchWindowFixedBatchWindowCreate.update_forward_refs()
