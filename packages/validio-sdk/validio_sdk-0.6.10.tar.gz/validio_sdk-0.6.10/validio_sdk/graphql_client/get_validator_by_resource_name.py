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


class GetValidatorByResourceName(BaseModel):
    validator_by_resource_name: Optional[
        Annotated[
            Union[
                "GetValidatorByResourceNameValidatorByResourceNameValidator",
                "GetValidatorByResourceNameValidatorByResourceNameNumericValidator",
                "GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidator",
                "GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidator",
                "GetValidatorByResourceNameValidatorByResourceNameVolumeValidator",
                "GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidator",
                "GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidator",
                "GetValidatorByResourceNameValidatorByResourceNameFreshnessValidator",
                "GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidator",
            ],
            Field(discriminator="typename__"),
        ]
    ] = Field(alias="validatorByResourceName")


class GetValidatorByResourceNameValidatorByResourceNameValidator(BaseModel):
    typename__: Literal["Validator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorByResourceNameValidatorByResourceNameValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameValidatorSourceConfig(BaseModel):
    source: "GetValidatorByResourceNameValidatorByResourceNameValidatorSourceConfigSource"
    window: "GetValidatorByResourceNameValidatorByResourceNameValidatorSourceConfigWindow"
    segmentation: "GetValidatorByResourceNameValidatorByResourceNameValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorByResourceNameValidatorByResourceNameValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameNumericValidator(BaseModel):
    typename__: Literal["NumericValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorByResourceNameValidatorByResourceNameNumericValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorByResourceNameValidatorByResourceNameNumericValidatorConfig"


class GetValidatorByResourceNameValidatorByResourceNameNumericValidatorSourceConfig(
    BaseModel
):
    source: "GetValidatorByResourceNameValidatorByResourceNameNumericValidatorSourceConfigSource"
    window: "GetValidatorByResourceNameValidatorByResourceNameNumericValidatorSourceConfigWindow"
    segmentation: "GetValidatorByResourceNameValidatorByResourceNameNumericValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorByResourceNameValidatorByResourceNameNumericValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameNumericValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameNumericValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameNumericValidatorConfig(
    BaseModel
):
    source_field: JsonPointer = Field(alias="sourceField")
    metric: NumericMetric
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorByResourceNameValidatorByResourceNameNumericValidatorConfigThresholdDynamicThreshold",
        "GetValidatorByResourceNameValidatorByResourceNameNumericValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorByResourceNameValidatorByResourceNameNumericValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorByResourceNameValidatorByResourceNameNumericValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidator(
    BaseModel
):
    typename__: Literal["CategoricalDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorConfig"
    reference_source_config: "GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorSourceConfig(
    BaseModel
):
    source: "GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorSourceConfigSource"
    window: "GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorSourceConfigWindow"
    segmentation: "GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorConfig(
    BaseModel
):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    categorical_distribution_metric: CategoricalDistributionMetric = Field(
        alias="categoricalDistributionMetric"
    )
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorConfigThresholdDynamicThreshold",
        "GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorReferenceSourceConfig(
    BaseModel
):
    source: "GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorReferenceSourceConfigSource"
    window: "GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorReferenceSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidator(
    BaseModel
):
    typename__: Literal["NumericDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorConfig"
    reference_source_config: "GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorSourceConfig(
    BaseModel
):
    source: "GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorSourceConfigSource"
    window: "GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorSourceConfigWindow"
    segmentation: "GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorConfig(
    BaseModel
):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    distribution_metric: NumericDistributionMetric = Field(alias="distributionMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorConfigThresholdDynamicThreshold",
        "GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorReferenceSourceConfig(
    BaseModel
):
    source: "GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorReferenceSourceConfigSource"
    window: "GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorReferenceSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameVolumeValidator(BaseModel):
    typename__: Literal["VolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorConfig"
    destination: Optional[
        "GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorDestination"
    ]


class GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorSourceConfig(
    BaseModel
):
    source: "GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorSourceConfigSource"
    window: "GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorSourceConfigWindow"
    segmentation: "GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorConfig(BaseModel):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    source_fields: List[JsonPointer] = Field(alias="sourceFields")
    volume_metric: VolumeMetric = Field(alias="volumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorConfigThresholdDynamicThreshold",
        "GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorDestination(
    BaseModel
):
    name: str
    id: DestinationId
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidator(
    BaseModel
):
    typename__: Literal["NumericAnomalyValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorConfig"
    reference_source_config: "GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )
    destination: Optional[
        "GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorDestination"
    ]


class GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorSourceConfig(
    BaseModel
):
    source: "GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorSourceConfigSource"
    window: "GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorSourceConfigWindow"
    segmentation: "GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorConfig(
    BaseModel
):
    source_field: JsonPointer = Field(alias="sourceField")
    numeric_anomaly_metric: NumericAnomalyMetric = Field(alias="numericAnomalyMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorConfigThresholdDynamicThreshold",
        "GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorConfigThresholdFixedThreshold",
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


class GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorReferenceSourceConfig(
    BaseModel
):
    source: "GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorReferenceSourceConfigSource"
    window: "GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorReferenceSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorReferenceSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorDestination(
    BaseModel
):
    name: str
    id: DestinationId
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidator(BaseModel):
    typename__: Literal["RelativeTimeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorConfig"


class GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorSourceConfig(
    BaseModel
):
    source: "GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorSourceConfigSource"
    window: "GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorSourceConfigWindow"
    segmentation: "GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorConfig(
    BaseModel
):
    source_field_minuend: JsonPointer = Field(alias="sourceFieldMinuend")
    source_field_subtrahend: JsonPointer = Field(alias="sourceFieldSubtrahend")
    relative_time_metric: RelativeTimeMetric = Field(alias="relativeTimeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorConfigThresholdDynamicThreshold",
        "GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorByResourceNameValidatorByResourceNameFreshnessValidator(BaseModel):
    typename__: Literal["FreshnessValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorConfig"


class GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorSourceConfig(
    BaseModel
):
    source: "GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorSourceConfigSource"
    window: "GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorSourceConfigWindow"
    segmentation: "GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorConfig(
    BaseModel
):
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorConfigThresholdDynamicThreshold",
        "GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidator(
    BaseModel
):
    typename__: Literal["RelativeVolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorConfig"
    reference_source_config: "GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorSourceConfig(
    BaseModel
):
    source: "GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorSourceConfigSource"
    window: "GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorSourceConfigWindow"
    segmentation: "GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorConfig(
    BaseModel
):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    optional_reference_source_field: Optional[JsonPointer] = Field(
        alias="optionalReferenceSourceField"
    )
    relative_volume_metric: RelativeVolumeMetric = Field(alias="relativeVolumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorConfigThresholdDynamicThreshold",
        "GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorReferenceSourceConfig(
    BaseModel
):
    source: "GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorReferenceSourceConfigSource"
    window: "GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorReferenceSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorReferenceSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


GetValidatorByResourceName.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameValidator.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameValidatorSourceConfig.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameValidatorSourceConfigSource.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameValidatorSourceConfigWindow.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameValidatorSourceConfigSegmentation.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameNumericValidator.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameNumericValidatorSourceConfig.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameNumericValidatorSourceConfigSource.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameNumericValidatorSourceConfigWindow.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameNumericValidatorSourceConfigSegmentation.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameNumericValidatorConfig.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameNumericValidatorConfigThresholdDynamicThreshold.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameNumericValidatorConfigThresholdFixedThreshold.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidator.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorSourceConfig.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorSourceConfigSource.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorSourceConfigWindow.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorSourceConfigSegmentation.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorConfig.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorConfigThresholdDynamicThreshold.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorConfigThresholdFixedThreshold.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorReferenceSourceConfig.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorReferenceSourceConfigSource.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorReferenceSourceConfigWindow.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidator.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorSourceConfig.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorSourceConfigSource.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorSourceConfigWindow.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorSourceConfigSegmentation.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorConfig.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorConfigThresholdDynamicThreshold.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorConfigThresholdFixedThreshold.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorReferenceSourceConfig.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorReferenceSourceConfigSource.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorReferenceSourceConfigWindow.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameVolumeValidator.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorSourceConfig.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorSourceConfigSource.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorSourceConfigWindow.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorSourceConfigSegmentation.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorConfig.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorConfigThresholdDynamicThreshold.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorConfigThresholdFixedThreshold.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorDestination.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidator.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorSourceConfig.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorSourceConfigSource.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorSourceConfigWindow.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorSourceConfigSegmentation.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorConfig.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorConfigThresholdDynamicThreshold.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorConfigThresholdFixedThreshold.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorReferenceSourceConfig.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorReferenceSourceConfigSource.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorReferenceSourceConfigWindow.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorDestination.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidator.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorSourceConfig.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorSourceConfigSource.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorSourceConfigWindow.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorSourceConfigSegmentation.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorConfig.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorConfigThresholdDynamicThreshold.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorConfigThresholdFixedThreshold.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameFreshnessValidator.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorSourceConfig.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorSourceConfigSource.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorSourceConfigWindow.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorSourceConfigSegmentation.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorConfig.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorConfigThresholdDynamicThreshold.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorConfigThresholdFixedThreshold.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidator.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorSourceConfig.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorSourceConfigSource.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorSourceConfigWindow.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorSourceConfigSegmentation.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorConfig.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorConfigThresholdDynamicThreshold.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorConfigThresholdFixedThreshold.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorReferenceSourceConfig.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorReferenceSourceConfigSource.update_forward_refs()
GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorReferenceSourceConfigWindow.update_forward_refs()
