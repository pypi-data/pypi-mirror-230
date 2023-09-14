from datetime import datetime
from typing import Annotated, Any, List, Literal, Optional, Union

from pydantic import Field

from validio_sdk.scalars import (
    CredentialId,
    CronExpression,
    JsonTypeDefinition,
    SegmentationId,
    SourceId,
    WindowId,
)

from .base_model import BaseModel
from .enums import FileFormat, SourceState


class ListSources(BaseModel):
    sources_list: List[
        Annotated[
            Union[
                "ListSourcesSourcesListSource",
                "ListSourcesSourcesListGcpStorageSource",
                "ListSourcesSourcesListGcpBigQuerySource",
                "ListSourcesSourcesListGcpPubSubSource",
                "ListSourcesSourcesListGcpPubSubLiteSource",
                "ListSourcesSourcesListAwsAthenaSource",
                "ListSourcesSourcesListAwsKinesisSource",
                "ListSourcesSourcesListAwsRedshiftSource",
                "ListSourcesSourcesListAwsS3Source",
                "ListSourcesSourcesListPostgreSqlSource",
                "ListSourcesSourcesListSnowflakeSource",
                "ListSourcesSourcesListKafkaSource",
            ],
            Field(discriminator="typename__"),
        ]
    ] = Field(alias="sourcesList")


class ListSourcesSourcesListSource(BaseModel):
    typename__: Literal["DemoSource", "Source"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "ListSourcesSourcesListSourceCredential"
    windows: List["ListSourcesSourcesListSourceWindows"]
    segmentations: List["ListSourcesSourcesListSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListGcpStorageSource(BaseModel):
    typename__: Literal["GcpStorageSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "ListSourcesSourcesListGcpStorageSourceCredential"
    windows: List["ListSourcesSourcesListGcpStorageSourceWindows"]
    segmentations: List["ListSourcesSourcesListGcpStorageSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ListSourcesSourcesListGcpStorageSourceConfig"


class ListSourcesSourcesListGcpStorageSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListGcpStorageSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListGcpStorageSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListGcpStorageSourceConfig(BaseModel):
    project: str
    bucket: str
    folder: str
    csv: Optional["ListSourcesSourcesListGcpStorageSourceConfigCsv"]
    schedule: CronExpression
    file_pattern: Optional[str] = Field(alias="filePattern")
    file_format: Optional[FileFormat] = Field(alias="fileFormat")


class ListSourcesSourcesListGcpStorageSourceConfigCsv(BaseModel):
    null_marker: Optional[str] = Field(alias="nullMarker")
    delimiter: str


class ListSourcesSourcesListGcpBigQuerySource(BaseModel):
    typename__: Literal["GcpBigQuerySource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "ListSourcesSourcesListGcpBigQuerySourceCredential"
    windows: List["ListSourcesSourcesListGcpBigQuerySourceWindows"]
    segmentations: List["ListSourcesSourcesListGcpBigQuerySourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ListSourcesSourcesListGcpBigQuerySourceConfig"


class ListSourcesSourcesListGcpBigQuerySourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListGcpBigQuerySourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListGcpBigQuerySourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListGcpBigQuerySourceConfig(BaseModel):
    project: str
    dataset: str
    table: str
    cursor_field: str = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: CronExpression


class ListSourcesSourcesListGcpPubSubSource(BaseModel):
    typename__: Literal["GcpPubSubSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "ListSourcesSourcesListGcpPubSubSourceCredential"
    windows: List["ListSourcesSourcesListGcpPubSubSourceWindows"]
    segmentations: List["ListSourcesSourcesListGcpPubSubSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ListSourcesSourcesListGcpPubSubSourceConfig"


class ListSourcesSourcesListGcpPubSubSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListGcpPubSubSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListGcpPubSubSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListGcpPubSubSourceConfig(BaseModel):
    project: str
    subscription_id: str = Field(alias="subscriptionId")


class ListSourcesSourcesListGcpPubSubLiteSource(BaseModel):
    typename__: Literal["GcpPubSubLiteSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "ListSourcesSourcesListGcpPubSubLiteSourceCredential"
    windows: List["ListSourcesSourcesListGcpPubSubLiteSourceWindows"]
    segmentations: List["ListSourcesSourcesListGcpPubSubLiteSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ListSourcesSourcesListGcpPubSubLiteSourceConfig"


class ListSourcesSourcesListGcpPubSubLiteSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListGcpPubSubLiteSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListGcpPubSubLiteSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListGcpPubSubLiteSourceConfig(BaseModel):
    location: str
    project: str
    subscription_id: str = Field(alias="subscriptionId")


class ListSourcesSourcesListAwsAthenaSource(BaseModel):
    typename__: Literal["AwsAthenaSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "ListSourcesSourcesListAwsAthenaSourceCredential"
    windows: List["ListSourcesSourcesListAwsAthenaSourceWindows"]
    segmentations: List["ListSourcesSourcesListAwsAthenaSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ListSourcesSourcesListAwsAthenaSourceConfig"


class ListSourcesSourcesListAwsAthenaSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListAwsAthenaSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListAwsAthenaSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListAwsAthenaSourceConfig(BaseModel):
    catalog: str
    database: str
    table: str
    cursor_field: str = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: CronExpression


class ListSourcesSourcesListAwsKinesisSource(BaseModel):
    typename__: Literal["AwsKinesisSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "ListSourcesSourcesListAwsKinesisSourceCredential"
    windows: List["ListSourcesSourcesListAwsKinesisSourceWindows"]
    segmentations: List["ListSourcesSourcesListAwsKinesisSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ListSourcesSourcesListAwsKinesisSourceConfig"


class ListSourcesSourcesListAwsKinesisSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListAwsKinesisSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListAwsKinesisSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListAwsKinesisSourceConfig(BaseModel):
    region: str
    stream_name: str = Field(alias="streamName")


class ListSourcesSourcesListAwsRedshiftSource(BaseModel):
    typename__: Literal["AwsRedshiftSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "ListSourcesSourcesListAwsRedshiftSourceCredential"
    windows: List["ListSourcesSourcesListAwsRedshiftSourceWindows"]
    segmentations: List["ListSourcesSourcesListAwsRedshiftSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ListSourcesSourcesListAwsRedshiftSourceConfig"


class ListSourcesSourcesListAwsRedshiftSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListAwsRedshiftSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListAwsRedshiftSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListAwsRedshiftSourceConfig(BaseModel):
    database: str
    db_schema: Any = Field(alias="schema")
    table: str
    cursor_field: str = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: CronExpression


class ListSourcesSourcesListAwsS3Source(BaseModel):
    typename__: Literal["AwsS3Source"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "ListSourcesSourcesListAwsS3SourceCredential"
    windows: List["ListSourcesSourcesListAwsS3SourceWindows"]
    segmentations: List["ListSourcesSourcesListAwsS3SourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ListSourcesSourcesListAwsS3SourceConfig"


class ListSourcesSourcesListAwsS3SourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListAwsS3SourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListAwsS3SourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListAwsS3SourceConfig(BaseModel):
    bucket: str
    prefix: str
    csv: Optional["ListSourcesSourcesListAwsS3SourceConfigCsv"]
    schedule: CronExpression
    file_pattern: Optional[str] = Field(alias="filePattern")
    file_format: Optional[FileFormat] = Field(alias="fileFormat")


class ListSourcesSourcesListAwsS3SourceConfigCsv(BaseModel):
    null_marker: Optional[str] = Field(alias="nullMarker")
    delimiter: str


class ListSourcesSourcesListPostgreSqlSource(BaseModel):
    typename__: Literal["PostgreSqlSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "ListSourcesSourcesListPostgreSqlSourceCredential"
    windows: List["ListSourcesSourcesListPostgreSqlSourceWindows"]
    segmentations: List["ListSourcesSourcesListPostgreSqlSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ListSourcesSourcesListPostgreSqlSourceConfig"


class ListSourcesSourcesListPostgreSqlSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListPostgreSqlSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListPostgreSqlSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListPostgreSqlSourceConfig(BaseModel):
    database: str
    db_schema: Any = Field(alias="schema")
    table: str
    cursor_field: str = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: CronExpression


class ListSourcesSourcesListSnowflakeSource(BaseModel):
    typename__: Literal["SnowflakeSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "ListSourcesSourcesListSnowflakeSourceCredential"
    windows: List["ListSourcesSourcesListSnowflakeSourceWindows"]
    segmentations: List["ListSourcesSourcesListSnowflakeSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ListSourcesSourcesListSnowflakeSourceConfig"


class ListSourcesSourcesListSnowflakeSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListSnowflakeSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListSnowflakeSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListSnowflakeSourceConfig(BaseModel):
    role: Optional[str]
    warehouse: Optional[str]
    database: str
    db_schema: Any = Field(alias="schema")
    table: str
    cursor_field: str = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: CronExpression


class ListSourcesSourcesListKafkaSource(BaseModel):
    typename__: Literal["KafkaSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "ListSourcesSourcesListKafkaSourceCredential"
    windows: List["ListSourcesSourcesListKafkaSourceWindows"]
    segmentations: List["ListSourcesSourcesListKafkaSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ListSourcesSourcesListKafkaSourceConfig"


class ListSourcesSourcesListKafkaSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListKafkaSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListKafkaSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListSourcesSourcesListKafkaSourceConfig(BaseModel):
    topic: str


ListSources.update_forward_refs()
ListSourcesSourcesListSource.update_forward_refs()
ListSourcesSourcesListSourceCredential.update_forward_refs()
ListSourcesSourcesListSourceWindows.update_forward_refs()
ListSourcesSourcesListSourceSegmentations.update_forward_refs()
ListSourcesSourcesListGcpStorageSource.update_forward_refs()
ListSourcesSourcesListGcpStorageSourceCredential.update_forward_refs()
ListSourcesSourcesListGcpStorageSourceWindows.update_forward_refs()
ListSourcesSourcesListGcpStorageSourceSegmentations.update_forward_refs()
ListSourcesSourcesListGcpStorageSourceConfig.update_forward_refs()
ListSourcesSourcesListGcpStorageSourceConfigCsv.update_forward_refs()
ListSourcesSourcesListGcpBigQuerySource.update_forward_refs()
ListSourcesSourcesListGcpBigQuerySourceCredential.update_forward_refs()
ListSourcesSourcesListGcpBigQuerySourceWindows.update_forward_refs()
ListSourcesSourcesListGcpBigQuerySourceSegmentations.update_forward_refs()
ListSourcesSourcesListGcpBigQuerySourceConfig.update_forward_refs()
ListSourcesSourcesListGcpPubSubSource.update_forward_refs()
ListSourcesSourcesListGcpPubSubSourceCredential.update_forward_refs()
ListSourcesSourcesListGcpPubSubSourceWindows.update_forward_refs()
ListSourcesSourcesListGcpPubSubSourceSegmentations.update_forward_refs()
ListSourcesSourcesListGcpPubSubSourceConfig.update_forward_refs()
ListSourcesSourcesListGcpPubSubLiteSource.update_forward_refs()
ListSourcesSourcesListGcpPubSubLiteSourceCredential.update_forward_refs()
ListSourcesSourcesListGcpPubSubLiteSourceWindows.update_forward_refs()
ListSourcesSourcesListGcpPubSubLiteSourceSegmentations.update_forward_refs()
ListSourcesSourcesListGcpPubSubLiteSourceConfig.update_forward_refs()
ListSourcesSourcesListAwsAthenaSource.update_forward_refs()
ListSourcesSourcesListAwsAthenaSourceCredential.update_forward_refs()
ListSourcesSourcesListAwsAthenaSourceWindows.update_forward_refs()
ListSourcesSourcesListAwsAthenaSourceSegmentations.update_forward_refs()
ListSourcesSourcesListAwsAthenaSourceConfig.update_forward_refs()
ListSourcesSourcesListAwsKinesisSource.update_forward_refs()
ListSourcesSourcesListAwsKinesisSourceCredential.update_forward_refs()
ListSourcesSourcesListAwsKinesisSourceWindows.update_forward_refs()
ListSourcesSourcesListAwsKinesisSourceSegmentations.update_forward_refs()
ListSourcesSourcesListAwsKinesisSourceConfig.update_forward_refs()
ListSourcesSourcesListAwsRedshiftSource.update_forward_refs()
ListSourcesSourcesListAwsRedshiftSourceCredential.update_forward_refs()
ListSourcesSourcesListAwsRedshiftSourceWindows.update_forward_refs()
ListSourcesSourcesListAwsRedshiftSourceSegmentations.update_forward_refs()
ListSourcesSourcesListAwsRedshiftSourceConfig.update_forward_refs()
ListSourcesSourcesListAwsS3Source.update_forward_refs()
ListSourcesSourcesListAwsS3SourceCredential.update_forward_refs()
ListSourcesSourcesListAwsS3SourceWindows.update_forward_refs()
ListSourcesSourcesListAwsS3SourceSegmentations.update_forward_refs()
ListSourcesSourcesListAwsS3SourceConfig.update_forward_refs()
ListSourcesSourcesListAwsS3SourceConfigCsv.update_forward_refs()
ListSourcesSourcesListPostgreSqlSource.update_forward_refs()
ListSourcesSourcesListPostgreSqlSourceCredential.update_forward_refs()
ListSourcesSourcesListPostgreSqlSourceWindows.update_forward_refs()
ListSourcesSourcesListPostgreSqlSourceSegmentations.update_forward_refs()
ListSourcesSourcesListPostgreSqlSourceConfig.update_forward_refs()
ListSourcesSourcesListSnowflakeSource.update_forward_refs()
ListSourcesSourcesListSnowflakeSourceCredential.update_forward_refs()
ListSourcesSourcesListSnowflakeSourceWindows.update_forward_refs()
ListSourcesSourcesListSnowflakeSourceSegmentations.update_forward_refs()
ListSourcesSourcesListSnowflakeSourceConfig.update_forward_refs()
ListSourcesSourcesListKafkaSource.update_forward_refs()
ListSourcesSourcesListKafkaSourceCredential.update_forward_refs()
ListSourcesSourcesListKafkaSourceWindows.update_forward_refs()
ListSourcesSourcesListKafkaSourceSegmentations.update_forward_refs()
ListSourcesSourcesListKafkaSourceConfig.update_forward_refs()
