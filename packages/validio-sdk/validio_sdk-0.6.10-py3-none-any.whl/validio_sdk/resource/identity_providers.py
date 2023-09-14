"""Identity provider configuration."""
from abc import abstractmethod
from typing import TYPE_CHECKING, Any

from validio_sdk.graphql_client import IdentityProviderDeleteInput
from validio_sdk.resource._resource import Resource, ResourceGraph
from validio_sdk.resource._resource_graph import RESOURCE_GRAPH
from validio_sdk.resource._serde import (
    CONFIG_FIELD_NAME,
    _encode_resource,
    with_resource_graph_info,
)
from validio_sdk.validio_client import ValidioAPIClient

if TYPE_CHECKING:
    from validio_sdk.resource._diff import DiffContext


class IdentityProvider(Resource):
    """
    Base class for an identity provider resource.

    https://docs.validio.io/docs/settings#identity-providers
    """

    def __init__(self, name: str, __internal__=None):
        """
        Constructor.

        :param name: Unique resource name assigned to the identity provider
        :param __internal__: Should be left ignored. This is for internal usage only.
        """
        # Identity providers are at the root sub-graphs.
        g: ResourceGraph = __internal__ or RESOURCE_GRAPH
        super().__init__(name, g)

        self._resource_graph: ResourceGraph = g
        self._resource_graph._add_root(self)

    @abstractmethod
    def _immutable_fields(self) -> set[str]:
        pass

    @abstractmethod
    def _mutable_fields(self) -> set[str]:
        pass

    def resource_class_name(self) -> str:
        """Returns the base class name."""
        return "IdentityProvider"

    def _encode(self) -> dict[str, object]:
        return _encode_resource(self)

    @staticmethod
    def _decode(
        _ctx: "DiffContext",
        cls: type,
        obj: dict[str, dict[str, object]],
        g: ResourceGraph,
    ) -> "IdentityProvider":
        return cls(**with_resource_graph_info(obj[CONFIG_FIELD_NAME], g))

    async def _api_delete(self, client: ValidioAPIClient) -> Any:
        """IdentityProvider api is different from other resources for some reason."""
        response = await client.delete_identity_provider(
            IdentityProviderDeleteInput(id=self._must_id())
        )
        return self._check_graphql_response(
            response=response,
            method_name="delete_identity_provider",
            response_field=None,
        )


class SamlIdentityProvider(IdentityProvider):
    """
    Configuration to create a SAML 2.0 Identity Provider.

    https://docs.validio.io/docs/settings#identity-providers
    """

    def __init__(
        self,
        name: str,
        cert: str,
        entry_point: str,
        entity_id: str,
        disabled: bool = False,
        __internal__=None,
    ):
        """
        Constructor.

        :param cert: Certificate for the identity provider.
        :param entity_id: [Deployment instance URL]/saml2
        :param entry_point: SSO URL or Location URL for the configured
            identity provider.
        :param disabled: Disables the identity provider if set.
        """
        super().__init__(name, __internal__)
        self.cert = cert
        self.entry_point = entry_point
        self.entity_id = entity_id
        self.disabled = disabled

    def _mutable_fields(self) -> set[str]:
        return {"cert", "entry_point", "entity_id", "disabled"}

    def _immutable_fields(self) -> set[str]:
        return set({})
