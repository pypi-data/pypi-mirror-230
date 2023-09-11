from pydantic import Field

from .base_model import BaseModel
from .fragments import SourceCreation


class CreateAwsKinesisSource(BaseModel):
    aws_kinesis_source_create: "CreateAwsKinesisSourceAwsKinesisSourceCreate" = Field(
        alias="awsKinesisSourceCreate"
    )


class CreateAwsKinesisSourceAwsKinesisSourceCreate(SourceCreation):
    pass


CreateAwsKinesisSource.update_forward_refs()
CreateAwsKinesisSourceAwsKinesisSourceCreate.update_forward_refs()
