from typing import List, Optional

from .base_model import BaseModel
from .fragments import UserDetails


class GetUsers(BaseModel):
    users: Optional[List[Optional["GetUsersUsers"]]]


class GetUsersUsers(UserDetails):
    pass


GetUsers.update_forward_refs()
GetUsersUsers.update_forward_refs()
