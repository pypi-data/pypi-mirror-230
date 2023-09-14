from pydantic import Field

from .base_model import BaseModel
from .fragments import ValidatorCreation


class CreateNumericValidatorWithFixedThreshold(BaseModel):
    numeric_validator_with_fixed_threshold_create: "CreateNumericValidatorWithFixedThresholdNumericValidatorWithFixedThresholdCreate" = Field(
        alias="numericValidatorWithFixedThresholdCreate"
    )


class CreateNumericValidatorWithFixedThresholdNumericValidatorWithFixedThresholdCreate(
    ValidatorCreation
):
    pass


CreateNumericValidatorWithFixedThreshold.update_forward_refs()
CreateNumericValidatorWithFixedThresholdNumericValidatorWithFixedThresholdCreate.update_forward_refs()
