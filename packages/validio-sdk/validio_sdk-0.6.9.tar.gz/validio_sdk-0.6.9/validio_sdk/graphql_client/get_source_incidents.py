from datetime import datetime
from typing import Annotated, Any, List, Literal, Union

from pydantic import Field

from validio_sdk.scalars import SegmentationId

from .base_model import BaseModel
from .enums import NotificationSeverity


class GetSourceIncidents(BaseModel):
    source_incidents: List[
        Annotated[
            Union[
                "GetSourceIncidentsSourceIncidentsSchemaChangeNotification",
                "GetSourceIncidentsSourceIncidentsSegmentLimitExceededNotification",
            ],
            Field(discriminator="typename__"),
        ]
    ] = Field(alias="sourceIncidents")


class GetSourceIncidentsSourceIncidentsSchemaChangeNotification(BaseModel):
    typename__: Literal["SchemaChangeNotification"] = Field(alias="__typename")
    id: Any
    severity: NotificationSeverity
    created_at: datetime = Field(alias="createdAt")
    payload: Any


class GetSourceIncidentsSourceIncidentsSegmentLimitExceededNotification(BaseModel):
    typename__: Literal["SegmentLimitExceededNotification"] = Field(alias="__typename")
    id: Any
    severity: NotificationSeverity
    created_at: datetime = Field(alias="createdAt")
    limit: int
    segmentation: "GetSourceIncidentsSourceIncidentsSegmentLimitExceededNotificationSegmentation"


class GetSourceIncidentsSourceIncidentsSegmentLimitExceededNotificationSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str


GetSourceIncidents.update_forward_refs()
GetSourceIncidentsSourceIncidentsSchemaChangeNotification.update_forward_refs()
GetSourceIncidentsSourceIncidentsSegmentLimitExceededNotification.update_forward_refs()
GetSourceIncidentsSourceIncidentsSegmentLimitExceededNotificationSegmentation.update_forward_refs()
