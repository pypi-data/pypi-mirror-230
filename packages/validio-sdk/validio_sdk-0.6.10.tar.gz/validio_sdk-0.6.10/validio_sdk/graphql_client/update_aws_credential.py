from pydantic import Field

from .base_model import BaseModel
from .fragments import CredentialUpdate


class UpdateAwsCredential(BaseModel):
    aws_credential_update: "UpdateAwsCredentialAwsCredentialUpdate" = Field(
        alias="awsCredentialUpdate"
    )


class UpdateAwsCredentialAwsCredentialUpdate(CredentialUpdate):
    pass


UpdateAwsCredential.update_forward_refs()
UpdateAwsCredentialAwsCredentialUpdate.update_forward_refs()
