from typing import Optional

from pydantic import Field

from .base_model import BaseModel
from .fragments import UserDetails


class GetUserByResourceName(BaseModel):
    user_by_resource_name: Optional["GetUserByResourceNameUserByResourceName"] = Field(
        alias="userByResourceName"
    )


class GetUserByResourceNameUserByResourceName(UserDetails):
    pass


GetUserByResourceName.update_forward_refs()
GetUserByResourceNameUserByResourceName.update_forward_refs()
