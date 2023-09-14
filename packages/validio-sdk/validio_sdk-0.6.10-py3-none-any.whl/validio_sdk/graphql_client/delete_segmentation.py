from typing import List

from pydantic import Field

from .base_model import BaseModel
from .fragments import ErrorDetails


class DeleteSegmentation(BaseModel):
    segmentations_delete: "DeleteSegmentationSegmentationsDelete" = Field(
        alias="segmentationsDelete"
    )


class DeleteSegmentationSegmentationsDelete(BaseModel):
    errors: List["DeleteSegmentationSegmentationsDeleteErrors"]


class DeleteSegmentationSegmentationsDeleteErrors(ErrorDetails):
    pass


DeleteSegmentation.update_forward_refs()
DeleteSegmentationSegmentationsDelete.update_forward_refs()
DeleteSegmentationSegmentationsDeleteErrors.update_forward_refs()
