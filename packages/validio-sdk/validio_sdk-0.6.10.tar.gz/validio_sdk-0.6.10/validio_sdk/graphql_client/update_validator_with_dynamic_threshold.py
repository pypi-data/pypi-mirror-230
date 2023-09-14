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
from .fragments import ErrorDetails


class UpdateValidatorWithDynamicThreshold(BaseModel):
    validator_with_dynamic_threshold_update: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdate" = Field(
        alias="validatorWithDynamicThresholdUpdate"
    )


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdate(BaseModel):
    errors: List[
        "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateErrors"
    ]
    validator: Optional[
        Annotated[
            Union[
                "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorValidator",
                "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericValidator",
                "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidator",
                "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidator",
                "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorVolumeValidator",
                "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidator",
                "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeTimeValidator",
                "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorFreshnessValidator",
                "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidator",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateErrors(
    ErrorDetails
):
    pass


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorValidator(
    BaseModel
):
    typename__: Literal["Validator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorValidatorSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorValidatorSourceConfigSource"
    window: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorValidatorSourceConfigWindow"
    segmentation: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericValidator(
    BaseModel
):
    typename__: Literal["NumericValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericValidatorConfig"


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericValidatorSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericValidatorSourceConfigSource"
    window: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericValidatorSourceConfigWindow"
    segmentation: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericValidatorConfig(
    BaseModel
):
    source_field: JsonPointer = Field(alias="sourceField")
    metric: NumericMetric
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericValidatorConfigThresholdDynamicThreshold",
        "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidator(
    BaseModel
):
    typename__: Literal["CategoricalDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidatorConfig"
    reference_source_config: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfigSource"
    window: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfigWindow"
    segmentation: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidatorConfig(
    BaseModel
):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    categorical_distribution_metric: CategoricalDistributionMetric = Field(
        alias="categoricalDistributionMetric"
    )
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold",
        "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfigSource"
    window: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidator(
    BaseModel
):
    typename__: Literal["NumericDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidatorConfig"
    reference_source_config: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidatorSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidatorSourceConfigSource"
    window: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidatorSourceConfigWindow"
    segmentation: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidatorConfig(
    BaseModel
):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    distribution_metric: NumericDistributionMetric = Field(alias="distributionMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold",
        "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidatorReferenceSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidatorReferenceSourceConfigSource"
    window: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidatorReferenceSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorVolumeValidator(
    BaseModel
):
    typename__: Literal["VolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorVolumeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorVolumeValidatorConfig"
    destination: Optional[
        "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorVolumeValidatorDestination"
    ]


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorVolumeValidatorSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorVolumeValidatorSourceConfigSource"
    window: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorVolumeValidatorSourceConfigWindow"
    segmentation: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorVolumeValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorVolumeValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorVolumeValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorVolumeValidatorConfig(
    BaseModel
):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    source_fields: List[JsonPointer] = Field(alias="sourceFields")
    volume_metric: VolumeMetric = Field(alias="volumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorVolumeValidatorConfigThresholdDynamicThreshold",
        "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorVolumeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorVolumeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorVolumeValidatorDestination(
    BaseModel
):
    name: str
    id: DestinationId
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidator(
    BaseModel
):
    typename__: Literal["NumericAnomalyValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorConfig"
    reference_source_config: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )
    destination: Optional[
        "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorDestination"
    ]


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorSourceConfigSource"
    window: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorSourceConfigWindow"
    segmentation: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorConfig(
    BaseModel
):
    source_field: JsonPointer = Field(alias="sourceField")
    numeric_anomaly_metric: NumericAnomalyMetric = Field(alias="numericAnomalyMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold",
        "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold",
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


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorReferenceSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorReferenceSourceConfigSource"
    window: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorReferenceSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorReferenceSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorDestination(
    BaseModel
):
    name: str
    id: DestinationId
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeTimeValidator(
    BaseModel
):
    typename__: Literal["RelativeTimeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeTimeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeTimeValidatorConfig"


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeTimeValidatorSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeTimeValidatorSourceConfigSource"
    window: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeTimeValidatorSourceConfigWindow"
    segmentation: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeTimeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeTimeValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeTimeValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeTimeValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeTimeValidatorConfig(
    BaseModel
):
    source_field_minuend: JsonPointer = Field(alias="sourceFieldMinuend")
    source_field_subtrahend: JsonPointer = Field(alias="sourceFieldSubtrahend")
    relative_time_metric: RelativeTimeMetric = Field(alias="relativeTimeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold",
        "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeTimeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeTimeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorFreshnessValidator(
    BaseModel
):
    typename__: Literal["FreshnessValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorFreshnessValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorFreshnessValidatorConfig"


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorFreshnessValidatorSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorFreshnessValidatorSourceConfigSource"
    window: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorFreshnessValidatorSourceConfigWindow"
    segmentation: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorFreshnessValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorFreshnessValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorFreshnessValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorFreshnessValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorFreshnessValidatorConfig(
    BaseModel
):
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorFreshnessValidatorConfigThresholdDynamicThreshold",
        "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorFreshnessValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorFreshnessValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorFreshnessValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidator(
    BaseModel
):
    typename__: Literal["RelativeVolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidatorConfig"
    reference_source_config: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidatorSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidatorSourceConfigSource"
    window: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidatorSourceConfigWindow"
    segmentation: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidatorConfig(
    BaseModel
):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    optional_reference_source_field: Optional[JsonPointer] = Field(
        alias="optionalReferenceSourceField"
    )
    relative_volume_metric: RelativeVolumeMetric = Field(alias="relativeVolumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold",
        "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidatorReferenceSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidatorReferenceSourceConfigSource"
    window: "UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidatorReferenceSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidatorReferenceSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


UpdateValidatorWithDynamicThreshold.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdate.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateErrors.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorValidator.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorValidatorSourceConfig.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorValidatorSourceConfigSource.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorValidatorSourceConfigWindow.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorValidatorSourceConfigSegmentation.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericValidator.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericValidatorSourceConfig.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericValidatorSourceConfigSource.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericValidatorSourceConfigWindow.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericValidatorSourceConfigSegmentation.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericValidatorConfig.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericValidatorConfigThresholdDynamicThreshold.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericValidatorConfigThresholdFixedThreshold.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidator.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfig.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfigSource.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfigWindow.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfigSegmentation.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidatorConfig.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfig.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfigSource.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidator.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidatorSourceConfig.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidatorSourceConfigSource.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidatorSourceConfigWindow.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidatorSourceConfigSegmentation.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidatorConfig.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidatorConfigThresholdFixedThreshold.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidatorReferenceSourceConfig.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidatorReferenceSourceConfigSource.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericDistributionValidatorReferenceSourceConfigWindow.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorVolumeValidator.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorVolumeValidatorSourceConfig.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorVolumeValidatorSourceConfigSource.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorVolumeValidatorSourceConfigWindow.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorVolumeValidatorSourceConfigSegmentation.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorVolumeValidatorConfig.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorVolumeValidatorConfigThresholdDynamicThreshold.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorVolumeValidatorConfigThresholdFixedThreshold.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorVolumeValidatorDestination.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidator.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorSourceConfig.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorSourceConfigSource.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorSourceConfigWindow.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorSourceConfigSegmentation.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorConfig.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorReferenceSourceConfig.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorReferenceSourceConfigSource.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorReferenceSourceConfigWindow.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorNumericAnomalyValidatorDestination.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeTimeValidator.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeTimeValidatorSourceConfig.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeTimeValidatorSourceConfigSource.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeTimeValidatorSourceConfigWindow.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeTimeValidatorSourceConfigSegmentation.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeTimeValidatorConfig.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeTimeValidatorConfigThresholdFixedThreshold.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorFreshnessValidator.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorFreshnessValidatorSourceConfig.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorFreshnessValidatorSourceConfigSource.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorFreshnessValidatorSourceConfigWindow.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorFreshnessValidatorSourceConfigSegmentation.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorFreshnessValidatorConfig.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorFreshnessValidatorConfigThresholdDynamicThreshold.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorFreshnessValidatorConfigThresholdFixedThreshold.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidator.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidatorSourceConfig.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidatorSourceConfigSource.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidatorSourceConfigWindow.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidatorSourceConfigSegmentation.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidatorConfig.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidatorReferenceSourceConfig.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidatorReferenceSourceConfigSource.update_forward_refs()
UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdateValidatorRelativeVolumeValidatorReferenceSourceConfigWindow.update_forward_refs()
