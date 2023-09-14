from datetime import datetime
from typing import Any, Literal, Union

from pydantic import Field

from validio_sdk.scalars import SourceId

from .base_model import BaseModel


class GetRecommendation(BaseModel):
    recommendation: Union[
        "GetRecommendationRecommendationRecommendation",
        "GetRecommendationRecommendationValidatorCreateRecommendation",
        "GetRecommendationRecommendationValidatorUpdateRecommendation",
        "GetRecommendationRecommendationValidatorDeleteRecommendation",
    ] = Field(discriminator="typename__")


class GetRecommendationRecommendationRecommendation(BaseModel):
    typename__: Literal["Recommendation"] = Field(alias="__typename")
    id: Any
    description: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class GetRecommendationRecommendationValidatorCreateRecommendation(BaseModel):
    typename__: Literal["ValidatorCreateRecommendation"] = Field(alias="__typename")
    id: Any
    description: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_id: SourceId = Field(alias="sourceId")


class GetRecommendationRecommendationValidatorUpdateRecommendation(BaseModel):
    typename__: Literal["ValidatorUpdateRecommendation"] = Field(alias="__typename")
    id: Any
    description: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_id: SourceId = Field(alias="sourceId")


class GetRecommendationRecommendationValidatorDeleteRecommendation(BaseModel):
    typename__: Literal["ValidatorDeleteRecommendation"] = Field(alias="__typename")
    id: Any
    description: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_id: SourceId = Field(alias="sourceId")


GetRecommendation.update_forward_refs()
GetRecommendationRecommendationRecommendation.update_forward_refs()
GetRecommendationRecommendationValidatorCreateRecommendation.update_forward_refs()
GetRecommendationRecommendationValidatorUpdateRecommendation.update_forward_refs()
GetRecommendationRecommendationValidatorDeleteRecommendation.update_forward_refs()
