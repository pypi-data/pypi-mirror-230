from pydantic import Field

from .base_model import BaseModel
from .fragments import SourceCreation


class CreatePostgreSqlSource(BaseModel):
    postgre_sql_source_create: "CreatePostgreSqlSourcePostgreSqlSourceCreate" = Field(
        alias="postgreSqlSourceCreate"
    )


class CreatePostgreSqlSourcePostgreSqlSourceCreate(SourceCreation):
    pass


CreatePostgreSqlSource.update_forward_refs()
CreatePostgreSqlSourcePostgreSqlSourceCreate.update_forward_refs()
