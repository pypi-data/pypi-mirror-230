from pydantic import Field

from .base_model import BaseModel
from .fragments import SourceCreation


class CreateAwsRedshiftSource(BaseModel):
    aws_redshift_source_create: "CreateAwsRedshiftSourceAwsRedshiftSourceCreate" = (
        Field(alias="awsRedshiftSourceCreate")
    )


class CreateAwsRedshiftSourceAwsRedshiftSourceCreate(SourceCreation):
    pass


CreateAwsRedshiftSource.update_forward_refs()
CreateAwsRedshiftSourceAwsRedshiftSourceCreate.update_forward_refs()
