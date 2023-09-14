from datetime import datetime
from typing import Annotated, Any, List, Literal, Optional, Union

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
    ApiErrorCode,
    CategoricalDistributionMetric,
    ComparisonOperator,
    DecisionBoundsType,
    FileFormat,
    IdentityDeleteErrorCode,
    IdentityProviderCreateErrorCode,
    IdentityProviderDeleteErrorCode,
    IdentityProviderUpdateErrorCode,
    NotificationSeverity,
    NotificationTypename,
    NumericAnomalyMetric,
    NumericDistributionMetric,
    NumericMetric,
    RelativeTimeMetric,
    RelativeVolumeMetric,
    Role,
    SourceState,
    UserDeleteErrorCode,
    UserStatus,
    UserUpdateErrorCode,
    VolumeMetric,
    WindowTimeUnit,
)


class ErrorDetails(BaseModel):
    typename__: str = Field(alias="__typename")
    code: ApiErrorCode
    message: str


class ChannelCreation(BaseModel):
    errors: List["ChannelCreationErrors"]
    channel: Optional[
        Annotated[
            Union[
                "ChannelCreationChannelChannel",
                "ChannelCreationChannelSlackChannel",
                "ChannelCreationChannelWebhookChannel",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class ChannelCreationErrors(ErrorDetails):
    pass


class ChannelCreationChannelChannel(BaseModel):
    typename__: Literal["Channel"] = Field(alias="__typename")
    id: Any
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ChannelCreationChannelSlackChannel(BaseModel):
    typename__: Literal["SlackChannel"] = Field(alias="__typename")
    id: Any
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ChannelCreationChannelSlackChannelConfig"


class ChannelCreationChannelSlackChannelConfig(BaseModel):
    webhook_url: str = Field(alias="webhookUrl")
    timezone: Optional[str]
    application_link_url: str = Field(alias="applicationLinkUrl")


class ChannelCreationChannelWebhookChannel(BaseModel):
    typename__: Literal["WebhookChannel"] = Field(alias="__typename")
    id: Any
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ChannelCreationChannelWebhookChannelConfig"


class ChannelCreationChannelWebhookChannelConfig(BaseModel):
    webhook_url: str = Field(alias="webhookUrl")
    application_link_url: str = Field(alias="applicationLinkUrl")
    auth_header: Optional[str] = Field(alias="authHeader")


class ChannelDeletion(BaseModel):
    errors: List["ChannelDeletionErrors"]
    channel: Optional["ChannelDeletionChannel"]


class ChannelDeletionErrors(BaseModel):
    code: ApiErrorCode
    message: str


class ChannelDeletionChannel(BaseModel):
    id: Any
    name: str


class ChannelUpdate(BaseModel):
    errors: List["ChannelUpdateErrors"]
    channel: Optional[
        Annotated[
            Union[
                "ChannelUpdateChannelChannel",
                "ChannelUpdateChannelSlackChannel",
                "ChannelUpdateChannelWebhookChannel",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class ChannelUpdateErrors(BaseModel):
    code: ApiErrorCode
    message: str


class ChannelUpdateChannelChannel(BaseModel):
    typename__: Literal["Channel"] = Field(alias="__typename")
    id: Any
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ChannelUpdateChannelSlackChannel(BaseModel):
    typename__: Literal["SlackChannel"] = Field(alias="__typename")
    id: Any
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ChannelUpdateChannelSlackChannelConfig"


class ChannelUpdateChannelSlackChannelConfig(BaseModel):
    webhook_url: str = Field(alias="webhookUrl")
    timezone: Optional[str]
    application_link_url: str = Field(alias="applicationLinkUrl")


class ChannelUpdateChannelWebhookChannel(BaseModel):
    typename__: Literal["WebhookChannel"] = Field(alias="__typename")
    id: Any
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ChannelUpdateChannelWebhookChannelConfig"


class ChannelUpdateChannelWebhookChannelConfig(BaseModel):
    webhook_url: str = Field(alias="webhookUrl")
    application_link_url: str = Field(alias="applicationLinkUrl")
    auth_header: Optional[str] = Field(alias="authHeader")


class CredentialCreation(BaseModel):
    typename__: str = Field(alias="__typename")
    errors: List["CredentialCreationErrors"]
    credential: Optional[
        Annotated[
            Union[
                "CredentialCreationCredentialCredential",
                "CredentialCreationCredentialAwsCredential",
                "CredentialCreationCredentialAwsAthenaCredential",
                "CredentialCreationCredentialAwsRedshiftCredential",
                "CredentialCreationCredentialPostgreSqlCredential",
                "CredentialCreationCredentialSnowflakeCredential",
                "CredentialCreationCredentialKafkaSslCredential",
                "CredentialCreationCredentialKafkaSaslSslPlainCredential",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class CredentialCreationErrors(ErrorDetails):
    pass


class CredentialCreationCredentialCredential(BaseModel):
    typename__: Literal["Credential", "DemoCredential", "GcpCredential"] = Field(
        alias="__typename"
    )
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class CredentialCreationCredentialAwsCredential(BaseModel):
    typename__: Literal["AwsCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialCreationCredentialAwsCredentialConfig"


class CredentialCreationCredentialAwsCredentialConfig(BaseModel):
    access_key: str = Field(alias="accessKey")


class CredentialCreationCredentialAwsAthenaCredential(BaseModel):
    typename__: Literal["AwsAthenaCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialCreationCredentialAwsAthenaCredentialConfig"


class CredentialCreationCredentialAwsAthenaCredentialConfig(BaseModel):
    access_key: str = Field(alias="accessKey")
    region: str
    query_result_location: str = Field(alias="queryResultLocation")


class CredentialCreationCredentialAwsRedshiftCredential(BaseModel):
    typename__: Literal["AwsRedshiftCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialCreationCredentialAwsRedshiftCredentialConfig"


class CredentialCreationCredentialAwsRedshiftCredentialConfig(BaseModel):
    host: str
    port: int
    user: str
    default_database: str = Field(alias="defaultDatabase")


class CredentialCreationCredentialPostgreSqlCredential(BaseModel):
    typename__: Literal["PostgreSqlCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialCreationCredentialPostgreSqlCredentialConfig"


class CredentialCreationCredentialPostgreSqlCredentialConfig(BaseModel):
    host: str
    port: int
    user: str
    default_database: str = Field(alias="defaultDatabase")


class CredentialCreationCredentialSnowflakeCredential(BaseModel):
    typename__: Literal["SnowflakeCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialCreationCredentialSnowflakeCredentialConfig"


class CredentialCreationCredentialSnowflakeCredentialConfig(BaseModel):
    account: str
    user: str


class CredentialCreationCredentialKafkaSslCredential(BaseModel):
    typename__: Literal["KafkaSslCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialCreationCredentialKafkaSslCredentialConfig"


class CredentialCreationCredentialKafkaSslCredentialConfig(BaseModel):
    bootstrap_servers: List[str] = Field(alias="bootstrapServers")
    ca_certificate: str = Field(alias="caCertificate")


class CredentialCreationCredentialKafkaSaslSslPlainCredential(BaseModel):
    typename__: Literal["KafkaSaslSslPlainCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialCreationCredentialKafkaSaslSslPlainCredentialConfig"


class CredentialCreationCredentialKafkaSaslSslPlainCredentialConfig(BaseModel):
    bootstrap_servers: List[str] = Field(alias="bootstrapServers")
    username: str


class CredentialSecretChanged(BaseModel):
    errors: List["CredentialSecretChangedErrors"]
    has_changed: Optional[bool] = Field(alias="hasChanged")


class CredentialSecretChangedErrors(ErrorDetails):
    pass


class CredentialUpdate(BaseModel):
    errors: List["CredentialUpdateErrors"]
    credential: Optional[
        Annotated[
            Union[
                "CredentialUpdateCredentialCredential",
                "CredentialUpdateCredentialAwsCredential",
                "CredentialUpdateCredentialAwsAthenaCredential",
                "CredentialUpdateCredentialAwsRedshiftCredential",
                "CredentialUpdateCredentialPostgreSqlCredential",
                "CredentialUpdateCredentialSnowflakeCredential",
                "CredentialUpdateCredentialKafkaSslCredential",
                "CredentialUpdateCredentialKafkaSaslSslPlainCredential",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class CredentialUpdateErrors(ErrorDetails):
    pass


class CredentialUpdateCredentialCredential(BaseModel):
    typename__: Literal["Credential", "DemoCredential", "GcpCredential"] = Field(
        alias="__typename"
    )
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class CredentialUpdateCredentialAwsCredential(BaseModel):
    typename__: Literal["AwsCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialUpdateCredentialAwsCredentialConfig"


class CredentialUpdateCredentialAwsCredentialConfig(BaseModel):
    access_key: str = Field(alias="accessKey")


class CredentialUpdateCredentialAwsAthenaCredential(BaseModel):
    typename__: Literal["AwsAthenaCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialUpdateCredentialAwsAthenaCredentialConfig"


class CredentialUpdateCredentialAwsAthenaCredentialConfig(BaseModel):
    access_key: str = Field(alias="accessKey")
    region: str
    query_result_location: str = Field(alias="queryResultLocation")


class CredentialUpdateCredentialAwsRedshiftCredential(BaseModel):
    typename__: Literal["AwsRedshiftCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialUpdateCredentialAwsRedshiftCredentialConfig"


class CredentialUpdateCredentialAwsRedshiftCredentialConfig(BaseModel):
    host: str
    port: int
    user: str
    default_database: str = Field(alias="defaultDatabase")


class CredentialUpdateCredentialPostgreSqlCredential(BaseModel):
    typename__: Literal["PostgreSqlCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialUpdateCredentialPostgreSqlCredentialConfig"


class CredentialUpdateCredentialPostgreSqlCredentialConfig(BaseModel):
    host: str
    port: int
    user: str
    default_database: str = Field(alias="defaultDatabase")


class CredentialUpdateCredentialSnowflakeCredential(BaseModel):
    typename__: Literal["SnowflakeCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialUpdateCredentialSnowflakeCredentialConfig"


class CredentialUpdateCredentialSnowflakeCredentialConfig(BaseModel):
    account: str
    user: str


class CredentialUpdateCredentialKafkaSslCredential(BaseModel):
    typename__: Literal["KafkaSslCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialUpdateCredentialKafkaSslCredentialConfig"


class CredentialUpdateCredentialKafkaSslCredentialConfig(BaseModel):
    bootstrap_servers: List[str] = Field(alias="bootstrapServers")
    ca_certificate: str = Field(alias="caCertificate")


class CredentialUpdateCredentialKafkaSaslSslPlainCredential(BaseModel):
    typename__: Literal["KafkaSaslSslPlainCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialUpdateCredentialKafkaSaslSslPlainCredentialConfig"


class CredentialUpdateCredentialKafkaSaslSslPlainCredentialConfig(BaseModel):
    bootstrap_servers: List[str] = Field(alias="bootstrapServers")
    username: str


class DestinationCreation(BaseModel):
    errors: List["DestinationCreationErrors"]
    destination: Optional[
        Annotated[
            Union[
                "DestinationCreationDestinationDestination",
                "DestinationCreationDestinationGcpBigQueryDestination",
                "DestinationCreationDestinationSnowflakeDestination",
                "DestinationCreationDestinationAwsKinesisDestination",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class DestinationCreationErrors(ErrorDetails):
    pass


class DestinationCreationDestinationDestination(BaseModel):
    typename__: Literal["Destination"] = Field(alias="__typename")
    id: DestinationId
    name: str
    credential: "DestinationCreationDestinationDestinationCredential"
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class DestinationCreationDestinationDestinationCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class DestinationCreationDestinationGcpBigQueryDestination(BaseModel):
    typename__: Literal["GcpBigQueryDestination"] = Field(alias="__typename")
    id: DestinationId
    name: str
    credential: "DestinationCreationDestinationGcpBigQueryDestinationCredential"
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "DestinationCreationDestinationGcpBigQueryDestinationConfig"


class DestinationCreationDestinationGcpBigQueryDestinationCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class DestinationCreationDestinationGcpBigQueryDestinationConfig(BaseModel):
    project: str
    dataset: str
    table: str


class DestinationCreationDestinationSnowflakeDestination(BaseModel):
    typename__: Literal["SnowflakeDestination"] = Field(alias="__typename")
    id: DestinationId
    name: str
    credential: "DestinationCreationDestinationSnowflakeDestinationCredential"
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "DestinationCreationDestinationSnowflakeDestinationConfig"


class DestinationCreationDestinationSnowflakeDestinationCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class DestinationCreationDestinationSnowflakeDestinationConfig(BaseModel):
    database: str
    db_schema: Any = Field(alias="schema")
    table: str
    role: str
    warehouse: str


class DestinationCreationDestinationAwsKinesisDestination(BaseModel):
    typename__: Literal["AwsKinesisDestination"] = Field(alias="__typename")
    id: DestinationId
    name: str
    credential: "DestinationCreationDestinationAwsKinesisDestinationCredential"
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "DestinationCreationDestinationAwsKinesisDestinationConfig"


class DestinationCreationDestinationAwsKinesisDestinationCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class DestinationCreationDestinationAwsKinesisDestinationConfig(BaseModel):
    region: str
    stream_name: str = Field(alias="streamName")
    endpoint: Optional[str]


class DestinationUpdate(BaseModel):
    errors: List["DestinationUpdateErrors"]
    destination: Optional[
        Annotated[
            Union[
                "DestinationUpdateDestinationDestination",
                "DestinationUpdateDestinationGcpBigQueryDestination",
                "DestinationUpdateDestinationSnowflakeDestination",
                "DestinationUpdateDestinationAwsKinesisDestination",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class DestinationUpdateErrors(ErrorDetails):
    pass


class DestinationUpdateDestinationDestination(BaseModel):
    typename__: Literal["Destination"] = Field(alias="__typename")
    id: DestinationId
    name: str
    credential: "DestinationUpdateDestinationDestinationCredential"
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class DestinationUpdateDestinationDestinationCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class DestinationUpdateDestinationGcpBigQueryDestination(BaseModel):
    typename__: Literal["GcpBigQueryDestination"] = Field(alias="__typename")
    id: DestinationId
    name: str
    credential: "DestinationUpdateDestinationGcpBigQueryDestinationCredential"
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "DestinationUpdateDestinationGcpBigQueryDestinationConfig"


class DestinationUpdateDestinationGcpBigQueryDestinationCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class DestinationUpdateDestinationGcpBigQueryDestinationConfig(BaseModel):
    project: str
    dataset: str
    table: str


class DestinationUpdateDestinationSnowflakeDestination(BaseModel):
    typename__: Literal["SnowflakeDestination"] = Field(alias="__typename")
    id: DestinationId
    name: str
    credential: "DestinationUpdateDestinationSnowflakeDestinationCredential"
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "DestinationUpdateDestinationSnowflakeDestinationConfig"


class DestinationUpdateDestinationSnowflakeDestinationCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class DestinationUpdateDestinationSnowflakeDestinationConfig(BaseModel):
    database: str
    db_schema: Any = Field(alias="schema")
    table: str
    role: str
    warehouse: str


class DestinationUpdateDestinationAwsKinesisDestination(BaseModel):
    typename__: Literal["AwsKinesisDestination"] = Field(alias="__typename")
    id: DestinationId
    name: str
    credential: "DestinationUpdateDestinationAwsKinesisDestinationCredential"
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "DestinationUpdateDestinationAwsKinesisDestinationConfig"


class DestinationUpdateDestinationAwsKinesisDestinationCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class DestinationUpdateDestinationAwsKinesisDestinationConfig(BaseModel):
    region: str
    stream_name: str = Field(alias="streamName")
    endpoint: Optional[str]


class IdentityDeletion(BaseModel):
    errors: List["IdentityDeletionErrors"]


class IdentityDeletionErrors(BaseModel):
    code: IdentityDeleteErrorCode
    message: str


class IdentityProviderCreation(BaseModel):
    errors: List["IdentityProviderCreationErrors"]
    identity_provider: Optional[
        Annotated[
            Union[
                "IdentityProviderCreationIdentityProviderIdentityProvider",
                "IdentityProviderCreationIdentityProviderSamlIdentityProvider",
            ],
            Field(discriminator="typename__"),
        ]
    ] = Field(alias="identityProvider")


class IdentityProviderCreationErrors(BaseModel):
    code: IdentityProviderCreateErrorCode
    message: Optional[str]


class IdentityProviderCreationIdentityProviderIdentityProvider(BaseModel):
    typename__: Literal["IdentityProvider", "LocalIdentityProvider"] = Field(
        alias="__typename"
    )
    id: str
    name: str
    disabled: bool
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class IdentityProviderCreationIdentityProviderSamlIdentityProvider(BaseModel):
    typename__: Literal["SamlIdentityProvider"] = Field(alias="__typename")
    id: str
    name: str
    disabled: bool
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "IdentityProviderCreationIdentityProviderSamlIdentityProviderConfig"


class IdentityProviderCreationIdentityProviderSamlIdentityProviderConfig(BaseModel):
    entry_point: str = Field(alias="entryPoint")
    entity_id: str = Field(alias="entityId")
    cert: str


class IdentityProviderDeletion(BaseModel):
    errors: List["IdentityProviderDeletionErrors"]


class IdentityProviderDeletionErrors(BaseModel):
    code: IdentityProviderDeleteErrorCode
    message: Optional[str]


class IdentityProviderUpdate(BaseModel):
    errors: List["IdentityProviderUpdateErrors"]
    identity_provider: Optional[
        Annotated[
            Union[
                "IdentityProviderUpdateIdentityProviderIdentityProvider",
                "IdentityProviderUpdateIdentityProviderSamlIdentityProvider",
            ],
            Field(discriminator="typename__"),
        ]
    ] = Field(alias="identityProvider")


class IdentityProviderUpdateErrors(BaseModel):
    code: IdentityProviderUpdateErrorCode
    message: Optional[str]


class IdentityProviderUpdateIdentityProviderIdentityProvider(BaseModel):
    typename__: Literal["IdentityProvider", "LocalIdentityProvider"] = Field(
        alias="__typename"
    )
    id: str
    name: str
    disabled: bool
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class IdentityProviderUpdateIdentityProviderSamlIdentityProvider(BaseModel):
    typename__: Literal["SamlIdentityProvider"] = Field(alias="__typename")
    id: str
    name: str
    disabled: bool
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "IdentityProviderUpdateIdentityProviderSamlIdentityProviderConfig"


class IdentityProviderUpdateIdentityProviderSamlIdentityProviderConfig(BaseModel):
    entry_point: str = Field(alias="entryPoint")
    entity_id: str = Field(alias="entityId")
    cert: str


class NamespaceUpdate(BaseModel):
    errors: List["NamespaceUpdateErrors"]
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")


class NamespaceUpdateErrors(ErrorDetails):
    pass


class NotificationRuleDetails(BaseModel):
    typename__: str = Field(alias="__typename")
    id: Any
    name: str
    notification_typenames: List[NotificationTypename] = Field(
        alias="notificationTypenames"
    )
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    sources: List[Optional[SourceId]]
    channel: Union[
        "NotificationRuleDetailsChannelChannel",
        "NotificationRuleDetailsChannelSlackChannel",
        "NotificationRuleDetailsChannelWebhookChannel",
    ] = Field(discriminator="typename__")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class NotificationRuleDetailsChannelChannel(BaseModel):
    typename__: Literal["Channel"] = Field(alias="__typename")
    id: Any
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class NotificationRuleDetailsChannelSlackChannel(BaseModel):
    typename__: Literal["SlackChannel"] = Field(alias="__typename")
    id: Any
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "NotificationRuleDetailsChannelSlackChannelConfig"


class NotificationRuleDetailsChannelSlackChannelConfig(BaseModel):
    webhook_url: str = Field(alias="webhookUrl")
    timezone: Optional[str]
    application_link_url: str = Field(alias="applicationLinkUrl")


class NotificationRuleDetailsChannelWebhookChannel(BaseModel):
    typename__: Literal["WebhookChannel"] = Field(alias="__typename")
    id: Any
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "NotificationRuleDetailsChannelWebhookChannelConfig"


class NotificationRuleDetailsChannelWebhookChannelConfig(BaseModel):
    webhook_url: str = Field(alias="webhookUrl")
    application_link_url: str = Field(alias="applicationLinkUrl")
    auth_header: Optional[str] = Field(alias="authHeader")


class NotificationRuleCreation(BaseModel):
    errors: List["NotificationRuleCreationErrors"]
    notification_rule: Optional["NotificationRuleCreationNotificationRule"] = Field(
        alias="notificationRule"
    )


class NotificationRuleCreationErrors(BaseModel):
    code: ApiErrorCode
    message: str


class NotificationRuleCreationNotificationRule(NotificationRuleDetails):
    pass


class NotificationRuleDeletion(BaseModel):
    errors: List["NotificationRuleDeletionErrors"]
    notification_rule: Optional["NotificationRuleDeletionNotificationRule"] = Field(
        alias="notificationRule"
    )


class NotificationRuleDeletionErrors(BaseModel):
    code: ApiErrorCode
    message: str


class NotificationRuleDeletionNotificationRule(BaseModel):
    typename__: Literal["NotificationRule"] = Field(alias="__typename")
    id: Any
    name: str


class NotificationRuleUpdate(BaseModel):
    errors: List["NotificationRuleUpdateErrors"]
    notification_rule: Optional["NotificationRuleUpdateNotificationRule"] = Field(
        alias="notificationRule"
    )


class NotificationRuleUpdateErrors(BaseModel):
    code: ApiErrorCode
    message: str


class NotificationRuleUpdateNotificationRule(NotificationRuleDetails):
    pass


class ReferenceSourceConfigDetails(BaseModel):
    source: "ReferenceSourceConfigDetailsSource"
    window: "ReferenceSourceConfigDetailsWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class ReferenceSourceConfigDetailsSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ReferenceSourceConfigDetailsWindow(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SegmentDetails(BaseModel):
    typename__: str = Field(alias="__typename")
    id: Any
    fields: List["SegmentDetailsFields"]
    muted: bool


class SegmentDetailsFields(BaseModel):
    field: JsonPointer
    value: str


class SegmentationDetails(BaseModel):
    typename__: str = Field(alias="__typename")
    id: SegmentationId
    name: str
    source: "SegmentationDetailsSource"
    fields: List[str]
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SegmentationDetailsSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SegmentationCreation(BaseModel):
    errors: List["SegmentationCreationErrors"]
    segmentation: Optional["SegmentationCreationSegmentation"]


class SegmentationCreationErrors(ErrorDetails):
    pass


class SegmentationCreationSegmentation(SegmentationDetails):
    pass


class SegmentationSummary(BaseModel):
    typename__: str = Field(alias="__typename")
    id: SegmentationId
    name: str
    fields: List[str]
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class SourceCreation(BaseModel):
    errors: List["SourceCreationErrors"]
    source: Optional[
        Annotated[
            Union[
                "SourceCreationSourceSource",
                "SourceCreationSourceGcpStorageSource",
                "SourceCreationSourceGcpBigQuerySource",
                "SourceCreationSourceGcpPubSubSource",
                "SourceCreationSourceGcpPubSubLiteSource",
                "SourceCreationSourceAwsAthenaSource",
                "SourceCreationSourceAwsKinesisSource",
                "SourceCreationSourceAwsRedshiftSource",
                "SourceCreationSourceAwsS3Source",
                "SourceCreationSourcePostgreSqlSource",
                "SourceCreationSourceSnowflakeSource",
                "SourceCreationSourceKafkaSource",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class SourceCreationErrors(ErrorDetails):
    pass


class SourceCreationSourceSource(BaseModel):
    typename__: Literal["DemoSource", "Source"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceCreationSourceSourceCredential"
    windows: List["SourceCreationSourceSourceWindows"]
    segmentations: List["SourceCreationSourceSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceGcpStorageSource(BaseModel):
    typename__: Literal["GcpStorageSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceCreationSourceGcpStorageSourceCredential"
    windows: List["SourceCreationSourceGcpStorageSourceWindows"]
    segmentations: List["SourceCreationSourceGcpStorageSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "SourceCreationSourceGcpStorageSourceConfig"


class SourceCreationSourceGcpStorageSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceGcpStorageSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceGcpStorageSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceGcpStorageSourceConfig(BaseModel):
    project: str
    bucket: str
    folder: str
    csv: Optional["SourceCreationSourceGcpStorageSourceConfigCsv"]
    schedule: CronExpression
    file_pattern: Optional[str] = Field(alias="filePattern")
    file_format: Optional[FileFormat] = Field(alias="fileFormat")


class SourceCreationSourceGcpStorageSourceConfigCsv(BaseModel):
    null_marker: Optional[str] = Field(alias="nullMarker")
    delimiter: str


class SourceCreationSourceGcpBigQuerySource(BaseModel):
    typename__: Literal["GcpBigQuerySource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceCreationSourceGcpBigQuerySourceCredential"
    windows: List["SourceCreationSourceGcpBigQuerySourceWindows"]
    segmentations: List["SourceCreationSourceGcpBigQuerySourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "SourceCreationSourceGcpBigQuerySourceConfig"


class SourceCreationSourceGcpBigQuerySourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceGcpBigQuerySourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceGcpBigQuerySourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceGcpBigQuerySourceConfig(BaseModel):
    project: str
    dataset: str
    table: str
    cursor_field: str = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: CronExpression


class SourceCreationSourceGcpPubSubSource(BaseModel):
    typename__: Literal["GcpPubSubSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceCreationSourceGcpPubSubSourceCredential"
    windows: List["SourceCreationSourceGcpPubSubSourceWindows"]
    segmentations: List["SourceCreationSourceGcpPubSubSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "SourceCreationSourceGcpPubSubSourceConfig"


class SourceCreationSourceGcpPubSubSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceGcpPubSubSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceGcpPubSubSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceGcpPubSubSourceConfig(BaseModel):
    project: str
    subscription_id: str = Field(alias="subscriptionId")


class SourceCreationSourceGcpPubSubLiteSource(BaseModel):
    typename__: Literal["GcpPubSubLiteSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceCreationSourceGcpPubSubLiteSourceCredential"
    windows: List["SourceCreationSourceGcpPubSubLiteSourceWindows"]
    segmentations: List["SourceCreationSourceGcpPubSubLiteSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "SourceCreationSourceGcpPubSubLiteSourceConfig"


class SourceCreationSourceGcpPubSubLiteSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceGcpPubSubLiteSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceGcpPubSubLiteSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceGcpPubSubLiteSourceConfig(BaseModel):
    location: str
    project: str
    subscription_id: str = Field(alias="subscriptionId")


class SourceCreationSourceAwsAthenaSource(BaseModel):
    typename__: Literal["AwsAthenaSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceCreationSourceAwsAthenaSourceCredential"
    windows: List["SourceCreationSourceAwsAthenaSourceWindows"]
    segmentations: List["SourceCreationSourceAwsAthenaSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "SourceCreationSourceAwsAthenaSourceConfig"


class SourceCreationSourceAwsAthenaSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceAwsAthenaSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceAwsAthenaSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceAwsAthenaSourceConfig(BaseModel):
    catalog: str
    database: str
    table: str
    cursor_field: str = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: CronExpression


class SourceCreationSourceAwsKinesisSource(BaseModel):
    typename__: Literal["AwsKinesisSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceCreationSourceAwsKinesisSourceCredential"
    windows: List["SourceCreationSourceAwsKinesisSourceWindows"]
    segmentations: List["SourceCreationSourceAwsKinesisSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "SourceCreationSourceAwsKinesisSourceConfig"


class SourceCreationSourceAwsKinesisSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceAwsKinesisSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceAwsKinesisSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceAwsKinesisSourceConfig(BaseModel):
    region: str
    stream_name: str = Field(alias="streamName")


class SourceCreationSourceAwsRedshiftSource(BaseModel):
    typename__: Literal["AwsRedshiftSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceCreationSourceAwsRedshiftSourceCredential"
    windows: List["SourceCreationSourceAwsRedshiftSourceWindows"]
    segmentations: List["SourceCreationSourceAwsRedshiftSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "SourceCreationSourceAwsRedshiftSourceConfig"


class SourceCreationSourceAwsRedshiftSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceAwsRedshiftSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceAwsRedshiftSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceAwsRedshiftSourceConfig(BaseModel):
    database: str
    db_schema: Any = Field(alias="schema")
    table: str
    cursor_field: str = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: CronExpression


class SourceCreationSourceAwsS3Source(BaseModel):
    typename__: Literal["AwsS3Source"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceCreationSourceAwsS3SourceCredential"
    windows: List["SourceCreationSourceAwsS3SourceWindows"]
    segmentations: List["SourceCreationSourceAwsS3SourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "SourceCreationSourceAwsS3SourceConfig"


class SourceCreationSourceAwsS3SourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceAwsS3SourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceAwsS3SourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceAwsS3SourceConfig(BaseModel):
    bucket: str
    prefix: str
    csv: Optional["SourceCreationSourceAwsS3SourceConfigCsv"]
    schedule: CronExpression
    file_pattern: Optional[str] = Field(alias="filePattern")
    file_format: Optional[FileFormat] = Field(alias="fileFormat")


class SourceCreationSourceAwsS3SourceConfigCsv(BaseModel):
    null_marker: Optional[str] = Field(alias="nullMarker")
    delimiter: str


class SourceCreationSourcePostgreSqlSource(BaseModel):
    typename__: Literal["PostgreSqlSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceCreationSourcePostgreSqlSourceCredential"
    windows: List["SourceCreationSourcePostgreSqlSourceWindows"]
    segmentations: List["SourceCreationSourcePostgreSqlSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "SourceCreationSourcePostgreSqlSourceConfig"


class SourceCreationSourcePostgreSqlSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourcePostgreSqlSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourcePostgreSqlSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourcePostgreSqlSourceConfig(BaseModel):
    database: str
    db_schema: Any = Field(alias="schema")
    table: str
    cursor_field: str = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: CronExpression


class SourceCreationSourceSnowflakeSource(BaseModel):
    typename__: Literal["SnowflakeSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceCreationSourceSnowflakeSourceCredential"
    windows: List["SourceCreationSourceSnowflakeSourceWindows"]
    segmentations: List["SourceCreationSourceSnowflakeSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "SourceCreationSourceSnowflakeSourceConfig"


class SourceCreationSourceSnowflakeSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceSnowflakeSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceSnowflakeSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceSnowflakeSourceConfig(BaseModel):
    role: Optional[str]
    warehouse: Optional[str]
    database: str
    db_schema: Any = Field(alias="schema")
    table: str
    cursor_field: str = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: CronExpression


class SourceCreationSourceKafkaSource(BaseModel):
    typename__: Literal["KafkaSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceCreationSourceKafkaSourceCredential"
    windows: List["SourceCreationSourceKafkaSourceWindows"]
    segmentations: List["SourceCreationSourceKafkaSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "SourceCreationSourceKafkaSourceConfig"


class SourceCreationSourceKafkaSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceKafkaSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceKafkaSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceKafkaSourceConfig(BaseModel):
    topic: str


class SourceUpdate(BaseModel):
    errors: List["SourceUpdateErrors"]
    source: Optional[
        Annotated[
            Union[
                "SourceUpdateSourceSource",
                "SourceUpdateSourceGcpStorageSource",
                "SourceUpdateSourceGcpBigQuerySource",
                "SourceUpdateSourceGcpPubSubSource",
                "SourceUpdateSourceGcpPubSubLiteSource",
                "SourceUpdateSourceAwsAthenaSource",
                "SourceUpdateSourceAwsKinesisSource",
                "SourceUpdateSourceAwsRedshiftSource",
                "SourceUpdateSourceAwsS3Source",
                "SourceUpdateSourcePostgreSqlSource",
                "SourceUpdateSourceSnowflakeSource",
                "SourceUpdateSourceKafkaSource",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class SourceUpdateErrors(ErrorDetails):
    pass


class SourceUpdateSourceSource(BaseModel):
    typename__: Literal["DemoSource", "Source"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceUpdateSourceSourceCredential"
    windows: List["SourceUpdateSourceSourceWindows"]
    segmentations: List["SourceUpdateSourceSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceGcpStorageSource(BaseModel):
    typename__: Literal["GcpStorageSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceUpdateSourceGcpStorageSourceCredential"
    windows: List["SourceUpdateSourceGcpStorageSourceWindows"]
    segmentations: List["SourceUpdateSourceGcpStorageSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "SourceUpdateSourceGcpStorageSourceConfig"


class SourceUpdateSourceGcpStorageSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceGcpStorageSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceGcpStorageSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceGcpStorageSourceConfig(BaseModel):
    project: str
    bucket: str
    folder: str
    csv: Optional["SourceUpdateSourceGcpStorageSourceConfigCsv"]
    schedule: CronExpression
    file_pattern: Optional[str] = Field(alias="filePattern")
    file_format: Optional[FileFormat] = Field(alias="fileFormat")


class SourceUpdateSourceGcpStorageSourceConfigCsv(BaseModel):
    null_marker: Optional[str] = Field(alias="nullMarker")
    delimiter: str


class SourceUpdateSourceGcpBigQuerySource(BaseModel):
    typename__: Literal["GcpBigQuerySource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceUpdateSourceGcpBigQuerySourceCredential"
    windows: List["SourceUpdateSourceGcpBigQuerySourceWindows"]
    segmentations: List["SourceUpdateSourceGcpBigQuerySourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "SourceUpdateSourceGcpBigQuerySourceConfig"


class SourceUpdateSourceGcpBigQuerySourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceGcpBigQuerySourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceGcpBigQuerySourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceGcpBigQuerySourceConfig(BaseModel):
    project: str
    dataset: str
    table: str
    cursor_field: str = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: CronExpression


class SourceUpdateSourceGcpPubSubSource(BaseModel):
    typename__: Literal["GcpPubSubSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceUpdateSourceGcpPubSubSourceCredential"
    windows: List["SourceUpdateSourceGcpPubSubSourceWindows"]
    segmentations: List["SourceUpdateSourceGcpPubSubSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "SourceUpdateSourceGcpPubSubSourceConfig"


class SourceUpdateSourceGcpPubSubSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceGcpPubSubSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceGcpPubSubSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceGcpPubSubSourceConfig(BaseModel):
    project: str
    subscription_id: str = Field(alias="subscriptionId")


class SourceUpdateSourceGcpPubSubLiteSource(BaseModel):
    typename__: Literal["GcpPubSubLiteSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceUpdateSourceGcpPubSubLiteSourceCredential"
    windows: List["SourceUpdateSourceGcpPubSubLiteSourceWindows"]
    segmentations: List["SourceUpdateSourceGcpPubSubLiteSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "SourceUpdateSourceGcpPubSubLiteSourceConfig"


class SourceUpdateSourceGcpPubSubLiteSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceGcpPubSubLiteSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceGcpPubSubLiteSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceGcpPubSubLiteSourceConfig(BaseModel):
    location: str
    project: str
    subscription_id: str = Field(alias="subscriptionId")


class SourceUpdateSourceAwsAthenaSource(BaseModel):
    typename__: Literal["AwsAthenaSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceUpdateSourceAwsAthenaSourceCredential"
    windows: List["SourceUpdateSourceAwsAthenaSourceWindows"]
    segmentations: List["SourceUpdateSourceAwsAthenaSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "SourceUpdateSourceAwsAthenaSourceConfig"


class SourceUpdateSourceAwsAthenaSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceAwsAthenaSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceAwsAthenaSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceAwsAthenaSourceConfig(BaseModel):
    catalog: str
    database: str
    table: str
    cursor_field: str = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: CronExpression


class SourceUpdateSourceAwsKinesisSource(BaseModel):
    typename__: Literal["AwsKinesisSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceUpdateSourceAwsKinesisSourceCredential"
    windows: List["SourceUpdateSourceAwsKinesisSourceWindows"]
    segmentations: List["SourceUpdateSourceAwsKinesisSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "SourceUpdateSourceAwsKinesisSourceConfig"


class SourceUpdateSourceAwsKinesisSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceAwsKinesisSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceAwsKinesisSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceAwsKinesisSourceConfig(BaseModel):
    region: str
    stream_name: str = Field(alias="streamName")


class SourceUpdateSourceAwsRedshiftSource(BaseModel):
    typename__: Literal["AwsRedshiftSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceUpdateSourceAwsRedshiftSourceCredential"
    windows: List["SourceUpdateSourceAwsRedshiftSourceWindows"]
    segmentations: List["SourceUpdateSourceAwsRedshiftSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "SourceUpdateSourceAwsRedshiftSourceConfig"


class SourceUpdateSourceAwsRedshiftSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceAwsRedshiftSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceAwsRedshiftSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceAwsRedshiftSourceConfig(BaseModel):
    database: str
    db_schema: Any = Field(alias="schema")
    table: str
    cursor_field: str = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: CronExpression


class SourceUpdateSourceAwsS3Source(BaseModel):
    typename__: Literal["AwsS3Source"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceUpdateSourceAwsS3SourceCredential"
    windows: List["SourceUpdateSourceAwsS3SourceWindows"]
    segmentations: List["SourceUpdateSourceAwsS3SourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "SourceUpdateSourceAwsS3SourceConfig"


class SourceUpdateSourceAwsS3SourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceAwsS3SourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceAwsS3SourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceAwsS3SourceConfig(BaseModel):
    bucket: str
    prefix: str
    csv: Optional["SourceUpdateSourceAwsS3SourceConfigCsv"]
    schedule: CronExpression
    file_pattern: Optional[str] = Field(alias="filePattern")
    file_format: Optional[FileFormat] = Field(alias="fileFormat")


class SourceUpdateSourceAwsS3SourceConfigCsv(BaseModel):
    null_marker: Optional[str] = Field(alias="nullMarker")
    delimiter: str


class SourceUpdateSourcePostgreSqlSource(BaseModel):
    typename__: Literal["PostgreSqlSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceUpdateSourcePostgreSqlSourceCredential"
    windows: List["SourceUpdateSourcePostgreSqlSourceWindows"]
    segmentations: List["SourceUpdateSourcePostgreSqlSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "SourceUpdateSourcePostgreSqlSourceConfig"


class SourceUpdateSourcePostgreSqlSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourcePostgreSqlSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourcePostgreSqlSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourcePostgreSqlSourceConfig(BaseModel):
    database: str
    db_schema: Any = Field(alias="schema")
    table: str
    cursor_field: str = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: CronExpression


class SourceUpdateSourceSnowflakeSource(BaseModel):
    typename__: Literal["SnowflakeSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceUpdateSourceSnowflakeSourceCredential"
    windows: List["SourceUpdateSourceSnowflakeSourceWindows"]
    segmentations: List["SourceUpdateSourceSnowflakeSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "SourceUpdateSourceSnowflakeSourceConfig"


class SourceUpdateSourceSnowflakeSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceSnowflakeSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceSnowflakeSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceSnowflakeSourceConfig(BaseModel):
    role: Optional[str]
    warehouse: Optional[str]
    database: str
    db_schema: Any = Field(alias="schema")
    table: str
    cursor_field: str = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: CronExpression


class SourceUpdateSourceKafkaSource(BaseModel):
    typename__: Literal["KafkaSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceUpdateSourceKafkaSourceCredential"
    windows: List["SourceUpdateSourceKafkaSourceWindows"]
    segmentations: List["SourceUpdateSourceKafkaSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "SourceUpdateSourceKafkaSourceConfig"


class SourceUpdateSourceKafkaSourceCredential(BaseModel):
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceKafkaSourceWindows(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceKafkaSourceSegmentations(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceKafkaSourceConfig(BaseModel):
    topic: str


class UserDetails(BaseModel):
    id: str
    display_name: str = Field(alias="displayName")
    full_name: Optional[str] = Field(alias="fullName")
    email: Optional[str]
    role: Role
    status: UserStatus
    identities: List[
        Annotated[
            Union[
                "UserDetailsIdentitiesFederatedIdentity",
                "UserDetailsIdentitiesLocalIdentity",
            ],
            Field(discriminator="typename__"),
        ]
    ]
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UserDetailsIdentitiesFederatedIdentity(BaseModel):
    typename__: Literal["FederatedIdentity"] = Field(alias="__typename")
    id: str
    user_id: Optional[str] = Field(alias="userId")
    idp: "UserDetailsIdentitiesFederatedIdentityIdp"
    created_at: datetime = Field(alias="createdAt")


class UserDetailsIdentitiesFederatedIdentityIdp(BaseModel):
    typename__: Literal[
        "IdentityProvider", "LocalIdentityProvider", "SamlIdentityProvider"
    ] = Field(alias="__typename")
    id: str
    name: str


class UserDetailsIdentitiesLocalIdentity(BaseModel):
    typename__: Literal["LocalIdentity"] = Field(alias="__typename")
    id: str
    user_id: Optional[str] = Field(alias="userId")
    username: str
    created_at: datetime = Field(alias="createdAt")


class UserCreation(BaseModel):
    errors: List["UserCreationErrors"]
    user: Optional["UserCreationUser"]


class UserCreationErrors(BaseModel):
    code: Optional[str]
    message: Optional[str]


class UserCreationUser(UserDetails):
    pass


class UserDeletion(BaseModel):
    errors: List["UserDeletionErrors"]
    user: Optional["UserDeletionUser"]


class UserDeletionErrors(BaseModel):
    code: UserDeleteErrorCode
    message: str


class UserDeletionUser(UserDetails):
    pass


class UserUpdate(BaseModel):
    errors: List["UserUpdateErrors"]
    user: Optional["UserUpdateUser"]


class UserUpdateErrors(BaseModel):
    code: UserUpdateErrorCode
    message: str


class UserUpdateUser(UserDetails):
    pass


class ValidatorCreation(BaseModel):
    errors: List["ValidatorCreationErrors"]
    validator: Optional[
        Annotated[
            Union[
                "ValidatorCreationValidatorValidator",
                "ValidatorCreationValidatorNumericValidator",
                "ValidatorCreationValidatorCategoricalDistributionValidator",
                "ValidatorCreationValidatorNumericDistributionValidator",
                "ValidatorCreationValidatorVolumeValidator",
                "ValidatorCreationValidatorNumericAnomalyValidator",
                "ValidatorCreationValidatorRelativeTimeValidator",
                "ValidatorCreationValidatorFreshnessValidator",
                "ValidatorCreationValidatorRelativeVolumeValidator",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class ValidatorCreationErrors(ErrorDetails):
    pass


class ValidatorCreationValidatorValidator(BaseModel):
    typename__: Literal["Validator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorCreationValidatorValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorValidatorSourceConfig(BaseModel):
    source: "ValidatorCreationValidatorValidatorSourceConfigSource"
    window: "ValidatorCreationValidatorValidatorSourceConfigWindow"
    segmentation: "ValidatorCreationValidatorValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorCreationValidatorValidatorSourceConfigSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorValidatorSourceConfigWindow(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorValidatorSourceConfigSegmentation(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorNumericValidator(BaseModel):
    typename__: Literal["NumericValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorCreationValidatorNumericValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorCreationValidatorNumericValidatorConfig"


class ValidatorCreationValidatorNumericValidatorSourceConfig(BaseModel):
    source: "ValidatorCreationValidatorNumericValidatorSourceConfigSource"
    window: "ValidatorCreationValidatorNumericValidatorSourceConfigWindow"
    segmentation: "ValidatorCreationValidatorNumericValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorCreationValidatorNumericValidatorSourceConfigSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorNumericValidatorSourceConfigWindow(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorNumericValidatorSourceConfigSegmentation(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorNumericValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    metric: NumericMetric
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ValidatorCreationValidatorNumericValidatorConfigThresholdDynamicThreshold",
        "ValidatorCreationValidatorNumericValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ValidatorCreationValidatorNumericValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorCreationValidatorNumericValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorCreationValidatorCategoricalDistributionValidator(BaseModel):
    typename__: Literal["CategoricalDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorCreationValidatorCategoricalDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorCreationValidatorCategoricalDistributionValidatorConfig"
    reference_source_config: "ValidatorCreationValidatorCategoricalDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class ValidatorCreationValidatorCategoricalDistributionValidatorSourceConfig(BaseModel):
    source: "ValidatorCreationValidatorCategoricalDistributionValidatorSourceConfigSource"
    window: "ValidatorCreationValidatorCategoricalDistributionValidatorSourceConfigWindow"
    segmentation: "ValidatorCreationValidatorCategoricalDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorCreationValidatorCategoricalDistributionValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorCategoricalDistributionValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorCategoricalDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorCategoricalDistributionValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    categorical_distribution_metric: CategoricalDistributionMetric = Field(
        alias="categoricalDistributionMetric"
    )
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ValidatorCreationValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold",
        "ValidatorCreationValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ValidatorCreationValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorCreationValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorCreationValidatorCategoricalDistributionValidatorReferenceSourceConfig(
    BaseModel
):
    source: "ValidatorCreationValidatorCategoricalDistributionValidatorReferenceSourceConfigSource"
    window: "ValidatorCreationValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class ValidatorCreationValidatorCategoricalDistributionValidatorReferenceSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorNumericDistributionValidator(BaseModel):
    typename__: Literal["NumericDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorCreationValidatorNumericDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorCreationValidatorNumericDistributionValidatorConfig"
    reference_source_config: "ValidatorCreationValidatorNumericDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class ValidatorCreationValidatorNumericDistributionValidatorSourceConfig(BaseModel):
    source: "ValidatorCreationValidatorNumericDistributionValidatorSourceConfigSource"
    window: "ValidatorCreationValidatorNumericDistributionValidatorSourceConfigWindow"
    segmentation: "ValidatorCreationValidatorNumericDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorCreationValidatorNumericDistributionValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorNumericDistributionValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorNumericDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorNumericDistributionValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    distribution_metric: NumericDistributionMetric = Field(alias="distributionMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ValidatorCreationValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold",
        "ValidatorCreationValidatorNumericDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ValidatorCreationValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorCreationValidatorNumericDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorCreationValidatorNumericDistributionValidatorReferenceSourceConfig(
    BaseModel
):
    source: "ValidatorCreationValidatorNumericDistributionValidatorReferenceSourceConfigSource"
    window: "ValidatorCreationValidatorNumericDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class ValidatorCreationValidatorNumericDistributionValidatorReferenceSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorNumericDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorVolumeValidator(BaseModel):
    typename__: Literal["VolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorCreationValidatorVolumeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorCreationValidatorVolumeValidatorConfig"
    destination: Optional["ValidatorCreationValidatorVolumeValidatorDestination"]


class ValidatorCreationValidatorVolumeValidatorSourceConfig(BaseModel):
    source: "ValidatorCreationValidatorVolumeValidatorSourceConfigSource"
    window: "ValidatorCreationValidatorVolumeValidatorSourceConfigWindow"
    segmentation: "ValidatorCreationValidatorVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorCreationValidatorVolumeValidatorSourceConfigSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorVolumeValidatorSourceConfigWindow(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorVolumeValidatorSourceConfigSegmentation(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorVolumeValidatorConfig(BaseModel):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    source_fields: List[JsonPointer] = Field(alias="sourceFields")
    volume_metric: VolumeMetric = Field(alias="volumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ValidatorCreationValidatorVolumeValidatorConfigThresholdDynamicThreshold",
        "ValidatorCreationValidatorVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ValidatorCreationValidatorVolumeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorCreationValidatorVolumeValidatorConfigThresholdFixedThreshold(BaseModel):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorCreationValidatorVolumeValidatorDestination(BaseModel):
    name: str
    id: DestinationId
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorNumericAnomalyValidator(BaseModel):
    typename__: Literal["NumericAnomalyValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorCreationValidatorNumericAnomalyValidatorSourceConfig" = (
        Field(alias="sourceConfig")
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorCreationValidatorNumericAnomalyValidatorConfig"
    reference_source_config: "ValidatorCreationValidatorNumericAnomalyValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )
    destination: Optional[
        "ValidatorCreationValidatorNumericAnomalyValidatorDestination"
    ]


class ValidatorCreationValidatorNumericAnomalyValidatorSourceConfig(BaseModel):
    source: "ValidatorCreationValidatorNumericAnomalyValidatorSourceConfigSource"
    window: "ValidatorCreationValidatorNumericAnomalyValidatorSourceConfigWindow"
    segmentation: "ValidatorCreationValidatorNumericAnomalyValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorCreationValidatorNumericAnomalyValidatorSourceConfigSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorNumericAnomalyValidatorSourceConfigWindow(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorNumericAnomalyValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorNumericAnomalyValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    numeric_anomaly_metric: NumericAnomalyMetric = Field(alias="numericAnomalyMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ValidatorCreationValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold",
        "ValidatorCreationValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    sensitivity: float
    minimum_reference_datapoints: Optional[float] = Field(
        alias="minimumReferenceDatapoints"
    )
    minimum_absolute_difference: float = Field(alias="minimumAbsoluteDifference")
    minimum_relative_difference_percent: float = Field(
        alias="minimumRelativeDifferencePercent"
    )


class ValidatorCreationValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorCreationValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorCreationValidatorNumericAnomalyValidatorReferenceSourceConfig(BaseModel):
    source: "ValidatorCreationValidatorNumericAnomalyValidatorReferenceSourceConfigSource"
    window: "ValidatorCreationValidatorNumericAnomalyValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class ValidatorCreationValidatorNumericAnomalyValidatorReferenceSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorNumericAnomalyValidatorReferenceSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorNumericAnomalyValidatorDestination(BaseModel):
    name: str
    id: DestinationId
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorRelativeTimeValidator(BaseModel):
    typename__: Literal["RelativeTimeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorCreationValidatorRelativeTimeValidatorSourceConfig" = (
        Field(alias="sourceConfig")
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorCreationValidatorRelativeTimeValidatorConfig"


class ValidatorCreationValidatorRelativeTimeValidatorSourceConfig(BaseModel):
    source: "ValidatorCreationValidatorRelativeTimeValidatorSourceConfigSource"
    window: "ValidatorCreationValidatorRelativeTimeValidatorSourceConfigWindow"
    segmentation: "ValidatorCreationValidatorRelativeTimeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorCreationValidatorRelativeTimeValidatorSourceConfigSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorRelativeTimeValidatorSourceConfigWindow(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorRelativeTimeValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorRelativeTimeValidatorConfig(BaseModel):
    source_field_minuend: JsonPointer = Field(alias="sourceFieldMinuend")
    source_field_subtrahend: JsonPointer = Field(alias="sourceFieldSubtrahend")
    relative_time_metric: RelativeTimeMetric = Field(alias="relativeTimeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ValidatorCreationValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold",
        "ValidatorCreationValidatorRelativeTimeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ValidatorCreationValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorCreationValidatorRelativeTimeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorCreationValidatorFreshnessValidator(BaseModel):
    typename__: Literal["FreshnessValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorCreationValidatorFreshnessValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorCreationValidatorFreshnessValidatorConfig"


class ValidatorCreationValidatorFreshnessValidatorSourceConfig(BaseModel):
    source: "ValidatorCreationValidatorFreshnessValidatorSourceConfigSource"
    window: "ValidatorCreationValidatorFreshnessValidatorSourceConfigWindow"
    segmentation: "ValidatorCreationValidatorFreshnessValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorCreationValidatorFreshnessValidatorSourceConfigSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorFreshnessValidatorSourceConfigWindow(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorFreshnessValidatorSourceConfigSegmentation(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorFreshnessValidatorConfig(BaseModel):
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ValidatorCreationValidatorFreshnessValidatorConfigThresholdDynamicThreshold",
        "ValidatorCreationValidatorFreshnessValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ValidatorCreationValidatorFreshnessValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorCreationValidatorFreshnessValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorCreationValidatorRelativeVolumeValidator(BaseModel):
    typename__: Literal["RelativeVolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorCreationValidatorRelativeVolumeValidatorSourceConfig" = (
        Field(alias="sourceConfig")
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorCreationValidatorRelativeVolumeValidatorConfig"
    reference_source_config: "ValidatorCreationValidatorRelativeVolumeValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class ValidatorCreationValidatorRelativeVolumeValidatorSourceConfig(BaseModel):
    source: "ValidatorCreationValidatorRelativeVolumeValidatorSourceConfigSource"
    window: "ValidatorCreationValidatorRelativeVolumeValidatorSourceConfigWindow"
    segmentation: "ValidatorCreationValidatorRelativeVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorCreationValidatorRelativeVolumeValidatorSourceConfigSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorRelativeVolumeValidatorSourceConfigWindow(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorRelativeVolumeValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorRelativeVolumeValidatorConfig(BaseModel):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    optional_reference_source_field: Optional[JsonPointer] = Field(
        alias="optionalReferenceSourceField"
    )
    relative_volume_metric: RelativeVolumeMetric = Field(alias="relativeVolumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ValidatorCreationValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold",
        "ValidatorCreationValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ValidatorCreationValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorCreationValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorCreationValidatorRelativeVolumeValidatorReferenceSourceConfig(BaseModel):
    source: "ValidatorCreationValidatorRelativeVolumeValidatorReferenceSourceConfigSource"
    window: "ValidatorCreationValidatorRelativeVolumeValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class ValidatorCreationValidatorRelativeVolumeValidatorReferenceSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorRelativeVolumeValidatorReferenceSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorIncidents(BaseModel):
    typename__: str = Field(alias="__typename")
    id: Any
    severity: NotificationSeverity
    segment: "ValidatorIncidentsSegment"
    metric: Union[
        "ValidatorIncidentsMetricValidatorMetric",
        "ValidatorIncidentsMetricValidatorMetricWithFixedThreshold",
        "ValidatorIncidentsMetricValidatorMetricWithDynamicThreshold",
    ] = Field(discriminator="typename__")


class ValidatorIncidentsSegment(SegmentDetails):
    pass


class ValidatorIncidentsMetricValidatorMetric(BaseModel):
    typename__: Literal["ValidatorMetric"] = Field(alias="__typename")
    start_time: datetime = Field(alias="startTime")
    end_time: datetime = Field(alias="endTime")
    is_incident: bool = Field(alias="isIncident")
    value: float


class ValidatorIncidentsMetricValidatorMetricWithFixedThreshold(BaseModel):
    typename__: Literal["ValidatorMetricWithFixedThreshold"] = Field(alias="__typename")
    start_time: datetime = Field(alias="startTime")
    end_time: datetime = Field(alias="endTime")
    is_incident: bool = Field(alias="isIncident")
    value: float
    operator: ComparisonOperator
    bound: float


class ValidatorIncidentsMetricValidatorMetricWithDynamicThreshold(BaseModel):
    typename__: Literal["ValidatorMetricWithDynamicThreshold"] = Field(
        alias="__typename"
    )
    start_time: datetime = Field(alias="startTime")
    end_time: datetime = Field(alias="endTime")
    is_incident: bool = Field(alias="isIncident")
    value: float
    lower_bound: float = Field(alias="lowerBound")
    upper_bound: float = Field(alias="upperBound")
    decision_bounds_type: DecisionBoundsType = Field(alias="decisionBoundsType")
    is_burn_in: bool = Field(alias="isBurnIn")


class ValidatorRecommendationApplication(BaseModel):
    typename__: str = Field(alias="__typename")
    failed_ids: List[Any] = Field(alias="failedIds")
    success_ids: List[str] = Field(alias="successIds")


class ValidatorRecommendationDismissal(BaseModel):
    typename__: str = Field(alias="__typename")
    errors: List["ValidatorRecommendationDismissalErrors"]
    recommendation_ids: List[str] = Field(alias="recommendationIds")


class ValidatorRecommendationDismissalErrors(ErrorDetails):
    pass


class ValidatorUpdate(BaseModel):
    errors: List["ValidatorUpdateErrors"]
    validator: Optional[
        Annotated[
            Union[
                "ValidatorUpdateValidatorValidator",
                "ValidatorUpdateValidatorNumericValidator",
                "ValidatorUpdateValidatorCategoricalDistributionValidator",
                "ValidatorUpdateValidatorNumericDistributionValidator",
                "ValidatorUpdateValidatorVolumeValidator",
                "ValidatorUpdateValidatorNumericAnomalyValidator",
                "ValidatorUpdateValidatorRelativeTimeValidator",
                "ValidatorUpdateValidatorFreshnessValidator",
                "ValidatorUpdateValidatorRelativeVolumeValidator",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class ValidatorUpdateErrors(ErrorDetails):
    pass


class ValidatorUpdateValidatorValidator(BaseModel):
    typename__: Literal["Validator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorUpdateValidatorValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorValidatorSourceConfig(BaseModel):
    source: "ValidatorUpdateValidatorValidatorSourceConfigSource"
    window: "ValidatorUpdateValidatorValidatorSourceConfigWindow"
    segmentation: "ValidatorUpdateValidatorValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorUpdateValidatorValidatorSourceConfigSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorValidatorSourceConfigWindow(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorValidatorSourceConfigSegmentation(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorNumericValidator(BaseModel):
    typename__: Literal["NumericValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorUpdateValidatorNumericValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorUpdateValidatorNumericValidatorConfig"


class ValidatorUpdateValidatorNumericValidatorSourceConfig(BaseModel):
    source: "ValidatorUpdateValidatorNumericValidatorSourceConfigSource"
    window: "ValidatorUpdateValidatorNumericValidatorSourceConfigWindow"
    segmentation: "ValidatorUpdateValidatorNumericValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorUpdateValidatorNumericValidatorSourceConfigSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorNumericValidatorSourceConfigWindow(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorNumericValidatorSourceConfigSegmentation(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorNumericValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    metric: NumericMetric
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ValidatorUpdateValidatorNumericValidatorConfigThresholdDynamicThreshold",
        "ValidatorUpdateValidatorNumericValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ValidatorUpdateValidatorNumericValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorUpdateValidatorNumericValidatorConfigThresholdFixedThreshold(BaseModel):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorUpdateValidatorCategoricalDistributionValidator(BaseModel):
    typename__: Literal["CategoricalDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorUpdateValidatorCategoricalDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorUpdateValidatorCategoricalDistributionValidatorConfig"
    reference_source_config: "ValidatorUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class ValidatorUpdateValidatorCategoricalDistributionValidatorSourceConfig(BaseModel):
    source: "ValidatorUpdateValidatorCategoricalDistributionValidatorSourceConfigSource"
    window: "ValidatorUpdateValidatorCategoricalDistributionValidatorSourceConfigWindow"
    segmentation: "ValidatorUpdateValidatorCategoricalDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorUpdateValidatorCategoricalDistributionValidatorSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorCategoricalDistributionValidatorSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorCategoricalDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorCategoricalDistributionValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    categorical_distribution_metric: CategoricalDistributionMetric = Field(
        alias="categoricalDistributionMetric"
    )
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ValidatorUpdateValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold",
        "ValidatorUpdateValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ValidatorUpdateValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorUpdateValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfig(
    BaseModel
):
    source: "ValidatorUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfigSource"
    window: "ValidatorUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class ValidatorUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorNumericDistributionValidator(BaseModel):
    typename__: Literal["NumericDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorUpdateValidatorNumericDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorUpdateValidatorNumericDistributionValidatorConfig"
    reference_source_config: "ValidatorUpdateValidatorNumericDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class ValidatorUpdateValidatorNumericDistributionValidatorSourceConfig(BaseModel):
    source: "ValidatorUpdateValidatorNumericDistributionValidatorSourceConfigSource"
    window: "ValidatorUpdateValidatorNumericDistributionValidatorSourceConfigWindow"
    segmentation: "ValidatorUpdateValidatorNumericDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorUpdateValidatorNumericDistributionValidatorSourceConfigSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorNumericDistributionValidatorSourceConfigWindow(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorNumericDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorNumericDistributionValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    distribution_metric: NumericDistributionMetric = Field(alias="distributionMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ValidatorUpdateValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold",
        "ValidatorUpdateValidatorNumericDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ValidatorUpdateValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorUpdateValidatorNumericDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorUpdateValidatorNumericDistributionValidatorReferenceSourceConfig(
    BaseModel
):
    source: "ValidatorUpdateValidatorNumericDistributionValidatorReferenceSourceConfigSource"
    window: "ValidatorUpdateValidatorNumericDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class ValidatorUpdateValidatorNumericDistributionValidatorReferenceSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorNumericDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorVolumeValidator(BaseModel):
    typename__: Literal["VolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorUpdateValidatorVolumeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorUpdateValidatorVolumeValidatorConfig"
    destination: Optional["ValidatorUpdateValidatorVolumeValidatorDestination"]


class ValidatorUpdateValidatorVolumeValidatorSourceConfig(BaseModel):
    source: "ValidatorUpdateValidatorVolumeValidatorSourceConfigSource"
    window: "ValidatorUpdateValidatorVolumeValidatorSourceConfigWindow"
    segmentation: "ValidatorUpdateValidatorVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorUpdateValidatorVolumeValidatorSourceConfigSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorVolumeValidatorSourceConfigWindow(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorVolumeValidatorSourceConfigSegmentation(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorVolumeValidatorConfig(BaseModel):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    source_fields: List[JsonPointer] = Field(alias="sourceFields")
    volume_metric: VolumeMetric = Field(alias="volumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ValidatorUpdateValidatorVolumeValidatorConfigThresholdDynamicThreshold",
        "ValidatorUpdateValidatorVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ValidatorUpdateValidatorVolumeValidatorConfigThresholdDynamicThreshold(BaseModel):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorUpdateValidatorVolumeValidatorConfigThresholdFixedThreshold(BaseModel):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorUpdateValidatorVolumeValidatorDestination(BaseModel):
    name: str
    id: DestinationId
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorNumericAnomalyValidator(BaseModel):
    typename__: Literal["NumericAnomalyValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorUpdateValidatorNumericAnomalyValidatorSourceConfig" = (
        Field(alias="sourceConfig")
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorUpdateValidatorNumericAnomalyValidatorConfig"
    reference_source_config: "ValidatorUpdateValidatorNumericAnomalyValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )
    destination: Optional["ValidatorUpdateValidatorNumericAnomalyValidatorDestination"]


class ValidatorUpdateValidatorNumericAnomalyValidatorSourceConfig(BaseModel):
    source: "ValidatorUpdateValidatorNumericAnomalyValidatorSourceConfigSource"
    window: "ValidatorUpdateValidatorNumericAnomalyValidatorSourceConfigWindow"
    segmentation: "ValidatorUpdateValidatorNumericAnomalyValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorUpdateValidatorNumericAnomalyValidatorSourceConfigSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorNumericAnomalyValidatorSourceConfigWindow(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorNumericAnomalyValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorNumericAnomalyValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    numeric_anomaly_metric: NumericAnomalyMetric = Field(alias="numericAnomalyMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ValidatorUpdateValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold",
        "ValidatorUpdateValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    sensitivity: float
    minimum_reference_datapoints: Optional[float] = Field(
        alias="minimumReferenceDatapoints"
    )
    minimum_absolute_difference: float = Field(alias="minimumAbsoluteDifference")
    minimum_relative_difference_percent: float = Field(
        alias="minimumRelativeDifferencePercent"
    )


class ValidatorUpdateValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorUpdateValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorUpdateValidatorNumericAnomalyValidatorReferenceSourceConfig(BaseModel):
    source: "ValidatorUpdateValidatorNumericAnomalyValidatorReferenceSourceConfigSource"
    window: "ValidatorUpdateValidatorNumericAnomalyValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class ValidatorUpdateValidatorNumericAnomalyValidatorReferenceSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorNumericAnomalyValidatorReferenceSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorNumericAnomalyValidatorDestination(BaseModel):
    name: str
    id: DestinationId
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorRelativeTimeValidator(BaseModel):
    typename__: Literal["RelativeTimeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorUpdateValidatorRelativeTimeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorUpdateValidatorRelativeTimeValidatorConfig"


class ValidatorUpdateValidatorRelativeTimeValidatorSourceConfig(BaseModel):
    source: "ValidatorUpdateValidatorRelativeTimeValidatorSourceConfigSource"
    window: "ValidatorUpdateValidatorRelativeTimeValidatorSourceConfigWindow"
    segmentation: "ValidatorUpdateValidatorRelativeTimeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorUpdateValidatorRelativeTimeValidatorSourceConfigSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorRelativeTimeValidatorSourceConfigWindow(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorRelativeTimeValidatorSourceConfigSegmentation(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorRelativeTimeValidatorConfig(BaseModel):
    source_field_minuend: JsonPointer = Field(alias="sourceFieldMinuend")
    source_field_subtrahend: JsonPointer = Field(alias="sourceFieldSubtrahend")
    relative_time_metric: RelativeTimeMetric = Field(alias="relativeTimeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ValidatorUpdateValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold",
        "ValidatorUpdateValidatorRelativeTimeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ValidatorUpdateValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorUpdateValidatorRelativeTimeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorUpdateValidatorFreshnessValidator(BaseModel):
    typename__: Literal["FreshnessValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorUpdateValidatorFreshnessValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorUpdateValidatorFreshnessValidatorConfig"


class ValidatorUpdateValidatorFreshnessValidatorSourceConfig(BaseModel):
    source: "ValidatorUpdateValidatorFreshnessValidatorSourceConfigSource"
    window: "ValidatorUpdateValidatorFreshnessValidatorSourceConfigWindow"
    segmentation: "ValidatorUpdateValidatorFreshnessValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorUpdateValidatorFreshnessValidatorSourceConfigSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorFreshnessValidatorSourceConfigWindow(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorFreshnessValidatorSourceConfigSegmentation(BaseModel):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorFreshnessValidatorConfig(BaseModel):
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ValidatorUpdateValidatorFreshnessValidatorConfigThresholdDynamicThreshold",
        "ValidatorUpdateValidatorFreshnessValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ValidatorUpdateValidatorFreshnessValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorUpdateValidatorFreshnessValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorUpdateValidatorRelativeVolumeValidator(BaseModel):
    typename__: Literal["RelativeVolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorUpdateValidatorRelativeVolumeValidatorSourceConfig" = (
        Field(alias="sourceConfig")
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorUpdateValidatorRelativeVolumeValidatorConfig"
    reference_source_config: "ValidatorUpdateValidatorRelativeVolumeValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class ValidatorUpdateValidatorRelativeVolumeValidatorSourceConfig(BaseModel):
    source: "ValidatorUpdateValidatorRelativeVolumeValidatorSourceConfigSource"
    window: "ValidatorUpdateValidatorRelativeVolumeValidatorSourceConfigWindow"
    segmentation: "ValidatorUpdateValidatorRelativeVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorUpdateValidatorRelativeVolumeValidatorSourceConfigSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorRelativeVolumeValidatorSourceConfigWindow(BaseModel):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorRelativeVolumeValidatorSourceConfigSegmentation(
    BaseModel
):
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorRelativeVolumeValidatorConfig(BaseModel):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    optional_reference_source_field: Optional[JsonPointer] = Field(
        alias="optionalReferenceSourceField"
    )
    relative_volume_metric: RelativeVolumeMetric = Field(alias="relativeVolumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ValidatorUpdateValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold",
        "ValidatorUpdateValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ValidatorUpdateValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorUpdateValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorUpdateValidatorRelativeVolumeValidatorReferenceSourceConfig(BaseModel):
    source: "ValidatorUpdateValidatorRelativeVolumeValidatorReferenceSourceConfigSource"
    window: "ValidatorUpdateValidatorRelativeVolumeValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class ValidatorUpdateValidatorRelativeVolumeValidatorReferenceSourceConfigSource(
    BaseModel
):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorRelativeVolumeValidatorReferenceSourceConfigWindow(
    BaseModel
):
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class WindowCreation(BaseModel):
    errors: List["WindowCreationErrors"]
    window: Optional[
        Annotated[
            Union[
                "WindowCreationWindowWindow",
                "WindowCreationWindowFixedBatchWindow",
                "WindowCreationWindowSessionizedWindow",
                "WindowCreationWindowTumblingWindow",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class WindowCreationErrors(ErrorDetails):
    pass


class WindowCreationWindowWindow(BaseModel):
    typename__: Literal["FileWindow", "Window"] = Field(alias="__typename")
    id: WindowId
    name: str
    source: "WindowCreationWindowWindowSource"
    data_time_field: JsonPointer = Field(alias="dataTimeField")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class WindowCreationWindowWindowSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class WindowCreationWindowFixedBatchWindow(BaseModel):
    typename__: Literal["FixedBatchWindow"] = Field(alias="__typename")
    id: WindowId
    name: str
    source: "WindowCreationWindowFixedBatchWindowSource"
    data_time_field: JsonPointer = Field(alias="dataTimeField")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "WindowCreationWindowFixedBatchWindowConfig"


class WindowCreationWindowFixedBatchWindowSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class WindowCreationWindowFixedBatchWindowConfig(BaseModel):
    batch_size: int = Field(alias="batchSize")
    segmented_batching: bool = Field(alias="segmentedBatching")
    batch_timeout_secs: Optional[int] = Field(alias="batchTimeoutSecs")


class WindowCreationWindowSessionizedWindow(BaseModel):
    typename__: Literal["SessionizedWindow"] = Field(alias="__typename")
    id: WindowId
    name: str
    source: "WindowCreationWindowSessionizedWindowSource"
    data_time_field: JsonPointer = Field(alias="dataTimeField")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "WindowCreationWindowSessionizedWindowConfig"


class WindowCreationWindowSessionizedWindowSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class WindowCreationWindowSessionizedWindowConfig(BaseModel):
    timeout: int
    timeout_unit: WindowTimeUnit = Field(alias="timeoutUnit")


class WindowCreationWindowTumblingWindow(BaseModel):
    typename__: Literal["TumblingWindow"] = Field(alias="__typename")
    id: WindowId
    name: str
    source: "WindowCreationWindowTumblingWindowSource"
    data_time_field: JsonPointer = Field(alias="dataTimeField")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "WindowCreationWindowTumblingWindowConfig"


class WindowCreationWindowTumblingWindowSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class WindowCreationWindowTumblingWindowConfig(BaseModel):
    window_size: int = Field(alias="windowSize")
    time_unit: WindowTimeUnit = Field(alias="timeUnit")


class WindowUpdate(BaseModel):
    errors: List["WindowUpdateErrors"]
    window: Optional[
        Annotated[
            Union[
                "WindowUpdateWindowWindow",
                "WindowUpdateWindowFixedBatchWindow",
                "WindowUpdateWindowSessionizedWindow",
                "WindowUpdateWindowTumblingWindow",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class WindowUpdateErrors(ErrorDetails):
    pass


class WindowUpdateWindowWindow(BaseModel):
    typename__: Literal["FileWindow", "Window"] = Field(alias="__typename")
    id: WindowId
    name: str
    source: "WindowUpdateWindowWindowSource"
    data_time_field: JsonPointer = Field(alias="dataTimeField")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class WindowUpdateWindowWindowSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class WindowUpdateWindowFixedBatchWindow(BaseModel):
    typename__: Literal["FixedBatchWindow"] = Field(alias="__typename")
    id: WindowId
    name: str
    source: "WindowUpdateWindowFixedBatchWindowSource"
    data_time_field: JsonPointer = Field(alias="dataTimeField")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "WindowUpdateWindowFixedBatchWindowConfig"


class WindowUpdateWindowFixedBatchWindowSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class WindowUpdateWindowFixedBatchWindowConfig(BaseModel):
    batch_size: int = Field(alias="batchSize")
    segmented_batching: bool = Field(alias="segmentedBatching")
    batch_timeout_secs: Optional[int] = Field(alias="batchTimeoutSecs")


class WindowUpdateWindowSessionizedWindow(BaseModel):
    typename__: Literal["SessionizedWindow"] = Field(alias="__typename")
    id: WindowId
    name: str
    source: "WindowUpdateWindowSessionizedWindowSource"
    data_time_field: JsonPointer = Field(alias="dataTimeField")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "WindowUpdateWindowSessionizedWindowConfig"


class WindowUpdateWindowSessionizedWindowSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class WindowUpdateWindowSessionizedWindowConfig(BaseModel):
    timeout: int
    timeout_unit: WindowTimeUnit = Field(alias="timeoutUnit")


class WindowUpdateWindowTumblingWindow(BaseModel):
    typename__: Literal["TumblingWindow"] = Field(alias="__typename")
    id: WindowId
    name: str
    source: "WindowUpdateWindowTumblingWindowSource"
    data_time_field: JsonPointer = Field(alias="dataTimeField")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "WindowUpdateWindowTumblingWindowConfig"


class WindowUpdateWindowTumblingWindowSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class WindowUpdateWindowTumblingWindowConfig(BaseModel):
    window_size: int = Field(alias="windowSize")
    time_unit: WindowTimeUnit = Field(alias="timeUnit")


ErrorDetails.update_forward_refs()
ChannelCreation.update_forward_refs()
ChannelCreationErrors.update_forward_refs()
ChannelCreationChannelChannel.update_forward_refs()
ChannelCreationChannelSlackChannel.update_forward_refs()
ChannelCreationChannelSlackChannelConfig.update_forward_refs()
ChannelCreationChannelWebhookChannel.update_forward_refs()
ChannelCreationChannelWebhookChannelConfig.update_forward_refs()
ChannelDeletion.update_forward_refs()
ChannelDeletionErrors.update_forward_refs()
ChannelDeletionChannel.update_forward_refs()
ChannelUpdate.update_forward_refs()
ChannelUpdateErrors.update_forward_refs()
ChannelUpdateChannelChannel.update_forward_refs()
ChannelUpdateChannelSlackChannel.update_forward_refs()
ChannelUpdateChannelSlackChannelConfig.update_forward_refs()
ChannelUpdateChannelWebhookChannel.update_forward_refs()
ChannelUpdateChannelWebhookChannelConfig.update_forward_refs()
CredentialCreation.update_forward_refs()
CredentialCreationErrors.update_forward_refs()
CredentialCreationCredentialCredential.update_forward_refs()
CredentialCreationCredentialAwsCredential.update_forward_refs()
CredentialCreationCredentialAwsCredentialConfig.update_forward_refs()
CredentialCreationCredentialAwsAthenaCredential.update_forward_refs()
CredentialCreationCredentialAwsAthenaCredentialConfig.update_forward_refs()
CredentialCreationCredentialAwsRedshiftCredential.update_forward_refs()
CredentialCreationCredentialAwsRedshiftCredentialConfig.update_forward_refs()
CredentialCreationCredentialPostgreSqlCredential.update_forward_refs()
CredentialCreationCredentialPostgreSqlCredentialConfig.update_forward_refs()
CredentialCreationCredentialSnowflakeCredential.update_forward_refs()
CredentialCreationCredentialSnowflakeCredentialConfig.update_forward_refs()
CredentialCreationCredentialKafkaSslCredential.update_forward_refs()
CredentialCreationCredentialKafkaSslCredentialConfig.update_forward_refs()
CredentialCreationCredentialKafkaSaslSslPlainCredential.update_forward_refs()
CredentialCreationCredentialKafkaSaslSslPlainCredentialConfig.update_forward_refs()
CredentialSecretChanged.update_forward_refs()
CredentialSecretChangedErrors.update_forward_refs()
CredentialUpdate.update_forward_refs()
CredentialUpdateErrors.update_forward_refs()
CredentialUpdateCredentialCredential.update_forward_refs()
CredentialUpdateCredentialAwsCredential.update_forward_refs()
CredentialUpdateCredentialAwsCredentialConfig.update_forward_refs()
CredentialUpdateCredentialAwsAthenaCredential.update_forward_refs()
CredentialUpdateCredentialAwsAthenaCredentialConfig.update_forward_refs()
CredentialUpdateCredentialAwsRedshiftCredential.update_forward_refs()
CredentialUpdateCredentialAwsRedshiftCredentialConfig.update_forward_refs()
CredentialUpdateCredentialPostgreSqlCredential.update_forward_refs()
CredentialUpdateCredentialPostgreSqlCredentialConfig.update_forward_refs()
CredentialUpdateCredentialSnowflakeCredential.update_forward_refs()
CredentialUpdateCredentialSnowflakeCredentialConfig.update_forward_refs()
CredentialUpdateCredentialKafkaSslCredential.update_forward_refs()
CredentialUpdateCredentialKafkaSslCredentialConfig.update_forward_refs()
CredentialUpdateCredentialKafkaSaslSslPlainCredential.update_forward_refs()
CredentialUpdateCredentialKafkaSaslSslPlainCredentialConfig.update_forward_refs()
DestinationCreation.update_forward_refs()
DestinationCreationErrors.update_forward_refs()
DestinationCreationDestinationDestination.update_forward_refs()
DestinationCreationDestinationDestinationCredential.update_forward_refs()
DestinationCreationDestinationGcpBigQueryDestination.update_forward_refs()
DestinationCreationDestinationGcpBigQueryDestinationCredential.update_forward_refs()
DestinationCreationDestinationGcpBigQueryDestinationConfig.update_forward_refs()
DestinationCreationDestinationSnowflakeDestination.update_forward_refs()
DestinationCreationDestinationSnowflakeDestinationCredential.update_forward_refs()
DestinationCreationDestinationSnowflakeDestinationConfig.update_forward_refs()
DestinationCreationDestinationAwsKinesisDestination.update_forward_refs()
DestinationCreationDestinationAwsKinesisDestinationCredential.update_forward_refs()
DestinationCreationDestinationAwsKinesisDestinationConfig.update_forward_refs()
DestinationUpdate.update_forward_refs()
DestinationUpdateErrors.update_forward_refs()
DestinationUpdateDestinationDestination.update_forward_refs()
DestinationUpdateDestinationDestinationCredential.update_forward_refs()
DestinationUpdateDestinationGcpBigQueryDestination.update_forward_refs()
DestinationUpdateDestinationGcpBigQueryDestinationCredential.update_forward_refs()
DestinationUpdateDestinationGcpBigQueryDestinationConfig.update_forward_refs()
DestinationUpdateDestinationSnowflakeDestination.update_forward_refs()
DestinationUpdateDestinationSnowflakeDestinationCredential.update_forward_refs()
DestinationUpdateDestinationSnowflakeDestinationConfig.update_forward_refs()
DestinationUpdateDestinationAwsKinesisDestination.update_forward_refs()
DestinationUpdateDestinationAwsKinesisDestinationCredential.update_forward_refs()
DestinationUpdateDestinationAwsKinesisDestinationConfig.update_forward_refs()
IdentityDeletion.update_forward_refs()
IdentityDeletionErrors.update_forward_refs()
IdentityProviderCreation.update_forward_refs()
IdentityProviderCreationErrors.update_forward_refs()
IdentityProviderCreationIdentityProviderIdentityProvider.update_forward_refs()
IdentityProviderCreationIdentityProviderSamlIdentityProvider.update_forward_refs()
IdentityProviderCreationIdentityProviderSamlIdentityProviderConfig.update_forward_refs()
IdentityProviderDeletion.update_forward_refs()
IdentityProviderDeletionErrors.update_forward_refs()
IdentityProviderUpdate.update_forward_refs()
IdentityProviderUpdateErrors.update_forward_refs()
IdentityProviderUpdateIdentityProviderIdentityProvider.update_forward_refs()
IdentityProviderUpdateIdentityProviderSamlIdentityProvider.update_forward_refs()
IdentityProviderUpdateIdentityProviderSamlIdentityProviderConfig.update_forward_refs()
NamespaceUpdate.update_forward_refs()
NamespaceUpdateErrors.update_forward_refs()
NotificationRuleDetails.update_forward_refs()
NotificationRuleDetailsChannelChannel.update_forward_refs()
NotificationRuleDetailsChannelSlackChannel.update_forward_refs()
NotificationRuleDetailsChannelSlackChannelConfig.update_forward_refs()
NotificationRuleDetailsChannelWebhookChannel.update_forward_refs()
NotificationRuleDetailsChannelWebhookChannelConfig.update_forward_refs()
NotificationRuleCreation.update_forward_refs()
NotificationRuleCreationErrors.update_forward_refs()
NotificationRuleCreationNotificationRule.update_forward_refs()
NotificationRuleDeletion.update_forward_refs()
NotificationRuleDeletionErrors.update_forward_refs()
NotificationRuleDeletionNotificationRule.update_forward_refs()
NotificationRuleUpdate.update_forward_refs()
NotificationRuleUpdateErrors.update_forward_refs()
NotificationRuleUpdateNotificationRule.update_forward_refs()
ReferenceSourceConfigDetails.update_forward_refs()
ReferenceSourceConfigDetailsSource.update_forward_refs()
ReferenceSourceConfigDetailsWindow.update_forward_refs()
SegmentDetails.update_forward_refs()
SegmentDetailsFields.update_forward_refs()
SegmentationDetails.update_forward_refs()
SegmentationDetailsSource.update_forward_refs()
SegmentationCreation.update_forward_refs()
SegmentationCreationErrors.update_forward_refs()
SegmentationCreationSegmentation.update_forward_refs()
SegmentationSummary.update_forward_refs()
SourceCreation.update_forward_refs()
SourceCreationErrors.update_forward_refs()
SourceCreationSourceSource.update_forward_refs()
SourceCreationSourceSourceCredential.update_forward_refs()
SourceCreationSourceSourceWindows.update_forward_refs()
SourceCreationSourceSourceSegmentations.update_forward_refs()
SourceCreationSourceGcpStorageSource.update_forward_refs()
SourceCreationSourceGcpStorageSourceCredential.update_forward_refs()
SourceCreationSourceGcpStorageSourceWindows.update_forward_refs()
SourceCreationSourceGcpStorageSourceSegmentations.update_forward_refs()
SourceCreationSourceGcpStorageSourceConfig.update_forward_refs()
SourceCreationSourceGcpStorageSourceConfigCsv.update_forward_refs()
SourceCreationSourceGcpBigQuerySource.update_forward_refs()
SourceCreationSourceGcpBigQuerySourceCredential.update_forward_refs()
SourceCreationSourceGcpBigQuerySourceWindows.update_forward_refs()
SourceCreationSourceGcpBigQuerySourceSegmentations.update_forward_refs()
SourceCreationSourceGcpBigQuerySourceConfig.update_forward_refs()
SourceCreationSourceGcpPubSubSource.update_forward_refs()
SourceCreationSourceGcpPubSubSourceCredential.update_forward_refs()
SourceCreationSourceGcpPubSubSourceWindows.update_forward_refs()
SourceCreationSourceGcpPubSubSourceSegmentations.update_forward_refs()
SourceCreationSourceGcpPubSubSourceConfig.update_forward_refs()
SourceCreationSourceGcpPubSubLiteSource.update_forward_refs()
SourceCreationSourceGcpPubSubLiteSourceCredential.update_forward_refs()
SourceCreationSourceGcpPubSubLiteSourceWindows.update_forward_refs()
SourceCreationSourceGcpPubSubLiteSourceSegmentations.update_forward_refs()
SourceCreationSourceGcpPubSubLiteSourceConfig.update_forward_refs()
SourceCreationSourceAwsAthenaSource.update_forward_refs()
SourceCreationSourceAwsAthenaSourceCredential.update_forward_refs()
SourceCreationSourceAwsAthenaSourceWindows.update_forward_refs()
SourceCreationSourceAwsAthenaSourceSegmentations.update_forward_refs()
SourceCreationSourceAwsAthenaSourceConfig.update_forward_refs()
SourceCreationSourceAwsKinesisSource.update_forward_refs()
SourceCreationSourceAwsKinesisSourceCredential.update_forward_refs()
SourceCreationSourceAwsKinesisSourceWindows.update_forward_refs()
SourceCreationSourceAwsKinesisSourceSegmentations.update_forward_refs()
SourceCreationSourceAwsKinesisSourceConfig.update_forward_refs()
SourceCreationSourceAwsRedshiftSource.update_forward_refs()
SourceCreationSourceAwsRedshiftSourceCredential.update_forward_refs()
SourceCreationSourceAwsRedshiftSourceWindows.update_forward_refs()
SourceCreationSourceAwsRedshiftSourceSegmentations.update_forward_refs()
SourceCreationSourceAwsRedshiftSourceConfig.update_forward_refs()
SourceCreationSourceAwsS3Source.update_forward_refs()
SourceCreationSourceAwsS3SourceCredential.update_forward_refs()
SourceCreationSourceAwsS3SourceWindows.update_forward_refs()
SourceCreationSourceAwsS3SourceSegmentations.update_forward_refs()
SourceCreationSourceAwsS3SourceConfig.update_forward_refs()
SourceCreationSourceAwsS3SourceConfigCsv.update_forward_refs()
SourceCreationSourcePostgreSqlSource.update_forward_refs()
SourceCreationSourcePostgreSqlSourceCredential.update_forward_refs()
SourceCreationSourcePostgreSqlSourceWindows.update_forward_refs()
SourceCreationSourcePostgreSqlSourceSegmentations.update_forward_refs()
SourceCreationSourcePostgreSqlSourceConfig.update_forward_refs()
SourceCreationSourceSnowflakeSource.update_forward_refs()
SourceCreationSourceSnowflakeSourceCredential.update_forward_refs()
SourceCreationSourceSnowflakeSourceWindows.update_forward_refs()
SourceCreationSourceSnowflakeSourceSegmentations.update_forward_refs()
SourceCreationSourceSnowflakeSourceConfig.update_forward_refs()
SourceCreationSourceKafkaSource.update_forward_refs()
SourceCreationSourceKafkaSourceCredential.update_forward_refs()
SourceCreationSourceKafkaSourceWindows.update_forward_refs()
SourceCreationSourceKafkaSourceSegmentations.update_forward_refs()
SourceCreationSourceKafkaSourceConfig.update_forward_refs()
SourceUpdate.update_forward_refs()
SourceUpdateErrors.update_forward_refs()
SourceUpdateSourceSource.update_forward_refs()
SourceUpdateSourceSourceCredential.update_forward_refs()
SourceUpdateSourceSourceWindows.update_forward_refs()
SourceUpdateSourceSourceSegmentations.update_forward_refs()
SourceUpdateSourceGcpStorageSource.update_forward_refs()
SourceUpdateSourceGcpStorageSourceCredential.update_forward_refs()
SourceUpdateSourceGcpStorageSourceWindows.update_forward_refs()
SourceUpdateSourceGcpStorageSourceSegmentations.update_forward_refs()
SourceUpdateSourceGcpStorageSourceConfig.update_forward_refs()
SourceUpdateSourceGcpStorageSourceConfigCsv.update_forward_refs()
SourceUpdateSourceGcpBigQuerySource.update_forward_refs()
SourceUpdateSourceGcpBigQuerySourceCredential.update_forward_refs()
SourceUpdateSourceGcpBigQuerySourceWindows.update_forward_refs()
SourceUpdateSourceGcpBigQuerySourceSegmentations.update_forward_refs()
SourceUpdateSourceGcpBigQuerySourceConfig.update_forward_refs()
SourceUpdateSourceGcpPubSubSource.update_forward_refs()
SourceUpdateSourceGcpPubSubSourceCredential.update_forward_refs()
SourceUpdateSourceGcpPubSubSourceWindows.update_forward_refs()
SourceUpdateSourceGcpPubSubSourceSegmentations.update_forward_refs()
SourceUpdateSourceGcpPubSubSourceConfig.update_forward_refs()
SourceUpdateSourceGcpPubSubLiteSource.update_forward_refs()
SourceUpdateSourceGcpPubSubLiteSourceCredential.update_forward_refs()
SourceUpdateSourceGcpPubSubLiteSourceWindows.update_forward_refs()
SourceUpdateSourceGcpPubSubLiteSourceSegmentations.update_forward_refs()
SourceUpdateSourceGcpPubSubLiteSourceConfig.update_forward_refs()
SourceUpdateSourceAwsAthenaSource.update_forward_refs()
SourceUpdateSourceAwsAthenaSourceCredential.update_forward_refs()
SourceUpdateSourceAwsAthenaSourceWindows.update_forward_refs()
SourceUpdateSourceAwsAthenaSourceSegmentations.update_forward_refs()
SourceUpdateSourceAwsAthenaSourceConfig.update_forward_refs()
SourceUpdateSourceAwsKinesisSource.update_forward_refs()
SourceUpdateSourceAwsKinesisSourceCredential.update_forward_refs()
SourceUpdateSourceAwsKinesisSourceWindows.update_forward_refs()
SourceUpdateSourceAwsKinesisSourceSegmentations.update_forward_refs()
SourceUpdateSourceAwsKinesisSourceConfig.update_forward_refs()
SourceUpdateSourceAwsRedshiftSource.update_forward_refs()
SourceUpdateSourceAwsRedshiftSourceCredential.update_forward_refs()
SourceUpdateSourceAwsRedshiftSourceWindows.update_forward_refs()
SourceUpdateSourceAwsRedshiftSourceSegmentations.update_forward_refs()
SourceUpdateSourceAwsRedshiftSourceConfig.update_forward_refs()
SourceUpdateSourceAwsS3Source.update_forward_refs()
SourceUpdateSourceAwsS3SourceCredential.update_forward_refs()
SourceUpdateSourceAwsS3SourceWindows.update_forward_refs()
SourceUpdateSourceAwsS3SourceSegmentations.update_forward_refs()
SourceUpdateSourceAwsS3SourceConfig.update_forward_refs()
SourceUpdateSourceAwsS3SourceConfigCsv.update_forward_refs()
SourceUpdateSourcePostgreSqlSource.update_forward_refs()
SourceUpdateSourcePostgreSqlSourceCredential.update_forward_refs()
SourceUpdateSourcePostgreSqlSourceWindows.update_forward_refs()
SourceUpdateSourcePostgreSqlSourceSegmentations.update_forward_refs()
SourceUpdateSourcePostgreSqlSourceConfig.update_forward_refs()
SourceUpdateSourceSnowflakeSource.update_forward_refs()
SourceUpdateSourceSnowflakeSourceCredential.update_forward_refs()
SourceUpdateSourceSnowflakeSourceWindows.update_forward_refs()
SourceUpdateSourceSnowflakeSourceSegmentations.update_forward_refs()
SourceUpdateSourceSnowflakeSourceConfig.update_forward_refs()
SourceUpdateSourceKafkaSource.update_forward_refs()
SourceUpdateSourceKafkaSourceCredential.update_forward_refs()
SourceUpdateSourceKafkaSourceWindows.update_forward_refs()
SourceUpdateSourceKafkaSourceSegmentations.update_forward_refs()
SourceUpdateSourceKafkaSourceConfig.update_forward_refs()
UserDetails.update_forward_refs()
UserDetailsIdentitiesFederatedIdentity.update_forward_refs()
UserDetailsIdentitiesFederatedIdentityIdp.update_forward_refs()
UserDetailsIdentitiesLocalIdentity.update_forward_refs()
UserCreation.update_forward_refs()
UserCreationErrors.update_forward_refs()
UserCreationUser.update_forward_refs()
UserDeletion.update_forward_refs()
UserDeletionErrors.update_forward_refs()
UserDeletionUser.update_forward_refs()
UserUpdate.update_forward_refs()
UserUpdateErrors.update_forward_refs()
UserUpdateUser.update_forward_refs()
ValidatorCreation.update_forward_refs()
ValidatorCreationErrors.update_forward_refs()
ValidatorCreationValidatorValidator.update_forward_refs()
ValidatorCreationValidatorValidatorSourceConfig.update_forward_refs()
ValidatorCreationValidatorValidatorSourceConfigSource.update_forward_refs()
ValidatorCreationValidatorValidatorSourceConfigWindow.update_forward_refs()
ValidatorCreationValidatorValidatorSourceConfigSegmentation.update_forward_refs()
ValidatorCreationValidatorNumericValidator.update_forward_refs()
ValidatorCreationValidatorNumericValidatorSourceConfig.update_forward_refs()
ValidatorCreationValidatorNumericValidatorSourceConfigSource.update_forward_refs()
ValidatorCreationValidatorNumericValidatorSourceConfigWindow.update_forward_refs()
ValidatorCreationValidatorNumericValidatorSourceConfigSegmentation.update_forward_refs()
ValidatorCreationValidatorNumericValidatorConfig.update_forward_refs()
ValidatorCreationValidatorNumericValidatorConfigThresholdDynamicThreshold.update_forward_refs()
ValidatorCreationValidatorNumericValidatorConfigThresholdFixedThreshold.update_forward_refs()
ValidatorCreationValidatorCategoricalDistributionValidator.update_forward_refs()
ValidatorCreationValidatorCategoricalDistributionValidatorSourceConfig.update_forward_refs()
ValidatorCreationValidatorCategoricalDistributionValidatorSourceConfigSource.update_forward_refs()
ValidatorCreationValidatorCategoricalDistributionValidatorSourceConfigWindow.update_forward_refs()
ValidatorCreationValidatorCategoricalDistributionValidatorSourceConfigSegmentation.update_forward_refs()
ValidatorCreationValidatorCategoricalDistributionValidatorConfig.update_forward_refs()
ValidatorCreationValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold.update_forward_refs()
ValidatorCreationValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold.update_forward_refs()
ValidatorCreationValidatorCategoricalDistributionValidatorReferenceSourceConfig.update_forward_refs()
ValidatorCreationValidatorCategoricalDistributionValidatorReferenceSourceConfigSource.update_forward_refs()
ValidatorCreationValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow.update_forward_refs()
ValidatorCreationValidatorNumericDistributionValidator.update_forward_refs()
ValidatorCreationValidatorNumericDistributionValidatorSourceConfig.update_forward_refs()
ValidatorCreationValidatorNumericDistributionValidatorSourceConfigSource.update_forward_refs()
ValidatorCreationValidatorNumericDistributionValidatorSourceConfigWindow.update_forward_refs()
ValidatorCreationValidatorNumericDistributionValidatorSourceConfigSegmentation.update_forward_refs()
ValidatorCreationValidatorNumericDistributionValidatorConfig.update_forward_refs()
ValidatorCreationValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold.update_forward_refs()
ValidatorCreationValidatorNumericDistributionValidatorConfigThresholdFixedThreshold.update_forward_refs()
ValidatorCreationValidatorNumericDistributionValidatorReferenceSourceConfig.update_forward_refs()
ValidatorCreationValidatorNumericDistributionValidatorReferenceSourceConfigSource.update_forward_refs()
ValidatorCreationValidatorNumericDistributionValidatorReferenceSourceConfigWindow.update_forward_refs()
ValidatorCreationValidatorVolumeValidator.update_forward_refs()
ValidatorCreationValidatorVolumeValidatorSourceConfig.update_forward_refs()
ValidatorCreationValidatorVolumeValidatorSourceConfigSource.update_forward_refs()
ValidatorCreationValidatorVolumeValidatorSourceConfigWindow.update_forward_refs()
ValidatorCreationValidatorVolumeValidatorSourceConfigSegmentation.update_forward_refs()
ValidatorCreationValidatorVolumeValidatorConfig.update_forward_refs()
ValidatorCreationValidatorVolumeValidatorConfigThresholdDynamicThreshold.update_forward_refs()
ValidatorCreationValidatorVolumeValidatorConfigThresholdFixedThreshold.update_forward_refs()
ValidatorCreationValidatorVolumeValidatorDestination.update_forward_refs()
ValidatorCreationValidatorNumericAnomalyValidator.update_forward_refs()
ValidatorCreationValidatorNumericAnomalyValidatorSourceConfig.update_forward_refs()
ValidatorCreationValidatorNumericAnomalyValidatorSourceConfigSource.update_forward_refs()
ValidatorCreationValidatorNumericAnomalyValidatorSourceConfigWindow.update_forward_refs()
ValidatorCreationValidatorNumericAnomalyValidatorSourceConfigSegmentation.update_forward_refs()
ValidatorCreationValidatorNumericAnomalyValidatorConfig.update_forward_refs()
ValidatorCreationValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold.update_forward_refs()
ValidatorCreationValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold.update_forward_refs()
ValidatorCreationValidatorNumericAnomalyValidatorReferenceSourceConfig.update_forward_refs()
ValidatorCreationValidatorNumericAnomalyValidatorReferenceSourceConfigSource.update_forward_refs()
ValidatorCreationValidatorNumericAnomalyValidatorReferenceSourceConfigWindow.update_forward_refs()
ValidatorCreationValidatorNumericAnomalyValidatorDestination.update_forward_refs()
ValidatorCreationValidatorRelativeTimeValidator.update_forward_refs()
ValidatorCreationValidatorRelativeTimeValidatorSourceConfig.update_forward_refs()
ValidatorCreationValidatorRelativeTimeValidatorSourceConfigSource.update_forward_refs()
ValidatorCreationValidatorRelativeTimeValidatorSourceConfigWindow.update_forward_refs()
ValidatorCreationValidatorRelativeTimeValidatorSourceConfigSegmentation.update_forward_refs()
ValidatorCreationValidatorRelativeTimeValidatorConfig.update_forward_refs()
ValidatorCreationValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold.update_forward_refs()
ValidatorCreationValidatorRelativeTimeValidatorConfigThresholdFixedThreshold.update_forward_refs()
ValidatorCreationValidatorFreshnessValidator.update_forward_refs()
ValidatorCreationValidatorFreshnessValidatorSourceConfig.update_forward_refs()
ValidatorCreationValidatorFreshnessValidatorSourceConfigSource.update_forward_refs()
ValidatorCreationValidatorFreshnessValidatorSourceConfigWindow.update_forward_refs()
ValidatorCreationValidatorFreshnessValidatorSourceConfigSegmentation.update_forward_refs()
ValidatorCreationValidatorFreshnessValidatorConfig.update_forward_refs()
ValidatorCreationValidatorFreshnessValidatorConfigThresholdDynamicThreshold.update_forward_refs()
ValidatorCreationValidatorFreshnessValidatorConfigThresholdFixedThreshold.update_forward_refs()
ValidatorCreationValidatorRelativeVolumeValidator.update_forward_refs()
ValidatorCreationValidatorRelativeVolumeValidatorSourceConfig.update_forward_refs()
ValidatorCreationValidatorRelativeVolumeValidatorSourceConfigSource.update_forward_refs()
ValidatorCreationValidatorRelativeVolumeValidatorSourceConfigWindow.update_forward_refs()
ValidatorCreationValidatorRelativeVolumeValidatorSourceConfigSegmentation.update_forward_refs()
ValidatorCreationValidatorRelativeVolumeValidatorConfig.update_forward_refs()
ValidatorCreationValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold.update_forward_refs()
ValidatorCreationValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold.update_forward_refs()
ValidatorCreationValidatorRelativeVolumeValidatorReferenceSourceConfig.update_forward_refs()
ValidatorCreationValidatorRelativeVolumeValidatorReferenceSourceConfigSource.update_forward_refs()
ValidatorCreationValidatorRelativeVolumeValidatorReferenceSourceConfigWindow.update_forward_refs()
ValidatorIncidents.update_forward_refs()
ValidatorIncidentsSegment.update_forward_refs()
ValidatorIncidentsMetricValidatorMetric.update_forward_refs()
ValidatorIncidentsMetricValidatorMetricWithFixedThreshold.update_forward_refs()
ValidatorIncidentsMetricValidatorMetricWithDynamicThreshold.update_forward_refs()
ValidatorRecommendationApplication.update_forward_refs()
ValidatorRecommendationDismissal.update_forward_refs()
ValidatorRecommendationDismissalErrors.update_forward_refs()
ValidatorUpdate.update_forward_refs()
ValidatorUpdateErrors.update_forward_refs()
ValidatorUpdateValidatorValidator.update_forward_refs()
ValidatorUpdateValidatorValidatorSourceConfig.update_forward_refs()
ValidatorUpdateValidatorValidatorSourceConfigSource.update_forward_refs()
ValidatorUpdateValidatorValidatorSourceConfigWindow.update_forward_refs()
ValidatorUpdateValidatorValidatorSourceConfigSegmentation.update_forward_refs()
ValidatorUpdateValidatorNumericValidator.update_forward_refs()
ValidatorUpdateValidatorNumericValidatorSourceConfig.update_forward_refs()
ValidatorUpdateValidatorNumericValidatorSourceConfigSource.update_forward_refs()
ValidatorUpdateValidatorNumericValidatorSourceConfigWindow.update_forward_refs()
ValidatorUpdateValidatorNumericValidatorSourceConfigSegmentation.update_forward_refs()
ValidatorUpdateValidatorNumericValidatorConfig.update_forward_refs()
ValidatorUpdateValidatorNumericValidatorConfigThresholdDynamicThreshold.update_forward_refs()
ValidatorUpdateValidatorNumericValidatorConfigThresholdFixedThreshold.update_forward_refs()
ValidatorUpdateValidatorCategoricalDistributionValidator.update_forward_refs()
ValidatorUpdateValidatorCategoricalDistributionValidatorSourceConfig.update_forward_refs()
ValidatorUpdateValidatorCategoricalDistributionValidatorSourceConfigSource.update_forward_refs()
ValidatorUpdateValidatorCategoricalDistributionValidatorSourceConfigWindow.update_forward_refs()
ValidatorUpdateValidatorCategoricalDistributionValidatorSourceConfigSegmentation.update_forward_refs()
ValidatorUpdateValidatorCategoricalDistributionValidatorConfig.update_forward_refs()
ValidatorUpdateValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold.update_forward_refs()
ValidatorUpdateValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold.update_forward_refs()
ValidatorUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfig.update_forward_refs()
ValidatorUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfigSource.update_forward_refs()
ValidatorUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow.update_forward_refs()
ValidatorUpdateValidatorNumericDistributionValidator.update_forward_refs()
ValidatorUpdateValidatorNumericDistributionValidatorSourceConfig.update_forward_refs()
ValidatorUpdateValidatorNumericDistributionValidatorSourceConfigSource.update_forward_refs()
ValidatorUpdateValidatorNumericDistributionValidatorSourceConfigWindow.update_forward_refs()
ValidatorUpdateValidatorNumericDistributionValidatorSourceConfigSegmentation.update_forward_refs()
ValidatorUpdateValidatorNumericDistributionValidatorConfig.update_forward_refs()
ValidatorUpdateValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold.update_forward_refs()
ValidatorUpdateValidatorNumericDistributionValidatorConfigThresholdFixedThreshold.update_forward_refs()
ValidatorUpdateValidatorNumericDistributionValidatorReferenceSourceConfig.update_forward_refs()
ValidatorUpdateValidatorNumericDistributionValidatorReferenceSourceConfigSource.update_forward_refs()
ValidatorUpdateValidatorNumericDistributionValidatorReferenceSourceConfigWindow.update_forward_refs()
ValidatorUpdateValidatorVolumeValidator.update_forward_refs()
ValidatorUpdateValidatorVolumeValidatorSourceConfig.update_forward_refs()
ValidatorUpdateValidatorVolumeValidatorSourceConfigSource.update_forward_refs()
ValidatorUpdateValidatorVolumeValidatorSourceConfigWindow.update_forward_refs()
ValidatorUpdateValidatorVolumeValidatorSourceConfigSegmentation.update_forward_refs()
ValidatorUpdateValidatorVolumeValidatorConfig.update_forward_refs()
ValidatorUpdateValidatorVolumeValidatorConfigThresholdDynamicThreshold.update_forward_refs()
ValidatorUpdateValidatorVolumeValidatorConfigThresholdFixedThreshold.update_forward_refs()
ValidatorUpdateValidatorVolumeValidatorDestination.update_forward_refs()
ValidatorUpdateValidatorNumericAnomalyValidator.update_forward_refs()
ValidatorUpdateValidatorNumericAnomalyValidatorSourceConfig.update_forward_refs()
ValidatorUpdateValidatorNumericAnomalyValidatorSourceConfigSource.update_forward_refs()
ValidatorUpdateValidatorNumericAnomalyValidatorSourceConfigWindow.update_forward_refs()
ValidatorUpdateValidatorNumericAnomalyValidatorSourceConfigSegmentation.update_forward_refs()
ValidatorUpdateValidatorNumericAnomalyValidatorConfig.update_forward_refs()
ValidatorUpdateValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold.update_forward_refs()
ValidatorUpdateValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold.update_forward_refs()
ValidatorUpdateValidatorNumericAnomalyValidatorReferenceSourceConfig.update_forward_refs()
ValidatorUpdateValidatorNumericAnomalyValidatorReferenceSourceConfigSource.update_forward_refs()
ValidatorUpdateValidatorNumericAnomalyValidatorReferenceSourceConfigWindow.update_forward_refs()
ValidatorUpdateValidatorNumericAnomalyValidatorDestination.update_forward_refs()
ValidatorUpdateValidatorRelativeTimeValidator.update_forward_refs()
ValidatorUpdateValidatorRelativeTimeValidatorSourceConfig.update_forward_refs()
ValidatorUpdateValidatorRelativeTimeValidatorSourceConfigSource.update_forward_refs()
ValidatorUpdateValidatorRelativeTimeValidatorSourceConfigWindow.update_forward_refs()
ValidatorUpdateValidatorRelativeTimeValidatorSourceConfigSegmentation.update_forward_refs()
ValidatorUpdateValidatorRelativeTimeValidatorConfig.update_forward_refs()
ValidatorUpdateValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold.update_forward_refs()
ValidatorUpdateValidatorRelativeTimeValidatorConfigThresholdFixedThreshold.update_forward_refs()
ValidatorUpdateValidatorFreshnessValidator.update_forward_refs()
ValidatorUpdateValidatorFreshnessValidatorSourceConfig.update_forward_refs()
ValidatorUpdateValidatorFreshnessValidatorSourceConfigSource.update_forward_refs()
ValidatorUpdateValidatorFreshnessValidatorSourceConfigWindow.update_forward_refs()
ValidatorUpdateValidatorFreshnessValidatorSourceConfigSegmentation.update_forward_refs()
ValidatorUpdateValidatorFreshnessValidatorConfig.update_forward_refs()
ValidatorUpdateValidatorFreshnessValidatorConfigThresholdDynamicThreshold.update_forward_refs()
ValidatorUpdateValidatorFreshnessValidatorConfigThresholdFixedThreshold.update_forward_refs()
ValidatorUpdateValidatorRelativeVolumeValidator.update_forward_refs()
ValidatorUpdateValidatorRelativeVolumeValidatorSourceConfig.update_forward_refs()
ValidatorUpdateValidatorRelativeVolumeValidatorSourceConfigSource.update_forward_refs()
ValidatorUpdateValidatorRelativeVolumeValidatorSourceConfigWindow.update_forward_refs()
ValidatorUpdateValidatorRelativeVolumeValidatorSourceConfigSegmentation.update_forward_refs()
ValidatorUpdateValidatorRelativeVolumeValidatorConfig.update_forward_refs()
ValidatorUpdateValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold.update_forward_refs()
ValidatorUpdateValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold.update_forward_refs()
ValidatorUpdateValidatorRelativeVolumeValidatorReferenceSourceConfig.update_forward_refs()
ValidatorUpdateValidatorRelativeVolumeValidatorReferenceSourceConfigSource.update_forward_refs()
ValidatorUpdateValidatorRelativeVolumeValidatorReferenceSourceConfigWindow.update_forward_refs()
WindowCreation.update_forward_refs()
WindowCreationErrors.update_forward_refs()
WindowCreationWindowWindow.update_forward_refs()
WindowCreationWindowWindowSource.update_forward_refs()
WindowCreationWindowFixedBatchWindow.update_forward_refs()
WindowCreationWindowFixedBatchWindowSource.update_forward_refs()
WindowCreationWindowFixedBatchWindowConfig.update_forward_refs()
WindowCreationWindowSessionizedWindow.update_forward_refs()
WindowCreationWindowSessionizedWindowSource.update_forward_refs()
WindowCreationWindowSessionizedWindowConfig.update_forward_refs()
WindowCreationWindowTumblingWindow.update_forward_refs()
WindowCreationWindowTumblingWindowSource.update_forward_refs()
WindowCreationWindowTumblingWindowConfig.update_forward_refs()
WindowUpdate.update_forward_refs()
WindowUpdateErrors.update_forward_refs()
WindowUpdateWindowWindow.update_forward_refs()
WindowUpdateWindowWindowSource.update_forward_refs()
WindowUpdateWindowFixedBatchWindow.update_forward_refs()
WindowUpdateWindowFixedBatchWindowSource.update_forward_refs()
WindowUpdateWindowFixedBatchWindowConfig.update_forward_refs()
WindowUpdateWindowSessionizedWindow.update_forward_refs()
WindowUpdateWindowSessionizedWindowSource.update_forward_refs()
WindowUpdateWindowSessionizedWindowConfig.update_forward_refs()
WindowUpdateWindowTumblingWindow.update_forward_refs()
WindowUpdateWindowTumblingWindowSource.update_forward_refs()
WindowUpdateWindowTumblingWindowConfig.update_forward_refs()
