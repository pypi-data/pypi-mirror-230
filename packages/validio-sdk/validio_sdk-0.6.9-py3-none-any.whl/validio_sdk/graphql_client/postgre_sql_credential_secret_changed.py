from pydantic import Field

from .base_model import BaseModel
from .fragments import CredentialSecretChanged


class PostgreSqlCredentialSecretChanged(BaseModel):
    postgre_sql_credential_secret_changed: "PostgreSqlCredentialSecretChangedPostgreSqlCredentialSecretChanged" = Field(
        alias="postgreSqlCredentialSecretChanged"
    )


class PostgreSqlCredentialSecretChangedPostgreSqlCredentialSecretChanged(
    CredentialSecretChanged
):
    pass


PostgreSqlCredentialSecretChanged.update_forward_refs()
PostgreSqlCredentialSecretChangedPostgreSqlCredentialSecretChanged.update_forward_refs()
