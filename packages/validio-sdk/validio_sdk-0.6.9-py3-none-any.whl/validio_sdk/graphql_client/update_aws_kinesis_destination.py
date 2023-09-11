from pydantic import Field

from .base_model import BaseModel
from .fragments import DestinationUpdate


class UpdateAwsKinesisDestination(BaseModel):
    aws_kinesis_destination_update: "UpdateAwsKinesisDestinationAwsKinesisDestinationUpdate" = Field(
        alias="awsKinesisDestinationUpdate"
    )


class UpdateAwsKinesisDestinationAwsKinesisDestinationUpdate(DestinationUpdate):
    pass


UpdateAwsKinesisDestination.update_forward_refs()
UpdateAwsKinesisDestinationAwsKinesisDestinationUpdate.update_forward_refs()
