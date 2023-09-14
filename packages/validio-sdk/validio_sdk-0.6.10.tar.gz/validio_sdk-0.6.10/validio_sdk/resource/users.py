"""User configuration."""
from typing import TYPE_CHECKING, Any

from validio_sdk.graphql_client import UserDeleteInput
from validio_sdk.graphql_client.enums import Role, UserStatus
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


class User(Resource):
    """
    Base class for a user resource.

    https://docs.validio.io/docs/settings#users-1
    """

    def __init__(
        self,
        name: str,
        role: Role,
        display_name: str,
        email: str,
        username: str | None = None,
        password: str | None = None,
        full_name: str | None = "",
        status: UserStatus = UserStatus.ACTIVE,
        __internal__=None,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the user
        :param username: Username. If unspecified, a name is auto generated and
            sent to the user's email address
        :param password: Password for the user. If unspecified a password is
            auto generated and sent to the user's email address
        :param display_name: Display name for the user
        :param email: Email address for the user.
        :param role: Specify which role and access privileges the
            user should be assigned:
        :param full_name: Full name of the user
        :param status: Account status of the user.
        :param __internal__: Should be left ignored. This is for internal usage only.
        """
        # Users are at the root sub-graphs.
        g: ResourceGraph = __internal__ or RESOURCE_GRAPH
        super().__init__(name, g)

        self._resource_graph: ResourceGraph = g
        self._resource_graph._add_root(self)

        self.display_name = display_name
        self.email = email
        self.full_name = full_name
        self.username = username
        self.password = password
        self.role: Role = (
            # When we decode, enums are passed in a strings
            role
            if isinstance(role, Role)
            else Role(role)
        )
        self.status: UserStatus = (
            # When we decode, enums are passed in a strings
            status
            if isinstance(status, UserStatus)
            else UserStatus(status)
        )

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {
            "display_name",
            "email",
            "full_name",
            "username",
            "password",
            "role",
            "status",
        }

    def _secret_fields(self) -> set[str] | None:
        return {self.password} if self.password else None

    def resource_class_name(self) -> str:
        """Returns the base class name."""
        return "User"

    def _encode(self) -> dict[str, object]:
        return _encode_resource(self)

    @staticmethod
    def _decode(
        _ctx: "DiffContext",
        cls: type,
        obj: dict[str, dict[str, object]],
        g: ResourceGraph,
    ) -> "User":
        return cls(**with_resource_graph_info(obj[CONFIG_FIELD_NAME], g))

    async def _api_delete(self, client: ValidioAPIClient) -> Any:
        """User api is different from other resources for some reason."""
        response = await client.delete_user(UserDeleteInput(id=self._must_id()))
        return self._check_graphql_response(
            response=response,
            method_name="delete_user",
            response_field=None,
        )
