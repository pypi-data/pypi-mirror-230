from pydantic import Field

from .base_model import BaseModel
from .fragments import ValidatorCreation


class CreateNumericValidatorWithDynamicThreshold(BaseModel):
    numeric_validator_with_dynamic_threshold_create: "CreateNumericValidatorWithDynamicThresholdNumericValidatorWithDynamicThresholdCreate" = Field(
        alias="numericValidatorWithDynamicThresholdCreate"
    )


class CreateNumericValidatorWithDynamicThresholdNumericValidatorWithDynamicThresholdCreate(
    ValidatorCreation
):
    pass


CreateNumericValidatorWithDynamicThreshold.update_forward_refs()
CreateNumericValidatorWithDynamicThresholdNumericValidatorWithDynamicThresholdCreate.update_forward_refs()
