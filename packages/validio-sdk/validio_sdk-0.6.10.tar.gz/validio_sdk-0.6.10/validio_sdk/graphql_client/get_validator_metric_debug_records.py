from typing import Any, List

from pydantic import Field

from .base_model import BaseModel


class GetValidatorMetricDebugRecords(BaseModel):
    validator_metric_debug_records: List[Any] = Field(
        alias="validatorMetricDebugRecords"
    )


GetValidatorMetricDebugRecords.update_forward_refs()
