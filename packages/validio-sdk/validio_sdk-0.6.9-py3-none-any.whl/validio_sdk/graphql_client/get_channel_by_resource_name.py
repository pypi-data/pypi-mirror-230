from datetime import datetime
from typing import Annotated, Any, Literal, Optional, Union

from pydantic import Field

from .base_model import BaseModel


class GetChannelByResourceName(BaseModel):
    channel_by_resource_name: Optional[
        Annotated[
            Union[
                "GetChannelByResourceNameChannelByResourceNameChannel",
                "GetChannelByResourceNameChannelByResourceNameSlackChannel",
                "GetChannelByResourceNameChannelByResourceNameWebhookChannel",
            ],
            Field(discriminator="typename__"),
        ]
    ] = Field(alias="channelByResourceName")


class GetChannelByResourceNameChannelByResourceNameChannel(BaseModel):
    typename__: Literal["Channel"] = Field(alias="__typename")
    id: Any
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetChannelByResourceNameChannelByResourceNameSlackChannel(BaseModel):
    typename__: Literal["SlackChannel"] = Field(alias="__typename")
    id: Any
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetChannelByResourceNameChannelByResourceNameSlackChannelConfig"


class GetChannelByResourceNameChannelByResourceNameSlackChannelConfig(BaseModel):
    webhook_url: str = Field(alias="webhookUrl")
    timezone: Optional[str]
    application_link_url: str = Field(alias="applicationLinkUrl")


class GetChannelByResourceNameChannelByResourceNameWebhookChannel(BaseModel):
    typename__: Literal["WebhookChannel"] = Field(alias="__typename")
    id: Any
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetChannelByResourceNameChannelByResourceNameWebhookChannelConfig"


class GetChannelByResourceNameChannelByResourceNameWebhookChannelConfig(BaseModel):
    webhook_url: str = Field(alias="webhookUrl")
    application_link_url: str = Field(alias="applicationLinkUrl")
    auth_header: Optional[str] = Field(alias="authHeader")


GetChannelByResourceName.update_forward_refs()
GetChannelByResourceNameChannelByResourceNameChannel.update_forward_refs()
GetChannelByResourceNameChannelByResourceNameSlackChannel.update_forward_refs()
GetChannelByResourceNameChannelByResourceNameSlackChannelConfig.update_forward_refs()
GetChannelByResourceNameChannelByResourceNameWebhookChannel.update_forward_refs()
GetChannelByResourceNameChannelByResourceNameWebhookChannelConfig.update_forward_refs()
