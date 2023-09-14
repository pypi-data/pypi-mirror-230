from pydantic import Field

from .base_model import BaseModel
from .fragments import SourceUpdate


class UpdatePostgreSqlSource(BaseModel):
    postgre_sql_source_update: "UpdatePostgreSqlSourcePostgreSqlSourceUpdate" = Field(
        alias="postgreSqlSourceUpdate"
    )


class UpdatePostgreSqlSourcePostgreSqlSourceUpdate(SourceUpdate):
    pass


UpdatePostgreSqlSource.update_forward_refs()
UpdatePostgreSqlSourcePostgreSqlSourceUpdate.update_forward_refs()
