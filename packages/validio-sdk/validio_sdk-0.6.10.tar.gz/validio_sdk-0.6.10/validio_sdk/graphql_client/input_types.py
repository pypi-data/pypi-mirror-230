from datetime import datetime
from typing import Any, List, Optional

from pydantic import Field

from validio_sdk.scalars import (
    CredentialId,
    CronExpression,
    DestinationId,
    JsonFilterExpression,
    JsonPointer,
    JsonTypeDefinition,
    SegmentationId,
    SourceId,
    ValidatorId,
    WindowId,
)

from .base_model import BaseModel
from .enums import (
    CategoricalDistributionMetric,
    ComparisonOperator,
    DecisionBoundsType,
    FileFormat,
    NotificationTypename,
    NumericAnomalyMetric,
    NumericDistributionMetric,
    NumericMetric,
    RelativeTimeMetric,
    RelativeVolumeMetric,
    Role,
    UserStatus,
    VolumeMetric,
    WindowTimeUnit,
)


class AwsAthenaCredentialCreateInput(BaseModel):
    access_key: str = Field(alias="accessKey")
    name: str
    query_result_location: str = Field(alias="queryResultLocation")
    region: str
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    secret_key: str = Field(alias="secretKey")


class AwsAthenaCredentialSecretChangedInput(BaseModel):
    id: CredentialId
    secret_key: str = Field(alias="secretKey")


class AwsAthenaCredentialUpdateInput(BaseModel):
    access_key: str = Field(alias="accessKey")
    id: CredentialId
    query_result_location: str = Field(alias="queryResultLocation")
    region: str
    secret_key: str = Field(alias="secretKey")


class AwsAthenaInferSchemaInput(BaseModel):
    catalog: str
    credential_id: CredentialId = Field(alias="credentialId")
    database: str
    table: str


class AwsAthenaSourceCreateInput(BaseModel):
    catalog: str
    credential_id: CredentialId = Field(alias="credentialId")
    cursor_field: str = Field(alias="cursorField")
    database: str
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    lookback_days: int = Field(alias="lookbackDays")
    name: str
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    schedule: CronExpression
    table: str


class AwsAthenaSourceUpdateInput(BaseModel):
    id: SourceId
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: CronExpression


class AwsCredentialCreateInput(BaseModel):
    access_key: str = Field(alias="accessKey")
    name: str
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    secret_key: str = Field(alias="secretKey")


class AwsCredentialSecretChangedInput(BaseModel):
    id: CredentialId
    secret_key: str = Field(alias="secretKey")


class AwsCredentialUpdateInput(BaseModel):
    access_key: str = Field(alias="accessKey")
    id: CredentialId
    secret_key: str = Field(alias="secretKey")


class AwsKinesisDestinationCreateInput(BaseModel):
    credential_id: CredentialId = Field(alias="credentialId")
    endpoint: Optional[str]
    name: str
    region: str
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    stream_name: str = Field(alias="streamName")


class AwsKinesisDestinationUpdateInput(BaseModel):
    credential_id: CredentialId = Field(alias="credentialId")
    endpoint: Optional[str]
    id: DestinationId
    region: str
    stream_name: str = Field(alias="streamName")


class AwsKinesisInferSchemaInput(BaseModel):
    credential_id: CredentialId = Field(alias="credentialId")
    region: str
    stream_name: str = Field(alias="streamName")


class AwsKinesisSourceCreateInput(BaseModel):
    credential_id: CredentialId = Field(alias="credentialId")
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    name: str
    region: str
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    stream_name: str = Field(alias="streamName")


class AwsKinesisSourceUpdateInput(BaseModel):
    id: SourceId
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")


class AwsRedshiftCredentialCreateInput(BaseModel):
    default_database: str = Field(alias="defaultDatabase")
    host: str
    name: str
    password: str
    port: int
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    user: str


class AwsRedshiftCredentialSecretChangedInput(BaseModel):
    id: CredentialId
    password: str


class AwsRedshiftCredentialUpdateInput(BaseModel):
    default_database: str = Field(alias="defaultDatabase")
    host: str
    id: CredentialId
    password: str
    port: int
    user: str


class AwsRedshiftInferSchemaInput(BaseModel):
    credential_id: CredentialId = Field(alias="credentialId")
    database: Optional[str]
    db_schema: Any = Field(alias="schema")
    table: str


class AwsRedshiftSourceCreateInput(BaseModel):
    credential_id: CredentialId = Field(alias="credentialId")
    cursor_field: str = Field(alias="cursorField")
    database: Optional[str]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    lookback_days: int = Field(alias="lookbackDays")
    name: str
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    schedule: CronExpression
    db_schema: Any = Field(alias="schema")
    table: str


class AwsRedshiftSourceUpdateInput(BaseModel):
    id: SourceId
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: CronExpression


class AwsS3InferSchemaInput(BaseModel):
    bucket: str
    credential_id: CredentialId = Field(alias="credentialId")
    csv: Optional["CsvParserInput"]
    file_format: Optional[FileFormat] = Field(alias="fileFormat")
    file_pattern: Optional[str] = Field(alias="filePattern")
    prefix: str


class AwsS3SourceCreateInput(BaseModel):
    bucket: str
    credential_id: CredentialId = Field(alias="credentialId")
    csv: Optional["CsvParserInput"]
    file_format: Optional[FileFormat] = Field(alias="fileFormat")
    file_pattern: Optional[str] = Field(alias="filePattern")
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    name: str
    prefix: str
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    schedule: CronExpression


class AwsS3SourceUpdateInput(BaseModel):
    csv: Optional["CsvParserInput"]
    file_pattern: Optional[str] = Field(alias="filePattern")
    id: SourceId
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    schedule: CronExpression


class CategoricalDistributionValidatorCreateInput(BaseModel):
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    metric: CategoricalDistributionMetric
    name: Optional[str]
    reference_source_config: "ReferenceSourceConfigCreateInput" = Field(
        alias="referenceSourceConfig"
    )
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    source_config: "SourceConfigCreateInput" = Field(alias="sourceConfig")
    source_field: JsonPointer = Field(alias="sourceField")


class CategoricalDistributionValidatorUpdateInput(BaseModel):
    id: ValidatorId
    reference_source_config: "ReferenceSourceConfigUpdateInput" = Field(
        alias="referenceSourceConfig"
    )
    source_config: "SourceConfigUpdateInput" = Field(alias="sourceConfig")


class ChannelDeleteInput(BaseModel):
    id: Any


class CsvParserInput(BaseModel):
    delimiter: str
    null_marker: Optional[str] = Field(alias="nullMarker")


class DemoCredentialCreateInput(BaseModel):
    name: str
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")


class DemoSourceCreateInput(BaseModel):
    credential_id: CredentialId = Field(alias="credentialId")
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    name: str
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")


class DynamicThresholdCreateInput(BaseModel):
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )
    sensitivity: float


class FileWindowCreateInput(BaseModel):
    data_time_field: JsonPointer = Field(alias="dataTimeField")
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    source_id: SourceId = Field(alias="sourceId")


class FixedBatchWindowCreateInput(BaseModel):
    batch_size: int = Field(alias="batchSize")
    batch_timeout_secs: Optional[int] = Field(alias="batchTimeoutSecs")
    data_time_field: JsonPointer = Field(alias="dataTimeField")
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    segmented_batching: bool = Field(alias="segmentedBatching")
    source_id: SourceId = Field(alias="sourceId")


class FixedBatchWindowUpdateInput(BaseModel):
    batch_size: int = Field(alias="batchSize")
    batch_timeout_secs: Optional[int] = Field(alias="batchTimeoutSecs")
    id: WindowId
    segmented_batching: bool = Field(alias="segmentedBatching")


class FixedThresholdCreateInput(BaseModel):
    operator: ComparisonOperator
    value: float


class FreshnessValidatorCreateInput(BaseModel):
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    name: Optional[str]
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    source_config: "SourceConfigCreateInput" = Field(alias="sourceConfig")


class FreshnessValidatorUpdateInput(BaseModel):
    id: ValidatorId
    source_config: "SourceConfigUpdateInput" = Field(alias="sourceConfig")


class GcpBigQueryDestinationCreateInput(BaseModel):
    credential_id: CredentialId = Field(alias="credentialId")
    dataset: str
    name: str
    project: str
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    table: str


class GcpBigQueryDestinationUpdateInput(BaseModel):
    credential_id: CredentialId = Field(alias="credentialId")
    dataset: str
    id: DestinationId
    project: str
    table: str


class GcpBigQueryInferSchemaInput(BaseModel):
    credential_id: CredentialId = Field(alias="credentialId")
    dataset: str
    project: str
    table: str


class GcpBigQuerySourceCreateInput(BaseModel):
    credential_id: CredentialId = Field(alias="credentialId")
    cursor_field: str = Field(alias="cursorField")
    dataset: str
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    lookback_days: int = Field(alias="lookbackDays")
    name: str
    project: str
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    schedule: CronExpression
    table: str


class GcpBigQuerySourceUpdateInput(BaseModel):
    id: SourceId
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: CronExpression


class GcpCredentialCreateInput(BaseModel):
    credential: str
    name: str
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")


class GcpCredentialSecretChangedInput(BaseModel):
    credential: str
    id: CredentialId


class GcpCredentialUpdateInput(BaseModel):
    credential: str
    id: CredentialId


class GcpPubSubInferSchemaInput(BaseModel):
    credential_id: CredentialId = Field(alias="credentialId")
    project: str
    subscription_id: str = Field(alias="subscriptionId")


class GcpPubSubLiteInferSchemaInput(BaseModel):
    credential_id: CredentialId = Field(alias="credentialId")
    location: str
    project: str
    subscription_id: str = Field(alias="subscriptionId")


class GcpPubSubLiteSourceCreateInput(BaseModel):
    credential_id: CredentialId = Field(alias="credentialId")
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    location: str
    name: str
    project: str
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    subscription_id: str = Field(alias="subscriptionId")


class GcpPubSubLiteSourceUpdateInput(BaseModel):
    id: SourceId
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")


class GcpPubSubSourceCreateInput(BaseModel):
    credential_id: CredentialId = Field(alias="credentialId")
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    name: str
    project: str
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    subscription_id: str = Field(alias="subscriptionId")


class GcpPubSubSourceUpdateInput(BaseModel):
    id: SourceId
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")


class GcpStorageInferSchemaInput(BaseModel):
    bucket: str
    credential_id: CredentialId = Field(alias="credentialId")
    csv: Optional["CsvParserInput"]
    file_format: Optional[FileFormat] = Field(alias="fileFormat")
    file_pattern: Optional[str] = Field(alias="filePattern")
    folder: str
    project: str


class GcpStorageSourceCreateInput(BaseModel):
    bucket: str
    credential_id: CredentialId = Field(alias="credentialId")
    csv: Optional["CsvParserInput"]
    file_format: Optional[FileFormat] = Field(alias="fileFormat")
    file_pattern: Optional[str] = Field(alias="filePattern")
    folder: str
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    name: str
    project: str
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    schedule: CronExpression


class GcpStorageSourceUpdateInput(BaseModel):
    csv: Optional["CsvParserInput"]
    file_pattern: Optional[str] = Field(alias="filePattern")
    id: SourceId
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    schedule: CronExpression


class IdentityDeleteInput(BaseModel):
    id: str


class IdentityProviderDeleteInput(BaseModel):
    id: str


class IncidentsInput(BaseModel):
    time_range: "TimeRangeInput" = Field(alias="timeRange")


class KafkaInferSchemaInput(BaseModel):
    credential_id: CredentialId = Field(alias="credentialId")
    topic: str


class KafkaSaslSslPlainCredentialCreateInput(BaseModel):
    bootstrap_servers: List[str] = Field(alias="bootstrapServers")
    name: str
    password: str
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    username: str


class KafkaSaslSslPlainCredentialSecretChangedInput(BaseModel):
    id: CredentialId
    password: str


class KafkaSaslSslPlainCredentialUpdateInput(BaseModel):
    bootstrap_servers: List[str] = Field(alias="bootstrapServers")
    id: CredentialId
    password: str
    username: str


class KafkaSourceCreateInput(BaseModel):
    credential_id: CredentialId = Field(alias="credentialId")
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    name: str
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    topic: str


class KafkaSourceUpdateInput(BaseModel):
    id: SourceId
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")


class KafkaSslCredentialCreateInput(BaseModel):
    bootstrap_servers: List[str] = Field(alias="bootstrapServers")
    ca_certificate: str = Field(alias="caCertificate")
    client_certificate: str = Field(alias="clientCertificate")
    client_private_key: str = Field(alias="clientPrivateKey")
    client_private_key_password: str = Field(alias="clientPrivateKeyPassword")
    name: str
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")


class KafkaSslCredentialSecretChangedInput(BaseModel):
    ca_certificate: str = Field(alias="caCertificate")
    client_certificate: str = Field(alias="clientCertificate")
    client_private_key: str = Field(alias="clientPrivateKey")
    client_private_key_password: str = Field(alias="clientPrivateKeyPassword")
    id: CredentialId


class KafkaSslCredentialUpdateInput(BaseModel):
    bootstrap_servers: List[str] = Field(alias="bootstrapServers")
    ca_certificate: str = Field(alias="caCertificate")
    client_certificate: str = Field(alias="clientCertificate")
    client_private_key: str = Field(alias="clientPrivateKey")
    client_private_key_password: str = Field(alias="clientPrivateKeyPassword")
    id: CredentialId


class LocalIdentityProviderUpdateInput(BaseModel):
    disabled: bool
    id: str
    name: str


class NotificationRuleCreateInput(BaseModel):
    channel_id: Any = Field(alias="channelId")
    name: str
    notification_typenames: List[NotificationTypename] = Field(
        alias="notificationTypenames"
    )
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    sources: List[SourceId]


class NotificationRuleDeleteInput(BaseModel):
    id: Any


class NotificationRuleUpdateInput(BaseModel):
    id: Any
    name: Optional[str]
    notification_typenames: List[NotificationTypename] = Field(
        alias="notificationTypenames"
    )
    sources: List[SourceId]


class NumericAnomalyValidatorCreateInput(BaseModel):
    destination_id: Optional[DestinationId] = Field(alias="destinationId")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    metric: NumericAnomalyMetric
    minimum_absolute_difference: float = Field(alias="minimumAbsoluteDifference")
    minimum_reference_datapoints: Optional[float] = Field(
        alias="minimumReferenceDatapoints"
    )
    minimum_relative_difference_percent: float = Field(
        alias="minimumRelativeDifferencePercent"
    )
    name: Optional[str]
    reference_source_config: "ReferenceSourceConfigCreateInput" = Field(
        alias="referenceSourceConfig"
    )
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    sensitivity: float
    source_config: "SourceConfigCreateInput" = Field(alias="sourceConfig")
    source_field: JsonPointer = Field(alias="sourceField")


class NumericAnomalyValidatorUpdateInput(BaseModel):
    id: ValidatorId
    reference_source_config: "ReferenceSourceConfigUpdateInput" = Field(
        alias="referenceSourceConfig"
    )
    source_config: "SourceConfigUpdateInput" = Field(alias="sourceConfig")


class NumericDistributionValidatorCreateInput(BaseModel):
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    metric: NumericDistributionMetric
    name: Optional[str]
    reference_source_config: "ReferenceSourceConfigCreateInput" = Field(
        alias="referenceSourceConfig"
    )
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    source_config: "SourceConfigCreateInput" = Field(alias="sourceConfig")
    source_field: JsonPointer = Field(alias="sourceField")


class NumericDistributionValidatorUpdateInput(BaseModel):
    id: ValidatorId
    reference_source_config: "ReferenceSourceConfigUpdateInput" = Field(
        alias="referenceSourceConfig"
    )
    source_config: "SourceConfigUpdateInput" = Field(alias="sourceConfig")


class NumericValidatorCreateInput(BaseModel):
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    metric: NumericMetric
    name: Optional[str]
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    source_config: "SourceConfigCreateInput" = Field(alias="sourceConfig")
    source_field: JsonPointer = Field(alias="sourceField")


class NumericValidatorUpdateInput(BaseModel):
    id: ValidatorId
    source_config: "SourceConfigUpdateInput" = Field(alias="sourceConfig")


class PostgreSqlCredentialCreateInput(BaseModel):
    default_database: str = Field(alias="defaultDatabase")
    host: str
    name: str
    password: str
    port: int
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    user: str


class PostgreSqlCredentialSecretChangedInput(BaseModel):
    id: CredentialId
    password: str


class PostgreSqlCredentialUpdateInput(BaseModel):
    default_database: str = Field(alias="defaultDatabase")
    host: str
    id: CredentialId
    password: str
    port: int
    user: str


class PostgreSqlInferSchemaInput(BaseModel):
    credential_id: CredentialId = Field(alias="credentialId")
    database: Optional[str]
    db_schema: Any = Field(alias="schema")
    table: str


class PostgreSqlSourceCreateInput(BaseModel):
    credential_id: CredentialId = Field(alias="credentialId")
    cursor_field: str = Field(alias="cursorField")
    database: Optional[str]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    lookback_days: int = Field(alias="lookbackDays")
    name: str
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    schedule: CronExpression
    db_schema: Any = Field(alias="schema")
    table: str


class PostgreSqlSourceUpdateInput(BaseModel):
    id: SourceId
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: CronExpression


class ReferenceSourceConfigCreateInput(BaseModel):
    filter: Optional[JsonFilterExpression]
    history: int
    offset: int
    source_id: SourceId = Field(alias="sourceId")
    window_id: WindowId = Field(alias="windowId")


class ReferenceSourceConfigUpdateInput(BaseModel):
    filter: Optional[JsonFilterExpression]
    history: int
    offset: int


class RelativeTimeValidatorCreateInput(BaseModel):
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    metric: RelativeTimeMetric
    name: Optional[str]
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    source_config: "SourceConfigCreateInput" = Field(alias="sourceConfig")
    source_field_minuend: JsonPointer = Field(alias="sourceFieldMinuend")
    source_field_subtrahend: JsonPointer = Field(alias="sourceFieldSubtrahend")


class RelativeTimeValidatorUpdateInput(BaseModel):
    id: ValidatorId
    source_config: "SourceConfigUpdateInput" = Field(alias="sourceConfig")


class RelativeVolumeValidatorCreateInput(BaseModel):
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    metric: RelativeVolumeMetric
    name: Optional[str]
    reference_source_config: "ReferenceSourceConfigCreateInput" = Field(
        alias="referenceSourceConfig"
    )
    reference_source_field: Optional[JsonPointer] = Field(alias="referenceSourceField")
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    source_config: "SourceConfigCreateInput" = Field(alias="sourceConfig")
    source_field: Optional[JsonPointer] = Field(alias="sourceField")


class RelativeVolumeValidatorUpdateInput(BaseModel):
    id: ValidatorId
    reference_source_config: "ReferenceSourceConfigUpdateInput" = Field(
        alias="referenceSourceConfig"
    )
    source_config: "SourceConfigUpdateInput" = Field(alias="sourceConfig")


class ResourceFilter(BaseModel):
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")


class ResourceNamespaceUpdateInput(BaseModel):
    new_resource_namespace: str = Field(alias="newResourceNamespace")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SamlIdentityProviderCreateInput(BaseModel):
    cert: str
    disabled: bool
    entity_id: str = Field(alias="entityId")
    entry_point: str = Field(alias="entryPoint")
    name: str
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")


class SamlIdentityProviderUpdateInput(BaseModel):
    cert: str
    disabled: bool
    entity_id: str = Field(alias="entityId")
    entry_point: str = Field(alias="entryPoint")
    id: str
    name: str


class SegmentIncidentsInput(BaseModel):
    segment_id: Any = Field(alias="segmentId")
    time_range: "TimeRangeInput" = Field(alias="timeRange")


class SegmentationCreateInput(BaseModel):
    fields: List[str]
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    source_id: SourceId = Field(alias="sourceId")


class SessionizedWindowCreateInput(BaseModel):
    data_time_field: JsonPointer = Field(alias="dataTimeField")
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    source_id: SourceId = Field(alias="sourceId")
    timeout: int
    timeout_unit: WindowTimeUnit = Field(alias="timeoutUnit")


class SessionizedWindowUpdateInput(BaseModel):
    id: WindowId
    timeout: int
    timeout_unit: WindowTimeUnit = Field(alias="timeoutUnit")


class SlackChannelCreateInput(BaseModel):
    application_link_url: str = Field(alias="applicationLinkUrl")
    name: str
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    timezone: Optional[str]
    webhook_url: str = Field(alias="webhookUrl")


class SlackChannelUpdateInput(BaseModel):
    application_link_url: str = Field(alias="applicationLinkUrl")
    id: Any
    name: Optional[str]
    timezone: Optional[str]
    webhook_url: str = Field(alias="webhookUrl")


class SnowflakeCredentialCreateInput(BaseModel):
    account: str
    name: str
    password: str
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    user: str


class SnowflakeCredentialSecretChangedInput(BaseModel):
    id: CredentialId
    password: str


class SnowflakeCredentialUpdateInput(BaseModel):
    account: str
    id: CredentialId
    password: str
    user: str


class SnowflakeDestinationCreateInput(BaseModel):
    credential_id: CredentialId = Field(alias="credentialId")
    database: str
    name: str
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    role: str
    db_schema: Any = Field(alias="schema")
    table: str
    warehouse: str


class SnowflakeDestinationUpdateInput(BaseModel):
    credential_id: CredentialId = Field(alias="credentialId")
    database: str
    id: DestinationId
    role: str
    db_schema: Any = Field(alias="schema")
    table: str
    warehouse: str


class SnowflakeInferSchemaInput(BaseModel):
    credential_id: CredentialId = Field(alias="credentialId")
    database: str
    role: Optional[str]
    db_schema: Any = Field(alias="schema")
    table: str
    warehouse: Optional[str]


class SnowflakeSourceCreateInput(BaseModel):
    credential_id: CredentialId = Field(alias="credentialId")
    cursor_field: str = Field(alias="cursorField")
    database: str
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    lookback_days: int = Field(alias="lookbackDays")
    name: str
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    role: Optional[str]
    schedule: CronExpression
    db_schema: Any = Field(alias="schema")
    table: str
    warehouse: Optional[str]


class SnowflakeSourceUpdateInput(BaseModel):
    id: SourceId
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: CronExpression


class SourceConfigCreateInput(BaseModel):
    filter: Optional[JsonFilterExpression]
    segmentation_id: SegmentationId = Field(alias="segmentationId")
    source_id: SourceId = Field(alias="sourceId")
    window_id: WindowId = Field(alias="windowId")


class SourceConfigUpdateInput(BaseModel):
    filter: Optional[JsonFilterExpression]


class SourceIncidentsInput(BaseModel):
    source_id: SourceId = Field(alias="sourceId")
    time_range: "TimeRangeInput" = Field(alias="timeRange")


class TimeRangeInput(BaseModel):
    end: datetime
    start: datetime


class TumblingWindowCreateInput(BaseModel):
    data_time_field: JsonPointer = Field(alias="dataTimeField")
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    source_id: SourceId = Field(alias="sourceId")
    time_unit: WindowTimeUnit = Field(alias="timeUnit")
    window_size: int = Field(alias="windowSize")


class TumblingWindowUpdateInput(BaseModel):
    id: WindowId
    time_unit: WindowTimeUnit = Field(alias="timeUnit")
    window_size: int = Field(alias="windowSize")


class UserCreateInput(BaseModel):
    display_name: str = Field(alias="displayName")
    email: str
    full_name: Optional[str] = Field(alias="fullName")
    password: Optional[str]
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    role: Role
    status: UserStatus
    username: Optional[str]


class UserDeleteInput(BaseModel):
    id: str


class UserUpdateInput(BaseModel):
    display_name: str = Field(alias="displayName")
    email: Optional[str]
    full_name: Optional[str] = Field(alias="fullName")
    id: str
    password: Optional[str]
    role: Role
    status: UserStatus
    username: Optional[str]


class ValidatorIncidentsInput(BaseModel):
    time_range: "TimeRangeInput" = Field(alias="timeRange")
    validator_id: ValidatorId = Field(alias="validatorId")


class ValidatorMetricDebugInfoInput(BaseModel):
    incident_id: Any = Field(alias="incidentId")


class ValidatorRecommendationApplyInput(BaseModel):
    ids: List[Any]
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")


class ValidatorRecommendationDismissInput(BaseModel):
    ids: List[Any]


class ValidatorSegmentIncidentsInput(BaseModel):
    segment_id: Any = Field(alias="segmentId")
    time_range: "TimeRangeInput" = Field(alias="timeRange")
    validator_id: ValidatorId = Field(alias="validatorId")


class ValidatorSegmentMetricsInput(BaseModel):
    segment_id: Any = Field(alias="segmentId")
    time_range: "TimeRangeInput" = Field(alias="timeRange")
    validator_id: ValidatorId = Field(alias="validatorId")


class ValidatorWithDynamicThresholdUpdateInput(BaseModel):
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )
    sensitivity: float
    validator_id: ValidatorId = Field(alias="validatorId")


class ValidatorWithFixedThresholdUpdateInput(BaseModel):
    operator: ComparisonOperator
    validator_id: ValidatorId = Field(alias="validatorId")
    value: float


class VolumeValidatorCreateInput(BaseModel):
    destination_id: Optional[DestinationId] = Field(alias="destinationId")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    metric: VolumeMetric
    name: Optional[str]
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    source_config: "SourceConfigCreateInput" = Field(alias="sourceConfig")
    source_field: Optional[JsonPointer] = Field(alias="sourceField")
    source_fields: List[JsonPointer] = Field(alias="sourceFields")


class VolumeValidatorUpdateInput(BaseModel):
    id: ValidatorId
    source_config: "SourceConfigUpdateInput" = Field(alias="sourceConfig")


class WebhookChannelCreateInput(BaseModel):
    application_link_url: str = Field(alias="applicationLinkUrl")
    auth_header: Optional[str] = Field(alias="authHeader")
    name: str
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")
    webhook_url: str = Field(alias="webhookUrl")


class WebhookChannelUpdateInput(BaseModel):
    application_link_url: str = Field(alias="applicationLinkUrl")
    auth_header: Optional[str] = Field(alias="authHeader")
    id: Any
    name: Optional[str]
    webhook_url: str = Field(alias="webhookUrl")


AwsAthenaCredentialCreateInput.update_forward_refs()
AwsAthenaCredentialSecretChangedInput.update_forward_refs()
AwsAthenaCredentialUpdateInput.update_forward_refs()
AwsAthenaInferSchemaInput.update_forward_refs()
AwsAthenaSourceCreateInput.update_forward_refs()
AwsAthenaSourceUpdateInput.update_forward_refs()
AwsCredentialCreateInput.update_forward_refs()
AwsCredentialSecretChangedInput.update_forward_refs()
AwsCredentialUpdateInput.update_forward_refs()
AwsKinesisDestinationCreateInput.update_forward_refs()
AwsKinesisDestinationUpdateInput.update_forward_refs()
AwsKinesisInferSchemaInput.update_forward_refs()
AwsKinesisSourceCreateInput.update_forward_refs()
AwsKinesisSourceUpdateInput.update_forward_refs()
AwsRedshiftCredentialCreateInput.update_forward_refs()
AwsRedshiftCredentialSecretChangedInput.update_forward_refs()
AwsRedshiftCredentialUpdateInput.update_forward_refs()
AwsRedshiftInferSchemaInput.update_forward_refs()
AwsRedshiftSourceCreateInput.update_forward_refs()
AwsRedshiftSourceUpdateInput.update_forward_refs()
AwsS3InferSchemaInput.update_forward_refs()
AwsS3SourceCreateInput.update_forward_refs()
AwsS3SourceUpdateInput.update_forward_refs()
CategoricalDistributionValidatorCreateInput.update_forward_refs()
CategoricalDistributionValidatorUpdateInput.update_forward_refs()
ChannelDeleteInput.update_forward_refs()
CsvParserInput.update_forward_refs()
DemoCredentialCreateInput.update_forward_refs()
DemoSourceCreateInput.update_forward_refs()
DynamicThresholdCreateInput.update_forward_refs()
FileWindowCreateInput.update_forward_refs()
FixedBatchWindowCreateInput.update_forward_refs()
FixedBatchWindowUpdateInput.update_forward_refs()
FixedThresholdCreateInput.update_forward_refs()
FreshnessValidatorCreateInput.update_forward_refs()
FreshnessValidatorUpdateInput.update_forward_refs()
GcpBigQueryDestinationCreateInput.update_forward_refs()
GcpBigQueryDestinationUpdateInput.update_forward_refs()
GcpBigQueryInferSchemaInput.update_forward_refs()
GcpBigQuerySourceCreateInput.update_forward_refs()
GcpBigQuerySourceUpdateInput.update_forward_refs()
GcpCredentialCreateInput.update_forward_refs()
GcpCredentialSecretChangedInput.update_forward_refs()
GcpCredentialUpdateInput.update_forward_refs()
GcpPubSubInferSchemaInput.update_forward_refs()
GcpPubSubLiteInferSchemaInput.update_forward_refs()
GcpPubSubLiteSourceCreateInput.update_forward_refs()
GcpPubSubLiteSourceUpdateInput.update_forward_refs()
GcpPubSubSourceCreateInput.update_forward_refs()
GcpPubSubSourceUpdateInput.update_forward_refs()
GcpStorageInferSchemaInput.update_forward_refs()
GcpStorageSourceCreateInput.update_forward_refs()
GcpStorageSourceUpdateInput.update_forward_refs()
IdentityDeleteInput.update_forward_refs()
IdentityProviderDeleteInput.update_forward_refs()
IncidentsInput.update_forward_refs()
KafkaInferSchemaInput.update_forward_refs()
KafkaSaslSslPlainCredentialCreateInput.update_forward_refs()
KafkaSaslSslPlainCredentialSecretChangedInput.update_forward_refs()
KafkaSaslSslPlainCredentialUpdateInput.update_forward_refs()
KafkaSourceCreateInput.update_forward_refs()
KafkaSourceUpdateInput.update_forward_refs()
KafkaSslCredentialCreateInput.update_forward_refs()
KafkaSslCredentialSecretChangedInput.update_forward_refs()
KafkaSslCredentialUpdateInput.update_forward_refs()
LocalIdentityProviderUpdateInput.update_forward_refs()
NotificationRuleCreateInput.update_forward_refs()
NotificationRuleDeleteInput.update_forward_refs()
NotificationRuleUpdateInput.update_forward_refs()
NumericAnomalyValidatorCreateInput.update_forward_refs()
NumericAnomalyValidatorUpdateInput.update_forward_refs()
NumericDistributionValidatorCreateInput.update_forward_refs()
NumericDistributionValidatorUpdateInput.update_forward_refs()
NumericValidatorCreateInput.update_forward_refs()
NumericValidatorUpdateInput.update_forward_refs()
PostgreSqlCredentialCreateInput.update_forward_refs()
PostgreSqlCredentialSecretChangedInput.update_forward_refs()
PostgreSqlCredentialUpdateInput.update_forward_refs()
PostgreSqlInferSchemaInput.update_forward_refs()
PostgreSqlSourceCreateInput.update_forward_refs()
PostgreSqlSourceUpdateInput.update_forward_refs()
ReferenceSourceConfigCreateInput.update_forward_refs()
ReferenceSourceConfigUpdateInput.update_forward_refs()
RelativeTimeValidatorCreateInput.update_forward_refs()
RelativeTimeValidatorUpdateInput.update_forward_refs()
RelativeVolumeValidatorCreateInput.update_forward_refs()
RelativeVolumeValidatorUpdateInput.update_forward_refs()
ResourceFilter.update_forward_refs()
ResourceNamespaceUpdateInput.update_forward_refs()
SamlIdentityProviderCreateInput.update_forward_refs()
SamlIdentityProviderUpdateInput.update_forward_refs()
SegmentIncidentsInput.update_forward_refs()
SegmentationCreateInput.update_forward_refs()
SessionizedWindowCreateInput.update_forward_refs()
SessionizedWindowUpdateInput.update_forward_refs()
SlackChannelCreateInput.update_forward_refs()
SlackChannelUpdateInput.update_forward_refs()
SnowflakeCredentialCreateInput.update_forward_refs()
SnowflakeCredentialSecretChangedInput.update_forward_refs()
SnowflakeCredentialUpdateInput.update_forward_refs()
SnowflakeDestinationCreateInput.update_forward_refs()
SnowflakeDestinationUpdateInput.update_forward_refs()
SnowflakeInferSchemaInput.update_forward_refs()
SnowflakeSourceCreateInput.update_forward_refs()
SnowflakeSourceUpdateInput.update_forward_refs()
SourceConfigCreateInput.update_forward_refs()
SourceConfigUpdateInput.update_forward_refs()
SourceIncidentsInput.update_forward_refs()
TimeRangeInput.update_forward_refs()
TumblingWindowCreateInput.update_forward_refs()
TumblingWindowUpdateInput.update_forward_refs()
UserCreateInput.update_forward_refs()
UserDeleteInput.update_forward_refs()
UserUpdateInput.update_forward_refs()
ValidatorIncidentsInput.update_forward_refs()
ValidatorMetricDebugInfoInput.update_forward_refs()
ValidatorRecommendationApplyInput.update_forward_refs()
ValidatorRecommendationDismissInput.update_forward_refs()
ValidatorSegmentIncidentsInput.update_forward_refs()
ValidatorSegmentMetricsInput.update_forward_refs()
ValidatorWithDynamicThresholdUpdateInput.update_forward_refs()
ValidatorWithFixedThresholdUpdateInput.update_forward_refs()
VolumeValidatorCreateInput.update_forward_refs()
VolumeValidatorUpdateInput.update_forward_refs()
WebhookChannelCreateInput.update_forward_refs()
WebhookChannelUpdateInput.update_forward_refs()
