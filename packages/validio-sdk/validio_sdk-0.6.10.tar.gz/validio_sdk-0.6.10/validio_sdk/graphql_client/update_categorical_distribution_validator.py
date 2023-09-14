from pydantic import Field

from .base_model import BaseModel
from .fragments import ValidatorUpdate


class UpdateCategoricalDistributionValidator(BaseModel):
    categorical_distribution_validator_update: "UpdateCategoricalDistributionValidatorCategoricalDistributionValidatorUpdate" = Field(
        alias="categoricalDistributionValidatorUpdate"
    )


class UpdateCategoricalDistributionValidatorCategoricalDistributionValidatorUpdate(
    ValidatorUpdate
):
    pass


UpdateCategoricalDistributionValidator.update_forward_refs()
UpdateCategoricalDistributionValidatorCategoricalDistributionValidatorUpdate.update_forward_refs()
