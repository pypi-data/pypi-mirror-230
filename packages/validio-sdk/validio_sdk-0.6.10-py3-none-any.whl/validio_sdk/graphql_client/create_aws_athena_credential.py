from pydantic import Field

from .base_model import BaseModel
from .fragments import CredentialCreation


class CreateAwsAthenaCredential(BaseModel):
    aws_athena_credential_create: "CreateAwsAthenaCredentialAwsAthenaCredentialCreate" = Field(
        alias="awsAthenaCredentialCreate"
    )


class CreateAwsAthenaCredentialAwsAthenaCredentialCreate(CredentialCreation):
    pass


CreateAwsAthenaCredential.update_forward_refs()
CreateAwsAthenaCredentialAwsAthenaCredentialCreate.update_forward_refs()
