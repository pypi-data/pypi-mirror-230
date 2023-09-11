from datetime import datetime
from typing import Annotated, Literal, Optional, Union

from pydantic import Field

from validio_sdk.scalars import JsonPointer, SourceId, WindowId

from .base_model import BaseModel
from .enums import WindowTimeUnit


class GetWindowByResourceName(BaseModel):
    window_by_resource_name: Optional[
        Annotated[
            Union[
                "GetWindowByResourceNameWindowByResourceNameWindow",
                "GetWindowByResourceNameWindowByResourceNameFixedBatchWindow",
                "GetWindowByResourceNameWindowByResourceNameSessionizedWindow",
                "GetWindowByResourceNameWindowByResourceNameTumblingWindow",
            ],
            Field(discriminator="typename__"),
        ]
    ] = Field(alias="windowByResourceName")


class GetWindowByResourceNameWindowByResourceNameWindow(BaseModel):
    typename__: Literal["FileWindow", "Window"] = Field(alias="__typename")
    id: WindowId
    name: str
    source: "GetWindowByResourceNameWindowByResourceNameWindowSource"
    data_time_field: JsonPointer = Field(alias="dataTimeField")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetWindowByResourceNameWindowByResourceNameWindowSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetWindowByResourceNameWindowByResourceNameFixedBatchWindow(BaseModel):
    typename__: Literal["FixedBatchWindow"] = Field(alias="__typename")
    id: WindowId
    name: str
    source: "GetWindowByResourceNameWindowByResourceNameFixedBatchWindowSource"
    data_time_field: JsonPointer = Field(alias="dataTimeField")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetWindowByResourceNameWindowByResourceNameFixedBatchWindowConfig"


class GetWindowByResourceNameWindowByResourceNameFixedBatchWindowSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetWindowByResourceNameWindowByResourceNameFixedBatchWindowConfig(BaseModel):
    batch_size: int = Field(alias="batchSize")
    segmented_batching: bool = Field(alias="segmentedBatching")
    batch_timeout_secs: Optional[int] = Field(alias="batchTimeoutSecs")


class GetWindowByResourceNameWindowByResourceNameSessionizedWindow(BaseModel):
    typename__: Literal["SessionizedWindow"] = Field(alias="__typename")
    id: WindowId
    name: str
    source: "GetWindowByResourceNameWindowByResourceNameSessionizedWindowSource"
    data_time_field: JsonPointer = Field(alias="dataTimeField")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetWindowByResourceNameWindowByResourceNameSessionizedWindowConfig"


class GetWindowByResourceNameWindowByResourceNameSessionizedWindowSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetWindowByResourceNameWindowByResourceNameSessionizedWindowConfig(BaseModel):
    timeout: int
    timeout_unit: WindowTimeUnit = Field(alias="timeoutUnit")


class GetWindowByResourceNameWindowByResourceNameTumblingWindow(BaseModel):
    typename__: Literal["TumblingWindow"] = Field(alias="__typename")
    id: WindowId
    name: str
    source: "GetWindowByResourceNameWindowByResourceNameTumblingWindowSource"
    data_time_field: JsonPointer = Field(alias="dataTimeField")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetWindowByResourceNameWindowByResourceNameTumblingWindowConfig"


class GetWindowByResourceNameWindowByResourceNameTumblingWindowSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetWindowByResourceNameWindowByResourceNameTumblingWindowConfig(BaseModel):
    window_size: int = Field(alias="windowSize")
    time_unit: WindowTimeUnit = Field(alias="timeUnit")


GetWindowByResourceName.update_forward_refs()
GetWindowByResourceNameWindowByResourceNameWindow.update_forward_refs()
GetWindowByResourceNameWindowByResourceNameWindowSource.update_forward_refs()
GetWindowByResourceNameWindowByResourceNameFixedBatchWindow.update_forward_refs()
GetWindowByResourceNameWindowByResourceNameFixedBatchWindowSource.update_forward_refs()
GetWindowByResourceNameWindowByResourceNameFixedBatchWindowConfig.update_forward_refs()
GetWindowByResourceNameWindowByResourceNameSessionizedWindow.update_forward_refs()
GetWindowByResourceNameWindowByResourceNameSessionizedWindowSource.update_forward_refs()
GetWindowByResourceNameWindowByResourceNameSessionizedWindowConfig.update_forward_refs()
GetWindowByResourceNameWindowByResourceNameTumblingWindow.update_forward_refs()
GetWindowByResourceNameWindowByResourceNameTumblingWindowSource.update_forward_refs()
GetWindowByResourceNameWindowByResourceNameTumblingWindowConfig.update_forward_refs()
