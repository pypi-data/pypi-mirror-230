from pydantic import Field

from .base_model import BaseModel
from .fragments import ValidatorCreation


class CreateRelativeVolumeValidatorWithFixedThreshold(BaseModel):
    relative_volume_validator_with_fixed_threshold_create: "CreateRelativeVolumeValidatorWithFixedThresholdRelativeVolumeValidatorWithFixedThresholdCreate" = Field(
        alias="relativeVolumeValidatorWithFixedThresholdCreate"
    )


class CreateRelativeVolumeValidatorWithFixedThresholdRelativeVolumeValidatorWithFixedThresholdCreate(
    ValidatorCreation
):
    pass


CreateRelativeVolumeValidatorWithFixedThreshold.update_forward_refs()
CreateRelativeVolumeValidatorWithFixedThresholdRelativeVolumeValidatorWithFixedThresholdCreate.update_forward_refs()
