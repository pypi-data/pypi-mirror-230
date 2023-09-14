from pydantic import Field

from .base_model import BaseModel
from .fragments import CredentialCreation


class CreateKafkaSaslSslPlainCredential(BaseModel):
    kafka_sasl_ssl_plain_credential_create: "CreateKafkaSaslSslPlainCredentialKafkaSaslSslPlainCredentialCreate" = Field(
        alias="kafkaSaslSslPlainCredentialCreate"
    )


class CreateKafkaSaslSslPlainCredentialKafkaSaslSslPlainCredentialCreate(
    CredentialCreation
):
    pass


CreateKafkaSaslSslPlainCredential.update_forward_refs()
CreateKafkaSaslSslPlainCredentialKafkaSaslSslPlainCredentialCreate.update_forward_refs()
