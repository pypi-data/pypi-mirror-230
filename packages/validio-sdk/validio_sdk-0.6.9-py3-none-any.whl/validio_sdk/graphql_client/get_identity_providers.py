from datetime import datetime
from typing import Annotated, List, Literal, Optional, Union

from pydantic import Field

from .base_model import BaseModel


class GetIdentityProviders(BaseModel):
    identity_providers: Optional[
        List[
            Optional[
                Annotated[
                    Union[
                        "GetIdentityProvidersIdentityProvidersIdentityProvider",
                        "GetIdentityProvidersIdentityProvidersSamlIdentityProvider",
                    ],
                    Field(discriminator="typename__"),
                ]
            ]
        ]
    ] = Field(alias="identityProviders")


class GetIdentityProvidersIdentityProvidersIdentityProvider(BaseModel):
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


class GetIdentityProvidersIdentityProvidersSamlIdentityProvider(BaseModel):
    typename__: Literal["SamlIdentityProvider"] = Field(alias="__typename")
    id: str
    name: str
    disabled: bool
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetIdentityProvidersIdentityProvidersSamlIdentityProviderConfig"


class GetIdentityProvidersIdentityProvidersSamlIdentityProviderConfig(BaseModel):
    entry_point: str = Field(alias="entryPoint")
    entity_id: str = Field(alias="entityId")
    cert: str


GetIdentityProviders.update_forward_refs()
GetIdentityProvidersIdentityProvidersIdentityProvider.update_forward_refs()
GetIdentityProvidersIdentityProvidersSamlIdentityProvider.update_forward_refs()
GetIdentityProvidersIdentityProvidersSamlIdentityProviderConfig.update_forward_refs()
