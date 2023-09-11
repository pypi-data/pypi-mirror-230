from pydantic import Field

from .base_model import BaseModel
from .fragments import ValidatorCreation


class CreateFreshnessValidatorWithFixedThreshold(BaseModel):
    freshness_validator_with_fixed_threshold_create: "CreateFreshnessValidatorWithFixedThresholdFreshnessValidatorWithFixedThresholdCreate" = Field(
        alias="freshnessValidatorWithFixedThresholdCreate"
    )


class CreateFreshnessValidatorWithFixedThresholdFreshnessValidatorWithFixedThresholdCreate(
    ValidatorCreation
):
    pass


CreateFreshnessValidatorWithFixedThreshold.update_forward_refs()
CreateFreshnessValidatorWithFixedThresholdFreshnessValidatorWithFixedThresholdCreate.update_forward_refs()
