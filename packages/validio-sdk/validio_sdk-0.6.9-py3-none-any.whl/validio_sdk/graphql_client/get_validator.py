from datetime import datetime
from typing import Annotated, List, Literal, Optional, Union

from pydantic import Field

from validio_sdk.scalars import (
    DestinationId,
    JsonFilterExpression,
    JsonPointer,
    SegmentationId,
    SourceId,
    ValidatorId,
    WindowId,
)

from .base_model import BaseModel
from .enums import (
    CategoricalDistributionMetric,
    ComparisonOperator,
    DecisionBoundsType,
    NumericAnomalyMetric,
    NumericDistributionMetric,
    NumericMetric,
    RelativeTimeMetric,
    RelativeVolumeMetric,
    VolumeMetric,
)


class GetValidator(BaseModel):
    validator: Optional[
        Annotated[
            Union[
                "GetValidatorValidatorValidator",
                "GetValidatorValidatorNumericValidator",
                "GetValidatorValidatorCategoricalDistributionValidator",
                "GetValidatorValidatorNumericDistributionValidator",
                "GetValidatorValidatorVolumeValidator",
                "GetValidatorValidatorNumericAnomalyValidator",
                "GetValidatorValidatorRelativeTimeValidator",
                "GetValidatorValidatorFreshnessValidator",
                "GetValidatorValidatorRelativeVolumeValidator",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class GetValidatorValidatorValidator(BaseModel):
    typename__: Literal["Validator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorValidatorValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorValidatorSourceConfig(BaseModel):
    source: "GetValidatorValidatorValidatorSourceConfigSource"
    window: "GetValidatorValidatorValidatorSourceConfigWindow"
    segmentation: "GetValidatorValidatorValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorValidatorValidatorSourceConfigSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorValidatorSourceConfigWindow(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorValidatorSourceConfigSegmentation(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorNumericValidator(BaseModel):
    typename__: Literal["NumericValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorValidatorNumericValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorValidatorNumericValidatorConfig"


class GetValidatorValidatorNumericValidatorSourceConfig(BaseModel):
    source: "GetValidatorValidatorNumericValidatorSourceConfigSource"
    window: "GetValidatorValidatorNumericValidatorSourceConfigWindow"
    segmentation: "GetValidatorValidatorNumericValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorValidatorNumericValidatorSourceConfigSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorNumericValidatorSourceConfigWindow(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorNumericValidatorSourceConfigSegmentation(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorNumericValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    metric: NumericMetric
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorValidatorNumericValidatorConfigThresholdDynamicThreshold",
        "GetValidatorValidatorNumericValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorValidatorNumericValidatorConfigThresholdDynamicThreshold(BaseModel):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorValidatorNumericValidatorConfigThresholdFixedThreshold(BaseModel):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorValidatorCategoricalDistributionValidator(BaseModel):
    typename__: Literal["CategoricalDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorValidatorCategoricalDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorValidatorCategoricalDistributionValidatorConfig"
    reference_source_config: "GetValidatorValidatorCategoricalDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class GetValidatorValidatorCategoricalDistributionValidatorSourceConfig(BaseModel):
    source: "GetValidatorValidatorCategoricalDistributionValidatorSourceConfigSource"
    window: "GetValidatorValidatorCategoricalDistributionValidatorSourceConfigWindow"
    segmentation: "GetValidatorValidatorCategoricalDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorValidatorCategoricalDistributionValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorCategoricalDistributionValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorCategoricalDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorCategoricalDistributionValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    categorical_distribution_metric: CategoricalDistributionMetric = Field(
        alias="categoricalDistributionMetric"
    )
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold",
        "GetValidatorValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorValidatorCategoricalDistributionValidatorReferenceSourceConfig(
    BaseModel
):
    source: "GetValidatorValidatorCategoricalDistributionValidatorReferenceSourceConfigSource"
    window: "GetValidatorValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class GetValidatorValidatorCategoricalDistributionValidatorReferenceSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorNumericDistributionValidator(BaseModel):
    typename__: Literal["NumericDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorValidatorNumericDistributionValidatorSourceConfig" = (
        Field(alias="sourceConfig")
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorValidatorNumericDistributionValidatorConfig"
    reference_source_config: "GetValidatorValidatorNumericDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class GetValidatorValidatorNumericDistributionValidatorSourceConfig(BaseModel):
    source: "GetValidatorValidatorNumericDistributionValidatorSourceConfigSource"
    window: "GetValidatorValidatorNumericDistributionValidatorSourceConfigWindow"
    segmentation: "GetValidatorValidatorNumericDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorValidatorNumericDistributionValidatorSourceConfigSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorNumericDistributionValidatorSourceConfigWindow(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorNumericDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorNumericDistributionValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    distribution_metric: NumericDistributionMetric = Field(alias="distributionMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold",
        "GetValidatorValidatorNumericDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorValidatorNumericDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorValidatorNumericDistributionValidatorReferenceSourceConfig(BaseModel):
    source: "GetValidatorValidatorNumericDistributionValidatorReferenceSourceConfigSource"
    window: "GetValidatorValidatorNumericDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class GetValidatorValidatorNumericDistributionValidatorReferenceSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorNumericDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorVolumeValidator(BaseModel):
    typename__: Literal["VolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorValidatorVolumeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorValidatorVolumeValidatorConfig"
    destination: Optional["GetValidatorValidatorVolumeValidatorDestination"]


class GetValidatorValidatorVolumeValidatorSourceConfig(BaseModel):
    source: "GetValidatorValidatorVolumeValidatorSourceConfigSource"
    window: "GetValidatorValidatorVolumeValidatorSourceConfigWindow"
    segmentation: "GetValidatorValidatorVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorValidatorVolumeValidatorSourceConfigSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorVolumeValidatorSourceConfigWindow(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorVolumeValidatorSourceConfigSegmentation(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorVolumeValidatorConfig(BaseModel):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    source_fields: List[JsonPointer] = Field(alias="sourceFields")
    volume_metric: VolumeMetric = Field(alias="volumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorValidatorVolumeValidatorConfigThresholdDynamicThreshold",
        "GetValidatorValidatorVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorValidatorVolumeValidatorConfigThresholdDynamicThreshold(BaseModel):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorValidatorVolumeValidatorConfigThresholdFixedThreshold(BaseModel):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorValidatorVolumeValidatorDestination(BaseModel):
    name: str
    id: DestinationId
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorNumericAnomalyValidator(BaseModel):
    typename__: Literal["NumericAnomalyValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorValidatorNumericAnomalyValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorValidatorNumericAnomalyValidatorConfig"
    reference_source_config: "GetValidatorValidatorNumericAnomalyValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )
    destination: Optional["GetValidatorValidatorNumericAnomalyValidatorDestination"]


class GetValidatorValidatorNumericAnomalyValidatorSourceConfig(BaseModel):
    source: "GetValidatorValidatorNumericAnomalyValidatorSourceConfigSource"
    window: "GetValidatorValidatorNumericAnomalyValidatorSourceConfigWindow"
    segmentation: "GetValidatorValidatorNumericAnomalyValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorValidatorNumericAnomalyValidatorSourceConfigSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorNumericAnomalyValidatorSourceConfigWindow(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorNumericAnomalyValidatorSourceConfigSegmentation(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorNumericAnomalyValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    numeric_anomaly_metric: NumericAnomalyMetric = Field(alias="numericAnomalyMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold",
        "GetValidatorValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    sensitivity: float
    minimum_reference_datapoints: Optional[float] = Field(
        alias="minimumReferenceDatapoints"
    )
    minimum_absolute_difference: float = Field(alias="minimumAbsoluteDifference")
    minimum_relative_difference_percent: float = Field(
        alias="minimumRelativeDifferencePercent"
    )


class GetValidatorValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorValidatorNumericAnomalyValidatorReferenceSourceConfig(BaseModel):
    source: "GetValidatorValidatorNumericAnomalyValidatorReferenceSourceConfigSource"
    window: "GetValidatorValidatorNumericAnomalyValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class GetValidatorValidatorNumericAnomalyValidatorReferenceSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorNumericAnomalyValidatorReferenceSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorNumericAnomalyValidatorDestination(BaseModel):
    name: str
    id: DestinationId
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorRelativeTimeValidator(BaseModel):
    typename__: Literal["RelativeTimeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorValidatorRelativeTimeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorValidatorRelativeTimeValidatorConfig"


class GetValidatorValidatorRelativeTimeValidatorSourceConfig(BaseModel):
    source: "GetValidatorValidatorRelativeTimeValidatorSourceConfigSource"
    window: "GetValidatorValidatorRelativeTimeValidatorSourceConfigWindow"
    segmentation: "GetValidatorValidatorRelativeTimeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorValidatorRelativeTimeValidatorSourceConfigSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorRelativeTimeValidatorSourceConfigWindow(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorRelativeTimeValidatorSourceConfigSegmentation(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorRelativeTimeValidatorConfig(BaseModel):
    source_field_minuend: JsonPointer = Field(alias="sourceFieldMinuend")
    source_field_subtrahend: JsonPointer = Field(alias="sourceFieldSubtrahend")
    relative_time_metric: RelativeTimeMetric = Field(alias="relativeTimeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold",
        "GetValidatorValidatorRelativeTimeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorValidatorRelativeTimeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorValidatorFreshnessValidator(BaseModel):
    typename__: Literal["FreshnessValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorValidatorFreshnessValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorValidatorFreshnessValidatorConfig"


class GetValidatorValidatorFreshnessValidatorSourceConfig(BaseModel):
    source: "GetValidatorValidatorFreshnessValidatorSourceConfigSource"
    window: "GetValidatorValidatorFreshnessValidatorSourceConfigWindow"
    segmentation: "GetValidatorValidatorFreshnessValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorValidatorFreshnessValidatorSourceConfigSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorFreshnessValidatorSourceConfigWindow(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorFreshnessValidatorSourceConfigSegmentation(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorFreshnessValidatorConfig(BaseModel):
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorValidatorFreshnessValidatorConfigThresholdDynamicThreshold",
        "GetValidatorValidatorFreshnessValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorValidatorFreshnessValidatorConfigThresholdDynamicThreshold(BaseModel):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorValidatorFreshnessValidatorConfigThresholdFixedThreshold(BaseModel):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorValidatorRelativeVolumeValidator(BaseModel):
    typename__: Literal["RelativeVolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorValidatorRelativeVolumeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorValidatorRelativeVolumeValidatorConfig"
    reference_source_config: "GetValidatorValidatorRelativeVolumeValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class GetValidatorValidatorRelativeVolumeValidatorSourceConfig(BaseModel):
    source: "GetValidatorValidatorRelativeVolumeValidatorSourceConfigSource"
    window: "GetValidatorValidatorRelativeVolumeValidatorSourceConfigWindow"
    segmentation: "GetValidatorValidatorRelativeVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorValidatorRelativeVolumeValidatorSourceConfigSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorRelativeVolumeValidatorSourceConfigWindow(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorRelativeVolumeValidatorSourceConfigSegmentation(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorRelativeVolumeValidatorConfig(BaseModel):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    optional_reference_source_field: Optional[JsonPointer] = Field(
        alias="optionalReferenceSourceField"
    )
    relative_volume_metric: RelativeVolumeMetric = Field(alias="relativeVolumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold",
        "GetValidatorValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorValidatorRelativeVolumeValidatorReferenceSourceConfig(BaseModel):
    source: "GetValidatorValidatorRelativeVolumeValidatorReferenceSourceConfigSource"
    window: "GetValidatorValidatorRelativeVolumeValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class GetValidatorValidatorRelativeVolumeValidatorReferenceSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorRelativeVolumeValidatorReferenceSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


GetValidator.update_forward_refs()
GetValidatorValidatorValidator.update_forward_refs()
GetValidatorValidatorValidatorSourceConfig.update_forward_refs()
GetValidatorValidatorValidatorSourceConfigSource.update_forward_refs()
GetValidatorValidatorValidatorSourceConfigWindow.update_forward_refs()
GetValidatorValidatorValidatorSourceConfigSegmentation.update_forward_refs()
GetValidatorValidatorNumericValidator.update_forward_refs()
GetValidatorValidatorNumericValidatorSourceConfig.update_forward_refs()
GetValidatorValidatorNumericValidatorSourceConfigSource.update_forward_refs()
GetValidatorValidatorNumericValidatorSourceConfigWindow.update_forward_refs()
GetValidatorValidatorNumericValidatorSourceConfigSegmentation.update_forward_refs()
GetValidatorValidatorNumericValidatorConfig.update_forward_refs()
GetValidatorValidatorNumericValidatorConfigThresholdDynamicThreshold.update_forward_refs()
GetValidatorValidatorNumericValidatorConfigThresholdFixedThreshold.update_forward_refs()
GetValidatorValidatorCategoricalDistributionValidator.update_forward_refs()
GetValidatorValidatorCategoricalDistributionValidatorSourceConfig.update_forward_refs()
GetValidatorValidatorCategoricalDistributionValidatorSourceConfigSource.update_forward_refs()
GetValidatorValidatorCategoricalDistributionValidatorSourceConfigWindow.update_forward_refs()
GetValidatorValidatorCategoricalDistributionValidatorSourceConfigSegmentation.update_forward_refs()
GetValidatorValidatorCategoricalDistributionValidatorConfig.update_forward_refs()
GetValidatorValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold.update_forward_refs()
GetValidatorValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold.update_forward_refs()
GetValidatorValidatorCategoricalDistributionValidatorReferenceSourceConfig.update_forward_refs()
GetValidatorValidatorCategoricalDistributionValidatorReferenceSourceConfigSource.update_forward_refs()
GetValidatorValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow.update_forward_refs()
GetValidatorValidatorNumericDistributionValidator.update_forward_refs()
GetValidatorValidatorNumericDistributionValidatorSourceConfig.update_forward_refs()
GetValidatorValidatorNumericDistributionValidatorSourceConfigSource.update_forward_refs()
GetValidatorValidatorNumericDistributionValidatorSourceConfigWindow.update_forward_refs()
GetValidatorValidatorNumericDistributionValidatorSourceConfigSegmentation.update_forward_refs()
GetValidatorValidatorNumericDistributionValidatorConfig.update_forward_refs()
GetValidatorValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold.update_forward_refs()
GetValidatorValidatorNumericDistributionValidatorConfigThresholdFixedThreshold.update_forward_refs()
GetValidatorValidatorNumericDistributionValidatorReferenceSourceConfig.update_forward_refs()
GetValidatorValidatorNumericDistributionValidatorReferenceSourceConfigSource.update_forward_refs()
GetValidatorValidatorNumericDistributionValidatorReferenceSourceConfigWindow.update_forward_refs()
GetValidatorValidatorVolumeValidator.update_forward_refs()
GetValidatorValidatorVolumeValidatorSourceConfig.update_forward_refs()
GetValidatorValidatorVolumeValidatorSourceConfigSource.update_forward_refs()
GetValidatorValidatorVolumeValidatorSourceConfigWindow.update_forward_refs()
GetValidatorValidatorVolumeValidatorSourceConfigSegmentation.update_forward_refs()
GetValidatorValidatorVolumeValidatorConfig.update_forward_refs()
GetValidatorValidatorVolumeValidatorConfigThresholdDynamicThreshold.update_forward_refs()
GetValidatorValidatorVolumeValidatorConfigThresholdFixedThreshold.update_forward_refs()
GetValidatorValidatorVolumeValidatorDestination.update_forward_refs()
GetValidatorValidatorNumericAnomalyValidator.update_forward_refs()
GetValidatorValidatorNumericAnomalyValidatorSourceConfig.update_forward_refs()
GetValidatorValidatorNumericAnomalyValidatorSourceConfigSource.update_forward_refs()
GetValidatorValidatorNumericAnomalyValidatorSourceConfigWindow.update_forward_refs()
GetValidatorValidatorNumericAnomalyValidatorSourceConfigSegmentation.update_forward_refs()
GetValidatorValidatorNumericAnomalyValidatorConfig.update_forward_refs()
GetValidatorValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold.update_forward_refs()
GetValidatorValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold.update_forward_refs()
GetValidatorValidatorNumericAnomalyValidatorReferenceSourceConfig.update_forward_refs()
GetValidatorValidatorNumericAnomalyValidatorReferenceSourceConfigSource.update_forward_refs()
GetValidatorValidatorNumericAnomalyValidatorReferenceSourceConfigWindow.update_forward_refs()
GetValidatorValidatorNumericAnomalyValidatorDestination.update_forward_refs()
GetValidatorValidatorRelativeTimeValidator.update_forward_refs()
GetValidatorValidatorRelativeTimeValidatorSourceConfig.update_forward_refs()
GetValidatorValidatorRelativeTimeValidatorSourceConfigSource.update_forward_refs()
GetValidatorValidatorRelativeTimeValidatorSourceConfigWindow.update_forward_refs()
GetValidatorValidatorRelativeTimeValidatorSourceConfigSegmentation.update_forward_refs()
GetValidatorValidatorRelativeTimeValidatorConfig.update_forward_refs()
GetValidatorValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold.update_forward_refs()
GetValidatorValidatorRelativeTimeValidatorConfigThresholdFixedThreshold.update_forward_refs()
GetValidatorValidatorFreshnessValidator.update_forward_refs()
GetValidatorValidatorFreshnessValidatorSourceConfig.update_forward_refs()
GetValidatorValidatorFreshnessValidatorSourceConfigSource.update_forward_refs()
GetValidatorValidatorFreshnessValidatorSourceConfigWindow.update_forward_refs()
GetValidatorValidatorFreshnessValidatorSourceConfigSegmentation.update_forward_refs()
GetValidatorValidatorFreshnessValidatorConfig.update_forward_refs()
GetValidatorValidatorFreshnessValidatorConfigThresholdDynamicThreshold.update_forward_refs()
GetValidatorValidatorFreshnessValidatorConfigThresholdFixedThreshold.update_forward_refs()
GetValidatorValidatorRelativeVolumeValidator.update_forward_refs()
GetValidatorValidatorRelativeVolumeValidatorSourceConfig.update_forward_refs()
GetValidatorValidatorRelativeVolumeValidatorSourceConfigSource.update_forward_refs()
GetValidatorValidatorRelativeVolumeValidatorSourceConfigWindow.update_forward_refs()
GetValidatorValidatorRelativeVolumeValidatorSourceConfigSegmentation.update_forward_refs()
GetValidatorValidatorRelativeVolumeValidatorConfig.update_forward_refs()
GetValidatorValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold.update_forward_refs()
GetValidatorValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold.update_forward_refs()
GetValidatorValidatorRelativeVolumeValidatorReferenceSourceConfig.update_forward_refs()
GetValidatorValidatorRelativeVolumeValidatorReferenceSourceConfigSource.update_forward_refs()
GetValidatorValidatorRelativeVolumeValidatorReferenceSourceConfigWindow.update_forward_refs()
