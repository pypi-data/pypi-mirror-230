from datetime import datetime
from typing import Annotated, Any, List, Literal, Union

from pydantic import Field

from validio_sdk.scalars import SegmentationId

from .base_model import BaseModel
from .enums import ComparisonOperator, DecisionBoundsType, NotificationSeverity
from .fragments import SegmentDetails


class GetIncidents(BaseModel):
    incidents: List[
        Annotated[
            Union[
                "GetIncidentsIncidentsNotification",
                "GetIncidentsIncidentsSchemaChangeNotification",
                "GetIncidentsIncidentsSegmentLimitExceededNotification",
                "GetIncidentsIncidentsValidatorThresholdFailureNotification",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class GetIncidentsIncidentsNotification(BaseModel):
    typename__: Literal["Notification"] = Field(alias="__typename")
    id: Any
    severity: NotificationSeverity


class GetIncidentsIncidentsSchemaChangeNotification(BaseModel):
    typename__: Literal["SchemaChangeNotification"] = Field(alias="__typename")
    id: Any
    severity: NotificationSeverity
    created_at: datetime = Field(alias="createdAt")
    payload: Any


class GetIncidentsIncidentsSegmentLimitExceededNotification(BaseModel):
    typename__: Literal["SegmentLimitExceededNotification"] = Field(alias="__typename")
    id: Any
    severity: NotificationSeverity
    created_at: datetime = Field(alias="createdAt")
    limit: int
    segmentation: "GetIncidentsIncidentsSegmentLimitExceededNotificationSegmentation"


class GetIncidentsIncidentsSegmentLimitExceededNotificationSegmentation(BaseModel):
    id: SegmentationId
    name: str


class GetIncidentsIncidentsValidatorThresholdFailureNotification(BaseModel):
    typename__: Literal["ValidatorThresholdFailureNotification"] = Field(
        alias="__typename"
    )
    id: Any
    severity: NotificationSeverity
    segment: "GetIncidentsIncidentsValidatorThresholdFailureNotificationSegment"
    metric: Union[
        "GetIncidentsIncidentsValidatorThresholdFailureNotificationMetricValidatorMetric",
        "GetIncidentsIncidentsValidatorThresholdFailureNotificationMetricValidatorMetricWithFixedThreshold",
        "GetIncidentsIncidentsValidatorThresholdFailureNotificationMetricValidatorMetricWithDynamicThreshold",
    ] = Field(discriminator="typename__")


class GetIncidentsIncidentsValidatorThresholdFailureNotificationSegment(SegmentDetails):
    pass


class GetIncidentsIncidentsValidatorThresholdFailureNotificationMetricValidatorMetric(
    BaseModel
):
    typename__: Literal["ValidatorMetric"] = Field(alias="__typename")
    start_time: datetime = Field(alias="startTime")
    end_time: datetime = Field(alias="endTime")
    is_incident: bool = Field(alias="isIncident")
    value: float


class GetIncidentsIncidentsValidatorThresholdFailureNotificationMetricValidatorMetricWithFixedThreshold(
    BaseModel
):
    typename__: Literal["ValidatorMetricWithFixedThreshold"] = Field(alias="__typename")
    start_time: datetime = Field(alias="startTime")
    end_time: datetime = Field(alias="endTime")
    is_incident: bool = Field(alias="isIncident")
    value: float
    operator: ComparisonOperator
    bound: float


class GetIncidentsIncidentsValidatorThresholdFailureNotificationMetricValidatorMetricWithDynamicThreshold(
    BaseModel
):
    typename__: Literal["ValidatorMetricWithDynamicThreshold"] = Field(
        alias="__typename"
    )
    start_time: datetime = Field(alias="startTime")
    end_time: datetime = Field(alias="endTime")
    is_incident: bool = Field(alias="isIncident")
    value: float
    lower_bound: float = Field(alias="lowerBound")
    upper_bound: float = Field(alias="upperBound")
    decision_bounds_type: DecisionBoundsType = Field(alias="decisionBoundsType")
    is_burn_in: bool = Field(alias="isBurnIn")


GetIncidents.update_forward_refs()
GetIncidentsIncidentsNotification.update_forward_refs()
GetIncidentsIncidentsSchemaChangeNotification.update_forward_refs()
GetIncidentsIncidentsSegmentLimitExceededNotification.update_forward_refs()
GetIncidentsIncidentsSegmentLimitExceededNotificationSegmentation.update_forward_refs()
GetIncidentsIncidentsValidatorThresholdFailureNotification.update_forward_refs()
GetIncidentsIncidentsValidatorThresholdFailureNotificationSegment.update_forward_refs()
GetIncidentsIncidentsValidatorThresholdFailureNotificationMetricValidatorMetric.update_forward_refs()
GetIncidentsIncidentsValidatorThresholdFailureNotificationMetricValidatorMetricWithFixedThreshold.update_forward_refs()
GetIncidentsIncidentsValidatorThresholdFailureNotificationMetricValidatorMetricWithDynamicThreshold.update_forward_refs()
