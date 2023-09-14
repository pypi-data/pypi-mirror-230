from datetime import datetime
from typing import Annotated, List, Literal, Optional, Union

from pydantic import Field

from validio_sdk.scalars import SourceId, ValidatorId

from .base_model import BaseModel
from .enums import (
    CategoricalDistributionMetric,
    NumericAnomalyMetric,
    NumericDistributionMetric,
    NumericMetric,
    RelativeTimeMetric,
    RelativeVolumeMetric,
    ValidatorState,
    VolumeMetric,
)
from .fragments import SegmentationSummary


class GetSourceRecommendedValidators(BaseModel):
    source: Optional["GetSourceRecommendedValidatorsSource"]


class GetSourceRecommendedValidatorsSource(BaseModel):
    recommended_validators: List[
        Annotated[
            Union[
                "GetSourceRecommendedValidatorsSourceRecommendedValidatorsValidator",
                "GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericValidator",
                "GetSourceRecommendedValidatorsSourceRecommendedValidatorsCategoricalDistributionValidator",
                "GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericDistributionValidator",
                "GetSourceRecommendedValidatorsSourceRecommendedValidatorsVolumeValidator",
                "GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericAnomalyValidator",
                "GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeTimeValidator",
                "GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeVolumeValidator",
            ],
            Field(discriminator="typename__"),
        ]
    ] = Field(alias="recommendedValidators")


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsValidator(BaseModel):
    typename__: Literal["FreshnessValidator", "Validator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    state: ValidatorState
    progress: Optional[
        "GetSourceRecommendedValidatorsSourceRecommendedValidatorsValidatorProgress"
    ]
    stats: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsValidatorStats"
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    source_config: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsValidatorProgress(
    BaseModel
):
    percentage: float
    processed: int
    total: int


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsValidatorStats(
    BaseModel
):
    last_artifact_at: Optional[datetime] = Field(alias="lastArtifactAt")
    last_incident_at: Optional[datetime] = Field(alias="lastIncidentAt")


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsValidatorSourceConfig(
    BaseModel
):
    source: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsValidatorSourceConfigSource"
    segmentation: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsValidatorSourceConfigSegmentation"


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsValidatorSourceConfigSegmentation(
    SegmentationSummary
):
    pass


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericValidator(
    BaseModel
):
    typename__: Literal["NumericValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    state: ValidatorState
    progress: Optional[
        "GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericValidatorProgress"
    ]
    stats: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericValidatorStats"
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    source_config: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    config: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericValidatorConfig"


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericValidatorProgress(
    BaseModel
):
    percentage: float
    processed: int
    total: int


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericValidatorStats(
    BaseModel
):
    last_artifact_at: Optional[datetime] = Field(alias="lastArtifactAt")
    last_incident_at: Optional[datetime] = Field(alias="lastIncidentAt")


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericValidatorSourceConfig(
    BaseModel
):
    source: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericValidatorSourceConfigSource"
    segmentation: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericValidatorSourceConfigSegmentation"


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericValidatorSourceConfigSegmentation(
    SegmentationSummary
):
    pass


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericValidatorConfig(
    BaseModel
):
    metric: NumericMetric


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsCategoricalDistributionValidator(
    BaseModel
):
    typename__: Literal["CategoricalDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    state: ValidatorState
    progress: Optional[
        "GetSourceRecommendedValidatorsSourceRecommendedValidatorsCategoricalDistributionValidatorProgress"
    ]
    stats: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsCategoricalDistributionValidatorStats"
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    source_config: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsCategoricalDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    config: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsCategoricalDistributionValidatorConfig"


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsCategoricalDistributionValidatorProgress(
    BaseModel
):
    percentage: float
    processed: int
    total: int


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsCategoricalDistributionValidatorStats(
    BaseModel
):
    last_artifact_at: Optional[datetime] = Field(alias="lastArtifactAt")
    last_incident_at: Optional[datetime] = Field(alias="lastIncidentAt")


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsCategoricalDistributionValidatorSourceConfig(
    BaseModel
):
    source: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsCategoricalDistributionValidatorSourceConfigSource"
    segmentation: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsCategoricalDistributionValidatorSourceConfigSegmentation"


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsCategoricalDistributionValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsCategoricalDistributionValidatorSourceConfigSegmentation(
    SegmentationSummary
):
    pass


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsCategoricalDistributionValidatorConfig(
    BaseModel
):
    categorical_distribution_metric: CategoricalDistributionMetric = Field(
        alias="categoricalDistributionMetric"
    )


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericDistributionValidator(
    BaseModel
):
    typename__: Literal["NumericDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    state: ValidatorState
    progress: Optional[
        "GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericDistributionValidatorProgress"
    ]
    stats: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericDistributionValidatorStats"
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    source_config: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    config: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericDistributionValidatorConfig"


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericDistributionValidatorProgress(
    BaseModel
):
    percentage: float
    processed: int
    total: int


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericDistributionValidatorStats(
    BaseModel
):
    last_artifact_at: Optional[datetime] = Field(alias="lastArtifactAt")
    last_incident_at: Optional[datetime] = Field(alias="lastIncidentAt")


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericDistributionValidatorSourceConfig(
    BaseModel
):
    source: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericDistributionValidatorSourceConfigSource"
    segmentation: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericDistributionValidatorSourceConfigSegmentation"


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericDistributionValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericDistributionValidatorSourceConfigSegmentation(
    SegmentationSummary
):
    pass


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericDistributionValidatorConfig(
    BaseModel
):
    distribution_metric: NumericDistributionMetric = Field(alias="distributionMetric")


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsVolumeValidator(
    BaseModel
):
    typename__: Literal["VolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    state: ValidatorState
    progress: Optional[
        "GetSourceRecommendedValidatorsSourceRecommendedValidatorsVolumeValidatorProgress"
    ]
    stats: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsVolumeValidatorStats"
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    source_config: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsVolumeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    config: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsVolumeValidatorConfig"


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsVolumeValidatorProgress(
    BaseModel
):
    percentage: float
    processed: int
    total: int


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsVolumeValidatorStats(
    BaseModel
):
    last_artifact_at: Optional[datetime] = Field(alias="lastArtifactAt")
    last_incident_at: Optional[datetime] = Field(alias="lastIncidentAt")


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsVolumeValidatorSourceConfig(
    BaseModel
):
    source: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsVolumeValidatorSourceConfigSource"
    segmentation: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsVolumeValidatorSourceConfigSegmentation"


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsVolumeValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsVolumeValidatorSourceConfigSegmentation(
    SegmentationSummary
):
    pass


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsVolumeValidatorConfig(
    BaseModel
):
    volume_metric: VolumeMetric = Field(alias="volumeMetric")


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericAnomalyValidator(
    BaseModel
):
    typename__: Literal["NumericAnomalyValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    state: ValidatorState
    progress: Optional[
        "GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericAnomalyValidatorProgress"
    ]
    stats: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericAnomalyValidatorStats"
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    source_config: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericAnomalyValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    config: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericAnomalyValidatorConfig"


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericAnomalyValidatorProgress(
    BaseModel
):
    percentage: float
    processed: int
    total: int


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericAnomalyValidatorStats(
    BaseModel
):
    last_artifact_at: Optional[datetime] = Field(alias="lastArtifactAt")
    last_incident_at: Optional[datetime] = Field(alias="lastIncidentAt")


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericAnomalyValidatorSourceConfig(
    BaseModel
):
    source: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericAnomalyValidatorSourceConfigSource"
    segmentation: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericAnomalyValidatorSourceConfigSegmentation"


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericAnomalyValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericAnomalyValidatorSourceConfigSegmentation(
    SegmentationSummary
):
    pass


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericAnomalyValidatorConfig(
    BaseModel
):
    numeric_anomaly_metric: NumericAnomalyMetric = Field(alias="numericAnomalyMetric")


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeTimeValidator(
    BaseModel
):
    typename__: Literal["RelativeTimeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    state: ValidatorState
    progress: Optional[
        "GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeTimeValidatorProgress"
    ]
    stats: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeTimeValidatorStats"
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    source_config: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeTimeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    config: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeTimeValidatorConfig"


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeTimeValidatorProgress(
    BaseModel
):
    percentage: float
    processed: int
    total: int


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeTimeValidatorStats(
    BaseModel
):
    last_artifact_at: Optional[datetime] = Field(alias="lastArtifactAt")
    last_incident_at: Optional[datetime] = Field(alias="lastIncidentAt")


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeTimeValidatorSourceConfig(
    BaseModel
):
    source: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeTimeValidatorSourceConfigSource"
    segmentation: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeTimeValidatorSourceConfigSegmentation"


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeTimeValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeTimeValidatorSourceConfigSegmentation(
    SegmentationSummary
):
    pass


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeTimeValidatorConfig(
    BaseModel
):
    relative_time_metric: RelativeTimeMetric = Field(alias="relativeTimeMetric")


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeVolumeValidator(
    BaseModel
):
    typename__: Literal["RelativeVolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    state: ValidatorState
    progress: Optional[
        "GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeVolumeValidatorProgress"
    ]
    stats: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeVolumeValidatorStats"
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    source_config: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeVolumeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    config: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeVolumeValidatorConfig"


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeVolumeValidatorProgress(
    BaseModel
):
    percentage: float
    processed: int
    total: int


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeVolumeValidatorStats(
    BaseModel
):
    last_artifact_at: Optional[datetime] = Field(alias="lastArtifactAt")
    last_incident_at: Optional[datetime] = Field(alias="lastIncidentAt")


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeVolumeValidatorSourceConfig(
    BaseModel
):
    source: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeVolumeValidatorSourceConfigSource"
    segmentation: "GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeVolumeValidatorSourceConfigSegmentation"


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeVolumeValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeVolumeValidatorSourceConfigSegmentation(
    SegmentationSummary
):
    pass


class GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeVolumeValidatorConfig(
    BaseModel
):
    relative_volume_metric: RelativeVolumeMetric = Field(alias="relativeVolumeMetric")


GetSourceRecommendedValidators.update_forward_refs()
GetSourceRecommendedValidatorsSource.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsValidator.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsValidatorProgress.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsValidatorStats.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsValidatorSourceConfig.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsValidatorSourceConfigSource.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsValidatorSourceConfigSegmentation.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericValidator.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericValidatorProgress.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericValidatorStats.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericValidatorSourceConfig.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericValidatorSourceConfigSource.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericValidatorSourceConfigSegmentation.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericValidatorConfig.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsCategoricalDistributionValidator.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsCategoricalDistributionValidatorProgress.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsCategoricalDistributionValidatorStats.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsCategoricalDistributionValidatorSourceConfig.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsCategoricalDistributionValidatorSourceConfigSource.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsCategoricalDistributionValidatorSourceConfigSegmentation.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsCategoricalDistributionValidatorConfig.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericDistributionValidator.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericDistributionValidatorProgress.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericDistributionValidatorStats.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericDistributionValidatorSourceConfig.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericDistributionValidatorSourceConfigSource.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericDistributionValidatorSourceConfigSegmentation.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericDistributionValidatorConfig.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsVolumeValidator.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsVolumeValidatorProgress.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsVolumeValidatorStats.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsVolumeValidatorSourceConfig.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsVolumeValidatorSourceConfigSource.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsVolumeValidatorSourceConfigSegmentation.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsVolumeValidatorConfig.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericAnomalyValidator.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericAnomalyValidatorProgress.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericAnomalyValidatorStats.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericAnomalyValidatorSourceConfig.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericAnomalyValidatorSourceConfigSource.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericAnomalyValidatorSourceConfigSegmentation.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsNumericAnomalyValidatorConfig.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeTimeValidator.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeTimeValidatorProgress.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeTimeValidatorStats.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeTimeValidatorSourceConfig.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeTimeValidatorSourceConfigSource.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeTimeValidatorSourceConfigSegmentation.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeTimeValidatorConfig.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeVolumeValidator.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeVolumeValidatorProgress.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeVolumeValidatorStats.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeVolumeValidatorSourceConfig.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeVolumeValidatorSourceConfigSource.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeVolumeValidatorSourceConfigSegmentation.update_forward_refs()
GetSourceRecommendedValidatorsSourceRecommendedValidatorsRelativeVolumeValidatorConfig.update_forward_refs()
