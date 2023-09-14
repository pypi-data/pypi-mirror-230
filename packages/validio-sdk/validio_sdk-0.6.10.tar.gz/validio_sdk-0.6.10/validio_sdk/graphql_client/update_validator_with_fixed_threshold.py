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


class UpdateValidatorWithFixedThreshold(BaseModel):
    validator_with_fixed_threshold_update: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdate" = Field(
        alias="validatorWithFixedThresholdUpdate"
    )


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdate(BaseModel):
    errors: List[
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateErrors"
    ]
    validator: Optional[
        Annotated[
            Union[
                "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorValidator",
                "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidator",
                "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidator",
                "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidator",
                "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidator",
                "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidator",
                "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidator",
                "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidator",
                "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidator",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateErrors(
    ErrorDetails
):
    pass


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorValidator(
    BaseModel
):
    typename__: Literal["Validator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorValidatorSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorValidatorSourceConfigSource"
    window: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorValidatorSourceConfigWindow"
    segmentation: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidator(
    BaseModel
):
    typename__: Literal["NumericValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorConfig"


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorSourceConfigSource"
    window: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorSourceConfigWindow"
    segmentation: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorConfig(
    BaseModel
):
    source_field: JsonPointer = Field(alias="sourceField")
    metric: NumericMetric
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorConfigThresholdDynamicThreshold",
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidator(
    BaseModel
):
    typename__: Literal["CategoricalDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorConfig"
    reference_source_config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfigSource"
    window: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfigWindow"
    segmentation: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorConfig(
    BaseModel
):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    categorical_distribution_metric: CategoricalDistributionMetric = Field(
        alias="categoricalDistributionMetric"
    )
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold",
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfigSource"
    window: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidator(
    BaseModel
):
    typename__: Literal["NumericDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorConfig"
    reference_source_config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorSourceConfigSource"
    window: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorSourceConfigWindow"
    segmentation: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorConfig(
    BaseModel
):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    distribution_metric: NumericDistributionMetric = Field(alias="distributionMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold",
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorReferenceSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorReferenceSourceConfigSource"
    window: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorReferenceSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidator(
    BaseModel
):
    typename__: Literal["VolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorConfig"
    destination: Optional[
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorDestination"
    ]


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorSourceConfigSource"
    window: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorSourceConfigWindow"
    segmentation: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorConfig(
    BaseModel
):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    source_fields: List[JsonPointer] = Field(alias="sourceFields")
    volume_metric: VolumeMetric = Field(alias="volumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorConfigThresholdDynamicThreshold",
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorDestination(
    BaseModel
):
    name: str
    id: DestinationId
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidator(
    BaseModel
):
    typename__: Literal["NumericAnomalyValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorConfig"
    reference_source_config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )
    destination: Optional[
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorDestination"
    ]


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorSourceConfigSource"
    window: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorSourceConfigWindow"
    segmentation: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorConfig(
    BaseModel
):
    source_field: JsonPointer = Field(alias="sourceField")
    numeric_anomaly_metric: NumericAnomalyMetric = Field(alias="numericAnomalyMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold",
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold",
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


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorReferenceSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorReferenceSourceConfigSource"
    window: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorReferenceSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorReferenceSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorDestination(
    BaseModel
):
    name: str
    id: DestinationId
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidator(
    BaseModel
):
    typename__: Literal["RelativeTimeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorConfig"


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorSourceConfigSource"
    window: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorSourceConfigWindow"
    segmentation: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorConfig(
    BaseModel
):
    source_field_minuend: JsonPointer = Field(alias="sourceFieldMinuend")
    source_field_subtrahend: JsonPointer = Field(alias="sourceFieldSubtrahend")
    relative_time_metric: RelativeTimeMetric = Field(alias="relativeTimeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold",
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidator(
    BaseModel
):
    typename__: Literal["FreshnessValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorConfig"


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorSourceConfigSource"
    window: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorSourceConfigWindow"
    segmentation: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorConfig(
    BaseModel
):
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorConfigThresholdDynamicThreshold",
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidator(
    BaseModel
):
    typename__: Literal["RelativeVolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorConfig"
    reference_source_config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorSourceConfigSource"
    window: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorSourceConfigWindow"
    segmentation: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorConfig(
    BaseModel
):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    optional_reference_source_field: Optional[JsonPointer] = Field(
        alias="optionalReferenceSourceField"
    )
    relative_volume_metric: RelativeVolumeMetric = Field(alias="relativeVolumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold",
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorReferenceSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorReferenceSourceConfigSource"
    window: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorReferenceSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorReferenceSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


UpdateValidatorWithFixedThreshold.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdate.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateErrors.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorValidator.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorValidatorSourceConfig.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorValidatorSourceConfigSource.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorValidatorSourceConfigWindow.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorValidatorSourceConfigSegmentation.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidator.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorSourceConfig.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorSourceConfigSource.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorSourceConfigWindow.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorSourceConfigSegmentation.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorConfig.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorConfigThresholdDynamicThreshold.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorConfigThresholdFixedThreshold.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidator.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfig.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfigSource.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfigWindow.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfigSegmentation.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorConfig.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfig.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfigSource.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidator.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorSourceConfig.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorSourceConfigSource.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorSourceConfigWindow.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorSourceConfigSegmentation.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorConfig.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorConfigThresholdFixedThreshold.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorReferenceSourceConfig.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorReferenceSourceConfigSource.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorReferenceSourceConfigWindow.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidator.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorSourceConfig.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorSourceConfigSource.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorSourceConfigWindow.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorSourceConfigSegmentation.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorConfig.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorConfigThresholdDynamicThreshold.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorConfigThresholdFixedThreshold.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorDestination.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidator.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorSourceConfig.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorSourceConfigSource.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorSourceConfigWindow.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorSourceConfigSegmentation.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorConfig.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorReferenceSourceConfig.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorReferenceSourceConfigSource.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorReferenceSourceConfigWindow.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorDestination.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidator.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorSourceConfig.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorSourceConfigSource.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorSourceConfigWindow.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorSourceConfigSegmentation.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorConfig.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorConfigThresholdFixedThreshold.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidator.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorSourceConfig.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorSourceConfigSource.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorSourceConfigWindow.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorSourceConfigSegmentation.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorConfig.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorConfigThresholdDynamicThreshold.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorConfigThresholdFixedThreshold.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidator.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorSourceConfig.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorSourceConfigSource.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorSourceConfigWindow.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorSourceConfigSegmentation.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorConfig.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorReferenceSourceConfig.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorReferenceSourceConfigSource.update_forward_refs()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorReferenceSourceConfigWindow.update_forward_refs()
