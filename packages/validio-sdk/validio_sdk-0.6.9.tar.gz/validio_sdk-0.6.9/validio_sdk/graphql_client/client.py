from typing import Any, List, Optional, Union

from validio_sdk.scalars import (
    CredentialId,
    DestinationId,
    JsonTypeDefinition,
    SegmentationId,
    SourceId,
    ValidatorId,
    WindowId,
)

from .apply_validator_recommendation import (
    ApplyValidatorRecommendation,
    ApplyValidatorRecommendationValidatorRecommendationApply,
)
from .async_base_client import AsyncBaseClient
from .aws_athena_credential_secret_changed import (
    AwsAthenaCredentialSecretChanged,
    AwsAthenaCredentialSecretChangedAwsAthenaCredentialSecretChanged,
)
from .aws_credential_secret_changed import (
    AwsCredentialSecretChanged,
    AwsCredentialSecretChangedAwsCredentialSecretChanged,
)
from .aws_redshift_credential_secret_changed import (
    AwsRedshiftCredentialSecretChanged,
    AwsRedshiftCredentialSecretChangedAwsRedshiftCredentialSecretChanged,
)
from .backfill_source import BackfillSource, BackfillSourceSourceBackfill
from .base_model import UNSET, UnsetType
from .create_aws_athena_credential import (
    CreateAwsAthenaCredential,
    CreateAwsAthenaCredentialAwsAthenaCredentialCreate,
)
from .create_aws_athena_source import (
    CreateAwsAthenaSource,
    CreateAwsAthenaSourceAwsAthenaSourceCreate,
)
from .create_aws_credential import (
    CreateAwsCredential,
    CreateAwsCredentialAwsCredentialCreate,
)
from .create_aws_kinesis_destination import (
    CreateAwsKinesisDestination,
    CreateAwsKinesisDestinationAwsKinesisDestinationCreate,
)
from .create_aws_kinesis_source import (
    CreateAwsKinesisSource,
    CreateAwsKinesisSourceAwsKinesisSourceCreate,
)
from .create_aws_redshift_credential import (
    CreateAwsRedshiftCredential,
    CreateAwsRedshiftCredentialAwsRedshiftCredentialCreate,
)
from .create_aws_redshift_source import (
    CreateAwsRedshiftSource,
    CreateAwsRedshiftSourceAwsRedshiftSourceCreate,
)
from .create_aws_s3_source import CreateAwsS3Source, CreateAwsS3SourceAwsS3SourceCreate
from .create_categorical_distribution_validator_with_dynamic_threshold import (
    CreateCategoricalDistributionValidatorWithDynamicThreshold,
    CreateCategoricalDistributionValidatorWithDynamicThresholdCategoricalDistributionValidatorWithDynamicThresholdCreate,
)
from .create_categorical_distribution_validator_with_fixed_threshold import (
    CreateCategoricalDistributionValidatorWithFixedThreshold,
    CreateCategoricalDistributionValidatorWithFixedThresholdCategoricalDistributionValidatorWithFixedThresholdCreate,
)
from .create_demo_credential import (
    CreateDemoCredential,
    CreateDemoCredentialDemoCredentialCreate,
)
from .create_demo_source import CreateDemoSource, CreateDemoSourceDemoSourceCreate
from .create_file_window import CreateFileWindow, CreateFileWindowFileWindowCreate
from .create_fixed_batch_window import (
    CreateFixedBatchWindow,
    CreateFixedBatchWindowFixedBatchWindowCreate,
)
from .create_freshness_validator_with_dynamic_threshold import (
    CreateFreshnessValidatorWithDynamicThreshold,
    CreateFreshnessValidatorWithDynamicThresholdFreshnessValidatorWithDynamicThresholdCreate,
)
from .create_freshness_validator_with_fixed_threshold import (
    CreateFreshnessValidatorWithFixedThreshold,
    CreateFreshnessValidatorWithFixedThresholdFreshnessValidatorWithFixedThresholdCreate,
)
from .create_gcp_big_query_destination import (
    CreateGcpBigQueryDestination,
    CreateGcpBigQueryDestinationGcpBigQueryDestinationCreate,
)
from .create_gcp_big_query_source import (
    CreateGcpBigQuerySource,
    CreateGcpBigQuerySourceGcpBigQuerySourceCreate,
)
from .create_gcp_credential import (
    CreateGcpCredential,
    CreateGcpCredentialGcpCredentialCreate,
)
from .create_gcp_pub_sub_lite_source import (
    CreateGcpPubSubLiteSource,
    CreateGcpPubSubLiteSourceGcpPubSubLiteSourceCreate,
)
from .create_gcp_pub_sub_source import (
    CreateGcpPubSubSource,
    CreateGcpPubSubSourceGcpPubSubSourceCreate,
)
from .create_gcp_storage_source import (
    CreateGcpStorageSource,
    CreateGcpStorageSourceGcpStorageSourceCreate,
)
from .create_kafka_sasl_ssl_plain_credential import (
    CreateKafkaSaslSslPlainCredential,
    CreateKafkaSaslSslPlainCredentialKafkaSaslSslPlainCredentialCreate,
)
from .create_kafka_source import CreateKafkaSource, CreateKafkaSourceKafkaSourceCreate
from .create_kafka_ssl_credential import (
    CreateKafkaSslCredential,
    CreateKafkaSslCredentialKafkaSslCredentialCreate,
)
from .create_notification_rule import (
    CreateNotificationRule,
    CreateNotificationRuleNotificationRuleCreate,
)
from .create_numeric_anomaly_validator_with_dynamic_threshold import (
    CreateNumericAnomalyValidatorWithDynamicThreshold,
    CreateNumericAnomalyValidatorWithDynamicThresholdNumericAnomalyValidatorWithDynamicThresholdCreate,
)
from .create_numeric_anomaly_validator_with_fixed_threshold import (
    CreateNumericAnomalyValidatorWithFixedThreshold,
    CreateNumericAnomalyValidatorWithFixedThresholdNumericAnomalyValidatorWithFixedThresholdCreate,
)
from .create_numeric_distribution_validator_with_dynamic_threshold import (
    CreateNumericDistributionValidatorWithDynamicThreshold,
    CreateNumericDistributionValidatorWithDynamicThresholdNumericDistributionValidatorWithDynamicThresholdCreate,
)
from .create_numeric_distribution_validator_with_fixed_threshold import (
    CreateNumericDistributionValidatorWithFixedThreshold,
    CreateNumericDistributionValidatorWithFixedThresholdNumericDistributionValidatorWithFixedThresholdCreate,
)
from .create_numeric_validator_with_dynamic_threshold import (
    CreateNumericValidatorWithDynamicThreshold,
    CreateNumericValidatorWithDynamicThresholdNumericValidatorWithDynamicThresholdCreate,
)
from .create_numeric_validator_with_fixed_threshold import (
    CreateNumericValidatorWithFixedThreshold,
    CreateNumericValidatorWithFixedThresholdNumericValidatorWithFixedThresholdCreate,
)
from .create_postgre_sql_credential import (
    CreatePostgreSqlCredential,
    CreatePostgreSqlCredentialPostgreSqlCredentialCreate,
)
from .create_postgre_sql_source import (
    CreatePostgreSqlSource,
    CreatePostgreSqlSourcePostgreSqlSourceCreate,
)
from .create_relative_time_validator_with_dynamic_threshold import (
    CreateRelativeTimeValidatorWithDynamicThreshold,
    CreateRelativeTimeValidatorWithDynamicThresholdRelativeTimeValidatorWithDynamicThresholdCreate,
)
from .create_relative_time_validator_with_fixed_threshold import (
    CreateRelativeTimeValidatorWithFixedThreshold,
    CreateRelativeTimeValidatorWithFixedThresholdRelativeTimeValidatorWithFixedThresholdCreate,
)
from .create_relative_volume_validator_with_dynamic_threshold import (
    CreateRelativeVolumeValidatorWithDynamicThreshold,
    CreateRelativeVolumeValidatorWithDynamicThresholdRelativeVolumeValidatorWithDynamicThresholdCreate,
)
from .create_relative_volume_validator_with_fixed_threshold import (
    CreateRelativeVolumeValidatorWithFixedThreshold,
    CreateRelativeVolumeValidatorWithFixedThresholdRelativeVolumeValidatorWithFixedThresholdCreate,
)
from .create_saml_identity_provider import (
    CreateSamlIdentityProvider,
    CreateSamlIdentityProviderSamlIdentityProviderCreate,
)
from .create_segmentation import (
    CreateSegmentation,
    CreateSegmentationSegmentationCreate,
)
from .create_sessionized_window import (
    CreateSessionizedWindow,
    CreateSessionizedWindowSessionizedWindowCreate,
)
from .create_slack_channel import (
    CreateSlackChannel,
    CreateSlackChannelSlackChannelCreate,
)
from .create_snowflake_credential import (
    CreateSnowflakeCredential,
    CreateSnowflakeCredentialSnowflakeCredentialCreate,
)
from .create_snowflake_destination import (
    CreateSnowflakeDestination,
    CreateSnowflakeDestinationSnowflakeDestinationCreate,
)
from .create_snowflake_source import (
    CreateSnowflakeSource,
    CreateSnowflakeSourceSnowflakeSourceCreate,
)
from .create_tumbling_window import (
    CreateTumblingWindow,
    CreateTumblingWindowTumblingWindowCreate,
)
from .create_user import CreateUser, CreateUserUserCreate
from .create_volume_validator_with_dynamic_threshold import (
    CreateVolumeValidatorWithDynamicThreshold,
    CreateVolumeValidatorWithDynamicThresholdVolumeValidatorWithDynamicThresholdCreate,
)
from .create_volume_validator_with_fixed_threshold import (
    CreateVolumeValidatorWithFixedThreshold,
    CreateVolumeValidatorWithFixedThresholdVolumeValidatorWithFixedThresholdCreate,
)
from .create_webhook_channel import (
    CreateWebhookChannel,
    CreateWebhookChannelWebhookChannelCreate,
)
from .delete_channel import DeleteChannel, DeleteChannelChannelDelete
from .delete_credential import DeleteCredential, DeleteCredentialCredentialsDelete
from .delete_credentials import DeleteCredentials, DeleteCredentialsCredentialsDelete
from .delete_destination import DeleteDestination, DeleteDestinationDestinationsDelete
from .delete_destinations import (
    DeleteDestinations,
    DeleteDestinationsDestinationsDelete,
)
from .delete_identity import DeleteIdentity, DeleteIdentityIdentityDelete
from .delete_identity_provider import (
    DeleteIdentityProvider,
    DeleteIdentityProviderIdentityProviderDelete,
)
from .delete_notification_rule import (
    DeleteNotificationRule,
    DeleteNotificationRuleNotificationRuleDelete,
)
from .delete_segmentation import (
    DeleteSegmentation,
    DeleteSegmentationSegmentationsDelete,
)
from .delete_source import DeleteSource, DeleteSourceSourcesDelete
from .delete_sources import DeleteSources, DeleteSourcesSourcesDelete
from .delete_user import DeleteUser, DeleteUserUserDelete
from .delete_validators import DeleteValidators, DeleteValidatorsValidatorsDelete
from .delete_window import DeleteWindow, DeleteWindowWindowsDelete
from .delete_windows import DeleteWindows, DeleteWindowsWindowsDelete
from .dismiss_validator_recommendation import (
    DismissValidatorRecommendation,
    DismissValidatorRecommendationValidatorRecommendationDismiss,
)
from .gcp_credential_secret_changed import (
    GcpCredentialSecretChanged,
    GcpCredentialSecretChangedGcpCredentialSecretChanged,
)
from .get_channel_by_resource_name import (
    GetChannelByResourceName,
    GetChannelByResourceNameChannelByResourceNameChannel,
    GetChannelByResourceNameChannelByResourceNameSlackChannel,
    GetChannelByResourceNameChannelByResourceNameWebhookChannel,
)
from .get_channels import (
    GetChannels,
    GetChannelsChannelsChannel,
    GetChannelsChannelsSlackChannel,
    GetChannelsChannelsWebhookChannel,
)
from .get_credential_by_resource_name import (
    GetCredentialByResourceName,
    GetCredentialByResourceNameCredentialByResourceNameAwsAthenaCredential,
    GetCredentialByResourceNameCredentialByResourceNameAwsCredential,
    GetCredentialByResourceNameCredentialByResourceNameAwsRedshiftCredential,
    GetCredentialByResourceNameCredentialByResourceNameCredential,
    GetCredentialByResourceNameCredentialByResourceNameKafkaSaslSslPlainCredential,
    GetCredentialByResourceNameCredentialByResourceNameKafkaSslCredential,
    GetCredentialByResourceNameCredentialByResourceNamePostgreSqlCredential,
    GetCredentialByResourceNameCredentialByResourceNameSnowflakeCredential,
)
from .get_destination_by_resource_name import (
    GetDestinationByResourceName,
    GetDestinationByResourceNameDestinationByResourceNameAwsKinesisDestination,
    GetDestinationByResourceNameDestinationByResourceNameDestination,
    GetDestinationByResourceNameDestinationByResourceNameGcpBigQueryDestination,
    GetDestinationByResourceNameDestinationByResourceNameSnowflakeDestination,
)
from .get_identity_provider_by_resource_name import (
    GetIdentityProviderByResourceName,
    GetIdentityProviderByResourceNameIdentityProviderByResourceNameIdentityProvider,
    GetIdentityProviderByResourceNameIdentityProviderByResourceNameSamlIdentityProvider,
)
from .get_identity_providers import (
    GetIdentityProviders,
    GetIdentityProvidersIdentityProvidersIdentityProvider,
    GetIdentityProvidersIdentityProvidersSamlIdentityProvider,
)
from .get_incidents import (
    GetIncidents,
    GetIncidentsIncidentsNotification,
    GetIncidentsIncidentsSchemaChangeNotification,
    GetIncidentsIncidentsSegmentLimitExceededNotification,
    GetIncidentsIncidentsValidatorThresholdFailureNotification,
)
from .get_notification_rule_by_resource_name import (
    GetNotificationRuleByResourceName,
    GetNotificationRuleByResourceNameNotificationRuleByResourceName,
)
from .get_notification_rules import (
    GetNotificationRules,
    GetNotificationRulesNotificationRules,
)
from .get_recommendation import (
    GetRecommendation,
    GetRecommendationRecommendationRecommendation,
    GetRecommendationRecommendationValidatorCreateRecommendation,
    GetRecommendationRecommendationValidatorDeleteRecommendation,
    GetRecommendationRecommendationValidatorUpdateRecommendation,
)
from .get_segment_incidents import (
    GetSegmentIncidents,
    GetSegmentIncidentsSegmentIncidents,
)
from .get_segmentation import GetSegmentation, GetSegmentationSegmentation
from .get_segmentation_by_resource_name import (
    GetSegmentationByResourceName,
    GetSegmentationByResourceNameSegmentationByResourceName,
)
from .get_source import (
    GetSource,
    GetSourceSourceAwsAthenaSource,
    GetSourceSourceAwsKinesisSource,
    GetSourceSourceAwsRedshiftSource,
    GetSourceSourceAwsS3Source,
    GetSourceSourceGcpBigQuerySource,
    GetSourceSourceGcpPubSubLiteSource,
    GetSourceSourceGcpPubSubSource,
    GetSourceSourceGcpStorageSource,
    GetSourceSourceKafkaSource,
    GetSourceSourcePostgreSqlSource,
    GetSourceSourceSnowflakeSource,
    GetSourceSourceSource,
)
from .get_source_by_resource_name import (
    GetSourceByResourceName,
    GetSourceByResourceNameSourceByResourceNameAwsAthenaSource,
    GetSourceByResourceNameSourceByResourceNameAwsKinesisSource,
    GetSourceByResourceNameSourceByResourceNameAwsRedshiftSource,
    GetSourceByResourceNameSourceByResourceNameAwsS3Source,
    GetSourceByResourceNameSourceByResourceNameGcpBigQuerySource,
    GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSource,
    GetSourceByResourceNameSourceByResourceNameGcpPubSubSource,
    GetSourceByResourceNameSourceByResourceNameGcpStorageSource,
    GetSourceByResourceNameSourceByResourceNameKafkaSource,
    GetSourceByResourceNameSourceByResourceNamePostgreSqlSource,
    GetSourceByResourceNameSourceByResourceNameSnowflakeSource,
    GetSourceByResourceNameSourceByResourceNameSource,
)
from .get_source_incidents import (
    GetSourceIncidents,
    GetSourceIncidentsSourceIncidentsSchemaChangeNotification,
    GetSourceIncidentsSourceIncidentsSegmentLimitExceededNotification,
)
from .get_source_recommended_validators import (
    GetSourceRecommendedValidators,
    GetSourceRecommendedValidatorsSource,
)
from .get_user_by_resource_name import (
    GetUserByResourceName,
    GetUserByResourceNameUserByResourceName,
)
from .get_users import GetUsers, GetUsersUsers
from .get_validator import (
    GetValidator,
    GetValidatorValidatorCategoricalDistributionValidator,
    GetValidatorValidatorFreshnessValidator,
    GetValidatorValidatorNumericAnomalyValidator,
    GetValidatorValidatorNumericDistributionValidator,
    GetValidatorValidatorNumericValidator,
    GetValidatorValidatorRelativeTimeValidator,
    GetValidatorValidatorRelativeVolumeValidator,
    GetValidatorValidatorValidator,
    GetValidatorValidatorVolumeValidator,
)
from .get_validator_by_resource_name import (
    GetValidatorByResourceName,
    GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidator,
    GetValidatorByResourceNameValidatorByResourceNameFreshnessValidator,
    GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidator,
    GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidator,
    GetValidatorByResourceNameValidatorByResourceNameNumericValidator,
    GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidator,
    GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidator,
    GetValidatorByResourceNameValidatorByResourceNameValidator,
    GetValidatorByResourceNameValidatorByResourceNameVolumeValidator,
)
from .get_validator_incidents import (
    GetValidatorIncidents,
    GetValidatorIncidentsValidatorIncidents,
)
from .get_validator_metric_debug_info import (
    GetValidatorMetricDebugInfo,
    GetValidatorMetricDebugInfoValidatorMetricDebugInfoAwsAthenaSourceDebugInfo,
    GetValidatorMetricDebugInfoValidatorMetricDebugInfoAwsRedShiftSourceDebugInfo,
    GetValidatorMetricDebugInfoValidatorMetricDebugInfoAwsS3SourceDebugInfo,
    GetValidatorMetricDebugInfoValidatorMetricDebugInfoGcpBigQuerySourceDebugInfo,
    GetValidatorMetricDebugInfoValidatorMetricDebugInfoGcpStorageSourceDebugInfo,
    GetValidatorMetricDebugInfoValidatorMetricDebugInfoPostgreSQLSourceDebugInfo,
    GetValidatorMetricDebugInfoValidatorMetricDebugInfoSnowflakeSourceDebugInfo,
    GetValidatorMetricDebugInfoValidatorMetricDebugInfoValidatorMetricDebugInfo,
)
from .get_validator_metric_debug_records import GetValidatorMetricDebugRecords
from .get_validator_segment_incidents import (
    GetValidatorSegmentIncidents,
    GetValidatorSegmentIncidentsValidatorSegmentIncidents,
)
from .get_validator_segment_metrics import (
    GetValidatorSegmentMetrics,
    GetValidatorSegmentMetricsValidatorSegmentMetricsValidatorMetricWithDynamicThresholdHistory,
    GetValidatorSegmentMetricsValidatorSegmentMetricsValidatorMetricWithFixedThresholdHistory,
)
from .get_window_by_resource_name import (
    GetWindowByResourceName,
    GetWindowByResourceNameWindowByResourceNameFixedBatchWindow,
    GetWindowByResourceNameWindowByResourceNameSessionizedWindow,
    GetWindowByResourceNameWindowByResourceNameTumblingWindow,
    GetWindowByResourceNameWindowByResourceNameWindow,
)
from .infer_aws_athena_schema import InferAwsAthenaSchema
from .infer_aws_kinesis_schema import InferAwsKinesisSchema
from .infer_aws_redshift_schema import InferAwsRedshiftSchema
from .infer_aws_s3_schema import InferAwsS3Schema
from .infer_demo_schema import InferDemoSchema
from .infer_gcp_big_query_schema import InferGcpBigQuerySchema
from .infer_gcp_pub_sub_lite_schema import InferGcpPubSubLiteSchema
from .infer_gcp_pub_sub_schema import InferGcpPubSubSchema
from .infer_gcp_storage_schema import InferGcpStorageSchema
from .infer_kafka_schema import InferKafkaSchema
from .infer_postgre_sql_schema import InferPostgreSqlSchema
from .infer_snowflake_schema import InferSnowflakeSchema
from .input_types import (
    AwsAthenaCredentialCreateInput,
    AwsAthenaCredentialSecretChangedInput,
    AwsAthenaCredentialUpdateInput,
    AwsAthenaInferSchemaInput,
    AwsAthenaSourceCreateInput,
    AwsAthenaSourceUpdateInput,
    AwsCredentialCreateInput,
    AwsCredentialSecretChangedInput,
    AwsCredentialUpdateInput,
    AwsKinesisDestinationCreateInput,
    AwsKinesisDestinationUpdateInput,
    AwsKinesisInferSchemaInput,
    AwsKinesisSourceCreateInput,
    AwsKinesisSourceUpdateInput,
    AwsRedshiftCredentialCreateInput,
    AwsRedshiftCredentialSecretChangedInput,
    AwsRedshiftCredentialUpdateInput,
    AwsRedshiftInferSchemaInput,
    AwsRedshiftSourceCreateInput,
    AwsRedshiftSourceUpdateInput,
    AwsS3InferSchemaInput,
    AwsS3SourceCreateInput,
    AwsS3SourceUpdateInput,
    CategoricalDistributionValidatorCreateInput,
    CategoricalDistributionValidatorUpdateInput,
    ChannelDeleteInput,
    DemoCredentialCreateInput,
    DemoSourceCreateInput,
    DynamicThresholdCreateInput,
    FileWindowCreateInput,
    FixedBatchWindowCreateInput,
    FixedBatchWindowUpdateInput,
    FixedThresholdCreateInput,
    FreshnessValidatorCreateInput,
    FreshnessValidatorUpdateInput,
    GcpBigQueryDestinationCreateInput,
    GcpBigQueryDestinationUpdateInput,
    GcpBigQueryInferSchemaInput,
    GcpBigQuerySourceCreateInput,
    GcpBigQuerySourceUpdateInput,
    GcpCredentialCreateInput,
    GcpCredentialSecretChangedInput,
    GcpCredentialUpdateInput,
    GcpPubSubInferSchemaInput,
    GcpPubSubLiteInferSchemaInput,
    GcpPubSubLiteSourceCreateInput,
    GcpPubSubLiteSourceUpdateInput,
    GcpPubSubSourceCreateInput,
    GcpPubSubSourceUpdateInput,
    GcpStorageInferSchemaInput,
    GcpStorageSourceCreateInput,
    GcpStorageSourceUpdateInput,
    IdentityDeleteInput,
    IdentityProviderDeleteInput,
    IncidentsInput,
    KafkaInferSchemaInput,
    KafkaSaslSslPlainCredentialCreateInput,
    KafkaSaslSslPlainCredentialSecretChangedInput,
    KafkaSaslSslPlainCredentialUpdateInput,
    KafkaSourceCreateInput,
    KafkaSourceUpdateInput,
    KafkaSslCredentialCreateInput,
    KafkaSslCredentialSecretChangedInput,
    KafkaSslCredentialUpdateInput,
    LocalIdentityProviderUpdateInput,
    NotificationRuleCreateInput,
    NotificationRuleDeleteInput,
    NotificationRuleUpdateInput,
    NumericAnomalyValidatorCreateInput,
    NumericAnomalyValidatorUpdateInput,
    NumericDistributionValidatorCreateInput,
    NumericDistributionValidatorUpdateInput,
    NumericValidatorCreateInput,
    NumericValidatorUpdateInput,
    PostgreSqlCredentialCreateInput,
    PostgreSqlCredentialSecretChangedInput,
    PostgreSqlCredentialUpdateInput,
    PostgreSqlInferSchemaInput,
    PostgreSqlSourceCreateInput,
    PostgreSqlSourceUpdateInput,
    RelativeTimeValidatorCreateInput,
    RelativeTimeValidatorUpdateInput,
    RelativeVolumeValidatorCreateInput,
    RelativeVolumeValidatorUpdateInput,
    ResourceFilter,
    ResourceNamespaceUpdateInput,
    SamlIdentityProviderCreateInput,
    SamlIdentityProviderUpdateInput,
    SegmentationCreateInput,
    SegmentIncidentsInput,
    SessionizedWindowCreateInput,
    SessionizedWindowUpdateInput,
    SlackChannelCreateInput,
    SlackChannelUpdateInput,
    SnowflakeCredentialCreateInput,
    SnowflakeCredentialSecretChangedInput,
    SnowflakeCredentialUpdateInput,
    SnowflakeDestinationCreateInput,
    SnowflakeDestinationUpdateInput,
    SnowflakeInferSchemaInput,
    SnowflakeSourceCreateInput,
    SnowflakeSourceUpdateInput,
    SourceIncidentsInput,
    TumblingWindowCreateInput,
    TumblingWindowUpdateInput,
    UserCreateInput,
    UserDeleteInput,
    UserUpdateInput,
    ValidatorIncidentsInput,
    ValidatorMetricDebugInfoInput,
    ValidatorRecommendationApplyInput,
    ValidatorRecommendationDismissInput,
    ValidatorSegmentIncidentsInput,
    ValidatorSegmentMetricsInput,
    ValidatorWithDynamicThresholdUpdateInput,
    ValidatorWithFixedThresholdUpdateInput,
    VolumeValidatorCreateInput,
    VolumeValidatorUpdateInput,
    WebhookChannelCreateInput,
    WebhookChannelUpdateInput,
)
from .kafka_sasl_ssl_plain_credential_secret_changed import (
    KafkaSaslSslPlainCredentialSecretChanged,
    KafkaSaslSslPlainCredentialSecretChangedKafkaSaslSslPlainCredentialSecretChanged,
)
from .kafka_ssl_credential_secret_changed import (
    KafkaSslCredentialSecretChanged,
    KafkaSslCredentialSecretChangedKafkaSslCredentialSecretChanged,
)
from .list_credentials import (
    ListCredentials,
    ListCredentialsCredentialsListAwsAthenaCredential,
    ListCredentialsCredentialsListAwsCredential,
    ListCredentialsCredentialsListAwsRedshiftCredential,
    ListCredentialsCredentialsListCredential,
    ListCredentialsCredentialsListKafkaSaslSslPlainCredential,
    ListCredentialsCredentialsListKafkaSslCredential,
    ListCredentialsCredentialsListPostgreSqlCredential,
    ListCredentialsCredentialsListSnowflakeCredential,
)
from .list_destinations import (
    ListDestinations,
    ListDestinationsDestinationsListAwsKinesisDestination,
    ListDestinationsDestinationsListDestination,
    ListDestinationsDestinationsListGcpBigQueryDestination,
    ListDestinationsDestinationsListSnowflakeDestination,
)
from .list_segmentations import ListSegmentations, ListSegmentationsSegmentationsList
from .list_sources import (
    ListSources,
    ListSourcesSourcesListAwsAthenaSource,
    ListSourcesSourcesListAwsKinesisSource,
    ListSourcesSourcesListAwsRedshiftSource,
    ListSourcesSourcesListAwsS3Source,
    ListSourcesSourcesListGcpBigQuerySource,
    ListSourcesSourcesListGcpPubSubLiteSource,
    ListSourcesSourcesListGcpPubSubSource,
    ListSourcesSourcesListGcpStorageSource,
    ListSourcesSourcesListKafkaSource,
    ListSourcesSourcesListPostgreSqlSource,
    ListSourcesSourcesListSnowflakeSource,
    ListSourcesSourcesListSource,
)
from .list_validators import (
    ListValidators,
    ListValidatorsValidatorsListCategoricalDistributionValidator,
    ListValidatorsValidatorsListFreshnessValidator,
    ListValidatorsValidatorsListNumericAnomalyValidator,
    ListValidatorsValidatorsListNumericDistributionValidator,
    ListValidatorsValidatorsListNumericValidator,
    ListValidatorsValidatorsListRelativeTimeValidator,
    ListValidatorsValidatorsListRelativeVolumeValidator,
    ListValidatorsValidatorsListValidator,
    ListValidatorsValidatorsListVolumeValidator,
)
from .list_windows import (
    ListWindows,
    ListWindowsWindowsListFixedBatchWindow,
    ListWindowsWindowsListSessionizedWindow,
    ListWindowsWindowsListTumblingWindow,
    ListWindowsWindowsListWindow,
)
from .postgre_sql_credential_secret_changed import (
    PostgreSqlCredentialSecretChanged,
    PostgreSqlCredentialSecretChangedPostgreSqlCredentialSecretChanged,
)
from .reset_source import ResetSource, ResetSourceSourceReset
from .segments import Segments, SegmentsSegments
from .segments_by_resource_name import (
    SegmentsByResourceName,
    SegmentsByResourceNameSegmentsByResourceName,
)
from .snowflake_credential_secret_changed import (
    SnowflakeCredentialSecretChanged,
    SnowflakeCredentialSecretChangedSnowflakeCredentialSecretChanged,
)
from .start_source import StartSource, StartSourceSourceStart
from .stop_source import StopSource, StopSourceSourceStop
from .update_aws_athena_credential import (
    UpdateAwsAthenaCredential,
    UpdateAwsAthenaCredentialAwsAthenaCredentialUpdate,
)
from .update_aws_athena_source import (
    UpdateAwsAthenaSource,
    UpdateAwsAthenaSourceAwsAthenaSourceUpdate,
)
from .update_aws_credential import (
    UpdateAwsCredential,
    UpdateAwsCredentialAwsCredentialUpdate,
)
from .update_aws_kinesis_destination import (
    UpdateAwsKinesisDestination,
    UpdateAwsKinesisDestinationAwsKinesisDestinationUpdate,
)
from .update_aws_kinesis_source import (
    UpdateAwsKinesisSource,
    UpdateAwsKinesisSourceAwsKinesisSourceUpdate,
)
from .update_aws_redshift_credential import (
    UpdateAwsRedshiftCredential,
    UpdateAwsRedshiftCredentialAwsRedshiftCredentialUpdate,
)
from .update_aws_redshift_source import (
    UpdateAwsRedshiftSource,
    UpdateAwsRedshiftSourceAwsRedshiftSourceUpdate,
)
from .update_aws_s3_source import UpdateAwsS3Source, UpdateAwsS3SourceAwsS3SourceUpdate
from .update_categorical_distribution_validator import (
    UpdateCategoricalDistributionValidator,
    UpdateCategoricalDistributionValidatorCategoricalDistributionValidatorUpdate,
)
from .update_channel_namespace import (
    UpdateChannelNamespace,
    UpdateChannelNamespaceChannelNamespaceUpdate,
)
from .update_credential_namespace import (
    UpdateCredentialNamespace,
    UpdateCredentialNamespaceCredentialNamespaceUpdate,
)
from .update_destination_namespace import (
    UpdateDestinationNamespace,
    UpdateDestinationNamespaceDestinationNamespaceUpdate,
)
from .update_fixed_batch_window import (
    UpdateFixedBatchWindow,
    UpdateFixedBatchWindowFixedBatchWindowUpdate,
)
from .update_freshness_validator import (
    UpdateFreshnessValidator,
    UpdateFreshnessValidatorFreshnessValidatorUpdate,
)
from .update_gcp_big_query_destination import (
    UpdateGcpBigQueryDestination,
    UpdateGcpBigQueryDestinationGcpBigQueryDestinationUpdate,
)
from .update_gcp_big_query_source import (
    UpdateGcpBigQuerySource,
    UpdateGcpBigQuerySourceGcpBigQuerySourceUpdate,
)
from .update_gcp_credential import (
    UpdateGcpCredential,
    UpdateGcpCredentialGcpCredentialUpdate,
)
from .update_gcp_pub_sub_lite_source import (
    UpdateGcpPubSubLiteSource,
    UpdateGcpPubSubLiteSourceGcpPubSubLiteSourceUpdate,
)
from .update_gcp_pub_sub_source import (
    UpdateGcpPubSubSource,
    UpdateGcpPubSubSourceGcpPubSubSourceUpdate,
)
from .update_gcp_storage_source import (
    UpdateGcpStorageSource,
    UpdateGcpStorageSourceGcpStorageSourceUpdate,
)
from .update_identity_provider_namespace import (
    UpdateIdentityProviderNamespace,
    UpdateIdentityProviderNamespaceIdentityProviderNamespaceUpdate,
)
from .update_kafka_sasl_ssl_plain_credential import (
    UpdateKafkaSaslSslPlainCredential,
    UpdateKafkaSaslSslPlainCredentialKafkaSaslSslPlainCredentialUpdate,
)
from .update_kafka_source import UpdateKafkaSource, UpdateKafkaSourceKafkaSourceUpdate
from .update_kafka_ssl_credential import (
    UpdateKafkaSslCredential,
    UpdateKafkaSslCredentialKafkaSslCredentialUpdate,
)
from .update_local_identity_provider import (
    UpdateLocalIdentityProvider,
    UpdateLocalIdentityProviderLocalIdentityProviderUpdate,
)
from .update_notification_rule import (
    UpdateNotificationRule,
    UpdateNotificationRuleNotificationRuleUpdate,
)
from .update_notification_rule_namespace import (
    UpdateNotificationRuleNamespace,
    UpdateNotificationRuleNamespaceNotificationRuleNamespaceUpdate,
)
from .update_numeric_anomaly_validator import (
    UpdateNumericAnomalyValidator,
    UpdateNumericAnomalyValidatorNumericAnomalyValidatorUpdate,
)
from .update_numeric_distribution_validator import (
    UpdateNumericDistributionValidator,
    UpdateNumericDistributionValidatorNumericDistributionValidatorUpdate,
)
from .update_numeric_validator import (
    UpdateNumericValidator,
    UpdateNumericValidatorNumericValidatorUpdate,
)
from .update_postgre_sql_credential import (
    UpdatePostgreSqlCredential,
    UpdatePostgreSqlCredentialPostgreSqlCredentialUpdate,
)
from .update_postgre_sql_source import (
    UpdatePostgreSqlSource,
    UpdatePostgreSqlSourcePostgreSqlSourceUpdate,
)
from .update_relative_time_validator import (
    UpdateRelativeTimeValidator,
    UpdateRelativeTimeValidatorRelativeTimeValidatorUpdate,
)
from .update_relative_volume_validator import (
    UpdateRelativeVolumeValidator,
    UpdateRelativeVolumeValidatorRelativeVolumeValidatorUpdate,
)
from .update_saml_identity_provider import (
    UpdateSamlIdentityProvider,
    UpdateSamlIdentityProviderSamlIdentityProviderUpdate,
)
from .update_segmentation_namespace import (
    UpdateSegmentationNamespace,
    UpdateSegmentationNamespaceSegmentationNamespaceUpdate,
)
from .update_sessionized_window import (
    UpdateSessionizedWindow,
    UpdateSessionizedWindowSessionizedWindowUpdate,
)
from .update_slack_channel import (
    UpdateSlackChannel,
    UpdateSlackChannelSlackChannelUpdate,
)
from .update_snowflake_credential import (
    UpdateSnowflakeCredential,
    UpdateSnowflakeCredentialSnowflakeCredentialUpdate,
)
from .update_snowflake_destination import (
    UpdateSnowflakeDestination,
    UpdateSnowflakeDestinationSnowflakeDestinationUpdate,
)
from .update_snowflake_source import (
    UpdateSnowflakeSource,
    UpdateSnowflakeSourceSnowflakeSourceUpdate,
)
from .update_source_namespace import (
    UpdateSourceNamespace,
    UpdateSourceNamespaceSourceNamespaceUpdate,
)
from .update_tumbling_window import (
    UpdateTumblingWindow,
    UpdateTumblingWindowTumblingWindowUpdate,
)
from .update_user import UpdateUser, UpdateUserUserUpdate
from .update_user_namespace import (
    UpdateUserNamespace,
    UpdateUserNamespaceUserNamespaceUpdate,
)
from .update_validator_namespace import (
    UpdateValidatorNamespace,
    UpdateValidatorNamespaceValidatorNamespaceUpdate,
)
from .update_validator_with_dynamic_threshold import (
    UpdateValidatorWithDynamicThreshold,
    UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdate,
)
from .update_validator_with_fixed_threshold import (
    UpdateValidatorWithFixedThreshold,
    UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdate,
)
from .update_volume_validator import (
    UpdateVolumeValidator,
    UpdateVolumeValidatorVolumeValidatorUpdate,
)
from .update_webhook_channel import (
    UpdateWebhookChannel,
    UpdateWebhookChannelWebhookChannelUpdate,
)
from .update_window_namespace import (
    UpdateWindowNamespace,
    UpdateWindowNamespaceWindowNamespaceUpdate,
)


def gql(q: str) -> str:
    return q


class Client(AsyncBaseClient):
    async def apply_validator_recommendation(
        self, input: ValidatorRecommendationApplyInput
    ) -> ApplyValidatorRecommendationValidatorRecommendationApply:
        query = gql(
            """
            mutation ApplyValidatorRecommendation($input: ValidatorRecommendationApplyInput!) {
              validatorRecommendationApply(input: $input) {
                ...ValidatorRecommendationApplication
              }
            }

            fragment ValidatorRecommendationApplication on ValidatorRecommendationApplyResult {
              __typename
              failedIds
              successIds
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ApplyValidatorRecommendation.parse_obj(
            data
        ).validator_recommendation_apply

    async def aws_athena_credential_secret_changed(
        self, input: AwsAthenaCredentialSecretChangedInput
    ) -> AwsAthenaCredentialSecretChangedAwsAthenaCredentialSecretChanged:
        query = gql(
            """
            query AwsAthenaCredentialSecretChanged($input: AwsAthenaCredentialSecretChangedInput!) {
              awsAthenaCredentialSecretChanged(input: $input) {
                ...CredentialSecretChanged
              }
            }

            fragment CredentialSecretChanged on CredentialSecretChangedResult {
              errors {
                ...ErrorDetails
              }
              hasChanged
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return AwsAthenaCredentialSecretChanged.parse_obj(
            data
        ).aws_athena_credential_secret_changed

    async def aws_credential_secret_changed(
        self, input: AwsCredentialSecretChangedInput
    ) -> AwsCredentialSecretChangedAwsCredentialSecretChanged:
        query = gql(
            """
            query AwsCredentialSecretChanged($input: AwsCredentialSecretChangedInput!) {
              awsCredentialSecretChanged(input: $input) {
                ...CredentialSecretChanged
              }
            }

            fragment CredentialSecretChanged on CredentialSecretChangedResult {
              errors {
                ...ErrorDetails
              }
              hasChanged
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return AwsCredentialSecretChanged.parse_obj(data).aws_credential_secret_changed

    async def aws_redshift_credential_secret_changed(
        self, input: AwsRedshiftCredentialSecretChangedInput
    ) -> AwsRedshiftCredentialSecretChangedAwsRedshiftCredentialSecretChanged:
        query = gql(
            """
            query AwsRedshiftCredentialSecretChanged($input: AwsRedshiftCredentialSecretChangedInput!) {
              awsRedshiftCredentialSecretChanged(input: $input) {
                ...CredentialSecretChanged
              }
            }

            fragment CredentialSecretChanged on CredentialSecretChangedResult {
              errors {
                ...ErrorDetails
              }
              hasChanged
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return AwsRedshiftCredentialSecretChanged.parse_obj(
            data
        ).aws_redshift_credential_secret_changed

    async def backfill_source(self, id: SourceId) -> BackfillSourceSourceBackfill:
        query = gql(
            """
            mutation BackfillSource($id: SourceId!) {
              sourceBackfill(id: $id) {
                errors {
                  ...ErrorDetails
                }
                state
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"id": id}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return BackfillSource.parse_obj(data).source_backfill

    async def create_aws_athena_credential(
        self, input: AwsAthenaCredentialCreateInput
    ) -> CreateAwsAthenaCredentialAwsAthenaCredentialCreate:
        query = gql(
            """
            mutation CreateAwsAthenaCredential($input: AwsAthenaCredentialCreateInput!) {
              awsAthenaCredentialCreate(input: $input) {
                ...CredentialCreation
              }
            }

            fragment CredentialCreation on CredentialCreateResult {
              __typename
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateAwsAthenaCredential.parse_obj(data).aws_athena_credential_create

    async def create_aws_athena_source(
        self, input: AwsAthenaSourceCreateInput
    ) -> CreateAwsAthenaSourceAwsAthenaSourceCreate:
        query = gql(
            """
            mutation CreateAwsAthenaSource($input: AwsAthenaSourceCreateInput!) {
              awsAthenaSourceCreate(input: $input) {
                ...SourceCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceCreation on SourceCreateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateAwsAthenaSource.parse_obj(data).aws_athena_source_create

    async def create_aws_credential(
        self, input: AwsCredentialCreateInput
    ) -> CreateAwsCredentialAwsCredentialCreate:
        query = gql(
            """
            mutation CreateAwsCredential($input: AwsCredentialCreateInput!) {
              awsCredentialCreate(input: $input) {
                ...CredentialCreation
              }
            }

            fragment CredentialCreation on CredentialCreateResult {
              __typename
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateAwsCredential.parse_obj(data).aws_credential_create

    async def create_aws_kinesis_destination(
        self, input: AwsKinesisDestinationCreateInput
    ) -> CreateAwsKinesisDestinationAwsKinesisDestinationCreate:
        query = gql(
            """
            mutation CreateAwsKinesisDestination($input: AwsKinesisDestinationCreateInput!) {
              awsKinesisDestinationCreate(input: $input) {
                ...DestinationCreation
              }
            }

            fragment DestinationCreation on DestinationCreateResult {
              errors {
                ...ErrorDetails
              }
              destination {
                ...DestinationDetails
              }
            }

            fragment DestinationDetails on Destination {
              __typename
              id
              name
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on GcpBigQueryDestination {
                config {
                  project
                  dataset
                  table
                }
              }
              ... on SnowflakeDestination {
                config {
                  database
                  schema
                  table
                  role
                  warehouse
                }
              }
              ... on AwsKinesisDestination {
                config {
                  region
                  streamName
                  endpoint
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateAwsKinesisDestination.parse_obj(
            data
        ).aws_kinesis_destination_create

    async def create_aws_kinesis_source(
        self, input: AwsKinesisSourceCreateInput
    ) -> CreateAwsKinesisSourceAwsKinesisSourceCreate:
        query = gql(
            """
            mutation CreateAwsKinesisSource($input: AwsKinesisSourceCreateInput!) {
              awsKinesisSourceCreate(input: $input) {
                ...SourceCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceCreation on SourceCreateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateAwsKinesisSource.parse_obj(data).aws_kinesis_source_create

    async def create_aws_redshift_credential(
        self, input: AwsRedshiftCredentialCreateInput
    ) -> CreateAwsRedshiftCredentialAwsRedshiftCredentialCreate:
        query = gql(
            """
            mutation CreateAwsRedshiftCredential($input: AwsRedshiftCredentialCreateInput!) {
              awsRedshiftCredentialCreate(input: $input) {
                ...CredentialCreation
              }
            }

            fragment CredentialCreation on CredentialCreateResult {
              __typename
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateAwsRedshiftCredential.parse_obj(
            data
        ).aws_redshift_credential_create

    async def create_aws_redshift_source(
        self, input: AwsRedshiftSourceCreateInput
    ) -> CreateAwsRedshiftSourceAwsRedshiftSourceCreate:
        query = gql(
            """
            mutation CreateAwsRedshiftSource($input: AwsRedshiftSourceCreateInput!) {
              awsRedshiftSourceCreate(input: $input) {
                ...SourceCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceCreation on SourceCreateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateAwsRedshiftSource.parse_obj(data).aws_redshift_source_create

    async def create_aws_s3_source(
        self, input: AwsS3SourceCreateInput
    ) -> CreateAwsS3SourceAwsS3SourceCreate:
        query = gql(
            """
            mutation CreateAwsS3Source($input: AwsS3SourceCreateInput!) {
              awsS3SourceCreate(input: $input) {
                ...SourceCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceCreation on SourceCreateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateAwsS3Source.parse_obj(data).aws_s3_source_create

    async def create_categorical_distribution_validator_with_dynamic_threshold(
        self,
        input: CategoricalDistributionValidatorCreateInput,
        threshold: DynamicThresholdCreateInput,
    ) -> CreateCategoricalDistributionValidatorWithDynamicThresholdCategoricalDistributionValidatorWithDynamicThresholdCreate:
        query = gql(
            """
            mutation CreateCategoricalDistributionValidatorWithDynamicThreshold($input: CategoricalDistributionValidatorCreateInput!, $threshold: DynamicThresholdCreateInput!) {
              categoricalDistributionValidatorWithDynamicThresholdCreate(
                input: $input
                threshold: $threshold
              ) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateCategoricalDistributionValidatorWithDynamicThreshold.parse_obj(
            data
        ).categorical_distribution_validator_with_dynamic_threshold_create

    async def create_categorical_distribution_validator_with_fixed_threshold(
        self,
        input: CategoricalDistributionValidatorCreateInput,
        threshold: FixedThresholdCreateInput,
    ) -> CreateCategoricalDistributionValidatorWithFixedThresholdCategoricalDistributionValidatorWithFixedThresholdCreate:
        query = gql(
            """
            mutation CreateCategoricalDistributionValidatorWithFixedThreshold($input: CategoricalDistributionValidatorCreateInput!, $threshold: FixedThresholdCreateInput!) {
              categoricalDistributionValidatorWithFixedThresholdCreate(
                input: $input
                threshold: $threshold
              ) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateCategoricalDistributionValidatorWithFixedThreshold.parse_obj(
            data
        ).categorical_distribution_validator_with_fixed_threshold_create

    async def create_demo_credential(
        self, input: DemoCredentialCreateInput
    ) -> CreateDemoCredentialDemoCredentialCreate:
        query = gql(
            """
            mutation CreateDemoCredential($input: DemoCredentialCreateInput!) {
              demoCredentialCreate(input: $input) {
                ...CredentialCreation
              }
            }

            fragment CredentialCreation on CredentialCreateResult {
              __typename
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateDemoCredential.parse_obj(data).demo_credential_create

    async def create_demo_source(
        self, input: DemoSourceCreateInput
    ) -> CreateDemoSourceDemoSourceCreate:
        query = gql(
            """
            mutation CreateDemoSource($input: DemoSourceCreateInput!) {
              demoSourceCreate(input: $input) {
                ...SourceCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceCreation on SourceCreateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateDemoSource.parse_obj(data).demo_source_create

    async def create_file_window(
        self, input: FileWindowCreateInput
    ) -> CreateFileWindowFileWindowCreate:
        query = gql(
            """
            mutation CreateFileWindow($input: FileWindowCreateInput!) {
              fileWindowCreate(input: $input) {
                ...WindowCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment WindowCreation on WindowCreateResult {
              errors {
                ...ErrorDetails
              }
              window {
                ...WindowDetails
              }
            }

            fragment WindowDetails on Window {
              __typename
              id
              name
              source {
                id
                name
                resourceName
                resourceNamespace
              }
              dataTimeField
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on FixedBatchWindow {
                config {
                  batchSize
                  segmentedBatching
                  batchTimeoutSecs
                }
              }
              ... on SessionizedWindow {
                config {
                  timeout
                  timeoutUnit
                }
              }
              ... on TumblingWindow {
                config {
                  windowSize
                  timeUnit
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateFileWindow.parse_obj(data).file_window_create

    async def create_fixed_batch_window(
        self, input: FixedBatchWindowCreateInput
    ) -> CreateFixedBatchWindowFixedBatchWindowCreate:
        query = gql(
            """
            mutation CreateFixedBatchWindow($input: FixedBatchWindowCreateInput!) {
              fixedBatchWindowCreate(input: $input) {
                ...WindowCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment WindowCreation on WindowCreateResult {
              errors {
                ...ErrorDetails
              }
              window {
                ...WindowDetails
              }
            }

            fragment WindowDetails on Window {
              __typename
              id
              name
              source {
                id
                name
                resourceName
                resourceNamespace
              }
              dataTimeField
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on FixedBatchWindow {
                config {
                  batchSize
                  segmentedBatching
                  batchTimeoutSecs
                }
              }
              ... on SessionizedWindow {
                config {
                  timeout
                  timeoutUnit
                }
              }
              ... on TumblingWindow {
                config {
                  windowSize
                  timeUnit
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateFixedBatchWindow.parse_obj(data).fixed_batch_window_create

    async def create_freshness_validator_with_dynamic_threshold(
        self,
        input: FreshnessValidatorCreateInput,
        threshold: DynamicThresholdCreateInput,
    ) -> CreateFreshnessValidatorWithDynamicThresholdFreshnessValidatorWithDynamicThresholdCreate:
        query = gql(
            """
            mutation CreateFreshnessValidatorWithDynamicThreshold($input: FreshnessValidatorCreateInput!, $threshold: DynamicThresholdCreateInput!) {
              freshnessValidatorWithDynamicThresholdCreate(
                input: $input
                threshold: $threshold
              ) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateFreshnessValidatorWithDynamicThreshold.parse_obj(
            data
        ).freshness_validator_with_dynamic_threshold_create

    async def create_freshness_validator_with_fixed_threshold(
        self, input: FreshnessValidatorCreateInput, threshold: FixedThresholdCreateInput
    ) -> CreateFreshnessValidatorWithFixedThresholdFreshnessValidatorWithFixedThresholdCreate:
        query = gql(
            """
            mutation CreateFreshnessValidatorWithFixedThreshold($input: FreshnessValidatorCreateInput!, $threshold: FixedThresholdCreateInput!) {
              freshnessValidatorWithFixedThresholdCreate(input: $input, threshold: $threshold) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateFreshnessValidatorWithFixedThreshold.parse_obj(
            data
        ).freshness_validator_with_fixed_threshold_create

    async def create_gcp_big_query_destination(
        self, input: GcpBigQueryDestinationCreateInput
    ) -> CreateGcpBigQueryDestinationGcpBigQueryDestinationCreate:
        query = gql(
            """
            mutation CreateGcpBigQueryDestination($input: GcpBigQueryDestinationCreateInput!) {
              gcpBigQueryDestinationCreate(input: $input) {
                ...DestinationCreation
              }
            }

            fragment DestinationCreation on DestinationCreateResult {
              errors {
                ...ErrorDetails
              }
              destination {
                ...DestinationDetails
              }
            }

            fragment DestinationDetails on Destination {
              __typename
              id
              name
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on GcpBigQueryDestination {
                config {
                  project
                  dataset
                  table
                }
              }
              ... on SnowflakeDestination {
                config {
                  database
                  schema
                  table
                  role
                  warehouse
                }
              }
              ... on AwsKinesisDestination {
                config {
                  region
                  streamName
                  endpoint
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateGcpBigQueryDestination.parse_obj(
            data
        ).gcp_big_query_destination_create

    async def create_gcp_big_query_source(
        self, input: GcpBigQuerySourceCreateInput
    ) -> CreateGcpBigQuerySourceGcpBigQuerySourceCreate:
        query = gql(
            """
            mutation CreateGcpBigQuerySource($input: GcpBigQuerySourceCreateInput!) {
              gcpBigQuerySourceCreate(input: $input) {
                ...SourceCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceCreation on SourceCreateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateGcpBigQuerySource.parse_obj(data).gcp_big_query_source_create

    async def create_gcp_credential(
        self, input: GcpCredentialCreateInput
    ) -> CreateGcpCredentialGcpCredentialCreate:
        query = gql(
            """
            mutation CreateGcpCredential($input: GcpCredentialCreateInput!) {
              gcpCredentialCreate(input: $input) {
                ...CredentialCreation
              }
            }

            fragment CredentialCreation on CredentialCreateResult {
              __typename
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateGcpCredential.parse_obj(data).gcp_credential_create

    async def create_gcp_pub_sub_lite_source(
        self, input: GcpPubSubLiteSourceCreateInput
    ) -> CreateGcpPubSubLiteSourceGcpPubSubLiteSourceCreate:
        query = gql(
            """
            mutation CreateGcpPubSubLiteSource($input: GcpPubSubLiteSourceCreateInput!) {
              gcpPubSubLiteSourceCreate(input: $input) {
                ...SourceCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceCreation on SourceCreateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateGcpPubSubLiteSource.parse_obj(data).gcp_pub_sub_lite_source_create

    async def create_gcp_pub_sub_source(
        self, input: GcpPubSubSourceCreateInput
    ) -> CreateGcpPubSubSourceGcpPubSubSourceCreate:
        query = gql(
            """
            mutation CreateGcpPubSubSource($input: GcpPubSubSourceCreateInput!) {
              gcpPubSubSourceCreate(input: $input) {
                ...SourceCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceCreation on SourceCreateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateGcpPubSubSource.parse_obj(data).gcp_pub_sub_source_create

    async def create_gcp_storage_source(
        self, input: GcpStorageSourceCreateInput
    ) -> CreateGcpStorageSourceGcpStorageSourceCreate:
        query = gql(
            """
            mutation CreateGcpStorageSource($input: GcpStorageSourceCreateInput!) {
              gcpStorageSourceCreate(input: $input) {
                ...SourceCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceCreation on SourceCreateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateGcpStorageSource.parse_obj(data).gcp_storage_source_create

    async def create_kafka_sasl_ssl_plain_credential(
        self, input: KafkaSaslSslPlainCredentialCreateInput
    ) -> CreateKafkaSaslSslPlainCredentialKafkaSaslSslPlainCredentialCreate:
        query = gql(
            """
            mutation CreateKafkaSaslSslPlainCredential($input: KafkaSaslSslPlainCredentialCreateInput!) {
              kafkaSaslSslPlainCredentialCreate(input: $input) {
                ...CredentialCreation
              }
            }

            fragment CredentialCreation on CredentialCreateResult {
              __typename
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateKafkaSaslSslPlainCredential.parse_obj(
            data
        ).kafka_sasl_ssl_plain_credential_create

    async def create_kafka_source(
        self, input: KafkaSourceCreateInput
    ) -> CreateKafkaSourceKafkaSourceCreate:
        query = gql(
            """
            mutation CreateKafkaSource($input: KafkaSourceCreateInput!) {
              kafkaSourceCreate(input: $input) {
                ...SourceCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceCreation on SourceCreateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateKafkaSource.parse_obj(data).kafka_source_create

    async def create_kafka_ssl_credential(
        self, input: KafkaSslCredentialCreateInput
    ) -> CreateKafkaSslCredentialKafkaSslCredentialCreate:
        query = gql(
            """
            mutation CreateKafkaSslCredential($input: KafkaSslCredentialCreateInput!) {
              kafkaSslCredentialCreate(input: $input) {
                ...CredentialCreation
              }
            }

            fragment CredentialCreation on CredentialCreateResult {
              __typename
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateKafkaSslCredential.parse_obj(data).kafka_ssl_credential_create

    async def create_notification_rule(
        self, input: NotificationRuleCreateInput
    ) -> CreateNotificationRuleNotificationRuleCreate:
        query = gql(
            """
            mutation CreateNotificationRule($input: NotificationRuleCreateInput!) {
              notificationRuleCreate(input: $input) {
                ...NotificationRuleCreation
              }
            }

            fragment ChannelDetails on Channel {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on SlackChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
              ... on WebhookChannel {
                config {
                  webhookUrl
                  applicationLinkUrl
                  authHeader
                }
              }
            }

            fragment NotificationRuleCreation on NotificationRuleCreateResult {
              errors {
                code
                message
              }
              notificationRule {
                ...NotificationRuleDetails
              }
            }

            fragment NotificationRuleDetails on NotificationRule {
              __typename
              id
              name
              notificationTypenames
              createdAt
              updatedAt
              sources
              channel {
                ...ChannelDetails
              }
              resourceName
              resourceNamespace
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateNotificationRule.parse_obj(data).notification_rule_create

    async def create_numeric_anomaly_validator_with_dynamic_threshold(
        self,
        input: NumericAnomalyValidatorCreateInput,
        threshold: DynamicThresholdCreateInput,
    ) -> CreateNumericAnomalyValidatorWithDynamicThresholdNumericAnomalyValidatorWithDynamicThresholdCreate:
        query = gql(
            """
            mutation CreateNumericAnomalyValidatorWithDynamicThreshold($input: NumericAnomalyValidatorCreateInput!, $threshold: DynamicThresholdCreateInput!) {
              numericAnomalyValidatorWithDynamicThresholdCreate(
                input: $input
                threshold: $threshold
              ) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateNumericAnomalyValidatorWithDynamicThreshold.parse_obj(
            data
        ).numeric_anomaly_validator_with_dynamic_threshold_create

    async def create_numeric_anomaly_validator_with_fixed_threshold(
        self,
        input: NumericAnomalyValidatorCreateInput,
        threshold: FixedThresholdCreateInput,
    ) -> CreateNumericAnomalyValidatorWithFixedThresholdNumericAnomalyValidatorWithFixedThresholdCreate:
        query = gql(
            """
            mutation CreateNumericAnomalyValidatorWithFixedThreshold($input: NumericAnomalyValidatorCreateInput!, $threshold: FixedThresholdCreateInput!) {
              numericAnomalyValidatorWithFixedThresholdCreate(
                input: $input
                threshold: $threshold
              ) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateNumericAnomalyValidatorWithFixedThreshold.parse_obj(
            data
        ).numeric_anomaly_validator_with_fixed_threshold_create

    async def create_numeric_distribution_validator_with_dynamic_threshold(
        self,
        input: NumericDistributionValidatorCreateInput,
        threshold: DynamicThresholdCreateInput,
    ) -> CreateNumericDistributionValidatorWithDynamicThresholdNumericDistributionValidatorWithDynamicThresholdCreate:
        query = gql(
            """
            mutation CreateNumericDistributionValidatorWithDynamicThreshold($input: NumericDistributionValidatorCreateInput!, $threshold: DynamicThresholdCreateInput!) {
              numericDistributionValidatorWithDynamicThresholdCreate(
                input: $input
                threshold: $threshold
              ) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateNumericDistributionValidatorWithDynamicThreshold.parse_obj(
            data
        ).numeric_distribution_validator_with_dynamic_threshold_create

    async def create_numeric_distribution_validator_with_fixed_threshold(
        self,
        input: NumericDistributionValidatorCreateInput,
        threshold: FixedThresholdCreateInput,
    ) -> CreateNumericDistributionValidatorWithFixedThresholdNumericDistributionValidatorWithFixedThresholdCreate:
        query = gql(
            """
            mutation CreateNumericDistributionValidatorWithFixedThreshold($input: NumericDistributionValidatorCreateInput!, $threshold: FixedThresholdCreateInput!) {
              numericDistributionValidatorWithFixedThresholdCreate(
                input: $input
                threshold: $threshold
              ) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateNumericDistributionValidatorWithFixedThreshold.parse_obj(
            data
        ).numeric_distribution_validator_with_fixed_threshold_create

    async def create_numeric_validator_with_dynamic_threshold(
        self, input: NumericValidatorCreateInput, threshold: DynamicThresholdCreateInput
    ) -> CreateNumericValidatorWithDynamicThresholdNumericValidatorWithDynamicThresholdCreate:
        query = gql(
            """
            mutation CreateNumericValidatorWithDynamicThreshold($input: NumericValidatorCreateInput!, $threshold: DynamicThresholdCreateInput!) {
              numericValidatorWithDynamicThresholdCreate(input: $input, threshold: $threshold) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateNumericValidatorWithDynamicThreshold.parse_obj(
            data
        ).numeric_validator_with_dynamic_threshold_create

    async def create_numeric_validator_with_fixed_threshold(
        self, input: NumericValidatorCreateInput, threshold: FixedThresholdCreateInput
    ) -> CreateNumericValidatorWithFixedThresholdNumericValidatorWithFixedThresholdCreate:
        query = gql(
            """
            mutation CreateNumericValidatorWithFixedThreshold($input: NumericValidatorCreateInput!, $threshold: FixedThresholdCreateInput!) {
              numericValidatorWithFixedThresholdCreate(input: $input, threshold: $threshold) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateNumericValidatorWithFixedThreshold.parse_obj(
            data
        ).numeric_validator_with_fixed_threshold_create

    async def create_postgre_sql_credential(
        self, input: PostgreSqlCredentialCreateInput
    ) -> CreatePostgreSqlCredentialPostgreSqlCredentialCreate:
        query = gql(
            """
            mutation CreatePostgreSqlCredential($input: PostgreSqlCredentialCreateInput!) {
              postgreSqlCredentialCreate(input: $input) {
                ...CredentialCreation
              }
            }

            fragment CredentialCreation on CredentialCreateResult {
              __typename
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreatePostgreSqlCredential.parse_obj(data).postgre_sql_credential_create

    async def create_postgre_sql_source(
        self, input: PostgreSqlSourceCreateInput
    ) -> CreatePostgreSqlSourcePostgreSqlSourceCreate:
        query = gql(
            """
            mutation CreatePostgreSqlSource($input: PostgreSqlSourceCreateInput!) {
              postgreSqlSourceCreate(input: $input) {
                ...SourceCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceCreation on SourceCreateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreatePostgreSqlSource.parse_obj(data).postgre_sql_source_create

    async def create_relative_time_validator_with_dynamic_threshold(
        self,
        input: RelativeTimeValidatorCreateInput,
        threshold: DynamicThresholdCreateInput,
    ) -> CreateRelativeTimeValidatorWithDynamicThresholdRelativeTimeValidatorWithDynamicThresholdCreate:
        query = gql(
            """
            mutation CreateRelativeTimeValidatorWithDynamicThreshold($input: RelativeTimeValidatorCreateInput!, $threshold: DynamicThresholdCreateInput!) {
              relativeTimeValidatorWithDynamicThresholdCreate(
                input: $input
                threshold: $threshold
              ) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateRelativeTimeValidatorWithDynamicThreshold.parse_obj(
            data
        ).relative_time_validator_with_dynamic_threshold_create

    async def create_relative_time_validator_with_fixed_threshold(
        self,
        input: RelativeTimeValidatorCreateInput,
        threshold: FixedThresholdCreateInput,
    ) -> CreateRelativeTimeValidatorWithFixedThresholdRelativeTimeValidatorWithFixedThresholdCreate:
        query = gql(
            """
            mutation CreateRelativeTimeValidatorWithFixedThreshold($input: RelativeTimeValidatorCreateInput!, $threshold: FixedThresholdCreateInput!) {
              relativeTimeValidatorWithFixedThresholdCreate(
                input: $input
                threshold: $threshold
              ) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateRelativeTimeValidatorWithFixedThreshold.parse_obj(
            data
        ).relative_time_validator_with_fixed_threshold_create

    async def create_relative_volume_validator_with_dynamic_threshold(
        self,
        input: RelativeVolumeValidatorCreateInput,
        threshold: DynamicThresholdCreateInput,
    ) -> CreateRelativeVolumeValidatorWithDynamicThresholdRelativeVolumeValidatorWithDynamicThresholdCreate:
        query = gql(
            """
            mutation CreateRelativeVolumeValidatorWithDynamicThreshold($input: RelativeVolumeValidatorCreateInput!, $threshold: DynamicThresholdCreateInput!) {
              relativeVolumeValidatorWithDynamicThresholdCreate(
                input: $input
                threshold: $threshold
              ) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateRelativeVolumeValidatorWithDynamicThreshold.parse_obj(
            data
        ).relative_volume_validator_with_dynamic_threshold_create

    async def create_relative_volume_validator_with_fixed_threshold(
        self,
        input: RelativeVolumeValidatorCreateInput,
        threshold: FixedThresholdCreateInput,
    ) -> CreateRelativeVolumeValidatorWithFixedThresholdRelativeVolumeValidatorWithFixedThresholdCreate:
        query = gql(
            """
            mutation CreateRelativeVolumeValidatorWithFixedThreshold($input: RelativeVolumeValidatorCreateInput!, $threshold: FixedThresholdCreateInput!) {
              relativeVolumeValidatorWithFixedThresholdCreate(
                input: $input
                threshold: $threshold
              ) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateRelativeVolumeValidatorWithFixedThreshold.parse_obj(
            data
        ).relative_volume_validator_with_fixed_threshold_create

    async def create_saml_identity_provider(
        self, input: SamlIdentityProviderCreateInput
    ) -> CreateSamlIdentityProviderSamlIdentityProviderCreate:
        query = gql(
            """
            mutation CreateSamlIdentityProvider($input: SamlIdentityProviderCreateInput!) {
              samlIdentityProviderCreate(input: $input) {
                ...IdentityProviderCreation
              }
            }

            fragment IdentityProviderCreation on IdentityProviderCreateResult {
              errors {
                code
                message
              }
              identityProvider {
                ...IdentityProviderDetails
              }
            }

            fragment IdentityProviderDetails on IdentityProvider {
              __typename
              id
              name
              disabled
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on SamlIdentityProvider {
                config {
                  entryPoint
                  entityId
                  cert
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateSamlIdentityProvider.parse_obj(data).saml_identity_provider_create

    async def create_segmentation(
        self, input: SegmentationCreateInput
    ) -> CreateSegmentationSegmentationCreate:
        query = gql(
            """
            mutation CreateSegmentation($input: SegmentationCreateInput!) {
              segmentationCreate(input: $input) {
                ...SegmentationCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SegmentationCreation on SegmentationCreateResult {
              errors {
                ...ErrorDetails
              }
              segmentation {
                ...SegmentationDetails
              }
            }

            fragment SegmentationDetails on Segmentation {
              __typename
              id
              name
              source {
                id
                name
                resourceName
                resourceNamespace
              }
              fields
              createdAt
              updatedAt
              resourceName
              resourceNamespace
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateSegmentation.parse_obj(data).segmentation_create

    async def create_sessionized_window(
        self, input: SessionizedWindowCreateInput
    ) -> CreateSessionizedWindowSessionizedWindowCreate:
        query = gql(
            """
            mutation CreateSessionizedWindow($input: SessionizedWindowCreateInput!) {
              sessionizedWindowCreate(input: $input) {
                ...WindowCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment WindowCreation on WindowCreateResult {
              errors {
                ...ErrorDetails
              }
              window {
                ...WindowDetails
              }
            }

            fragment WindowDetails on Window {
              __typename
              id
              name
              source {
                id
                name
                resourceName
                resourceNamespace
              }
              dataTimeField
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on FixedBatchWindow {
                config {
                  batchSize
                  segmentedBatching
                  batchTimeoutSecs
                }
              }
              ... on SessionizedWindow {
                config {
                  timeout
                  timeoutUnit
                }
              }
              ... on TumblingWindow {
                config {
                  windowSize
                  timeUnit
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateSessionizedWindow.parse_obj(data).sessionized_window_create

    async def create_slack_channel(
        self, input: SlackChannelCreateInput
    ) -> CreateSlackChannelSlackChannelCreate:
        query = gql(
            """
            mutation CreateSlackChannel($input: SlackChannelCreateInput!) {
              slackChannelCreate(input: $input) {
                ...ChannelCreation
              }
            }

            fragment ChannelCreation on ChannelCreateResult {
              errors {
                ...ErrorDetails
              }
              channel {
                ...ChannelDetails
              }
            }

            fragment ChannelDetails on Channel {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on SlackChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
              ... on WebhookChannel {
                config {
                  webhookUrl
                  applicationLinkUrl
                  authHeader
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateSlackChannel.parse_obj(data).slack_channel_create

    async def create_snowflake_credential(
        self, input: SnowflakeCredentialCreateInput
    ) -> CreateSnowflakeCredentialSnowflakeCredentialCreate:
        query = gql(
            """
            mutation CreateSnowflakeCredential($input: SnowflakeCredentialCreateInput!) {
              snowflakeCredentialCreate(input: $input) {
                ...CredentialCreation
              }
            }

            fragment CredentialCreation on CredentialCreateResult {
              __typename
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateSnowflakeCredential.parse_obj(data).snowflake_credential_create

    async def create_snowflake_destination(
        self, input: SnowflakeDestinationCreateInput
    ) -> CreateSnowflakeDestinationSnowflakeDestinationCreate:
        query = gql(
            """
            mutation CreateSnowflakeDestination($input: SnowflakeDestinationCreateInput!) {
              snowflakeDestinationCreate(input: $input) {
                ...DestinationCreation
              }
            }

            fragment DestinationCreation on DestinationCreateResult {
              errors {
                ...ErrorDetails
              }
              destination {
                ...DestinationDetails
              }
            }

            fragment DestinationDetails on Destination {
              __typename
              id
              name
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on GcpBigQueryDestination {
                config {
                  project
                  dataset
                  table
                }
              }
              ... on SnowflakeDestination {
                config {
                  database
                  schema
                  table
                  role
                  warehouse
                }
              }
              ... on AwsKinesisDestination {
                config {
                  region
                  streamName
                  endpoint
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateSnowflakeDestination.parse_obj(data).snowflake_destination_create

    async def create_snowflake_source(
        self, input: SnowflakeSourceCreateInput
    ) -> CreateSnowflakeSourceSnowflakeSourceCreate:
        query = gql(
            """
            mutation CreateSnowflakeSource($input: SnowflakeSourceCreateInput!) {
              snowflakeSourceCreate(input: $input) {
                ...SourceCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceCreation on SourceCreateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateSnowflakeSource.parse_obj(data).snowflake_source_create

    async def create_tumbling_window(
        self, input: TumblingWindowCreateInput
    ) -> CreateTumblingWindowTumblingWindowCreate:
        query = gql(
            """
            mutation CreateTumblingWindow($input: TumblingWindowCreateInput!) {
              tumblingWindowCreate(input: $input) {
                ...WindowCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment WindowCreation on WindowCreateResult {
              errors {
                ...ErrorDetails
              }
              window {
                ...WindowDetails
              }
            }

            fragment WindowDetails on Window {
              __typename
              id
              name
              source {
                id
                name
                resourceName
                resourceNamespace
              }
              dataTimeField
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on FixedBatchWindow {
                config {
                  batchSize
                  segmentedBatching
                  batchTimeoutSecs
                }
              }
              ... on SessionizedWindow {
                config {
                  timeout
                  timeoutUnit
                }
              }
              ... on TumblingWindow {
                config {
                  windowSize
                  timeUnit
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateTumblingWindow.parse_obj(data).tumbling_window_create

    async def create_user(self, input: UserCreateInput) -> CreateUserUserCreate:
        query = gql(
            """
            mutation CreateUser($input: UserCreateInput!) {
              userCreate(input: $input) {
                ...UserCreation
              }
            }

            fragment IdentityDetails on Identity {
              ... on LocalIdentity {
                __typename
                id
                userId
                username
                createdAt
              }
              ... on FederatedIdentity {
                __typename
                id
                userId
                idp {
                  __typename
                  id
                  name
                }
                createdAt
              }
            }

            fragment UserCreation on UserCreateResult {
              errors {
                code
                message
              }
              user {
                ...UserDetails
              }
            }

            fragment UserDetails on User {
              id
              displayName
              fullName
              email
              role
              status
              identities {
                ...IdentityDetails
              }
              createdAt
              updatedAt
              resourceName
              resourceNamespace
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateUser.parse_obj(data).user_create

    async def create_volume_validator_with_dynamic_threshold(
        self, input: VolumeValidatorCreateInput, threshold: DynamicThresholdCreateInput
    ) -> CreateVolumeValidatorWithDynamicThresholdVolumeValidatorWithDynamicThresholdCreate:
        query = gql(
            """
            mutation CreateVolumeValidatorWithDynamicThreshold($input: VolumeValidatorCreateInput!, $threshold: DynamicThresholdCreateInput!) {
              volumeValidatorWithDynamicThresholdCreate(input: $input, threshold: $threshold) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateVolumeValidatorWithDynamicThreshold.parse_obj(
            data
        ).volume_validator_with_dynamic_threshold_create

    async def create_volume_validator_with_fixed_threshold(
        self, input: VolumeValidatorCreateInput, threshold: FixedThresholdCreateInput
    ) -> CreateVolumeValidatorWithFixedThresholdVolumeValidatorWithFixedThresholdCreate:
        query = gql(
            """
            mutation CreateVolumeValidatorWithFixedThreshold($input: VolumeValidatorCreateInput!, $threshold: FixedThresholdCreateInput!) {
              volumeValidatorWithFixedThresholdCreate(input: $input, threshold: $threshold) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateVolumeValidatorWithFixedThreshold.parse_obj(
            data
        ).volume_validator_with_fixed_threshold_create

    async def create_webhook_channel(
        self, input: WebhookChannelCreateInput
    ) -> CreateWebhookChannelWebhookChannelCreate:
        query = gql(
            """
            mutation CreateWebhookChannel($input: WebhookChannelCreateInput!) {
              webhookChannelCreate(input: $input) {
                ...ChannelCreation
              }
            }

            fragment ChannelCreation on ChannelCreateResult {
              errors {
                ...ErrorDetails
              }
              channel {
                ...ChannelDetails
              }
            }

            fragment ChannelDetails on Channel {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on SlackChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
              ... on WebhookChannel {
                config {
                  webhookUrl
                  applicationLinkUrl
                  authHeader
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateWebhookChannel.parse_obj(data).webhook_channel_create

    async def delete_channel(
        self, input: ChannelDeleteInput
    ) -> DeleteChannelChannelDelete:
        query = gql(
            """
            mutation DeleteChannel($input: ChannelDeleteInput!) {
              channelDelete(input: $input) {
                ...ChannelDeletion
              }
            }

            fragment ChannelDeletion on ChannelDeleteResult {
              errors {
                code
                message
              }
              channel {
                id
                name
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteChannel.parse_obj(data).channel_delete

    async def delete_credential(
        self, id: CredentialId
    ) -> DeleteCredentialCredentialsDelete:
        query = gql(
            """
            mutation DeleteCredential($id: CredentialId!) {
              credentialsDelete(ids: [$id]) {
                errors {
                  ...ErrorDetails
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"id": id}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteCredential.parse_obj(data).credentials_delete

    async def delete_credentials(
        self, ids: List[CredentialId]
    ) -> DeleteCredentialsCredentialsDelete:
        query = gql(
            """
            mutation DeleteCredentials($ids: [CredentialId!]!) {
              credentialsDelete(ids: $ids) {
                errors {
                  ...ErrorDetails
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"ids": ids}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteCredentials.parse_obj(data).credentials_delete

    async def delete_destination(
        self, id: DestinationId
    ) -> DeleteDestinationDestinationsDelete:
        query = gql(
            """
            mutation DeleteDestination($id: DestinationId!) {
              destinationsDelete(ids: [$id]) {
                errors {
                  ...ErrorDetails
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"id": id}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteDestination.parse_obj(data).destinations_delete

    async def delete_destinations(
        self, ids: List[DestinationId]
    ) -> DeleteDestinationsDestinationsDelete:
        query = gql(
            """
            mutation DeleteDestinations($ids: [DestinationId!]!) {
              destinationsDelete(ids: $ids) {
                errors {
                  ...ErrorDetails
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"ids": ids}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteDestinations.parse_obj(data).destinations_delete

    async def delete_identity(
        self, input: IdentityDeleteInput
    ) -> DeleteIdentityIdentityDelete:
        query = gql(
            """
            mutation DeleteIdentity($input: IdentityDeleteInput!) {
              identityDelete(input: $input) {
                ...IdentityDeletion
              }
            }

            fragment IdentityDeletion on IdentityDeleteResult {
              errors {
                code
                message
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteIdentity.parse_obj(data).identity_delete

    async def delete_identity_provider(
        self, input: IdentityProviderDeleteInput
    ) -> DeleteIdentityProviderIdentityProviderDelete:
        query = gql(
            """
            mutation DeleteIdentityProvider($input: IdentityProviderDeleteInput!) {
              identityProviderDelete(input: $input) {
                ...IdentityProviderDeletion
              }
            }

            fragment IdentityProviderDeletion on IdentityProviderDeleteResult {
              errors {
                code
                message
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteIdentityProvider.parse_obj(data).identity_provider_delete

    async def delete_notification_rule(
        self, input: NotificationRuleDeleteInput
    ) -> DeleteNotificationRuleNotificationRuleDelete:
        query = gql(
            """
            mutation DeleteNotificationRule($input: NotificationRuleDeleteInput!) {
              notificationRuleDelete(input: $input) {
                ...NotificationRuleDeletion
              }
            }

            fragment NotificationRuleDeletion on NotificationRuleDeleteResult {
              errors {
                code
                message
              }
              notificationRule {
                __typename
                id
                name
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteNotificationRule.parse_obj(data).notification_rule_delete

    async def delete_segmentation(
        self, id: SegmentationId
    ) -> DeleteSegmentationSegmentationsDelete:
        query = gql(
            """
            mutation DeleteSegmentation($id: SegmentationId!) {
              segmentationsDelete(ids: [$id]) {
                errors {
                  ...ErrorDetails
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"id": id}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteSegmentation.parse_obj(data).segmentations_delete

    async def delete_source(self, id: SourceId) -> DeleteSourceSourcesDelete:
        query = gql(
            """
            mutation DeleteSource($id: SourceId!) {
              sourcesDelete(ids: [$id]) {
                errors {
                  ...ErrorDetails
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"id": id}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteSource.parse_obj(data).sources_delete

    async def delete_sources(self, ids: List[SourceId]) -> DeleteSourcesSourcesDelete:
        query = gql(
            """
            mutation DeleteSources($ids: [SourceId!]!) {
              sourcesDelete(ids: $ids) {
                errors {
                  ...ErrorDetails
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"ids": ids}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteSources.parse_obj(data).sources_delete

    async def delete_user(self, input: UserDeleteInput) -> DeleteUserUserDelete:
        query = gql(
            """
            mutation DeleteUser($input: UserDeleteInput!) {
              userDelete(input: $input) {
                ...UserDeletion
              }
            }

            fragment IdentityDetails on Identity {
              ... on LocalIdentity {
                __typename
                id
                userId
                username
                createdAt
              }
              ... on FederatedIdentity {
                __typename
                id
                userId
                idp {
                  __typename
                  id
                  name
                }
                createdAt
              }
            }

            fragment UserDeletion on UserDeleteResult {
              errors {
                code
                message
              }
              user {
                ...UserDetails
              }
            }

            fragment UserDetails on User {
              id
              displayName
              fullName
              email
              role
              status
              identities {
                ...IdentityDetails
              }
              createdAt
              updatedAt
              resourceName
              resourceNamespace
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteUser.parse_obj(data).user_delete

    async def delete_validators(
        self, ids: List[ValidatorId]
    ) -> DeleteValidatorsValidatorsDelete:
        query = gql(
            """
            mutation DeleteValidators($ids: [ValidatorId!]!) {
              validatorsDelete(ids: $ids) {
                errors {
                  ...ErrorDetails
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"ids": ids}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteValidators.parse_obj(data).validators_delete

    async def delete_window(self, id: WindowId) -> DeleteWindowWindowsDelete:
        query = gql(
            """
            mutation DeleteWindow($id: WindowId!) {
              windowsDelete(ids: [$id]) {
                errors {
                  ...ErrorDetails
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"id": id}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteWindow.parse_obj(data).windows_delete

    async def delete_windows(self, ids: List[WindowId]) -> DeleteWindowsWindowsDelete:
        query = gql(
            """
            mutation DeleteWindows($ids: [WindowId!]!) {
              windowsDelete(ids: $ids) {
                errors {
                  ...ErrorDetails
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"ids": ids}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteWindows.parse_obj(data).windows_delete

    async def dismiss_validator_recommendation(
        self, input: ValidatorRecommendationDismissInput
    ) -> DismissValidatorRecommendationValidatorRecommendationDismiss:
        query = gql(
            """
            mutation DismissValidatorRecommendation($input: ValidatorRecommendationDismissInput!) {
              validatorRecommendationDismiss(input: $input) {
                ...ValidatorRecommendationDismissal
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorRecommendationDismissal on ValidatorRecommendationDismissResult {
              __typename
              errors {
                ...ErrorDetails
              }
              recommendationIds
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DismissValidatorRecommendation.parse_obj(
            data
        ).validator_recommendation_dismiss

    async def gcp_credential_secret_changed(
        self, input: GcpCredentialSecretChangedInput
    ) -> GcpCredentialSecretChangedGcpCredentialSecretChanged:
        query = gql(
            """
            query GcpCredentialSecretChanged($input: GcpCredentialSecretChangedInput!) {
              gcpCredentialSecretChanged(input: $input) {
                ...CredentialSecretChanged
              }
            }

            fragment CredentialSecretChanged on CredentialSecretChangedResult {
              errors {
                ...ErrorDetails
              }
              hasChanged
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GcpCredentialSecretChanged.parse_obj(data).gcp_credential_secret_changed

    async def get_channel_by_resource_name(
        self, resource_name: str, resource_namespace: str
    ) -> Optional[
        Union[
            GetChannelByResourceNameChannelByResourceNameChannel,
            GetChannelByResourceNameChannelByResourceNameSlackChannel,
            GetChannelByResourceNameChannelByResourceNameWebhookChannel,
        ]
    ]:
        query = gql(
            """
            query GetChannelByResourceName($resourceName: String!, $resourceNamespace: String! = "default") {
              channelByResourceName(
                resourceName: $resourceName
                resourceNamespace: $resourceNamespace
              ) {
                ...ChannelDetails
              }
            }

            fragment ChannelDetails on Channel {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on SlackChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
              ... on WebhookChannel {
                config {
                  webhookUrl
                  applicationLinkUrl
                  authHeader
                }
              }
            }
            """
        )
        variables: dict[str, object] = {
            "resourceName": resource_name,
            "resourceNamespace": resource_namespace,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetChannelByResourceName.parse_obj(data).channel_by_resource_name

    async def get_channels(
        self, filter: Union[Optional[ResourceFilter], UnsetType] = UNSET
    ) -> List[
        Union[
            GetChannelsChannelsChannel,
            GetChannelsChannelsSlackChannel,
            GetChannelsChannelsWebhookChannel,
        ]
    ]:
        query = gql(
            """
            query GetChannels($filter: ResourceFilter) {
              channels(filter: $filter) {
                ...ChannelDetails
              }
            }

            fragment ChannelDetails on Channel {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on SlackChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
              ... on WebhookChannel {
                config {
                  webhookUrl
                  applicationLinkUrl
                  authHeader
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"filter": filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetChannels.parse_obj(data).channels

    async def get_credential_by_resource_name(
        self, resource_name: str, resource_namespace: str
    ) -> Optional[
        Union[
            GetCredentialByResourceNameCredentialByResourceNameCredential,
            GetCredentialByResourceNameCredentialByResourceNameAwsCredential,
            GetCredentialByResourceNameCredentialByResourceNameAwsAthenaCredential,
            GetCredentialByResourceNameCredentialByResourceNameAwsRedshiftCredential,
            GetCredentialByResourceNameCredentialByResourceNamePostgreSqlCredential,
            GetCredentialByResourceNameCredentialByResourceNameSnowflakeCredential,
            GetCredentialByResourceNameCredentialByResourceNameKafkaSslCredential,
            GetCredentialByResourceNameCredentialByResourceNameKafkaSaslSslPlainCredential,
        ]
    ]:
        query = gql(
            """
            query GetCredentialByResourceName($resourceName: String!, $resourceNamespace: String! = "default") {
              credentialByResourceName(
                resourceName: $resourceName
                resourceNamespace: $resourceNamespace
              ) {
                ...CredentialDetails
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
            }
            """
        )
        variables: dict[str, object] = {
            "resourceName": resource_name,
            "resourceNamespace": resource_namespace,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetCredentialByResourceName.parse_obj(data).credential_by_resource_name

    async def get_destination_by_resource_name(
        self, resource_name: str, resource_namespace: str
    ) -> Optional[
        Union[
            GetDestinationByResourceNameDestinationByResourceNameDestination,
            GetDestinationByResourceNameDestinationByResourceNameGcpBigQueryDestination,
            GetDestinationByResourceNameDestinationByResourceNameSnowflakeDestination,
            GetDestinationByResourceNameDestinationByResourceNameAwsKinesisDestination,
        ]
    ]:
        query = gql(
            """
            query GetDestinationByResourceName($resourceName: String!, $resourceNamespace: String! = "default") {
              destinationByResourceName(
                resourceName: $resourceName
                resourceNamespace: $resourceNamespace
              ) {
                ...DestinationDetails
              }
            }

            fragment DestinationDetails on Destination {
              __typename
              id
              name
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on GcpBigQueryDestination {
                config {
                  project
                  dataset
                  table
                }
              }
              ... on SnowflakeDestination {
                config {
                  database
                  schema
                  table
                  role
                  warehouse
                }
              }
              ... on AwsKinesisDestination {
                config {
                  region
                  streamName
                  endpoint
                }
              }
            }
            """
        )
        variables: dict[str, object] = {
            "resourceName": resource_name,
            "resourceNamespace": resource_namespace,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetDestinationByResourceName.parse_obj(data).destination_by_resource_name

    async def get_identity_provider_by_resource_name(
        self, resource_name: str, resource_namespace: str
    ) -> Optional[
        Union[
            GetIdentityProviderByResourceNameIdentityProviderByResourceNameIdentityProvider,
            GetIdentityProviderByResourceNameIdentityProviderByResourceNameSamlIdentityProvider,
        ]
    ]:
        query = gql(
            """
            query GetIdentityProviderByResourceName($resourceName: String!, $resourceNamespace: String! = "default") {
              identityProviderByResourceName(
                resourceName: $resourceName
                resourceNamespace: $resourceNamespace
              ) {
                ...IdentityProviderDetails
              }
            }

            fragment IdentityProviderDetails on IdentityProvider {
              __typename
              id
              name
              disabled
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on SamlIdentityProvider {
                config {
                  entryPoint
                  entityId
                  cert
                }
              }
            }
            """
        )
        variables: dict[str, object] = {
            "resourceName": resource_name,
            "resourceNamespace": resource_namespace,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetIdentityProviderByResourceName.parse_obj(
            data
        ).identity_provider_by_resource_name

    async def get_identity_providers(
        self, filter: Union[Optional[ResourceFilter], UnsetType] = UNSET
    ) -> Optional[
        List[
            Optional[
                Union[
                    GetIdentityProvidersIdentityProvidersIdentityProvider,
                    GetIdentityProvidersIdentityProvidersSamlIdentityProvider,
                ]
            ]
        ]
    ]:
        query = gql(
            """
            query GetIdentityProviders($filter: ResourceFilter) {
              identityProviders(filter: $filter) {
                ...IdentityProviderDetails
              }
            }

            fragment IdentityProviderDetails on IdentityProvider {
              __typename
              id
              name
              disabled
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on SamlIdentityProvider {
                config {
                  entryPoint
                  entityId
                  cert
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"filter": filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetIdentityProviders.parse_obj(data).identity_providers

    async def get_incidents(
        self, input: IncidentsInput
    ) -> List[
        Union[
            GetIncidentsIncidentsNotification,
            GetIncidentsIncidentsSchemaChangeNotification,
            GetIncidentsIncidentsSegmentLimitExceededNotification,
            GetIncidentsIncidentsValidatorThresholdFailureNotification,
        ]
    ]:
        query = gql(
            """
            query GetIncidents($input: IncidentsInput!) {
              incidents(input: $input) {
                __typename
                id
                severity
                ... on SchemaChangeNotification {
                  createdAt
                  payload
                }
                ... on SegmentLimitExceededNotification {
                  createdAt
                  limit
                  segmentation {
                    id
                    name
                  }
                }
                ... on ValidatorThresholdFailureNotification {
                  segment {
                    ...SegmentDetails
                  }
                  metric {
                    ...ValidatorMetricDetails
                  }
                }
              }
            }

            fragment SegmentDetails on Segment {
              __typename
              id
              fields {
                field
                value
              }
              muted
            }

            fragment ValidatorMetricDetails on ValidatorMetric {
              __typename
              startTime
              endTime
              isIncident
              value
              ... on ValidatorMetricWithFixedThreshold {
                operator
                bound
              }
              ... on ValidatorMetricWithDynamicThreshold {
                lowerBound
                upperBound
                decisionBoundsType
                isBurnIn
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetIncidents.parse_obj(data).incidents

    async def get_notification_rule_by_resource_name(
        self, resource_name: str, resource_namespace: str
    ) -> Optional[GetNotificationRuleByResourceNameNotificationRuleByResourceName]:
        query = gql(
            """
            query GetNotificationRuleByResourceName($resourceName: String!, $resourceNamespace: String! = "default") {
              notificationRuleByResourceName(
                resourceName: $resourceName
                resourceNamespace: $resourceNamespace
              ) {
                ...NotificationRuleDetails
              }
            }

            fragment ChannelDetails on Channel {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on SlackChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
              ... on WebhookChannel {
                config {
                  webhookUrl
                  applicationLinkUrl
                  authHeader
                }
              }
            }

            fragment NotificationRuleDetails on NotificationRule {
              __typename
              id
              name
              notificationTypenames
              createdAt
              updatedAt
              sources
              channel {
                ...ChannelDetails
              }
              resourceName
              resourceNamespace
            }
            """
        )
        variables: dict[str, object] = {
            "resourceName": resource_name,
            "resourceNamespace": resource_namespace,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetNotificationRuleByResourceName.parse_obj(
            data
        ).notification_rule_by_resource_name

    async def get_notification_rules(
        self, filter: Union[Optional[ResourceFilter], UnsetType] = UNSET
    ) -> List[GetNotificationRulesNotificationRules]:
        query = gql(
            """
            query GetNotificationRules($filter: ResourceFilter) {
              notificationRules(filter: $filter) {
                ...NotificationRuleDetails
              }
            }

            fragment ChannelDetails on Channel {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on SlackChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
              ... on WebhookChannel {
                config {
                  webhookUrl
                  applicationLinkUrl
                  authHeader
                }
              }
            }

            fragment NotificationRuleDetails on NotificationRule {
              __typename
              id
              name
              notificationTypenames
              createdAt
              updatedAt
              sources
              channel {
                ...ChannelDetails
              }
              resourceName
              resourceNamespace
            }
            """
        )
        variables: dict[str, object] = {"filter": filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetNotificationRules.parse_obj(data).notification_rules

    async def get_recommendation(
        self, id: Any
    ) -> Union[
        GetRecommendationRecommendationRecommendation,
        GetRecommendationRecommendationValidatorCreateRecommendation,
        GetRecommendationRecommendationValidatorUpdateRecommendation,
        GetRecommendationRecommendationValidatorDeleteRecommendation,
    ]:
        query = gql(
            """
            query GetRecommendation($id: RecommendationId!) {
              recommendation(id: $id) {
                __typename
                ...RecommendationDetails
              }
            }

            fragment RecommendationDetails on Recommendation {
              id
              description
              createdAt
              updatedAt
              ... on ValidatorCreateRecommendation {
                sourceId
              }
              ... on ValidatorUpdateRecommendation {
                sourceId
              }
              ... on ValidatorDeleteRecommendation {
                sourceId
              }
            }
            """
        )
        variables: dict[str, object] = {"id": id}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetRecommendation.parse_obj(data).recommendation

    async def get_segment_incidents(
        self, input: SegmentIncidentsInput
    ) -> List[GetSegmentIncidentsSegmentIncidents]:
        query = gql(
            """
            query GetSegmentIncidents($input: SegmentIncidentsInput!) {
              segmentIncidents(input: $input) {
                ...ValidatorIncidents
              }
            }

            fragment SegmentDetails on Segment {
              __typename
              id
              fields {
                field
                value
              }
              muted
            }

            fragment ValidatorIncidents on ValidatorThresholdFailureNotification {
              __typename
              id
              severity
              segment {
                ...SegmentDetails
              }
              metric {
                ...ValidatorMetricDetails
              }
            }

            fragment ValidatorMetricDetails on ValidatorMetric {
              __typename
              startTime
              endTime
              isIncident
              value
              ... on ValidatorMetricWithFixedThreshold {
                operator
                bound
              }
              ... on ValidatorMetricWithDynamicThreshold {
                lowerBound
                upperBound
                decisionBoundsType
                isBurnIn
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetSegmentIncidents.parse_obj(data).segment_incidents

    async def get_segmentation(
        self, id: SegmentationId
    ) -> Optional[GetSegmentationSegmentation]:
        query = gql(
            """
            query GetSegmentation($id: SegmentationId!) {
              segmentation(id: $id) {
                ...SegmentationDetails
              }
            }

            fragment SegmentationDetails on Segmentation {
              __typename
              id
              name
              source {
                id
                name
                resourceName
                resourceNamespace
              }
              fields
              createdAt
              updatedAt
              resourceName
              resourceNamespace
            }
            """
        )
        variables: dict[str, object] = {"id": id}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetSegmentation.parse_obj(data).segmentation

    async def get_segmentation_by_resource_name(
        self, resource_name: str, resource_namespace: str
    ) -> Optional[GetSegmentationByResourceNameSegmentationByResourceName]:
        query = gql(
            """
            query GetSegmentationByResourceName($resourceName: String!, $resourceNamespace: String! = "default") {
              segmentationByResourceName(
                resourceName: $resourceName
                resourceNamespace: $resourceNamespace
              ) {
                ...SegmentationDetails
              }
            }

            fragment SegmentationDetails on Segmentation {
              __typename
              id
              name
              source {
                id
                name
                resourceName
                resourceNamespace
              }
              fields
              createdAt
              updatedAt
              resourceName
              resourceNamespace
            }
            """
        )
        variables: dict[str, object] = {
            "resourceName": resource_name,
            "resourceNamespace": resource_namespace,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetSegmentationByResourceName.parse_obj(
            data
        ).segmentation_by_resource_name

    async def get_source(
        self, id: SourceId
    ) -> Optional[
        Union[
            GetSourceSourceSource,
            GetSourceSourceGcpStorageSource,
            GetSourceSourceGcpBigQuerySource,
            GetSourceSourceGcpPubSubSource,
            GetSourceSourceGcpPubSubLiteSource,
            GetSourceSourceAwsAthenaSource,
            GetSourceSourceAwsKinesisSource,
            GetSourceSourceAwsRedshiftSource,
            GetSourceSourceAwsS3Source,
            GetSourceSourcePostgreSqlSource,
            GetSourceSourceSnowflakeSource,
            GetSourceSourceKafkaSource,
        ]
    ]:
        query = gql(
            """
            query GetSource($id: SourceId!) {
              source(id: $id) {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"id": id}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetSource.parse_obj(data).source

    async def get_source_by_resource_name(
        self, resource_name: str, resource_namespace: str
    ) -> Optional[
        Union[
            GetSourceByResourceNameSourceByResourceNameSource,
            GetSourceByResourceNameSourceByResourceNameGcpStorageSource,
            GetSourceByResourceNameSourceByResourceNameGcpBigQuerySource,
            GetSourceByResourceNameSourceByResourceNameGcpPubSubSource,
            GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSource,
            GetSourceByResourceNameSourceByResourceNameAwsAthenaSource,
            GetSourceByResourceNameSourceByResourceNameAwsKinesisSource,
            GetSourceByResourceNameSourceByResourceNameAwsRedshiftSource,
            GetSourceByResourceNameSourceByResourceNameAwsS3Source,
            GetSourceByResourceNameSourceByResourceNamePostgreSqlSource,
            GetSourceByResourceNameSourceByResourceNameSnowflakeSource,
            GetSourceByResourceNameSourceByResourceNameKafkaSource,
        ]
    ]:
        query = gql(
            """
            query GetSourceByResourceName($resourceName: String!, $resourceNamespace: String! = "default") {
              sourceByResourceName(
                resourceName: $resourceName
                resourceNamespace: $resourceNamespace
              ) {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                }
              }
            }
            """
        )
        variables: dict[str, object] = {
            "resourceName": resource_name,
            "resourceNamespace": resource_namespace,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetSourceByResourceName.parse_obj(data).source_by_resource_name

    async def get_source_incidents(
        self, input: SourceIncidentsInput
    ) -> List[
        Union[
            GetSourceIncidentsSourceIncidentsSchemaChangeNotification,
            GetSourceIncidentsSourceIncidentsSegmentLimitExceededNotification,
        ]
    ]:
        query = gql(
            """
            query GetSourceIncidents($input: SourceIncidentsInput!) {
              sourceIncidents(input: $input) {
                ...SourceIncidents
              }
            }

            fragment SourceIncidents on SourceIncidentNotification {
              __typename
              ... on SchemaChangeNotification {
                id
                severity
                createdAt
                payload
              }
              ... on SegmentLimitExceededNotification {
                id
                severity
                createdAt
                limit
                segmentation {
                  id
                  name
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetSourceIncidents.parse_obj(data).source_incidents

    async def get_source_recommended_validators(
        self, id: SourceId
    ) -> Optional[GetSourceRecommendedValidatorsSource]:
        query = gql(
            """
            query GetSourceRecommendedValidators($id: SourceId!) {
              source(id: $id) {
                recommendedValidators {
                  ...ValidatorSummary
                }
              }
            }

            fragment SegmentationSummary on Segmentation {
              __typename
              id
              name
              fields
              createdAt
              updatedAt
            }

            fragment ValidatorSummary on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              state
              progress {
                percentage
                processed
                total
              }
              stats {
                lastArtifactAt
                lastIncidentAt
              }
              stateUpdatedAt
              sourceConfig {
                source {
                  id
                }
                segmentation {
                  ...SegmentationSummary
                }
              }
              ... on NumericValidator {
                config {
                  metric
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  categoricalDistributionMetric: metric
                }
              }
              ... on NumericDistributionValidator {
                config {
                  distributionMetric: metric
                }
              }
              ... on VolumeValidator {
                config {
                  volumeMetric: metric
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  numericAnomalyMetric: metric
                }
              }
              ... on RelativeTimeValidator {
                config {
                  relativeTimeMetric: metric
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  relativeVolumeMetric: metric
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"id": id}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetSourceRecommendedValidators.parse_obj(data).source

    async def get_user_by_resource_name(
        self, resource_name: str, resource_namespace: str
    ) -> Optional[GetUserByResourceNameUserByResourceName]:
        query = gql(
            """
            query GetUserByResourceName($resourceName: String!, $resourceNamespace: String! = "default") {
              userByResourceName(
                resourceName: $resourceName
                resourceNamespace: $resourceNamespace
              ) {
                ...UserDetails
              }
            }

            fragment IdentityDetails on Identity {
              ... on LocalIdentity {
                __typename
                id
                userId
                username
                createdAt
              }
              ... on FederatedIdentity {
                __typename
                id
                userId
                idp {
                  __typename
                  id
                  name
                }
                createdAt
              }
            }

            fragment UserDetails on User {
              id
              displayName
              fullName
              email
              role
              status
              identities {
                ...IdentityDetails
              }
              createdAt
              updatedAt
              resourceName
              resourceNamespace
            }
            """
        )
        variables: dict[str, object] = {
            "resourceName": resource_name,
            "resourceNamespace": resource_namespace,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetUserByResourceName.parse_obj(data).user_by_resource_name

    async def get_users(
        self, filter: Union[Optional[ResourceFilter], UnsetType] = UNSET
    ) -> Optional[List[Optional[GetUsersUsers]]]:
        query = gql(
            """
            query GetUsers($filter: ResourceFilter) {
              users(filter: $filter) {
                ...UserDetails
              }
            }

            fragment IdentityDetails on Identity {
              ... on LocalIdentity {
                __typename
                id
                userId
                username
                createdAt
              }
              ... on FederatedIdentity {
                __typename
                id
                userId
                idp {
                  __typename
                  id
                  name
                }
                createdAt
              }
            }

            fragment UserDetails on User {
              id
              displayName
              fullName
              email
              role
              status
              identities {
                ...IdentityDetails
              }
              createdAt
              updatedAt
              resourceName
              resourceNamespace
            }
            """
        )
        variables: dict[str, object] = {"filter": filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetUsers.parse_obj(data).users

    async def get_validator(
        self, id: ValidatorId
    ) -> Optional[
        Union[
            GetValidatorValidatorValidator,
            GetValidatorValidatorNumericValidator,
            GetValidatorValidatorCategoricalDistributionValidator,
            GetValidatorValidatorNumericDistributionValidator,
            GetValidatorValidatorVolumeValidator,
            GetValidatorValidatorNumericAnomalyValidator,
            GetValidatorValidatorRelativeTimeValidator,
            GetValidatorValidatorFreshnessValidator,
            GetValidatorValidatorRelativeVolumeValidator,
        ]
    ]:
        query = gql(
            """
            query GetValidator($id: ValidatorId!) {
              validator(id: $id) {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"id": id}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetValidator.parse_obj(data).validator

    async def get_validator_by_resource_name(
        self, resource_name: str, resource_namespace: str
    ) -> Optional[
        Union[
            GetValidatorByResourceNameValidatorByResourceNameValidator,
            GetValidatorByResourceNameValidatorByResourceNameNumericValidator,
            GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidator,
            GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidator,
            GetValidatorByResourceNameValidatorByResourceNameVolumeValidator,
            GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidator,
            GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidator,
            GetValidatorByResourceNameValidatorByResourceNameFreshnessValidator,
            GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidator,
        ]
    ]:
        query = gql(
            """
            query GetValidatorByResourceName($resourceName: String!, $resourceNamespace: String! = "default") {
              validatorByResourceName(
                resourceName: $resourceName
                resourceNamespace: $resourceNamespace
              ) {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
            }
            """
        )
        variables: dict[str, object] = {
            "resourceName": resource_name,
            "resourceNamespace": resource_namespace,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetValidatorByResourceName.parse_obj(data).validator_by_resource_name

    async def get_validator_incidents(
        self, input: ValidatorIncidentsInput
    ) -> List[GetValidatorIncidentsValidatorIncidents]:
        query = gql(
            """
            query GetValidatorIncidents($input: ValidatorIncidentsInput!) {
              validatorIncidents(input: $input) {
                ...ValidatorIncidents
              }
            }

            fragment SegmentDetails on Segment {
              __typename
              id
              fields {
                field
                value
              }
              muted
            }

            fragment ValidatorIncidents on ValidatorThresholdFailureNotification {
              __typename
              id
              severity
              segment {
                ...SegmentDetails
              }
              metric {
                ...ValidatorMetricDetails
              }
            }

            fragment ValidatorMetricDetails on ValidatorMetric {
              __typename
              startTime
              endTime
              isIncident
              value
              ... on ValidatorMetricWithFixedThreshold {
                operator
                bound
              }
              ... on ValidatorMetricWithDynamicThreshold {
                lowerBound
                upperBound
                decisionBoundsType
                isBurnIn
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetValidatorIncidents.parse_obj(data).validator_incidents

    async def get_validator_metric_debug_info(
        self, input: ValidatorMetricDebugInfoInput
    ) -> Union[
        GetValidatorMetricDebugInfoValidatorMetricDebugInfoValidatorMetricDebugInfo,
        GetValidatorMetricDebugInfoValidatorMetricDebugInfoGcpBigQuerySourceDebugInfo,
        GetValidatorMetricDebugInfoValidatorMetricDebugInfoGcpStorageSourceDebugInfo,
        GetValidatorMetricDebugInfoValidatorMetricDebugInfoAwsS3SourceDebugInfo,
        GetValidatorMetricDebugInfoValidatorMetricDebugInfoAwsRedShiftSourceDebugInfo,
        GetValidatorMetricDebugInfoValidatorMetricDebugInfoAwsAthenaSourceDebugInfo,
        GetValidatorMetricDebugInfoValidatorMetricDebugInfoSnowflakeSourceDebugInfo,
        GetValidatorMetricDebugInfoValidatorMetricDebugInfoPostgreSQLSourceDebugInfo,
    ]:
        query = gql(
            """
            query GetValidatorMetricDebugInfo($input: ValidatorMetricDebugInfoInput!) {
              validatorMetricDebugInfo(input: $input) {
                ...ValidatorMetricDebugInfoDetails
              }
            }

            fragment ValidatorMetricDebugInfoDetails on ValidatorMetricDebugInfo {
              __typename
              startTime
              endTime
              ... on GcpBigQuerySourceDebugInfo {
                sqlQuery
              }
              ... on GcpStorageSourceDebugInfo {
                bucket
                filePath
              }
              ... on AwsS3SourceDebugInfo {
                bucket
                filePath
              }
              ... on AwsRedShiftSourceDebugInfo {
                sqlQuery
              }
              ... on AwsAthenaSourceDebugInfo {
                sqlQuery
              }
              ... on SnowflakeSourceDebugInfo {
                sqlQuery
              }
              ... on PostgreSQLSourceDebugInfo {
                sqlQuery
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetValidatorMetricDebugInfo.parse_obj(data).validator_metric_debug_info

    async def get_validator_metric_debug_records(
        self, input: ValidatorMetricDebugInfoInput
    ) -> List[Any]:
        query = gql(
            """
            query GetValidatorMetricDebugRecords($input: ValidatorMetricDebugInfoInput!) {
              validatorMetricDebugRecords(input: $input)
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetValidatorMetricDebugRecords.parse_obj(
            data
        ).validator_metric_debug_records

    async def get_validator_segment_incidents(
        self, input: ValidatorSegmentIncidentsInput
    ) -> List[GetValidatorSegmentIncidentsValidatorSegmentIncidents]:
        query = gql(
            """
            query GetValidatorSegmentIncidents($input: ValidatorSegmentIncidentsInput!) {
              validatorSegmentIncidents(input: $input) {
                ...ValidatorIncidents
              }
            }

            fragment SegmentDetails on Segment {
              __typename
              id
              fields {
                field
                value
              }
              muted
            }

            fragment ValidatorIncidents on ValidatorThresholdFailureNotification {
              __typename
              id
              severity
              segment {
                ...SegmentDetails
              }
              metric {
                ...ValidatorMetricDetails
              }
            }

            fragment ValidatorMetricDetails on ValidatorMetric {
              __typename
              startTime
              endTime
              isIncident
              value
              ... on ValidatorMetricWithFixedThreshold {
                operator
                bound
              }
              ... on ValidatorMetricWithDynamicThreshold {
                lowerBound
                upperBound
                decisionBoundsType
                isBurnIn
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetValidatorSegmentIncidents.parse_obj(data).validator_segment_incidents

    async def get_validator_segment_metrics(
        self, input: ValidatorSegmentMetricsInput
    ) -> Union[
        GetValidatorSegmentMetricsValidatorSegmentMetricsValidatorMetricWithDynamicThresholdHistory,
        GetValidatorSegmentMetricsValidatorSegmentMetricsValidatorMetricWithFixedThresholdHistory,
    ]:
        query = gql(
            """
            query GetValidatorSegmentMetrics($input: ValidatorSegmentMetricsInput!) {
              validatorSegmentMetrics(input: $input) {
                __typename
                ... on ValidatorMetricWithFixedThresholdHistory {
                  values {
                    ...ValidatorMetricDetails
                  }
                }
                ... on ValidatorMetricWithDynamicThresholdHistory {
                  values {
                    ...ValidatorMetricDetails
                  }
                }
              }
            }

            fragment ValidatorMetricDetails on ValidatorMetric {
              __typename
              startTime
              endTime
              isIncident
              value
              ... on ValidatorMetricWithFixedThreshold {
                operator
                bound
              }
              ... on ValidatorMetricWithDynamicThreshold {
                lowerBound
                upperBound
                decisionBoundsType
                isBurnIn
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetValidatorSegmentMetrics.parse_obj(data).validator_segment_metrics

    async def get_window_by_resource_name(
        self, resource_name: str, resource_namespace: str
    ) -> Optional[
        Union[
            GetWindowByResourceNameWindowByResourceNameWindow,
            GetWindowByResourceNameWindowByResourceNameFixedBatchWindow,
            GetWindowByResourceNameWindowByResourceNameSessionizedWindow,
            GetWindowByResourceNameWindowByResourceNameTumblingWindow,
        ]
    ]:
        query = gql(
            """
            query GetWindowByResourceName($resourceName: String!, $resourceNamespace: String! = "default") {
              windowByResourceName(
                resourceName: $resourceName
                resourceNamespace: $resourceNamespace
              ) {
                ...WindowDetails
              }
            }

            fragment WindowDetails on Window {
              __typename
              id
              name
              source {
                id
                name
                resourceName
                resourceNamespace
              }
              dataTimeField
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on FixedBatchWindow {
                config {
                  batchSize
                  segmentedBatching
                  batchTimeoutSecs
                }
              }
              ... on SessionizedWindow {
                config {
                  timeout
                  timeoutUnit
                }
              }
              ... on TumblingWindow {
                config {
                  windowSize
                  timeUnit
                }
              }
            }
            """
        )
        variables: dict[str, object] = {
            "resourceName": resource_name,
            "resourceNamespace": resource_namespace,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetWindowByResourceName.parse_obj(data).window_by_resource_name

    async def infer_aws_athena_schema(
        self, input: AwsAthenaInferSchemaInput
    ) -> JsonTypeDefinition:
        query = gql(
            """
            query InferAwsAthenaSchema($input: AwsAthenaInferSchemaInput!) {
              awsAthenaInferSchema(input: $input)
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return InferAwsAthenaSchema.parse_obj(data).aws_athena_infer_schema

    async def infer_aws_kinesis_schema(
        self, input: AwsKinesisInferSchemaInput
    ) -> JsonTypeDefinition:
        query = gql(
            """
            query InferAwsKinesisSchema($input: AwsKinesisInferSchemaInput!) {
              awsKinesisInferSchema(input: $input)
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return InferAwsKinesisSchema.parse_obj(data).aws_kinesis_infer_schema

    async def infer_aws_redshift_schema(
        self, input: AwsRedshiftInferSchemaInput
    ) -> JsonTypeDefinition:
        query = gql(
            """
            query InferAwsRedshiftSchema($input: AwsRedshiftInferSchemaInput!) {
              awsRedshiftInferSchema(input: $input)
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return InferAwsRedshiftSchema.parse_obj(data).aws_redshift_infer_schema

    async def infer_aws_s3_schema(
        self, input: AwsS3InferSchemaInput
    ) -> JsonTypeDefinition:
        query = gql(
            """
            query InferAwsS3Schema($input: AwsS3InferSchemaInput!) {
              awsS3InferSchema(input: $input)
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return InferAwsS3Schema.parse_obj(data).aws_s3_infer_schema

    async def infer_demo_schema(self) -> JsonTypeDefinition:
        query = gql(
            """
            query InferDemoSchema {
              demoInferSchema
            }
            """
        )
        variables: dict[str, object] = {}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return InferDemoSchema.parse_obj(data).demo_infer_schema

    async def infer_gcp_big_query_schema(
        self, input: GcpBigQueryInferSchemaInput
    ) -> JsonTypeDefinition:
        query = gql(
            """
            query InferGcpBigQuerySchema($input: GcpBigQueryInferSchemaInput!) {
              gcpBigQueryInferSchema(input: $input)
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return InferGcpBigQuerySchema.parse_obj(data).gcp_big_query_infer_schema

    async def infer_gcp_pub_sub_lite_schema(
        self, input: GcpPubSubLiteInferSchemaInput
    ) -> JsonTypeDefinition:
        query = gql(
            """
            query InferGcpPubSubLiteSchema($input: GcpPubSubLiteInferSchemaInput!) {
              gcpPubSubLiteInferSchema(input: $input)
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return InferGcpPubSubLiteSchema.parse_obj(data).gcp_pub_sub_lite_infer_schema

    async def infer_gcp_pub_sub_schema(
        self, input: GcpPubSubInferSchemaInput
    ) -> JsonTypeDefinition:
        query = gql(
            """
            query InferGcpPubSubSchema($input: GcpPubSubInferSchemaInput!) {
              gcpPubSubInferSchema(input: $input)
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return InferGcpPubSubSchema.parse_obj(data).gcp_pub_sub_infer_schema

    async def infer_gcp_storage_schema(
        self, input: GcpStorageInferSchemaInput
    ) -> JsonTypeDefinition:
        query = gql(
            """
            query InferGcpStorageSchema($input: GcpStorageInferSchemaInput!) {
              gcpStorageInferSchema(input: $input)
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return InferGcpStorageSchema.parse_obj(data).gcp_storage_infer_schema

    async def infer_kafka_schema(
        self, input: KafkaInferSchemaInput
    ) -> JsonTypeDefinition:
        query = gql(
            """
            query InferKafkaSchema($input: KafkaInferSchemaInput!) {
              kafkaInferSchema(input: $input)
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return InferKafkaSchema.parse_obj(data).kafka_infer_schema

    async def infer_postgre_sql_schema(
        self, input: PostgreSqlInferSchemaInput
    ) -> JsonTypeDefinition:
        query = gql(
            """
            query InferPostgreSqlSchema($input: PostgreSqlInferSchemaInput!) {
              postgreSqlInferSchema(input: $input)
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return InferPostgreSqlSchema.parse_obj(data).postgre_sql_infer_schema

    async def infer_snowflake_schema(
        self, input: SnowflakeInferSchemaInput
    ) -> JsonTypeDefinition:
        query = gql(
            """
            query InferSnowflakeSchema($input: SnowflakeInferSchemaInput!) {
              snowflakeInferSchema(input: $input)
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return InferSnowflakeSchema.parse_obj(data).snowflake_infer_schema

    async def kafka_sasl_ssl_plain_credential_secret_changed(
        self, input: KafkaSaslSslPlainCredentialSecretChangedInput
    ) -> KafkaSaslSslPlainCredentialSecretChangedKafkaSaslSslPlainCredentialSecretChanged:
        query = gql(
            """
            query KafkaSaslSslPlainCredentialSecretChanged($input: KafkaSaslSslPlainCredentialSecretChangedInput!) {
              kafkaSaslSslPlainCredentialSecretChanged(input: $input) {
                ...CredentialSecretChanged
              }
            }

            fragment CredentialSecretChanged on CredentialSecretChangedResult {
              errors {
                ...ErrorDetails
              }
              hasChanged
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return KafkaSaslSslPlainCredentialSecretChanged.parse_obj(
            data
        ).kafka_sasl_ssl_plain_credential_secret_changed

    async def kafka_ssl_credential_secret_changed(
        self, input: KafkaSslCredentialSecretChangedInput
    ) -> KafkaSslCredentialSecretChangedKafkaSslCredentialSecretChanged:
        query = gql(
            """
            query KafkaSslCredentialSecretChanged($input: KafkaSslCredentialSecretChangedInput!) {
              kafkaSslCredentialSecretChanged(input: $input) {
                ...CredentialSecretChanged
              }
            }

            fragment CredentialSecretChanged on CredentialSecretChangedResult {
              errors {
                ...ErrorDetails
              }
              hasChanged
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return KafkaSslCredentialSecretChanged.parse_obj(
            data
        ).kafka_ssl_credential_secret_changed

    async def list_credentials(
        self, filter: Union[Optional[ResourceFilter], UnsetType] = UNSET
    ) -> List[
        Union[
            ListCredentialsCredentialsListCredential,
            ListCredentialsCredentialsListAwsCredential,
            ListCredentialsCredentialsListAwsAthenaCredential,
            ListCredentialsCredentialsListAwsRedshiftCredential,
            ListCredentialsCredentialsListPostgreSqlCredential,
            ListCredentialsCredentialsListSnowflakeCredential,
            ListCredentialsCredentialsListKafkaSslCredential,
            ListCredentialsCredentialsListKafkaSaslSslPlainCredential,
        ]
    ]:
        query = gql(
            """
            query ListCredentials($filter: ResourceFilter) {
              credentialsList(filter: $filter) {
                ...CredentialDetails
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"filter": filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ListCredentials.parse_obj(data).credentials_list

    async def list_destinations(
        self, filter: Union[Optional[ResourceFilter], UnsetType] = UNSET
    ) -> List[
        Union[
            ListDestinationsDestinationsListDestination,
            ListDestinationsDestinationsListGcpBigQueryDestination,
            ListDestinationsDestinationsListSnowflakeDestination,
            ListDestinationsDestinationsListAwsKinesisDestination,
        ]
    ]:
        query = gql(
            """
            query ListDestinations($filter: ResourceFilter) {
              destinationsList(filter: $filter) {
                ...DestinationDetails
              }
            }

            fragment DestinationDetails on Destination {
              __typename
              id
              name
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on GcpBigQueryDestination {
                config {
                  project
                  dataset
                  table
                }
              }
              ... on SnowflakeDestination {
                config {
                  database
                  schema
                  table
                  role
                  warehouse
                }
              }
              ... on AwsKinesisDestination {
                config {
                  region
                  streamName
                  endpoint
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"filter": filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ListDestinations.parse_obj(data).destinations_list

    async def list_segmentations(
        self, filter: Union[Optional[ResourceFilter], UnsetType] = UNSET
    ) -> List[ListSegmentationsSegmentationsList]:
        query = gql(
            """
            query ListSegmentations($filter: ResourceFilter) {
              segmentationsList(filter: $filter) {
                ...SegmentationDetails
              }
            }

            fragment SegmentationDetails on Segmentation {
              __typename
              id
              name
              source {
                id
                name
                resourceName
                resourceNamespace
              }
              fields
              createdAt
              updatedAt
              resourceName
              resourceNamespace
            }
            """
        )
        variables: dict[str, object] = {"filter": filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ListSegmentations.parse_obj(data).segmentations_list

    async def list_sources(
        self, filter: Union[Optional[ResourceFilter], UnsetType] = UNSET
    ) -> List[
        Union[
            ListSourcesSourcesListSource,
            ListSourcesSourcesListGcpStorageSource,
            ListSourcesSourcesListGcpBigQuerySource,
            ListSourcesSourcesListGcpPubSubSource,
            ListSourcesSourcesListGcpPubSubLiteSource,
            ListSourcesSourcesListAwsAthenaSource,
            ListSourcesSourcesListAwsKinesisSource,
            ListSourcesSourcesListAwsRedshiftSource,
            ListSourcesSourcesListAwsS3Source,
            ListSourcesSourcesListPostgreSqlSource,
            ListSourcesSourcesListSnowflakeSource,
            ListSourcesSourcesListKafkaSource,
        ]
    ]:
        query = gql(
            """
            query ListSources($filter: ResourceFilter) {
              sourcesList(filter: $filter) {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"filter": filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ListSources.parse_obj(data).sources_list

    async def list_validators(
        self, id: SourceId, filter: Union[Optional[ResourceFilter], UnsetType] = UNSET
    ) -> List[
        Union[
            ListValidatorsValidatorsListValidator,
            ListValidatorsValidatorsListNumericValidator,
            ListValidatorsValidatorsListCategoricalDistributionValidator,
            ListValidatorsValidatorsListNumericDistributionValidator,
            ListValidatorsValidatorsListVolumeValidator,
            ListValidatorsValidatorsListNumericAnomalyValidator,
            ListValidatorsValidatorsListRelativeTimeValidator,
            ListValidatorsValidatorsListFreshnessValidator,
            ListValidatorsValidatorsListRelativeVolumeValidator,
        ]
    ]:
        query = gql(
            """
            query ListValidators($id: SourceId!, $filter: ResourceFilter) {
              validatorsList(id: $id, filter: $filter) {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"id": id, "filter": filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ListValidators.parse_obj(data).validators_list

    async def list_windows(
        self, filter: Union[Optional[ResourceFilter], UnsetType] = UNSET
    ) -> List[
        Union[
            ListWindowsWindowsListWindow,
            ListWindowsWindowsListFixedBatchWindow,
            ListWindowsWindowsListSessionizedWindow,
            ListWindowsWindowsListTumblingWindow,
        ]
    ]:
        query = gql(
            """
            query ListWindows($filter: ResourceFilter) {
              windowsList(filter: $filter) {
                ...WindowDetails
              }
            }

            fragment WindowDetails on Window {
              __typename
              id
              name
              source {
                id
                name
                resourceName
                resourceNamespace
              }
              dataTimeField
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on FixedBatchWindow {
                config {
                  batchSize
                  segmentedBatching
                  batchTimeoutSecs
                }
              }
              ... on SessionizedWindow {
                config {
                  timeout
                  timeoutUnit
                }
              }
              ... on TumblingWindow {
                config {
                  windowSize
                  timeUnit
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"filter": filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ListWindows.parse_obj(data).windows_list

    async def postgre_sql_credential_secret_changed(
        self, input: PostgreSqlCredentialSecretChangedInput
    ) -> PostgreSqlCredentialSecretChangedPostgreSqlCredentialSecretChanged:
        query = gql(
            """
            query PostgreSqlCredentialSecretChanged($input: PostgreSqlCredentialSecretChangedInput!) {
              postgreSqlCredentialSecretChanged(input: $input) {
                ...CredentialSecretChanged
              }
            }

            fragment CredentialSecretChanged on CredentialSecretChangedResult {
              errors {
                ...ErrorDetails
              }
              hasChanged
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return PostgreSqlCredentialSecretChanged.parse_obj(
            data
        ).postgre_sql_credential_secret_changed

    async def reset_source(self, id: SourceId) -> ResetSourceSourceReset:
        query = gql(
            """
            mutation ResetSource($id: SourceId!) {
              sourceReset(id: $id) {
                errors {
                  ...ErrorDetails
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"id": id}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ResetSource.parse_obj(data).source_reset

    async def segments(self, id: SegmentationId) -> List[SegmentsSegments]:
        query = gql(
            """
            query Segments($id: SegmentationId!) {
              segments(id: $id) {
                ...SegmentDetails
              }
            }

            fragment SegmentDetails on Segment {
              __typename
              id
              fields {
                field
                value
              }
              muted
            }
            """
        )
        variables: dict[str, object] = {"id": id}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return Segments.parse_obj(data).segments

    async def segments_by_resource_name(
        self, resource_name: str, resource_namespace: str
    ) -> List[SegmentsByResourceNameSegmentsByResourceName]:
        query = gql(
            """
            query SegmentsByResourceName($resourceName: String!, $resourceNamespace: String! = "default") {
              segmentsByResourceName(
                resourceName: $resourceName
                resourceNamespace: $resourceNamespace
              ) {
                ...SegmentDetails
              }
            }

            fragment SegmentDetails on Segment {
              __typename
              id
              fields {
                field
                value
              }
              muted
            }
            """
        )
        variables: dict[str, object] = {
            "resourceName": resource_name,
            "resourceNamespace": resource_namespace,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return SegmentsByResourceName.parse_obj(data).segments_by_resource_name

    async def snowflake_credential_secret_changed(
        self, input: SnowflakeCredentialSecretChangedInput
    ) -> SnowflakeCredentialSecretChangedSnowflakeCredentialSecretChanged:
        query = gql(
            """
            query SnowflakeCredentialSecretChanged($input: SnowflakeCredentialSecretChangedInput!) {
              snowflakeCredentialSecretChanged(input: $input) {
                ...CredentialSecretChanged
              }
            }

            fragment CredentialSecretChanged on CredentialSecretChangedResult {
              errors {
                ...ErrorDetails
              }
              hasChanged
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return SnowflakeCredentialSecretChanged.parse_obj(
            data
        ).snowflake_credential_secret_changed

    async def start_source(self, id: SourceId) -> StartSourceSourceStart:
        query = gql(
            """
            mutation StartSource($id: SourceId!) {
              sourceStart(id: $id) {
                errors {
                  ...ErrorDetails
                }
                state
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"id": id}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return StartSource.parse_obj(data).source_start

    async def stop_source(self, id: SourceId) -> StopSourceSourceStop:
        query = gql(
            """
            mutation StopSource($id: SourceId!) {
              sourceStop(id: $id) {
                errors {
                  ...ErrorDetails
                }
                state
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"id": id}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return StopSource.parse_obj(data).source_stop

    async def update_aws_athena_credential(
        self, input: AwsAthenaCredentialUpdateInput
    ) -> UpdateAwsAthenaCredentialAwsAthenaCredentialUpdate:
        query = gql(
            """
            mutation UpdateAwsAthenaCredential($input: AwsAthenaCredentialUpdateInput!) {
              awsAthenaCredentialUpdate(input: $input) {
                ...CredentialUpdate
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
            }

            fragment CredentialUpdate on CredentialUpdateResult {
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateAwsAthenaCredential.parse_obj(data).aws_athena_credential_update

    async def update_aws_athena_source(
        self, input: AwsAthenaSourceUpdateInput
    ) -> UpdateAwsAthenaSourceAwsAthenaSourceUpdate:
        query = gql(
            """
            mutation UpdateAwsAthenaSource($input: AwsAthenaSourceUpdateInput!) {
              awsAthenaSourceUpdate(input: $input) {
                ...SourceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                }
              }
            }

            fragment SourceUpdate on SourceUpdateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateAwsAthenaSource.parse_obj(data).aws_athena_source_update

    async def update_aws_credential(
        self, input: AwsCredentialUpdateInput
    ) -> UpdateAwsCredentialAwsCredentialUpdate:
        query = gql(
            """
            mutation UpdateAwsCredential($input: AwsCredentialUpdateInput!) {
              awsCredentialUpdate(input: $input) {
                ...CredentialUpdate
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
            }

            fragment CredentialUpdate on CredentialUpdateResult {
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateAwsCredential.parse_obj(data).aws_credential_update

    async def update_aws_kinesis_destination(
        self, input: AwsKinesisDestinationUpdateInput
    ) -> UpdateAwsKinesisDestinationAwsKinesisDestinationUpdate:
        query = gql(
            """
            mutation UpdateAwsKinesisDestination($input: AwsKinesisDestinationUpdateInput!) {
              awsKinesisDestinationUpdate(input: $input) {
                ...DestinationUpdate
              }
            }

            fragment DestinationDetails on Destination {
              __typename
              id
              name
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on GcpBigQueryDestination {
                config {
                  project
                  dataset
                  table
                }
              }
              ... on SnowflakeDestination {
                config {
                  database
                  schema
                  table
                  role
                  warehouse
                }
              }
              ... on AwsKinesisDestination {
                config {
                  region
                  streamName
                  endpoint
                }
              }
            }

            fragment DestinationUpdate on DestinationUpdateResult {
              errors {
                ...ErrorDetails
              }
              destination {
                ...DestinationDetails
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateAwsKinesisDestination.parse_obj(
            data
        ).aws_kinesis_destination_update

    async def update_aws_kinesis_source(
        self, input: AwsKinesisSourceUpdateInput
    ) -> UpdateAwsKinesisSourceAwsKinesisSourceUpdate:
        query = gql(
            """
            mutation UpdateAwsKinesisSource($input: AwsKinesisSourceUpdateInput!) {
              awsKinesisSourceUpdate(input: $input) {
                ...SourceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                }
              }
            }

            fragment SourceUpdate on SourceUpdateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateAwsKinesisSource.parse_obj(data).aws_kinesis_source_update

    async def update_aws_redshift_credential(
        self, input: AwsRedshiftCredentialUpdateInput
    ) -> UpdateAwsRedshiftCredentialAwsRedshiftCredentialUpdate:
        query = gql(
            """
            mutation UpdateAwsRedshiftCredential($input: AwsRedshiftCredentialUpdateInput!) {
              awsRedshiftCredentialUpdate(input: $input) {
                ...CredentialUpdate
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
            }

            fragment CredentialUpdate on CredentialUpdateResult {
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateAwsRedshiftCredential.parse_obj(
            data
        ).aws_redshift_credential_update

    async def update_aws_redshift_source(
        self, input: AwsRedshiftSourceUpdateInput
    ) -> UpdateAwsRedshiftSourceAwsRedshiftSourceUpdate:
        query = gql(
            """
            mutation UpdateAwsRedshiftSource($input: AwsRedshiftSourceUpdateInput!) {
              awsRedshiftSourceUpdate(input: $input) {
                ...SourceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                }
              }
            }

            fragment SourceUpdate on SourceUpdateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateAwsRedshiftSource.parse_obj(data).aws_redshift_source_update

    async def update_aws_s3_source(
        self, input: AwsS3SourceUpdateInput
    ) -> UpdateAwsS3SourceAwsS3SourceUpdate:
        query = gql(
            """
            mutation UpdateAwsS3Source($input: AwsS3SourceUpdateInput!) {
              awsS3SourceUpdate(input: $input) {
                ...SourceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                }
              }
            }

            fragment SourceUpdate on SourceUpdateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateAwsS3Source.parse_obj(data).aws_s3_source_update

    async def update_categorical_distribution_validator(
        self, input: CategoricalDistributionValidatorUpdateInput
    ) -> UpdateCategoricalDistributionValidatorCategoricalDistributionValidatorUpdate:
        query = gql(
            """
            mutation UpdateCategoricalDistributionValidator($input: CategoricalDistributionValidatorUpdateInput!) {
              categoricalDistributionValidatorUpdate(input: $input) {
                ...ValidatorUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
            }

            fragment ValidatorUpdate on ValidatorUpdateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateCategoricalDistributionValidator.parse_obj(
            data
        ).categorical_distribution_validator_update

    async def update_channel_namespace(
        self, input: ResourceNamespaceUpdateInput
    ) -> UpdateChannelNamespaceChannelNamespaceUpdate:
        query = gql(
            """
            mutation UpdateChannelNamespace($input: ResourceNamespaceUpdateInput!) {
              channelNamespaceUpdate(input: $input) {
                ...NamespaceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment NamespaceUpdate on ResourceNamespaceUpdatedResult {
              errors {
                ...ErrorDetails
              }
              resourceName
              resourceNamespace
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateChannelNamespace.parse_obj(data).channel_namespace_update

    async def update_credential_namespace(
        self, input: ResourceNamespaceUpdateInput
    ) -> UpdateCredentialNamespaceCredentialNamespaceUpdate:
        query = gql(
            """
            mutation UpdateCredentialNamespace($input: ResourceNamespaceUpdateInput!) {
              credentialNamespaceUpdate(input: $input) {
                ...NamespaceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment NamespaceUpdate on ResourceNamespaceUpdatedResult {
              errors {
                ...ErrorDetails
              }
              resourceName
              resourceNamespace
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateCredentialNamespace.parse_obj(data).credential_namespace_update

    async def update_destination_namespace(
        self, input: ResourceNamespaceUpdateInput
    ) -> UpdateDestinationNamespaceDestinationNamespaceUpdate:
        query = gql(
            """
            mutation UpdateDestinationNamespace($input: ResourceNamespaceUpdateInput!) {
              destinationNamespaceUpdate(input: $input) {
                ...NamespaceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment NamespaceUpdate on ResourceNamespaceUpdatedResult {
              errors {
                ...ErrorDetails
              }
              resourceName
              resourceNamespace
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateDestinationNamespace.parse_obj(data).destination_namespace_update

    async def update_fixed_batch_window(
        self, input: FixedBatchWindowUpdateInput
    ) -> UpdateFixedBatchWindowFixedBatchWindowUpdate:
        query = gql(
            """
            mutation UpdateFixedBatchWindow($input: FixedBatchWindowUpdateInput!) {
              fixedBatchWindowUpdate(input: $input) {
                ...WindowUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment WindowDetails on Window {
              __typename
              id
              name
              source {
                id
                name
                resourceName
                resourceNamespace
              }
              dataTimeField
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on FixedBatchWindow {
                config {
                  batchSize
                  segmentedBatching
                  batchTimeoutSecs
                }
              }
              ... on SessionizedWindow {
                config {
                  timeout
                  timeoutUnit
                }
              }
              ... on TumblingWindow {
                config {
                  windowSize
                  timeUnit
                }
              }
            }

            fragment WindowUpdate on WindowUpdateResult {
              errors {
                ...ErrorDetails
              }
              window {
                ...WindowDetails
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateFixedBatchWindow.parse_obj(data).fixed_batch_window_update

    async def update_freshness_validator(
        self, input: FreshnessValidatorUpdateInput
    ) -> UpdateFreshnessValidatorFreshnessValidatorUpdate:
        query = gql(
            """
            mutation UpdateFreshnessValidator($input: FreshnessValidatorUpdateInput!) {
              freshnessValidatorUpdate(input: $input) {
                ...ValidatorUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
            }

            fragment ValidatorUpdate on ValidatorUpdateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateFreshnessValidator.parse_obj(data).freshness_validator_update

    async def update_gcp_big_query_destination(
        self, input: GcpBigQueryDestinationUpdateInput
    ) -> UpdateGcpBigQueryDestinationGcpBigQueryDestinationUpdate:
        query = gql(
            """
            mutation UpdateGcpBigQueryDestination($input: GcpBigQueryDestinationUpdateInput!) {
              gcpBigQueryDestinationUpdate(input: $input) {
                ...DestinationUpdate
              }
            }

            fragment DestinationDetails on Destination {
              __typename
              id
              name
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on GcpBigQueryDestination {
                config {
                  project
                  dataset
                  table
                }
              }
              ... on SnowflakeDestination {
                config {
                  database
                  schema
                  table
                  role
                  warehouse
                }
              }
              ... on AwsKinesisDestination {
                config {
                  region
                  streamName
                  endpoint
                }
              }
            }

            fragment DestinationUpdate on DestinationUpdateResult {
              errors {
                ...ErrorDetails
              }
              destination {
                ...DestinationDetails
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateGcpBigQueryDestination.parse_obj(
            data
        ).gcp_big_query_destination_update

    async def update_gcp_big_query_source(
        self, input: GcpBigQuerySourceUpdateInput
    ) -> UpdateGcpBigQuerySourceGcpBigQuerySourceUpdate:
        query = gql(
            """
            mutation UpdateGcpBigQuerySource($input: GcpBigQuerySourceUpdateInput!) {
              gcpBigQuerySourceUpdate(input: $input) {
                ...SourceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                }
              }
            }

            fragment SourceUpdate on SourceUpdateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateGcpBigQuerySource.parse_obj(data).gcp_big_query_source_update

    async def update_gcp_credential(
        self, input: GcpCredentialUpdateInput
    ) -> UpdateGcpCredentialGcpCredentialUpdate:
        query = gql(
            """
            mutation UpdateGcpCredential($input: GcpCredentialUpdateInput!) {
              gcpCredentialUpdate(input: $input) {
                ...CredentialUpdate
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
            }

            fragment CredentialUpdate on CredentialUpdateResult {
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateGcpCredential.parse_obj(data).gcp_credential_update

    async def update_gcp_pub_sub_lite_source(
        self, input: GcpPubSubLiteSourceUpdateInput
    ) -> UpdateGcpPubSubLiteSourceGcpPubSubLiteSourceUpdate:
        query = gql(
            """
            mutation UpdateGcpPubSubLiteSource($input: GcpPubSubLiteSourceUpdateInput!) {
              gcpPubSubLiteSourceUpdate(input: $input) {
                ...SourceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                }
              }
            }

            fragment SourceUpdate on SourceUpdateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateGcpPubSubLiteSource.parse_obj(data).gcp_pub_sub_lite_source_update

    async def update_gcp_pub_sub_source(
        self, input: GcpPubSubSourceUpdateInput
    ) -> UpdateGcpPubSubSourceGcpPubSubSourceUpdate:
        query = gql(
            """
            mutation UpdateGcpPubSubSource($input: GcpPubSubSourceUpdateInput!) {
              gcpPubSubSourceUpdate(input: $input) {
                ...SourceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                }
              }
            }

            fragment SourceUpdate on SourceUpdateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateGcpPubSubSource.parse_obj(data).gcp_pub_sub_source_update

    async def update_gcp_storage_source(
        self, input: GcpStorageSourceUpdateInput
    ) -> UpdateGcpStorageSourceGcpStorageSourceUpdate:
        query = gql(
            """
            mutation UpdateGcpStorageSource($input: GcpStorageSourceUpdateInput!) {
              gcpStorageSourceUpdate(input: $input) {
                ...SourceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                }
              }
            }

            fragment SourceUpdate on SourceUpdateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateGcpStorageSource.parse_obj(data).gcp_storage_source_update

    async def update_identity_provider_namespace(
        self, input: ResourceNamespaceUpdateInput
    ) -> UpdateIdentityProviderNamespaceIdentityProviderNamespaceUpdate:
        query = gql(
            """
            mutation UpdateIdentityProviderNamespace($input: ResourceNamespaceUpdateInput!) {
              identityProviderNamespaceUpdate(input: $input) {
                ...NamespaceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment NamespaceUpdate on ResourceNamespaceUpdatedResult {
              errors {
                ...ErrorDetails
              }
              resourceName
              resourceNamespace
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateIdentityProviderNamespace.parse_obj(
            data
        ).identity_provider_namespace_update

    async def update_kafka_sasl_ssl_plain_credential(
        self, input: KafkaSaslSslPlainCredentialUpdateInput
    ) -> UpdateKafkaSaslSslPlainCredentialKafkaSaslSslPlainCredentialUpdate:
        query = gql(
            """
            mutation UpdateKafkaSaslSslPlainCredential($input: KafkaSaslSslPlainCredentialUpdateInput!) {
              kafkaSaslSslPlainCredentialUpdate(input: $input) {
                ...CredentialUpdate
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
            }

            fragment CredentialUpdate on CredentialUpdateResult {
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateKafkaSaslSslPlainCredential.parse_obj(
            data
        ).kafka_sasl_ssl_plain_credential_update

    async def update_kafka_source(
        self, input: KafkaSourceUpdateInput
    ) -> UpdateKafkaSourceKafkaSourceUpdate:
        query = gql(
            """
            mutation UpdateKafkaSource($input: KafkaSourceUpdateInput!) {
              kafkaSourceUpdate(input: $input) {
                ...SourceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                }
              }
            }

            fragment SourceUpdate on SourceUpdateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateKafkaSource.parse_obj(data).kafka_source_update

    async def update_kafka_ssl_credential(
        self, input: KafkaSslCredentialUpdateInput
    ) -> UpdateKafkaSslCredentialKafkaSslCredentialUpdate:
        query = gql(
            """
            mutation UpdateKafkaSslCredential($input: KafkaSslCredentialUpdateInput!) {
              kafkaSslCredentialUpdate(input: $input) {
                ...CredentialUpdate
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
            }

            fragment CredentialUpdate on CredentialUpdateResult {
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateKafkaSslCredential.parse_obj(data).kafka_ssl_credential_update

    async def update_local_identity_provider(
        self, input: LocalIdentityProviderUpdateInput
    ) -> UpdateLocalIdentityProviderLocalIdentityProviderUpdate:
        query = gql(
            """
            mutation UpdateLocalIdentityProvider($input: LocalIdentityProviderUpdateInput!) {
              localIdentityProviderUpdate(input: $input) {
                ...IdentityProviderUpdate
              }
            }

            fragment IdentityProviderDetails on IdentityProvider {
              __typename
              id
              name
              disabled
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on SamlIdentityProvider {
                config {
                  entryPoint
                  entityId
                  cert
                }
              }
            }

            fragment IdentityProviderUpdate on IdentityProviderUpdateResult {
              errors {
                code
                message
              }
              identityProvider {
                ...IdentityProviderDetails
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateLocalIdentityProvider.parse_obj(
            data
        ).local_identity_provider_update

    async def update_notification_rule(
        self, input: NotificationRuleUpdateInput
    ) -> UpdateNotificationRuleNotificationRuleUpdate:
        query = gql(
            """
            mutation UpdateNotificationRule($input: NotificationRuleUpdateInput!) {
              notificationRuleUpdate(input: $input) {
                ...NotificationRuleUpdate
              }
            }

            fragment ChannelDetails on Channel {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on SlackChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
              ... on WebhookChannel {
                config {
                  webhookUrl
                  applicationLinkUrl
                  authHeader
                }
              }
            }

            fragment NotificationRuleDetails on NotificationRule {
              __typename
              id
              name
              notificationTypenames
              createdAt
              updatedAt
              sources
              channel {
                ...ChannelDetails
              }
              resourceName
              resourceNamespace
            }

            fragment NotificationRuleUpdate on NotificationRuleUpdateResult {
              errors {
                code
                message
              }
              notificationRule {
                ...NotificationRuleDetails
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateNotificationRule.parse_obj(data).notification_rule_update

    async def update_notification_rule_namespace(
        self, input: ResourceNamespaceUpdateInput
    ) -> UpdateNotificationRuleNamespaceNotificationRuleNamespaceUpdate:
        query = gql(
            """
            mutation UpdateNotificationRuleNamespace($input: ResourceNamespaceUpdateInput!) {
              notificationRuleNamespaceUpdate(input: $input) {
                ...NamespaceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment NamespaceUpdate on ResourceNamespaceUpdatedResult {
              errors {
                ...ErrorDetails
              }
              resourceName
              resourceNamespace
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateNotificationRuleNamespace.parse_obj(
            data
        ).notification_rule_namespace_update

    async def update_numeric_anomaly_validator(
        self, input: NumericAnomalyValidatorUpdateInput
    ) -> UpdateNumericAnomalyValidatorNumericAnomalyValidatorUpdate:
        query = gql(
            """
            mutation UpdateNumericAnomalyValidator($input: NumericAnomalyValidatorUpdateInput!) {
              numericAnomalyValidatorUpdate(input: $input) {
                ...ValidatorUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
            }

            fragment ValidatorUpdate on ValidatorUpdateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateNumericAnomalyValidator.parse_obj(
            data
        ).numeric_anomaly_validator_update

    async def update_numeric_distribution_validator(
        self, input: NumericDistributionValidatorUpdateInput
    ) -> UpdateNumericDistributionValidatorNumericDistributionValidatorUpdate:
        query = gql(
            """
            mutation UpdateNumericDistributionValidator($input: NumericDistributionValidatorUpdateInput!) {
              numericDistributionValidatorUpdate(input: $input) {
                ...ValidatorUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
            }

            fragment ValidatorUpdate on ValidatorUpdateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateNumericDistributionValidator.parse_obj(
            data
        ).numeric_distribution_validator_update

    async def update_numeric_validator(
        self, input: NumericValidatorUpdateInput
    ) -> UpdateNumericValidatorNumericValidatorUpdate:
        query = gql(
            """
            mutation UpdateNumericValidator($input: NumericValidatorUpdateInput!) {
              numericValidatorUpdate(input: $input) {
                ...ValidatorUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
            }

            fragment ValidatorUpdate on ValidatorUpdateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateNumericValidator.parse_obj(data).numeric_validator_update

    async def update_postgre_sql_credential(
        self, input: PostgreSqlCredentialUpdateInput
    ) -> UpdatePostgreSqlCredentialPostgreSqlCredentialUpdate:
        query = gql(
            """
            mutation UpdatePostgreSqlCredential($input: PostgreSqlCredentialUpdateInput!) {
              postgreSqlCredentialUpdate(input: $input) {
                ...CredentialUpdate
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
            }

            fragment CredentialUpdate on CredentialUpdateResult {
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdatePostgreSqlCredential.parse_obj(data).postgre_sql_credential_update

    async def update_postgre_sql_source(
        self, input: PostgreSqlSourceUpdateInput
    ) -> UpdatePostgreSqlSourcePostgreSqlSourceUpdate:
        query = gql(
            """
            mutation UpdatePostgreSqlSource($input: PostgreSqlSourceUpdateInput!) {
              postgreSqlSourceUpdate(input: $input) {
                ...SourceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                }
              }
            }

            fragment SourceUpdate on SourceUpdateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdatePostgreSqlSource.parse_obj(data).postgre_sql_source_update

    async def update_relative_time_validator(
        self, input: RelativeTimeValidatorUpdateInput
    ) -> UpdateRelativeTimeValidatorRelativeTimeValidatorUpdate:
        query = gql(
            """
            mutation UpdateRelativeTimeValidator($input: RelativeTimeValidatorUpdateInput!) {
              relativeTimeValidatorUpdate(input: $input) {
                ...ValidatorUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
            }

            fragment ValidatorUpdate on ValidatorUpdateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateRelativeTimeValidator.parse_obj(
            data
        ).relative_time_validator_update

    async def update_relative_volume_validator(
        self, input: RelativeVolumeValidatorUpdateInput
    ) -> UpdateRelativeVolumeValidatorRelativeVolumeValidatorUpdate:
        query = gql(
            """
            mutation UpdateRelativeVolumeValidator($input: RelativeVolumeValidatorUpdateInput!) {
              relativeVolumeValidatorUpdate(input: $input) {
                ...ValidatorUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
            }

            fragment ValidatorUpdate on ValidatorUpdateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateRelativeVolumeValidator.parse_obj(
            data
        ).relative_volume_validator_update

    async def update_saml_identity_provider(
        self, input: SamlIdentityProviderUpdateInput
    ) -> UpdateSamlIdentityProviderSamlIdentityProviderUpdate:
        query = gql(
            """
            mutation UpdateSamlIdentityProvider($input: SamlIdentityProviderUpdateInput!) {
              samlIdentityProviderUpdate(input: $input) {
                ...IdentityProviderUpdate
              }
            }

            fragment IdentityProviderDetails on IdentityProvider {
              __typename
              id
              name
              disabled
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on SamlIdentityProvider {
                config {
                  entryPoint
                  entityId
                  cert
                }
              }
            }

            fragment IdentityProviderUpdate on IdentityProviderUpdateResult {
              errors {
                code
                message
              }
              identityProvider {
                ...IdentityProviderDetails
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateSamlIdentityProvider.parse_obj(data).saml_identity_provider_update

    async def update_segmentation_namespace(
        self, input: ResourceNamespaceUpdateInput
    ) -> UpdateSegmentationNamespaceSegmentationNamespaceUpdate:
        query = gql(
            """
            mutation UpdateSegmentationNamespace($input: ResourceNamespaceUpdateInput!) {
              segmentationNamespaceUpdate(input: $input) {
                ...NamespaceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment NamespaceUpdate on ResourceNamespaceUpdatedResult {
              errors {
                ...ErrorDetails
              }
              resourceName
              resourceNamespace
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateSegmentationNamespace.parse_obj(data).segmentation_namespace_update

    async def update_sessionized_window(
        self, input: SessionizedWindowUpdateInput
    ) -> UpdateSessionizedWindowSessionizedWindowUpdate:
        query = gql(
            """
            mutation UpdateSessionizedWindow($input: SessionizedWindowUpdateInput!) {
              sessionizedWindowUpdate(input: $input) {
                ...WindowUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment WindowDetails on Window {
              __typename
              id
              name
              source {
                id
                name
                resourceName
                resourceNamespace
              }
              dataTimeField
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on FixedBatchWindow {
                config {
                  batchSize
                  segmentedBatching
                  batchTimeoutSecs
                }
              }
              ... on SessionizedWindow {
                config {
                  timeout
                  timeoutUnit
                }
              }
              ... on TumblingWindow {
                config {
                  windowSize
                  timeUnit
                }
              }
            }

            fragment WindowUpdate on WindowUpdateResult {
              errors {
                ...ErrorDetails
              }
              window {
                ...WindowDetails
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateSessionizedWindow.parse_obj(data).sessionized_window_update

    async def update_slack_channel(
        self, input: SlackChannelUpdateInput
    ) -> UpdateSlackChannelSlackChannelUpdate:
        query = gql(
            """
            mutation UpdateSlackChannel($input: SlackChannelUpdateInput!) {
              slackChannelUpdate(input: $input) {
                ...ChannelUpdate
              }
            }

            fragment ChannelDetails on Channel {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on SlackChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
              ... on WebhookChannel {
                config {
                  webhookUrl
                  applicationLinkUrl
                  authHeader
                }
              }
            }

            fragment ChannelUpdate on ChannelUpdateResult {
              errors {
                code
                message
              }
              channel {
                ...ChannelDetails
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateSlackChannel.parse_obj(data).slack_channel_update

    async def update_snowflake_credential(
        self, input: SnowflakeCredentialUpdateInput
    ) -> UpdateSnowflakeCredentialSnowflakeCredentialUpdate:
        query = gql(
            """
            mutation UpdateSnowflakeCredential($input: SnowflakeCredentialUpdateInput!) {
              snowflakeCredentialUpdate(input: $input) {
                ...CredentialUpdate
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
            }

            fragment CredentialUpdate on CredentialUpdateResult {
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateSnowflakeCredential.parse_obj(data).snowflake_credential_update

    async def update_snowflake_destination(
        self, input: SnowflakeDestinationUpdateInput
    ) -> UpdateSnowflakeDestinationSnowflakeDestinationUpdate:
        query = gql(
            """
            mutation UpdateSnowflakeDestination($input: SnowflakeDestinationUpdateInput!) {
              snowflakeDestinationUpdate(input: $input) {
                ...DestinationUpdate
              }
            }

            fragment DestinationDetails on Destination {
              __typename
              id
              name
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on GcpBigQueryDestination {
                config {
                  project
                  dataset
                  table
                }
              }
              ... on SnowflakeDestination {
                config {
                  database
                  schema
                  table
                  role
                  warehouse
                }
              }
              ... on AwsKinesisDestination {
                config {
                  region
                  streamName
                  endpoint
                }
              }
            }

            fragment DestinationUpdate on DestinationUpdateResult {
              errors {
                ...ErrorDetails
              }
              destination {
                ...DestinationDetails
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateSnowflakeDestination.parse_obj(data).snowflake_destination_update

    async def update_snowflake_source(
        self, input: SnowflakeSourceUpdateInput
    ) -> UpdateSnowflakeSourceSnowflakeSourceUpdate:
        query = gql(
            """
            mutation UpdateSnowflakeSource($input: SnowflakeSourceUpdateInput!) {
              snowflakeSourceUpdate(input: $input) {
                ...SourceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                }
              }
            }

            fragment SourceUpdate on SourceUpdateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateSnowflakeSource.parse_obj(data).snowflake_source_update

    async def update_source_namespace(
        self, input: ResourceNamespaceUpdateInput
    ) -> UpdateSourceNamespaceSourceNamespaceUpdate:
        query = gql(
            """
            mutation UpdateSourceNamespace($input: ResourceNamespaceUpdateInput!) {
              sourceNamespaceUpdate(input: $input) {
                ...NamespaceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment NamespaceUpdate on ResourceNamespaceUpdatedResult {
              errors {
                ...ErrorDetails
              }
              resourceName
              resourceNamespace
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateSourceNamespace.parse_obj(data).source_namespace_update

    async def update_tumbling_window(
        self, input: TumblingWindowUpdateInput
    ) -> UpdateTumblingWindowTumblingWindowUpdate:
        query = gql(
            """
            mutation UpdateTumblingWindow($input: TumblingWindowUpdateInput!) {
              tumblingWindowUpdate(input: $input) {
                ...WindowUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment WindowDetails on Window {
              __typename
              id
              name
              source {
                id
                name
                resourceName
                resourceNamespace
              }
              dataTimeField
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on FixedBatchWindow {
                config {
                  batchSize
                  segmentedBatching
                  batchTimeoutSecs
                }
              }
              ... on SessionizedWindow {
                config {
                  timeout
                  timeoutUnit
                }
              }
              ... on TumblingWindow {
                config {
                  windowSize
                  timeUnit
                }
              }
            }

            fragment WindowUpdate on WindowUpdateResult {
              errors {
                ...ErrorDetails
              }
              window {
                ...WindowDetails
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateTumblingWindow.parse_obj(data).tumbling_window_update

    async def update_user(self, input: UserUpdateInput) -> UpdateUserUserUpdate:
        query = gql(
            """
            mutation UpdateUser($input: UserUpdateInput!) {
              userUpdate(input: $input) {
                ...UserUpdate
              }
            }

            fragment IdentityDetails on Identity {
              ... on LocalIdentity {
                __typename
                id
                userId
                username
                createdAt
              }
              ... on FederatedIdentity {
                __typename
                id
                userId
                idp {
                  __typename
                  id
                  name
                }
                createdAt
              }
            }

            fragment UserDetails on User {
              id
              displayName
              fullName
              email
              role
              status
              identities {
                ...IdentityDetails
              }
              createdAt
              updatedAt
              resourceName
              resourceNamespace
            }

            fragment UserUpdate on UserUpdateResult {
              errors {
                code
                message
              }
              user {
                ...UserDetails
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateUser.parse_obj(data).user_update

    async def update_user_namespace(
        self, input: ResourceNamespaceUpdateInput
    ) -> UpdateUserNamespaceUserNamespaceUpdate:
        query = gql(
            """
            mutation UpdateUserNamespace($input: ResourceNamespaceUpdateInput!) {
              userNamespaceUpdate(input: $input) {
                ...NamespaceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment NamespaceUpdate on ResourceNamespaceUpdatedResult {
              errors {
                ...ErrorDetails
              }
              resourceName
              resourceNamespace
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateUserNamespace.parse_obj(data).user_namespace_update

    async def update_validator_namespace(
        self, input: ResourceNamespaceUpdateInput
    ) -> UpdateValidatorNamespaceValidatorNamespaceUpdate:
        query = gql(
            """
            mutation UpdateValidatorNamespace($input: ResourceNamespaceUpdateInput!) {
              validatorNamespaceUpdate(input: $input) {
                ...NamespaceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment NamespaceUpdate on ResourceNamespaceUpdatedResult {
              errors {
                ...ErrorDetails
              }
              resourceName
              resourceNamespace
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateValidatorNamespace.parse_obj(data).validator_namespace_update

    async def update_validator_with_dynamic_threshold(
        self, input: ValidatorWithDynamicThresholdUpdateInput
    ) -> UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdate:
        query = gql(
            """
            mutation UpdateValidatorWithDynamicThreshold($input: ValidatorWithDynamicThresholdUpdateInput!) {
              validatorWithDynamicThresholdUpdate(input: $input) {
                errors {
                  ...ErrorDetails
                }
                validator {
                  ...ValidatorDetails
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateValidatorWithDynamicThreshold.parse_obj(
            data
        ).validator_with_dynamic_threshold_update

    async def update_validator_with_fixed_threshold(
        self, input: ValidatorWithFixedThresholdUpdateInput
    ) -> UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdate:
        query = gql(
            """
            mutation UpdateValidatorWithFixedThreshold($input: ValidatorWithFixedThresholdUpdateInput!) {
              validatorWithFixedThresholdUpdate(input: $input) {
                errors {
                  ...ErrorDetails
                }
                validator {
                  ...ValidatorDetails
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateValidatorWithFixedThreshold.parse_obj(
            data
        ).validator_with_fixed_threshold_update

    async def update_volume_validator(
        self, input: VolumeValidatorUpdateInput
    ) -> UpdateVolumeValidatorVolumeValidatorUpdate:
        query = gql(
            """
            mutation UpdateVolumeValidator($input: VolumeValidatorUpdateInput!) {
              volumeValidatorUpdate(input: $input) {
                ...ValidatorUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
                destination {
                  name
                  id
                  resourceName
                  resourceNamespace
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
            }

            fragment ValidatorUpdate on ValidatorUpdateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateVolumeValidator.parse_obj(data).volume_validator_update

    async def update_webhook_channel(
        self, input: WebhookChannelUpdateInput
    ) -> UpdateWebhookChannelWebhookChannelUpdate:
        query = gql(
            """
            mutation UpdateWebhookChannel($input: WebhookChannelUpdateInput!) {
              webhookChannelUpdate(input: $input) {
                ...ChannelUpdate
              }
            }

            fragment ChannelDetails on Channel {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on SlackChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
              ... on WebhookChannel {
                config {
                  webhookUrl
                  applicationLinkUrl
                  authHeader
                }
              }
            }

            fragment ChannelUpdate on ChannelUpdateResult {
              errors {
                code
                message
              }
              channel {
                ...ChannelDetails
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateWebhookChannel.parse_obj(data).webhook_channel_update

    async def update_window_namespace(
        self, input: ResourceNamespaceUpdateInput
    ) -> UpdateWindowNamespaceWindowNamespaceUpdate:
        query = gql(
            """
            mutation UpdateWindowNamespace($input: ResourceNamespaceUpdateInput!) {
              windowNamespaceUpdate(input: $input) {
                ...NamespaceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment NamespaceUpdate on ResourceNamespaceUpdatedResult {
              errors {
                ...ErrorDetails
              }
              resourceName
              resourceNamespace
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateWindowNamespace.parse_obj(data).window_namespace_update
