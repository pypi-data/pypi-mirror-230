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


class GetSourceByResourceName(BaseModel):
    source_by_resource_name: Optional[
        Annotated[
            Union[
                "GetSourceByResourceNameSourceByResourceNameSource",
                "GetSourceByResourceNameSourceByResourceNameGcpStorageSource",
                "GetSourceByResourceNameSourceByResourceNameGcpBigQuerySource",
                "GetSourceByResourceNameSourceByResourceNameGcpPubSubSource",
                "GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSource",
                "GetSourceByResourceNameSourceByResourceNameAwsAthenaSource",
                "GetSourceByResourceNameSourceByResourceNameAwsKinesisSource",
                "GetSourceByResourceNameSourceByResourceNameAwsRedshiftSource",
                "GetSourceByResourceNameSourceByResourceNameAwsS3Source",
                "GetSourceByResourceNameSourceByResourceNamePostgreSqlSource",
                "GetSourceByResourceNameSourceByResourceNameSnowflakeSource",
                "GetSourceByResourceNameSourceByResourceNameKafkaSource",
            ],
            Field(discriminator="typename__"),
        ]
    ] = Field(alias="sourceByResourceName")


class GetSourceByResourceNameSourceByResourceNameSource(BaseModel):
    typename__: Literal["DemoSource", "Source"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceByResourceNameSourceByResourceNameSourceCredential"
    windows: List["GetSourceByResourceNameSourceByResourceNameSourceWindows"]
    segmentations: List[
        "GetSourceByResourceNameSourceByResourceNameSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameGcpStorageSource(BaseModel):
    typename__: Literal["GcpStorageSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceByResourceNameSourceByResourceNameGcpStorageSourceCredential"
    windows: List["GetSourceByResourceNameSourceByResourceNameGcpStorageSourceWindows"]
    segmentations: List[
        "GetSourceByResourceNameSourceByResourceNameGcpStorageSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetSourceByResourceNameSourceByResourceNameGcpStorageSourceConfig"


class GetSourceByResourceNameSourceByResourceNameGcpStorageSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameGcpStorageSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameGcpStorageSourceSegmentations(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameGcpStorageSourceConfig(BaseModel):
    project: str
    bucket: str
    folder: str
    csv: Optional[
        "GetSourceByResourceNameSourceByResourceNameGcpStorageSourceConfigCsv"
    ]
    schedule: CronExpression
    file_pattern: Optional[str] = Field(alias="filePattern")
    file_format: Optional[FileFormat] = Field(alias="fileFormat")


class GetSourceByResourceNameSourceByResourceNameGcpStorageSourceConfigCsv(BaseModel):
    null_marker: Optional[str] = Field(alias="nullMarker")
    delimiter: str


class GetSourceByResourceNameSourceByResourceNameGcpBigQuerySource(BaseModel):
    typename__: Literal["GcpBigQuerySource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceByResourceNameSourceByResourceNameGcpBigQuerySourceCredential"
    windows: List["GetSourceByResourceNameSourceByResourceNameGcpBigQuerySourceWindows"]
    segmentations: List[
        "GetSourceByResourceNameSourceByResourceNameGcpBigQuerySourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetSourceByResourceNameSourceByResourceNameGcpBigQuerySourceConfig"


class GetSourceByResourceNameSourceByResourceNameGcpBigQuerySourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameGcpBigQuerySourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameGcpBigQuerySourceSegmentations(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameGcpBigQuerySourceConfig(BaseModel):
    project: str
    dataset: str
    table: str
    cursor_field: str = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: CronExpression


class GetSourceByResourceNameSourceByResourceNameGcpPubSubSource(BaseModel):
    typename__: Literal["GcpPubSubSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceByResourceNameSourceByResourceNameGcpPubSubSourceCredential"
    windows: List["GetSourceByResourceNameSourceByResourceNameGcpPubSubSourceWindows"]
    segmentations: List[
        "GetSourceByResourceNameSourceByResourceNameGcpPubSubSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetSourceByResourceNameSourceByResourceNameGcpPubSubSourceConfig"


class GetSourceByResourceNameSourceByResourceNameGcpPubSubSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameGcpPubSubSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameGcpPubSubSourceSegmentations(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameGcpPubSubSourceConfig(BaseModel):
    project: str
    subscription_id: str = Field(alias="subscriptionId")


class GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSource(BaseModel):
    typename__: Literal["GcpPubSubLiteSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSourceCredential"
    windows: List[
        "GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSourceWindows"
    ]
    segmentations: List[
        "GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSourceConfig"


class GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSourceCredential(
    BaseModel
):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSourceSegmentations(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSourceConfig(BaseModel):
    location: str
    project: str
    subscription_id: str = Field(alias="subscriptionId")


class GetSourceByResourceNameSourceByResourceNameAwsAthenaSource(BaseModel):
    typename__: Literal["AwsAthenaSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceByResourceNameSourceByResourceNameAwsAthenaSourceCredential"
    windows: List["GetSourceByResourceNameSourceByResourceNameAwsAthenaSourceWindows"]
    segmentations: List[
        "GetSourceByResourceNameSourceByResourceNameAwsAthenaSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetSourceByResourceNameSourceByResourceNameAwsAthenaSourceConfig"


class GetSourceByResourceNameSourceByResourceNameAwsAthenaSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameAwsAthenaSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameAwsAthenaSourceSegmentations(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameAwsAthenaSourceConfig(BaseModel):
    catalog: str
    database: str
    table: str
    cursor_field: str = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: CronExpression


class GetSourceByResourceNameSourceByResourceNameAwsKinesisSource(BaseModel):
    typename__: Literal["AwsKinesisSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceByResourceNameSourceByResourceNameAwsKinesisSourceCredential"
    windows: List["GetSourceByResourceNameSourceByResourceNameAwsKinesisSourceWindows"]
    segmentations: List[
        "GetSourceByResourceNameSourceByResourceNameAwsKinesisSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetSourceByResourceNameSourceByResourceNameAwsKinesisSourceConfig"


class GetSourceByResourceNameSourceByResourceNameAwsKinesisSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameAwsKinesisSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameAwsKinesisSourceSegmentations(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameAwsKinesisSourceConfig(BaseModel):
    region: str
    stream_name: str = Field(alias="streamName")


class GetSourceByResourceNameSourceByResourceNameAwsRedshiftSource(BaseModel):
    typename__: Literal["AwsRedshiftSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceByResourceNameSourceByResourceNameAwsRedshiftSourceCredential"
    windows: List["GetSourceByResourceNameSourceByResourceNameAwsRedshiftSourceWindows"]
    segmentations: List[
        "GetSourceByResourceNameSourceByResourceNameAwsRedshiftSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetSourceByResourceNameSourceByResourceNameAwsRedshiftSourceConfig"


class GetSourceByResourceNameSourceByResourceNameAwsRedshiftSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameAwsRedshiftSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameAwsRedshiftSourceSegmentations(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameAwsRedshiftSourceConfig(BaseModel):
    database: str
    db_schema: Any = Field(alias="schema")
    table: str
    cursor_field: str = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: CronExpression


class GetSourceByResourceNameSourceByResourceNameAwsS3Source(BaseModel):
    typename__: Literal["AwsS3Source"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceByResourceNameSourceByResourceNameAwsS3SourceCredential"
    windows: List["GetSourceByResourceNameSourceByResourceNameAwsS3SourceWindows"]
    segmentations: List[
        "GetSourceByResourceNameSourceByResourceNameAwsS3SourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetSourceByResourceNameSourceByResourceNameAwsS3SourceConfig"


class GetSourceByResourceNameSourceByResourceNameAwsS3SourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameAwsS3SourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameAwsS3SourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameAwsS3SourceConfig(BaseModel):
    bucket: str
    prefix: str
    csv: Optional["GetSourceByResourceNameSourceByResourceNameAwsS3SourceConfigCsv"]
    schedule: CronExpression
    file_pattern: Optional[str] = Field(alias="filePattern")
    file_format: Optional[FileFormat] = Field(alias="fileFormat")


class GetSourceByResourceNameSourceByResourceNameAwsS3SourceConfigCsv(BaseModel):
    null_marker: Optional[str] = Field(alias="nullMarker")
    delimiter: str


class GetSourceByResourceNameSourceByResourceNamePostgreSqlSource(BaseModel):
    typename__: Literal["PostgreSqlSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceByResourceNameSourceByResourceNamePostgreSqlSourceCredential"
    windows: List["GetSourceByResourceNameSourceByResourceNamePostgreSqlSourceWindows"]
    segmentations: List[
        "GetSourceByResourceNameSourceByResourceNamePostgreSqlSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetSourceByResourceNameSourceByResourceNamePostgreSqlSourceConfig"


class GetSourceByResourceNameSourceByResourceNamePostgreSqlSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNamePostgreSqlSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNamePostgreSqlSourceSegmentations(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNamePostgreSqlSourceConfig(BaseModel):
    database: str
    db_schema: Any = Field(alias="schema")
    table: str
    cursor_field: str = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: CronExpression


class GetSourceByResourceNameSourceByResourceNameSnowflakeSource(BaseModel):
    typename__: Literal["SnowflakeSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceByResourceNameSourceByResourceNameSnowflakeSourceCredential"
    windows: List["GetSourceByResourceNameSourceByResourceNameSnowflakeSourceWindows"]
    segmentations: List[
        "GetSourceByResourceNameSourceByResourceNameSnowflakeSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetSourceByResourceNameSourceByResourceNameSnowflakeSourceConfig"


class GetSourceByResourceNameSourceByResourceNameSnowflakeSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameSnowflakeSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameSnowflakeSourceSegmentations(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameSnowflakeSourceConfig(BaseModel):
    role: Optional[str]
    warehouse: Optional[str]
    database: str
    db_schema: Any = Field(alias="schema")
    table: str
    cursor_field: str = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: CronExpression


class GetSourceByResourceNameSourceByResourceNameKafkaSource(BaseModel):
    typename__: Literal["KafkaSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceByResourceNameSourceByResourceNameKafkaSourceCredential"
    windows: List["GetSourceByResourceNameSourceByResourceNameKafkaSourceWindows"]
    segmentations: List[
        "GetSourceByResourceNameSourceByResourceNameKafkaSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetSourceByResourceNameSourceByResourceNameKafkaSourceConfig"


class GetSourceByResourceNameSourceByResourceNameKafkaSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameKafkaSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameKafkaSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameKafkaSourceConfig(BaseModel):
    topic: str


GetSourceByResourceName.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameSource.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameSourceCredential.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameSourceWindows.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameSourceSegmentations.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameGcpStorageSource.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameGcpStorageSourceCredential.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameGcpStorageSourceWindows.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameGcpStorageSourceSegmentations.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameGcpStorageSourceConfig.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameGcpStorageSourceConfigCsv.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameGcpBigQuerySource.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameGcpBigQuerySourceCredential.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameGcpBigQuerySourceWindows.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameGcpBigQuerySourceSegmentations.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameGcpBigQuerySourceConfig.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameGcpPubSubSource.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameGcpPubSubSourceCredential.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameGcpPubSubSourceWindows.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameGcpPubSubSourceSegmentations.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameGcpPubSubSourceConfig.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSource.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSourceCredential.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSourceWindows.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSourceSegmentations.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSourceConfig.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameAwsAthenaSource.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameAwsAthenaSourceCredential.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameAwsAthenaSourceWindows.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameAwsAthenaSourceSegmentations.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameAwsAthenaSourceConfig.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameAwsKinesisSource.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameAwsKinesisSourceCredential.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameAwsKinesisSourceWindows.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameAwsKinesisSourceSegmentations.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameAwsKinesisSourceConfig.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameAwsRedshiftSource.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameAwsRedshiftSourceCredential.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameAwsRedshiftSourceWindows.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameAwsRedshiftSourceSegmentations.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameAwsRedshiftSourceConfig.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameAwsS3Source.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameAwsS3SourceCredential.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameAwsS3SourceWindows.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameAwsS3SourceSegmentations.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameAwsS3SourceConfig.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameAwsS3SourceConfigCsv.update_forward_refs()
GetSourceByResourceNameSourceByResourceNamePostgreSqlSource.update_forward_refs()
GetSourceByResourceNameSourceByResourceNamePostgreSqlSourceCredential.update_forward_refs()
GetSourceByResourceNameSourceByResourceNamePostgreSqlSourceWindows.update_forward_refs()
GetSourceByResourceNameSourceByResourceNamePostgreSqlSourceSegmentations.update_forward_refs()
GetSourceByResourceNameSourceByResourceNamePostgreSqlSourceConfig.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameSnowflakeSource.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameSnowflakeSourceCredential.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameSnowflakeSourceWindows.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameSnowflakeSourceSegmentations.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameSnowflakeSourceConfig.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameKafkaSource.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameKafkaSourceCredential.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameKafkaSourceWindows.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameKafkaSourceSegmentations.update_forward_refs()
GetSourceByResourceNameSourceByResourceNameKafkaSourceConfig.update_forward_refs()
