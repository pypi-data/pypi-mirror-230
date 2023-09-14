from datetime import datetime
from typing import List, Literal, Union

from pydantic import Field

from .base_model import BaseModel


class GetValidatorMetricDebugInfo(BaseModel):
    validator_metric_debug_info: Union[
        "GetValidatorMetricDebugInfoValidatorMetricDebugInfoValidatorMetricDebugInfo",
        "GetValidatorMetricDebugInfoValidatorMetricDebugInfoGcpBigQuerySourceDebugInfo",
        "GetValidatorMetricDebugInfoValidatorMetricDebugInfoGcpStorageSourceDebugInfo",
        "GetValidatorMetricDebugInfoValidatorMetricDebugInfoAwsS3SourceDebugInfo",
        "GetValidatorMetricDebugInfoValidatorMetricDebugInfoAwsRedShiftSourceDebugInfo",
        "GetValidatorMetricDebugInfoValidatorMetricDebugInfoAwsAthenaSourceDebugInfo",
        "GetValidatorMetricDebugInfoValidatorMetricDebugInfoSnowflakeSourceDebugInfo",
        "GetValidatorMetricDebugInfoValidatorMetricDebugInfoPostgreSQLSourceDebugInfo",
    ] = Field(alias="validatorMetricDebugInfo", discriminator="typename__")


class GetValidatorMetricDebugInfoValidatorMetricDebugInfoValidatorMetricDebugInfo(
    BaseModel
):
    typename__: Literal["ValidatorMetricDebugInfo"] = Field(alias="__typename")
    start_time: datetime = Field(alias="startTime")
    end_time: datetime = Field(alias="endTime")


class GetValidatorMetricDebugInfoValidatorMetricDebugInfoGcpBigQuerySourceDebugInfo(
    BaseModel
):
    typename__: Literal["GcpBigQuerySourceDebugInfo"] = Field(alias="__typename")
    start_time: datetime = Field(alias="startTime")
    end_time: datetime = Field(alias="endTime")
    sql_query: str = Field(alias="sqlQuery")


class GetValidatorMetricDebugInfoValidatorMetricDebugInfoGcpStorageSourceDebugInfo(
    BaseModel
):
    typename__: Literal["GcpStorageSourceDebugInfo"] = Field(alias="__typename")
    start_time: datetime = Field(alias="startTime")
    end_time: datetime = Field(alias="endTime")
    bucket: str
    file_path: List[str] = Field(alias="filePath")


class GetValidatorMetricDebugInfoValidatorMetricDebugInfoAwsS3SourceDebugInfo(
    BaseModel
):
    typename__: Literal["AwsS3SourceDebugInfo"] = Field(alias="__typename")
    start_time: datetime = Field(alias="startTime")
    end_time: datetime = Field(alias="endTime")
    bucket: str
    file_path: List[str] = Field(alias="filePath")


class GetValidatorMetricDebugInfoValidatorMetricDebugInfoAwsRedShiftSourceDebugInfo(
    BaseModel
):
    typename__: Literal["AwsRedShiftSourceDebugInfo"] = Field(alias="__typename")
    start_time: datetime = Field(alias="startTime")
    end_time: datetime = Field(alias="endTime")
    sql_query: str = Field(alias="sqlQuery")


class GetValidatorMetricDebugInfoValidatorMetricDebugInfoAwsAthenaSourceDebugInfo(
    BaseModel
):
    typename__: Literal["AwsAthenaSourceDebugInfo"] = Field(alias="__typename")
    start_time: datetime = Field(alias="startTime")
    end_time: datetime = Field(alias="endTime")
    sql_query: str = Field(alias="sqlQuery")


class GetValidatorMetricDebugInfoValidatorMetricDebugInfoSnowflakeSourceDebugInfo(
    BaseModel
):
    typename__: Literal["SnowflakeSourceDebugInfo"] = Field(alias="__typename")
    start_time: datetime = Field(alias="startTime")
    end_time: datetime = Field(alias="endTime")
    sql_query: str = Field(alias="sqlQuery")


class GetValidatorMetricDebugInfoValidatorMetricDebugInfoPostgreSQLSourceDebugInfo(
    BaseModel
):
    typename__: Literal["PostgreSQLSourceDebugInfo"] = Field(alias="__typename")
    start_time: datetime = Field(alias="startTime")
    end_time: datetime = Field(alias="endTime")
    sql_query: str = Field(alias="sqlQuery")


GetValidatorMetricDebugInfo.update_forward_refs()
GetValidatorMetricDebugInfoValidatorMetricDebugInfoValidatorMetricDebugInfo.update_forward_refs()
GetValidatorMetricDebugInfoValidatorMetricDebugInfoGcpBigQuerySourceDebugInfo.update_forward_refs()
GetValidatorMetricDebugInfoValidatorMetricDebugInfoGcpStorageSourceDebugInfo.update_forward_refs()
GetValidatorMetricDebugInfoValidatorMetricDebugInfoAwsS3SourceDebugInfo.update_forward_refs()
GetValidatorMetricDebugInfoValidatorMetricDebugInfoAwsRedShiftSourceDebugInfo.update_forward_refs()
GetValidatorMetricDebugInfoValidatorMetricDebugInfoAwsAthenaSourceDebugInfo.update_forward_refs()
GetValidatorMetricDebugInfoValidatorMetricDebugInfoSnowflakeSourceDebugInfo.update_forward_refs()
GetValidatorMetricDebugInfoValidatorMetricDebugInfoPostgreSQLSourceDebugInfo.update_forward_refs()
