from pydantic import Field

from .base_model import BaseModel
from .fragments import DestinationCreation


class CreateAwsKinesisDestination(BaseModel):
    aws_kinesis_destination_create: "CreateAwsKinesisDestinationAwsKinesisDestinationCreate" = Field(
        alias="awsKinesisDestinationCreate"
    )


class CreateAwsKinesisDestinationAwsKinesisDestinationCreate(DestinationCreation):
    pass


CreateAwsKinesisDestination.update_forward_refs()
CreateAwsKinesisDestinationAwsKinesisDestinationCreate.update_forward_refs()
