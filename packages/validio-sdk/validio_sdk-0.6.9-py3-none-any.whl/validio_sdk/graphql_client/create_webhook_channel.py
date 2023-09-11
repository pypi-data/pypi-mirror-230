from pydantic import Field

from .base_model import BaseModel
from .fragments import ChannelCreation


class CreateWebhookChannel(BaseModel):
    webhook_channel_create: "CreateWebhookChannelWebhookChannelCreate" = Field(
        alias="webhookChannelCreate"
    )


class CreateWebhookChannelWebhookChannelCreate(ChannelCreation):
    pass


CreateWebhookChannel.update_forward_refs()
CreateWebhookChannelWebhookChannelCreate.update_forward_refs()
