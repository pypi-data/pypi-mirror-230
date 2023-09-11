from datetime import datetime
from typing import Annotated, Any, List, Literal, Optional, Union

from pydantic import Field

from validio_sdk.scalars import CredentialId, DestinationId

from .base_model import BaseModel


class ListDestinations(BaseModel):
    destinations_list: List[
        Annotated[
            Union[
                "ListDestinationsDestinationsListDestination",
                "ListDestinationsDestinationsListGcpBigQueryDestination",
                "ListDestinationsDestinationsListSnowflakeDestination",
                "ListDestinationsDestinationsListAwsKinesisDestination",
            ],
            Field(discriminator="typename__"),
        ]
    ] = Field(alias="destinationsList")


class ListDestinationsDestinationsListDestination(BaseModel):
    typename__: Literal["Destination"] = Field(alias="__typename")
    id: DestinationId
    name: str
    credential: "ListDestinationsDestinationsListDestinationCredential"
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListDestinationsDestinationsListDestinationCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListDestinationsDestinationsListGcpBigQueryDestination(BaseModel):
    typename__: Literal["GcpBigQueryDestination"] = Field(alias="__typename")
    id: DestinationId
    name: str
    credential: "ListDestinationsDestinationsListGcpBigQueryDestinationCredential"
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ListDestinationsDestinationsListGcpBigQueryDestinationConfig"


class ListDestinationsDestinationsListGcpBigQueryDestinationCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListDestinationsDestinationsListGcpBigQueryDestinationConfig(BaseModel):
    project: str
    dataset: str
    table: str


class ListDestinationsDestinationsListSnowflakeDestination(BaseModel):
    typename__: Literal["SnowflakeDestination"] = Field(alias="__typename")
    id: DestinationId
    name: str
    credential: "ListDestinationsDestinationsListSnowflakeDestinationCredential"
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ListDestinationsDestinationsListSnowflakeDestinationConfig"


class ListDestinationsDestinationsListSnowflakeDestinationCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListDestinationsDestinationsListSnowflakeDestinationConfig(BaseModel):
    database: str
    db_schema: Any = Field(alias="schema")
    table: str
    role: str
    warehouse: str


class ListDestinationsDestinationsListAwsKinesisDestination(BaseModel):
    typename__: Literal["AwsKinesisDestination"] = Field(alias="__typename")
    id: DestinationId
    name: str
    credential: "ListDestinationsDestinationsListAwsKinesisDestinationCredential"
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ListDestinationsDestinationsListAwsKinesisDestinationConfig"


class ListDestinationsDestinationsListAwsKinesisDestinationCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListDestinationsDestinationsListAwsKinesisDestinationConfig(BaseModel):
    region: str
    stream_name: str = Field(alias="streamName")
    endpoint: Optional[str]


ListDestinations.update_forward_refs()
ListDestinationsDestinationsListDestination.update_forward_refs()
ListDestinationsDestinationsListDestinationCredential.update_forward_refs()
ListDestinationsDestinationsListGcpBigQueryDestination.update_forward_refs()
ListDestinationsDestinationsListGcpBigQueryDestinationCredential.update_forward_refs()
ListDestinationsDestinationsListGcpBigQueryDestinationConfig.update_forward_refs()
ListDestinationsDestinationsListSnowflakeDestination.update_forward_refs()
ListDestinationsDestinationsListSnowflakeDestinationCredential.update_forward_refs()
ListDestinationsDestinationsListSnowflakeDestinationConfig.update_forward_refs()
ListDestinationsDestinationsListAwsKinesisDestination.update_forward_refs()
ListDestinationsDestinationsListAwsKinesisDestinationCredential.update_forward_refs()
ListDestinationsDestinationsListAwsKinesisDestinationConfig.update_forward_refs()
