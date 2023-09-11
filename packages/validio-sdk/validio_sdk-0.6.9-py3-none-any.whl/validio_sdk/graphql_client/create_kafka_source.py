from pydantic import Field

from .base_model import BaseModel
from .fragments import SourceCreation


class CreateKafkaSource(BaseModel):
    kafka_source_create: "CreateKafkaSourceKafkaSourceCreate" = Field(
        alias="kafkaSourceCreate"
    )


class CreateKafkaSourceKafkaSourceCreate(SourceCreation):
    pass


CreateKafkaSource.update_forward_refs()
CreateKafkaSourceKafkaSourceCreate.update_forward_refs()
