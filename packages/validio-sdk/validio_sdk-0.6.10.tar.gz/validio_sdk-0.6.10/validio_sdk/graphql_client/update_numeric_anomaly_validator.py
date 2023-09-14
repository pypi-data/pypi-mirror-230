from pydantic import Field

from .base_model import BaseModel
from .fragments import ValidatorUpdate


class UpdateNumericAnomalyValidator(BaseModel):
    numeric_anomaly_validator_update: "UpdateNumericAnomalyValidatorNumericAnomalyValidatorUpdate" = Field(
        alias="numericAnomalyValidatorUpdate"
    )


class UpdateNumericAnomalyValidatorNumericAnomalyValidatorUpdate(ValidatorUpdate):
    pass


UpdateNumericAnomalyValidator.update_forward_refs()
UpdateNumericAnomalyValidatorNumericAnomalyValidatorUpdate.update_forward_refs()
