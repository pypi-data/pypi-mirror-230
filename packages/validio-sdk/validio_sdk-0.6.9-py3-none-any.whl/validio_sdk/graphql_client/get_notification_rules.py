from typing import List

from pydantic import Field

from .base_model import BaseModel
from .fragments import NotificationRuleDetails


class GetNotificationRules(BaseModel):
    notification_rules: List["GetNotificationRulesNotificationRules"] = Field(
        alias="notificationRules"
    )


class GetNotificationRulesNotificationRules(NotificationRuleDetails):
    pass


GetNotificationRules.update_forward_refs()
GetNotificationRulesNotificationRules.update_forward_refs()
