from datetime import datetime
from typing import Annotated, Any, Literal, Optional, Union

from pydantic import Field

from validio_sdk.scalars import CredentialId, DestinationId

from .base_model import BaseModel


class GetDestinationByResourceName(BaseModel):
    destination_by_resource_name: Optional[
        Annotated[
            Union[
                "GetDestinationByResourceNameDestinationByResourceNameDestination",
                "GetDestinationByResourceNameDestinationByResourceNameGcpBigQueryDestination",
                "GetDestinationByResourceNameDestinationByResourceNameSnowflakeDestination",
                "GetDestinationByResourceNameDestinationByResourceNameAwsKinesisDestination",
            ],
            Field(discriminator="typename__"),
        ]
    ] = Field(alias="destinationByResourceName")


class GetDestinationByResourceNameDestinationByResourceNameDestination(BaseModel):
    typename__: Literal["Destination"] = Field(alias="__typename")
    id: DestinationId
    name: str
    credential: "GetDestinationByResourceNameDestinationByResourceNameDestinationCredential"
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetDestinationByResourceNameDestinationByResourceNameDestinationCredential(
    BaseModel
):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetDestinationByResourceNameDestinationByResourceNameGcpBigQueryDestination(
    BaseModel
):
    typename__: Literal["GcpBigQueryDestination"] = Field(alias="__typename")
    id: DestinationId
    name: str
    credential: "GetDestinationByResourceNameDestinationByResourceNameGcpBigQueryDestinationCredential"
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetDestinationByResourceNameDestinationByResourceNameGcpBigQueryDestinationConfig"


class GetDestinationByResourceNameDestinationByResourceNameGcpBigQueryDestinationCredential(
    BaseModel
):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetDestinationByResourceNameDestinationByResourceNameGcpBigQueryDestinationConfig(
    BaseModel
):
    project: str
    dataset: str
    table: str


class GetDestinationByResourceNameDestinationByResourceNameSnowflakeDestination(
    BaseModel
):
    typename__: Literal["SnowflakeDestination"] = Field(alias="__typename")
    id: DestinationId
    name: str
    credential: "GetDestinationByResourceNameDestinationByResourceNameSnowflakeDestinationCredential"
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetDestinationByResourceNameDestinationByResourceNameSnowflakeDestinationConfig"


class GetDestinationByResourceNameDestinationByResourceNameSnowflakeDestinationCredential(
    BaseModel
):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetDestinationByResourceNameDestinationByResourceNameSnowflakeDestinationConfig(
    BaseModel
):
    database: str
    db_schema: Any = Field(alias="schema")
    table: str
    role: str
    warehouse: str


class GetDestinationByResourceNameDestinationByResourceNameAwsKinesisDestination(
    BaseModel
):
    typename__: Literal["AwsKinesisDestination"] = Field(alias="__typename")
    id: DestinationId
    name: str
    credential: "GetDestinationByResourceNameDestinationByResourceNameAwsKinesisDestinationCredential"
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetDestinationByResourceNameDestinationByResourceNameAwsKinesisDestinationConfig"


class GetDestinationByResourceNameDestinationByResourceNameAwsKinesisDestinationCredential(
    BaseModel
):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetDestinationByResourceNameDestinationByResourceNameAwsKinesisDestinationConfig(
    BaseModel
):
    region: str
    stream_name: str = Field(alias="streamName")
    endpoint: Optional[str]


GetDestinationByResourceName.update_forward_refs()
GetDestinationByResourceNameDestinationByResourceNameDestination.update_forward_refs()
GetDestinationByResourceNameDestinationByResourceNameDestinationCredential.update_forward_refs()
GetDestinationByResourceNameDestinationByResourceNameGcpBigQueryDestination.update_forward_refs()
GetDestinationByResourceNameDestinationByResourceNameGcpBigQueryDestinationCredential.update_forward_refs()
GetDestinationByResourceNameDestinationByResourceNameGcpBigQueryDestinationConfig.update_forward_refs()
GetDestinationByResourceNameDestinationByResourceNameSnowflakeDestination.update_forward_refs()
GetDestinationByResourceNameDestinationByResourceNameSnowflakeDestinationCredential.update_forward_refs()
GetDestinationByResourceNameDestinationByResourceNameSnowflakeDestinationConfig.update_forward_refs()
GetDestinationByResourceNameDestinationByResourceNameAwsKinesisDestination.update_forward_refs()
GetDestinationByResourceNameDestinationByResourceNameAwsKinesisDestinationCredential.update_forward_refs()
GetDestinationByResourceNameDestinationByResourceNameAwsKinesisDestinationConfig.update_forward_refs()
