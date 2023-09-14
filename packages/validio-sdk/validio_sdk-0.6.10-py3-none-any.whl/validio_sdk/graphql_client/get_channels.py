from datetime import datetime
from typing import Annotated, Any, List, Literal, Optional, Union

from pydantic import Field

from .base_model import BaseModel


class GetChannels(BaseModel):
    channels: List[
        Annotated[
            Union[
                "GetChannelsChannelsChannel",
                "GetChannelsChannelsSlackChannel",
                "GetChannelsChannelsWebhookChannel",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class GetChannelsChannelsChannel(BaseModel):
    typename__: Literal["Channel"] = Field(alias="__typename")
    id: Any
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetChannelsChannelsSlackChannel(BaseModel):
    typename__: Literal["SlackChannel"] = Field(alias="__typename")
    id: Any
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetChannelsChannelsSlackChannelConfig"


class GetChannelsChannelsSlackChannelConfig(BaseModel):
    webhook_url: str = Field(alias="webhookUrl")
    timezone: Optional[str]
    application_link_url: str = Field(alias="applicationLinkUrl")


class GetChannelsChannelsWebhookChannel(BaseModel):
    typename__: Literal["WebhookChannel"] = Field(alias="__typename")
    id: Any
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetChannelsChannelsWebhookChannelConfig"


class GetChannelsChannelsWebhookChannelConfig(BaseModel):
    webhook_url: str = Field(alias="webhookUrl")
    application_link_url: str = Field(alias="applicationLinkUrl")
    auth_header: Optional[str] = Field(alias="authHeader")


GetChannels.update_forward_refs()
GetChannelsChannelsChannel.update_forward_refs()
GetChannelsChannelsSlackChannel.update_forward_refs()
GetChannelsChannelsSlackChannelConfig.update_forward_refs()
GetChannelsChannelsWebhookChannel.update_forward_refs()
GetChannelsChannelsWebhookChannelConfig.update_forward_refs()
