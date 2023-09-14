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


class GetSource(BaseModel):
    source: Optional[
        Annotated[
            Union[
                "GetSourceSourceSource",
                "GetSourceSourceGcpStorageSource",
                "GetSourceSourceGcpBigQuerySource",
                "GetSourceSourceGcpPubSubSource",
                "GetSourceSourceGcpPubSubLiteSource",
                "GetSourceSourceAwsAthenaSource",
                "GetSourceSourceAwsKinesisSource",
                "GetSourceSourceAwsRedshiftSource",
                "GetSourceSourceAwsS3Source",
                "GetSourceSourcePostgreSqlSource",
                "GetSourceSourceSnowflakeSource",
                "GetSourceSourceKafkaSource",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class GetSourceSourceSource(BaseModel):
    typename__: Literal["DemoSource", "Source"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceSourceSourceCredential"
    windows: List["GetSourceSourceSourceWindows"]
    segmentations: List["GetSourceSourceSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceGcpStorageSource(BaseModel):
    typename__: Literal["GcpStorageSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceSourceGcpStorageSourceCredential"
    windows: List["GetSourceSourceGcpStorageSourceWindows"]
    segmentations: List["GetSourceSourceGcpStorageSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetSourceSourceGcpStorageSourceConfig"


class GetSourceSourceGcpStorageSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceGcpStorageSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceGcpStorageSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceGcpStorageSourceConfig(BaseModel):
    project: str
    bucket: str
    folder: str
    csv: Optional["GetSourceSourceGcpStorageSourceConfigCsv"]
    schedule: CronExpression
    file_pattern: Optional[str] = Field(alias="filePattern")
    file_format: Optional[FileFormat] = Field(alias="fileFormat")


class GetSourceSourceGcpStorageSourceConfigCsv(BaseModel):
    null_marker: Optional[str] = Field(alias="nullMarker")
    delimiter: str


class GetSourceSourceGcpBigQuerySource(BaseModel):
    typename__: Literal["GcpBigQuerySource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceSourceGcpBigQuerySourceCredential"
    windows: List["GetSourceSourceGcpBigQuerySourceWindows"]
    segmentations: List["GetSourceSourceGcpBigQuerySourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetSourceSourceGcpBigQuerySourceConfig"


class GetSourceSourceGcpBigQuerySourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceGcpBigQuerySourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceGcpBigQuerySourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceGcpBigQuerySourceConfig(BaseModel):
    project: str
    dataset: str
    table: str
    cursor_field: str = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: CronExpression


class GetSourceSourceGcpPubSubSource(BaseModel):
    typename__: Literal["GcpPubSubSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceSourceGcpPubSubSourceCredential"
    windows: List["GetSourceSourceGcpPubSubSourceWindows"]
    segmentations: List["GetSourceSourceGcpPubSubSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetSourceSourceGcpPubSubSourceConfig"


class GetSourceSourceGcpPubSubSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceGcpPubSubSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceGcpPubSubSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceGcpPubSubSourceConfig(BaseModel):
    project: str
    subscription_id: str = Field(alias="subscriptionId")


class GetSourceSourceGcpPubSubLiteSource(BaseModel):
    typename__: Literal["GcpPubSubLiteSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceSourceGcpPubSubLiteSourceCredential"
    windows: List["GetSourceSourceGcpPubSubLiteSourceWindows"]
    segmentations: List["GetSourceSourceGcpPubSubLiteSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetSourceSourceGcpPubSubLiteSourceConfig"


class GetSourceSourceGcpPubSubLiteSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceGcpPubSubLiteSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceGcpPubSubLiteSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceGcpPubSubLiteSourceConfig(BaseModel):
    location: str
    project: str
    subscription_id: str = Field(alias="subscriptionId")


class GetSourceSourceAwsAthenaSource(BaseModel):
    typename__: Literal["AwsAthenaSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceSourceAwsAthenaSourceCredential"
    windows: List["GetSourceSourceAwsAthenaSourceWindows"]
    segmentations: List["GetSourceSourceAwsAthenaSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetSourceSourceAwsAthenaSourceConfig"


class GetSourceSourceAwsAthenaSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceAwsAthenaSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceAwsAthenaSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceAwsAthenaSourceConfig(BaseModel):
    catalog: str
    database: str
    table: str
    cursor_field: str = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: CronExpression


class GetSourceSourceAwsKinesisSource(BaseModel):
    typename__: Literal["AwsKinesisSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceSourceAwsKinesisSourceCredential"
    windows: List["GetSourceSourceAwsKinesisSourceWindows"]
    segmentations: List["GetSourceSourceAwsKinesisSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetSourceSourceAwsKinesisSourceConfig"


class GetSourceSourceAwsKinesisSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceAwsKinesisSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceAwsKinesisSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceAwsKinesisSourceConfig(BaseModel):
    region: str
    stream_name: str = Field(alias="streamName")


class GetSourceSourceAwsRedshiftSource(BaseModel):
    typename__: Literal["AwsRedshiftSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceSourceAwsRedshiftSourceCredential"
    windows: List["GetSourceSourceAwsRedshiftSourceWindows"]
    segmentations: List["GetSourceSourceAwsRedshiftSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetSourceSourceAwsRedshiftSourceConfig"


class GetSourceSourceAwsRedshiftSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceAwsRedshiftSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceAwsRedshiftSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceAwsRedshiftSourceConfig(BaseModel):
    database: str
    db_schema: Any = Field(alias="schema")
    table: str
    cursor_field: str = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: CronExpression


class GetSourceSourceAwsS3Source(BaseModel):
    typename__: Literal["AwsS3Source"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceSourceAwsS3SourceCredential"
    windows: List["GetSourceSourceAwsS3SourceWindows"]
    segmentations: List["GetSourceSourceAwsS3SourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetSourceSourceAwsS3SourceConfig"


class GetSourceSourceAwsS3SourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceAwsS3SourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceAwsS3SourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceAwsS3SourceConfig(BaseModel):
    bucket: str
    prefix: str
    csv: Optional["GetSourceSourceAwsS3SourceConfigCsv"]
    schedule: CronExpression
    file_pattern: Optional[str] = Field(alias="filePattern")
    file_format: Optional[FileFormat] = Field(alias="fileFormat")


class GetSourceSourceAwsS3SourceConfigCsv(BaseModel):
    null_marker: Optional[str] = Field(alias="nullMarker")
    delimiter: str


class GetSourceSourcePostgreSqlSource(BaseModel):
    typename__: Literal["PostgreSqlSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceSourcePostgreSqlSourceCredential"
    windows: List["GetSourceSourcePostgreSqlSourceWindows"]
    segmentations: List["GetSourceSourcePostgreSqlSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetSourceSourcePostgreSqlSourceConfig"


class GetSourceSourcePostgreSqlSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourcePostgreSqlSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourcePostgreSqlSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourcePostgreSqlSourceConfig(BaseModel):
    database: str
    db_schema: Any = Field(alias="schema")
    table: str
    cursor_field: str = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: CronExpression


class GetSourceSourceSnowflakeSource(BaseModel):
    typename__: Literal["SnowflakeSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceSourceSnowflakeSourceCredential"
    windows: List["GetSourceSourceSnowflakeSourceWindows"]
    segmentations: List["GetSourceSourceSnowflakeSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetSourceSourceSnowflakeSourceConfig"


class GetSourceSourceSnowflakeSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceSnowflakeSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceSnowflakeSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceSnowflakeSourceConfig(BaseModel):
    role: Optional[str]
    warehouse: Optional[str]
    database: str
    db_schema: Any = Field(alias="schema")
    table: str
    cursor_field: str = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: CronExpression


class GetSourceSourceKafkaSource(BaseModel):
    typename__: Literal["KafkaSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceSourceKafkaSourceCredential"
    windows: List["GetSourceSourceKafkaSourceWindows"]
    segmentations: List["GetSourceSourceKafkaSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetSourceSourceKafkaSourceConfig"


class GetSourceSourceKafkaSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceKafkaSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceKafkaSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceKafkaSourceConfig(BaseModel):
    topic: str


GetSource.update_forward_refs()
GetSourceSourceSource.update_forward_refs()
GetSourceSourceSourceCredential.update_forward_refs()
GetSourceSourceSourceWindows.update_forward_refs()
GetSourceSourceSourceSegmentations.update_forward_refs()
GetSourceSourceGcpStorageSource.update_forward_refs()
GetSourceSourceGcpStorageSourceCredential.update_forward_refs()
GetSourceSourceGcpStorageSourceWindows.update_forward_refs()
GetSourceSourceGcpStorageSourceSegmentations.update_forward_refs()
GetSourceSourceGcpStorageSourceConfig.update_forward_refs()
GetSourceSourceGcpStorageSourceConfigCsv.update_forward_refs()
GetSourceSourceGcpBigQuerySource.update_forward_refs()
GetSourceSourceGcpBigQuerySourceCredential.update_forward_refs()
GetSourceSourceGcpBigQuerySourceWindows.update_forward_refs()
GetSourceSourceGcpBigQuerySourceSegmentations.update_forward_refs()
GetSourceSourceGcpBigQuerySourceConfig.update_forward_refs()
GetSourceSourceGcpPubSubSource.update_forward_refs()
GetSourceSourceGcpPubSubSourceCredential.update_forward_refs()
GetSourceSourceGcpPubSubSourceWindows.update_forward_refs()
GetSourceSourceGcpPubSubSourceSegmentations.update_forward_refs()
GetSourceSourceGcpPubSubSourceConfig.update_forward_refs()
GetSourceSourceGcpPubSubLiteSource.update_forward_refs()
GetSourceSourceGcpPubSubLiteSourceCredential.update_forward_refs()
GetSourceSourceGcpPubSubLiteSourceWindows.update_forward_refs()
GetSourceSourceGcpPubSubLiteSourceSegmentations.update_forward_refs()
GetSourceSourceGcpPubSubLiteSourceConfig.update_forward_refs()
GetSourceSourceAwsAthenaSource.update_forward_refs()
GetSourceSourceAwsAthenaSourceCredential.update_forward_refs()
GetSourceSourceAwsAthenaSourceWindows.update_forward_refs()
GetSourceSourceAwsAthenaSourceSegmentations.update_forward_refs()
GetSourceSourceAwsAthenaSourceConfig.update_forward_refs()
GetSourceSourceAwsKinesisSource.update_forward_refs()
GetSourceSourceAwsKinesisSourceCredential.update_forward_refs()
GetSourceSourceAwsKinesisSourceWindows.update_forward_refs()
GetSourceSourceAwsKinesisSourceSegmentations.update_forward_refs()
GetSourceSourceAwsKinesisSourceConfig.update_forward_refs()
GetSourceSourceAwsRedshiftSource.update_forward_refs()
GetSourceSourceAwsRedshiftSourceCredential.update_forward_refs()
GetSourceSourceAwsRedshiftSourceWindows.update_forward_refs()
GetSourceSourceAwsRedshiftSourceSegmentations.update_forward_refs()
GetSourceSourceAwsRedshiftSourceConfig.update_forward_refs()
GetSourceSourceAwsS3Source.update_forward_refs()
GetSourceSourceAwsS3SourceCredential.update_forward_refs()
GetSourceSourceAwsS3SourceWindows.update_forward_refs()
GetSourceSourceAwsS3SourceSegmentations.update_forward_refs()
GetSourceSourceAwsS3SourceConfig.update_forward_refs()
GetSourceSourceAwsS3SourceConfigCsv.update_forward_refs()
GetSourceSourcePostgreSqlSource.update_forward_refs()
GetSourceSourcePostgreSqlSourceCredential.update_forward_refs()
GetSourceSourcePostgreSqlSourceWindows.update_forward_refs()
GetSourceSourcePostgreSqlSourceSegmentations.update_forward_refs()
GetSourceSourcePostgreSqlSourceConfig.update_forward_refs()
GetSourceSourceSnowflakeSource.update_forward_refs()
GetSourceSourceSnowflakeSourceCredential.update_forward_refs()
GetSourceSourceSnowflakeSourceWindows.update_forward_refs()
GetSourceSourceSnowflakeSourceSegmentations.update_forward_refs()
GetSourceSourceSnowflakeSourceConfig.update_forward_refs()
GetSourceSourceKafkaSource.update_forward_refs()
GetSourceSourceKafkaSourceCredential.update_forward_refs()
GetSourceSourceKafkaSourceWindows.update_forward_refs()
GetSourceSourceKafkaSourceSegmentations.update_forward_refs()
GetSourceSourceKafkaSourceConfig.update_forward_refs()
