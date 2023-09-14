from pydantic import Field

from .base_model import BaseModel
from .fragments import ValidatorCreation


class CreateVolumeValidatorWithDynamicThreshold(BaseModel):
    volume_validator_with_dynamic_threshold_create: "CreateVolumeValidatorWithDynamicThresholdVolumeValidatorWithDynamicThresholdCreate" = Field(
        alias="volumeValidatorWithDynamicThresholdCreate"
    )


class CreateVolumeValidatorWithDynamicThresholdVolumeValidatorWithDynamicThresholdCreate(
    ValidatorCreation
):
    pass


CreateVolumeValidatorWithDynamicThreshold.update_forward_refs()
CreateVolumeValidatorWithDynamicThresholdVolumeValidatorWithDynamicThresholdCreate.update_forward_refs()
