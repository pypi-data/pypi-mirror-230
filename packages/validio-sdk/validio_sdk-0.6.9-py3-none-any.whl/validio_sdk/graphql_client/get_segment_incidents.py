from typing import List

from pydantic import Field

from .base_model import BaseModel
from .fragments import ValidatorIncidents


class GetSegmentIncidents(BaseModel):
    segment_incidents: List["GetSegmentIncidentsSegmentIncidents"] = Field(
        alias="segmentIncidents"
    )


class GetSegmentIncidentsSegmentIncidents(ValidatorIncidents):
    pass


GetSegmentIncidents.update_forward_refs()
GetSegmentIncidentsSegmentIncidents.update_forward_refs()
