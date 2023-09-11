from pydantic import Field

from .base_model import BaseModel
from .fragments import ValidatorRecommendationDismissal


class DismissValidatorRecommendation(BaseModel):
    validator_recommendation_dismiss: "DismissValidatorRecommendationValidatorRecommendationDismiss" = Field(
        alias="validatorRecommendationDismiss"
    )


class DismissValidatorRecommendationValidatorRecommendationDismiss(
    ValidatorRecommendationDismissal
):
    pass


DismissValidatorRecommendation.update_forward_refs()
DismissValidatorRecommendationValidatorRecommendationDismiss.update_forward_refs()
