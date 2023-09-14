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


class ListValidators(BaseModel):
    validators_list: List[
        Annotated[
            Union[
                "ListValidatorsValidatorsListValidator",
                "ListValidatorsValidatorsListNumericValidator",
                "ListValidatorsValidatorsListCategoricalDistributionValidator",
                "ListValidatorsValidatorsListNumericDistributionValidator",
                "ListValidatorsValidatorsListVolumeValidator",
                "ListValidatorsValidatorsListNumericAnomalyValidator",
                "ListValidatorsValidatorsListRelativeTimeValidator",
                "ListValidatorsValidatorsListFreshnessValidator",
                "ListValidatorsValidatorsListRelativeVolumeValidator",
            ],
            Field(discriminator="typename__"),
        ]
    ] = Field(alias="validatorsList")


class ListValidatorsValidatorsListValidator(BaseModel):
    typename__: Literal["Validator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ListValidatorsValidatorsListValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListValidatorSourceConfig(BaseModel):
    source: "ListValidatorsValidatorsListValidatorSourceConfigSource"
    window: "ListValidatorsValidatorsListValidatorSourceConfigWindow"
    segmentation: "ListValidatorsValidatorsListValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ListValidatorsValidatorsListValidatorSourceConfigSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListValidatorSourceConfigWindow(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListValidatorSourceConfigSegmentation(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListNumericValidator(BaseModel):
    typename__: Literal["NumericValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ListValidatorsValidatorsListNumericValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ListValidatorsValidatorsListNumericValidatorConfig"


class ListValidatorsValidatorsListNumericValidatorSourceConfig(BaseModel):
    source: "ListValidatorsValidatorsListNumericValidatorSourceConfigSource"
    window: "ListValidatorsValidatorsListNumericValidatorSourceConfigWindow"
    segmentation: "ListValidatorsValidatorsListNumericValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ListValidatorsValidatorsListNumericValidatorSourceConfigSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListNumericValidatorSourceConfigWindow(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListNumericValidatorSourceConfigSegmentation(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListNumericValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    metric: NumericMetric
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ListValidatorsValidatorsListNumericValidatorConfigThresholdDynamicThreshold",
        "ListValidatorsValidatorsListNumericValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ListValidatorsValidatorsListNumericValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ListValidatorsValidatorsListNumericValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ListValidatorsValidatorsListCategoricalDistributionValidator(BaseModel):
    typename__: Literal["CategoricalDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ListValidatorsValidatorsListCategoricalDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ListValidatorsValidatorsListCategoricalDistributionValidatorConfig"
    reference_source_config: "ListValidatorsValidatorsListCategoricalDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class ListValidatorsValidatorsListCategoricalDistributionValidatorSourceConfig(
    BaseModel
):
    source: "ListValidatorsValidatorsListCategoricalDistributionValidatorSourceConfigSource"
    window: "ListValidatorsValidatorsListCategoricalDistributionValidatorSourceConfigWindow"
    segmentation: "ListValidatorsValidatorsListCategoricalDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ListValidatorsValidatorsListCategoricalDistributionValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListCategoricalDistributionValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListCategoricalDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListCategoricalDistributionValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    categorical_distribution_metric: CategoricalDistributionMetric = Field(
        alias="categoricalDistributionMetric"
    )
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ListValidatorsValidatorsListCategoricalDistributionValidatorConfigThresholdDynamicThreshold",
        "ListValidatorsValidatorsListCategoricalDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ListValidatorsValidatorsListCategoricalDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ListValidatorsValidatorsListCategoricalDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ListValidatorsValidatorsListCategoricalDistributionValidatorReferenceSourceConfig(
    BaseModel
):
    source: "ListValidatorsValidatorsListCategoricalDistributionValidatorReferenceSourceConfigSource"
    window: "ListValidatorsValidatorsListCategoricalDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class ListValidatorsValidatorsListCategoricalDistributionValidatorReferenceSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListCategoricalDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListNumericDistributionValidator(BaseModel):
    typename__: Literal["NumericDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ListValidatorsValidatorsListNumericDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ListValidatorsValidatorsListNumericDistributionValidatorConfig"
    reference_source_config: "ListValidatorsValidatorsListNumericDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class ListValidatorsValidatorsListNumericDistributionValidatorSourceConfig(BaseModel):
    source: "ListValidatorsValidatorsListNumericDistributionValidatorSourceConfigSource"
    window: "ListValidatorsValidatorsListNumericDistributionValidatorSourceConfigWindow"
    segmentation: "ListValidatorsValidatorsListNumericDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ListValidatorsValidatorsListNumericDistributionValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListNumericDistributionValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListNumericDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListNumericDistributionValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    distribution_metric: NumericDistributionMetric = Field(alias="distributionMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ListValidatorsValidatorsListNumericDistributionValidatorConfigThresholdDynamicThreshold",
        "ListValidatorsValidatorsListNumericDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ListValidatorsValidatorsListNumericDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ListValidatorsValidatorsListNumericDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ListValidatorsValidatorsListNumericDistributionValidatorReferenceSourceConfig(
    BaseModel
):
    source: "ListValidatorsValidatorsListNumericDistributionValidatorReferenceSourceConfigSource"
    window: "ListValidatorsValidatorsListNumericDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class ListValidatorsValidatorsListNumericDistributionValidatorReferenceSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListNumericDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListVolumeValidator(BaseModel):
    typename__: Literal["VolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ListValidatorsValidatorsListVolumeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ListValidatorsValidatorsListVolumeValidatorConfig"
    destination: Optional["ListValidatorsValidatorsListVolumeValidatorDestination"]


class ListValidatorsValidatorsListVolumeValidatorSourceConfig(BaseModel):
    source: "ListValidatorsValidatorsListVolumeValidatorSourceConfigSource"
    window: "ListValidatorsValidatorsListVolumeValidatorSourceConfigWindow"
    segmentation: "ListValidatorsValidatorsListVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ListValidatorsValidatorsListVolumeValidatorSourceConfigSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListVolumeValidatorSourceConfigWindow(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListVolumeValidatorSourceConfigSegmentation(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListVolumeValidatorConfig(BaseModel):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    source_fields: List[JsonPointer] = Field(alias="sourceFields")
    volume_metric: VolumeMetric = Field(alias="volumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ListValidatorsValidatorsListVolumeValidatorConfigThresholdDynamicThreshold",
        "ListValidatorsValidatorsListVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ListValidatorsValidatorsListVolumeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ListValidatorsValidatorsListVolumeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ListValidatorsValidatorsListVolumeValidatorDestination(BaseModel):
    name: str
    id: DestinationId
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListNumericAnomalyValidator(BaseModel):
    typename__: Literal["NumericAnomalyValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ListValidatorsValidatorsListNumericAnomalyValidatorSourceConfig" = (
        Field(alias="sourceConfig")
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ListValidatorsValidatorsListNumericAnomalyValidatorConfig"
    reference_source_config: "ListValidatorsValidatorsListNumericAnomalyValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )
    destination: Optional[
        "ListValidatorsValidatorsListNumericAnomalyValidatorDestination"
    ]


class ListValidatorsValidatorsListNumericAnomalyValidatorSourceConfig(BaseModel):
    source: "ListValidatorsValidatorsListNumericAnomalyValidatorSourceConfigSource"
    window: "ListValidatorsValidatorsListNumericAnomalyValidatorSourceConfigWindow"
    segmentation: "ListValidatorsValidatorsListNumericAnomalyValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ListValidatorsValidatorsListNumericAnomalyValidatorSourceConfigSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListNumericAnomalyValidatorSourceConfigWindow(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListNumericAnomalyValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListNumericAnomalyValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    numeric_anomaly_metric: NumericAnomalyMetric = Field(alias="numericAnomalyMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ListValidatorsValidatorsListNumericAnomalyValidatorConfigThresholdDynamicThreshold",
        "ListValidatorsValidatorsListNumericAnomalyValidatorConfigThresholdFixedThreshold",
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


class ListValidatorsValidatorsListNumericAnomalyValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ListValidatorsValidatorsListNumericAnomalyValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ListValidatorsValidatorsListNumericAnomalyValidatorReferenceSourceConfig(
    BaseModel
):
    source: "ListValidatorsValidatorsListNumericAnomalyValidatorReferenceSourceConfigSource"
    window: "ListValidatorsValidatorsListNumericAnomalyValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class ListValidatorsValidatorsListNumericAnomalyValidatorReferenceSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListNumericAnomalyValidatorReferenceSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListNumericAnomalyValidatorDestination(BaseModel):
    name: str
    id: DestinationId
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListRelativeTimeValidator(BaseModel):
    typename__: Literal["RelativeTimeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ListValidatorsValidatorsListRelativeTimeValidatorSourceConfig" = (
        Field(alias="sourceConfig")
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ListValidatorsValidatorsListRelativeTimeValidatorConfig"


class ListValidatorsValidatorsListRelativeTimeValidatorSourceConfig(BaseModel):
    source: "ListValidatorsValidatorsListRelativeTimeValidatorSourceConfigSource"
    window: "ListValidatorsValidatorsListRelativeTimeValidatorSourceConfigWindow"
    segmentation: "ListValidatorsValidatorsListRelativeTimeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ListValidatorsValidatorsListRelativeTimeValidatorSourceConfigSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListRelativeTimeValidatorSourceConfigWindow(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListRelativeTimeValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListRelativeTimeValidatorConfig(BaseModel):
    source_field_minuend: JsonPointer = Field(alias="sourceFieldMinuend")
    source_field_subtrahend: JsonPointer = Field(alias="sourceFieldSubtrahend")
    relative_time_metric: RelativeTimeMetric = Field(alias="relativeTimeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ListValidatorsValidatorsListRelativeTimeValidatorConfigThresholdDynamicThreshold",
        "ListValidatorsValidatorsListRelativeTimeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ListValidatorsValidatorsListRelativeTimeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ListValidatorsValidatorsListRelativeTimeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ListValidatorsValidatorsListFreshnessValidator(BaseModel):
    typename__: Literal["FreshnessValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ListValidatorsValidatorsListFreshnessValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ListValidatorsValidatorsListFreshnessValidatorConfig"


class ListValidatorsValidatorsListFreshnessValidatorSourceConfig(BaseModel):
    source: "ListValidatorsValidatorsListFreshnessValidatorSourceConfigSource"
    window: "ListValidatorsValidatorsListFreshnessValidatorSourceConfigWindow"
    segmentation: "ListValidatorsValidatorsListFreshnessValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ListValidatorsValidatorsListFreshnessValidatorSourceConfigSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListFreshnessValidatorSourceConfigWindow(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListFreshnessValidatorSourceConfigSegmentation(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListFreshnessValidatorConfig(BaseModel):
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ListValidatorsValidatorsListFreshnessValidatorConfigThresholdDynamicThreshold",
        "ListValidatorsValidatorsListFreshnessValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ListValidatorsValidatorsListFreshnessValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ListValidatorsValidatorsListFreshnessValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ListValidatorsValidatorsListRelativeVolumeValidator(BaseModel):
    typename__: Literal["RelativeVolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ListValidatorsValidatorsListRelativeVolumeValidatorSourceConfig" = (
        Field(alias="sourceConfig")
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ListValidatorsValidatorsListRelativeVolumeValidatorConfig"
    reference_source_config: "ListValidatorsValidatorsListRelativeVolumeValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class ListValidatorsValidatorsListRelativeVolumeValidatorSourceConfig(BaseModel):
    source: "ListValidatorsValidatorsListRelativeVolumeValidatorSourceConfigSource"
    window: "ListValidatorsValidatorsListRelativeVolumeValidatorSourceConfigWindow"
    segmentation: "ListValidatorsValidatorsListRelativeVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ListValidatorsValidatorsListRelativeVolumeValidatorSourceConfigSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListRelativeVolumeValidatorSourceConfigWindow(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListRelativeVolumeValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListRelativeVolumeValidatorConfig(BaseModel):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    optional_reference_source_field: Optional[JsonPointer] = Field(
        alias="optionalReferenceSourceField"
    )
    relative_volume_metric: RelativeVolumeMetric = Field(alias="relativeVolumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ListValidatorsValidatorsListRelativeVolumeValidatorConfigThresholdDynamicThreshold",
        "ListValidatorsValidatorsListRelativeVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ListValidatorsValidatorsListRelativeVolumeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ListValidatorsValidatorsListRelativeVolumeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ListValidatorsValidatorsListRelativeVolumeValidatorReferenceSourceConfig(
    BaseModel
):
    source: "ListValidatorsValidatorsListRelativeVolumeValidatorReferenceSourceConfigSource"
    window: "ListValidatorsValidatorsListRelativeVolumeValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class ListValidatorsValidatorsListRelativeVolumeValidatorReferenceSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListRelativeVolumeValidatorReferenceSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


ListValidators.update_forward_refs()
ListValidatorsValidatorsListValidator.update_forward_refs()
ListValidatorsValidatorsListValidatorSourceConfig.update_forward_refs()
ListValidatorsValidatorsListValidatorSourceConfigSource.update_forward_refs()
ListValidatorsValidatorsListValidatorSourceConfigWindow.update_forward_refs()
ListValidatorsValidatorsListValidatorSourceConfigSegmentation.update_forward_refs()
ListValidatorsValidatorsListNumericValidator.update_forward_refs()
ListValidatorsValidatorsListNumericValidatorSourceConfig.update_forward_refs()
ListValidatorsValidatorsListNumericValidatorSourceConfigSource.update_forward_refs()
ListValidatorsValidatorsListNumericValidatorSourceConfigWindow.update_forward_refs()
ListValidatorsValidatorsListNumericValidatorSourceConfigSegmentation.update_forward_refs()
ListValidatorsValidatorsListNumericValidatorConfig.update_forward_refs()
ListValidatorsValidatorsListNumericValidatorConfigThresholdDynamicThreshold.update_forward_refs()
ListValidatorsValidatorsListNumericValidatorConfigThresholdFixedThreshold.update_forward_refs()
ListValidatorsValidatorsListCategoricalDistributionValidator.update_forward_refs()
ListValidatorsValidatorsListCategoricalDistributionValidatorSourceConfig.update_forward_refs()
ListValidatorsValidatorsListCategoricalDistributionValidatorSourceConfigSource.update_forward_refs()
ListValidatorsValidatorsListCategoricalDistributionValidatorSourceConfigWindow.update_forward_refs()
ListValidatorsValidatorsListCategoricalDistributionValidatorSourceConfigSegmentation.update_forward_refs()
ListValidatorsValidatorsListCategoricalDistributionValidatorConfig.update_forward_refs()
ListValidatorsValidatorsListCategoricalDistributionValidatorConfigThresholdDynamicThreshold.update_forward_refs()
ListValidatorsValidatorsListCategoricalDistributionValidatorConfigThresholdFixedThreshold.update_forward_refs()
ListValidatorsValidatorsListCategoricalDistributionValidatorReferenceSourceConfig.update_forward_refs()
ListValidatorsValidatorsListCategoricalDistributionValidatorReferenceSourceConfigSource.update_forward_refs()
ListValidatorsValidatorsListCategoricalDistributionValidatorReferenceSourceConfigWindow.update_forward_refs()
ListValidatorsValidatorsListNumericDistributionValidator.update_forward_refs()
ListValidatorsValidatorsListNumericDistributionValidatorSourceConfig.update_forward_refs()
ListValidatorsValidatorsListNumericDistributionValidatorSourceConfigSource.update_forward_refs()
ListValidatorsValidatorsListNumericDistributionValidatorSourceConfigWindow.update_forward_refs()
ListValidatorsValidatorsListNumericDistributionValidatorSourceConfigSegmentation.update_forward_refs()
ListValidatorsValidatorsListNumericDistributionValidatorConfig.update_forward_refs()
ListValidatorsValidatorsListNumericDistributionValidatorConfigThresholdDynamicThreshold.update_forward_refs()
ListValidatorsValidatorsListNumericDistributionValidatorConfigThresholdFixedThreshold.update_forward_refs()
ListValidatorsValidatorsListNumericDistributionValidatorReferenceSourceConfig.update_forward_refs()
ListValidatorsValidatorsListNumericDistributionValidatorReferenceSourceConfigSource.update_forward_refs()
ListValidatorsValidatorsListNumericDistributionValidatorReferenceSourceConfigWindow.update_forward_refs()
ListValidatorsValidatorsListVolumeValidator.update_forward_refs()
ListValidatorsValidatorsListVolumeValidatorSourceConfig.update_forward_refs()
ListValidatorsValidatorsListVolumeValidatorSourceConfigSource.update_forward_refs()
ListValidatorsValidatorsListVolumeValidatorSourceConfigWindow.update_forward_refs()
ListValidatorsValidatorsListVolumeValidatorSourceConfigSegmentation.update_forward_refs()
ListValidatorsValidatorsListVolumeValidatorConfig.update_forward_refs()
ListValidatorsValidatorsListVolumeValidatorConfigThresholdDynamicThreshold.update_forward_refs()
ListValidatorsValidatorsListVolumeValidatorConfigThresholdFixedThreshold.update_forward_refs()
ListValidatorsValidatorsListVolumeValidatorDestination.update_forward_refs()
ListValidatorsValidatorsListNumericAnomalyValidator.update_forward_refs()
ListValidatorsValidatorsListNumericAnomalyValidatorSourceConfig.update_forward_refs()
ListValidatorsValidatorsListNumericAnomalyValidatorSourceConfigSource.update_forward_refs()
ListValidatorsValidatorsListNumericAnomalyValidatorSourceConfigWindow.update_forward_refs()
ListValidatorsValidatorsListNumericAnomalyValidatorSourceConfigSegmentation.update_forward_refs()
ListValidatorsValidatorsListNumericAnomalyValidatorConfig.update_forward_refs()
ListValidatorsValidatorsListNumericAnomalyValidatorConfigThresholdDynamicThreshold.update_forward_refs()
ListValidatorsValidatorsListNumericAnomalyValidatorConfigThresholdFixedThreshold.update_forward_refs()
ListValidatorsValidatorsListNumericAnomalyValidatorReferenceSourceConfig.update_forward_refs()
ListValidatorsValidatorsListNumericAnomalyValidatorReferenceSourceConfigSource.update_forward_refs()
ListValidatorsValidatorsListNumericAnomalyValidatorReferenceSourceConfigWindow.update_forward_refs()
ListValidatorsValidatorsListNumericAnomalyValidatorDestination.update_forward_refs()
ListValidatorsValidatorsListRelativeTimeValidator.update_forward_refs()
ListValidatorsValidatorsListRelativeTimeValidatorSourceConfig.update_forward_refs()
ListValidatorsValidatorsListRelativeTimeValidatorSourceConfigSource.update_forward_refs()
ListValidatorsValidatorsListRelativeTimeValidatorSourceConfigWindow.update_forward_refs()
ListValidatorsValidatorsListRelativeTimeValidatorSourceConfigSegmentation.update_forward_refs()
ListValidatorsValidatorsListRelativeTimeValidatorConfig.update_forward_refs()
ListValidatorsValidatorsListRelativeTimeValidatorConfigThresholdDynamicThreshold.update_forward_refs()
ListValidatorsValidatorsListRelativeTimeValidatorConfigThresholdFixedThreshold.update_forward_refs()
ListValidatorsValidatorsListFreshnessValidator.update_forward_refs()
ListValidatorsValidatorsListFreshnessValidatorSourceConfig.update_forward_refs()
ListValidatorsValidatorsListFreshnessValidatorSourceConfigSource.update_forward_refs()
ListValidatorsValidatorsListFreshnessValidatorSourceConfigWindow.update_forward_refs()
ListValidatorsValidatorsListFreshnessValidatorSourceConfigSegmentation.update_forward_refs()
ListValidatorsValidatorsListFreshnessValidatorConfig.update_forward_refs()
ListValidatorsValidatorsListFreshnessValidatorConfigThresholdDynamicThreshold.update_forward_refs()
ListValidatorsValidatorsListFreshnessValidatorConfigThresholdFixedThreshold.update_forward_refs()
ListValidatorsValidatorsListRelativeVolumeValidator.update_forward_refs()
ListValidatorsValidatorsListRelativeVolumeValidatorSourceConfig.update_forward_refs()
ListValidatorsValidatorsListRelativeVolumeValidatorSourceConfigSource.update_forward_refs()
ListValidatorsValidatorsListRelativeVolumeValidatorSourceConfigWindow.update_forward_refs()
ListValidatorsValidatorsListRelativeVolumeValidatorSourceConfigSegmentation.update_forward_refs()
ListValidatorsValidatorsListRelativeVolumeValidatorConfig.update_forward_refs()
ListValidatorsValidatorsListRelativeVolumeValidatorConfigThresholdDynamicThreshold.update_forward_refs()
ListValidatorsValidatorsListRelativeVolumeValidatorConfigThresholdFixedThreshold.update_forward_refs()
ListValidatorsValidatorsListRelativeVolumeValidatorReferenceSourceConfig.update_forward_refs()
ListValidatorsValidatorsListRelativeVolumeValidatorReferenceSourceConfigSource.update_forward_refs()
ListValidatorsValidatorsListRelativeVolumeValidatorReferenceSourceConfigWindow.update_forward_refs()
