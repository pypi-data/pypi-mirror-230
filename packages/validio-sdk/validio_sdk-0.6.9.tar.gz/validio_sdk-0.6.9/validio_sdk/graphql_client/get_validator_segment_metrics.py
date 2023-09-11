from datetime import datetime
from typing import List, Literal, Union

from pydantic import Field

from .base_model import BaseModel
from .enums import ComparisonOperator, DecisionBoundsType


class GetValidatorSegmentMetrics(BaseModel):
    validator_segment_metrics: Union[
        "GetValidatorSegmentMetricsValidatorSegmentMetricsValidatorMetricWithDynamicThresholdHistory",
        "GetValidatorSegmentMetricsValidatorSegmentMetricsValidatorMetricWithFixedThresholdHistory",
    ] = Field(alias="validatorSegmentMetrics", discriminator="typename__")


class GetValidatorSegmentMetricsValidatorSegmentMetricsValidatorMetricWithDynamicThresholdHistory(
    BaseModel
):
    typename__: Literal["ValidatorMetricWithDynamicThresholdHistory"] = Field(
        alias="__typename"
    )
    values: List[
        "GetValidatorSegmentMetricsValidatorSegmentMetricsValidatorMetricWithDynamicThresholdHistoryValues"
    ]


class GetValidatorSegmentMetricsValidatorSegmentMetricsValidatorMetricWithDynamicThresholdHistoryValues(
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


class GetValidatorSegmentMetricsValidatorSegmentMetricsValidatorMetricWithFixedThresholdHistory(
    BaseModel
):
    typename__: Literal["ValidatorMetricWithFixedThresholdHistory"] = Field(
        alias="__typename"
    )
    values: List[
        "GetValidatorSegmentMetricsValidatorSegmentMetricsValidatorMetricWithFixedThresholdHistoryValues"
    ]


class GetValidatorSegmentMetricsValidatorSegmentMetricsValidatorMetricWithFixedThresholdHistoryValues(
    BaseModel
):
    typename__: Literal["ValidatorMetricWithFixedThreshold"] = Field(alias="__typename")
    start_time: datetime = Field(alias="startTime")
    end_time: datetime = Field(alias="endTime")
    is_incident: bool = Field(alias="isIncident")
    value: float
    operator: ComparisonOperator
    bound: float


GetValidatorSegmentMetrics.update_forward_refs()
GetValidatorSegmentMetricsValidatorSegmentMetricsValidatorMetricWithDynamicThresholdHistory.update_forward_refs()
GetValidatorSegmentMetricsValidatorSegmentMetricsValidatorMetricWithDynamicThresholdHistoryValues.update_forward_refs()
GetValidatorSegmentMetricsValidatorSegmentMetricsValidatorMetricWithFixedThresholdHistory.update_forward_refs()
GetValidatorSegmentMetricsValidatorSegmentMetricsValidatorMetricWithFixedThresholdHistoryValues.update_forward_refs()
