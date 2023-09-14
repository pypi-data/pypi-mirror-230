from pydantic import Field

from .base_model import BaseModel
from .fragments import CredentialUpdate


class UpdatePostgreSqlCredential(BaseModel):
    postgre_sql_credential_update: "UpdatePostgreSqlCredentialPostgreSqlCredentialUpdate" = Field(
        alias="postgreSqlCredentialUpdate"
    )


class UpdatePostgreSqlCredentialPostgreSqlCredentialUpdate(CredentialUpdate):
    pass


UpdatePostgreSqlCredential.update_forward_refs()
UpdatePostgreSqlCredentialPostgreSqlCredentialUpdate.update_forward_refs()
