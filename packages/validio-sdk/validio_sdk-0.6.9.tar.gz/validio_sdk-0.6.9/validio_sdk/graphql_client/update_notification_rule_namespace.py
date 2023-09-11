from pydantic import Field

from .base_model import BaseModel
from .fragments import NamespaceUpdate


class UpdateNotificationRuleNamespace(BaseModel):
    notification_rule_namespace_update: "UpdateNotificationRuleNamespaceNotificationRuleNamespaceUpdate" = Field(
        alias="notificationRuleNamespaceUpdate"
    )


class UpdateNotificationRuleNamespaceNotificationRuleNamespaceUpdate(NamespaceUpdate):
    pass


UpdateNotificationRuleNamespace.update_forward_refs()
UpdateNotificationRuleNamespaceNotificationRuleNamespaceUpdate.update_forward_refs()
