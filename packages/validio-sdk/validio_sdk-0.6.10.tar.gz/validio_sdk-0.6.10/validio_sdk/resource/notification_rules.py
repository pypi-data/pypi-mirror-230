"""Notification rule configuration."""
from typing import TYPE_CHECKING, Any

from validio_sdk.graphql_client import (
    NotificationRuleDeleteInput,
    NotificationTypename,
)
from validio_sdk.resource._resource import Resource
from validio_sdk.resource._serde import (
    CONFIG_FIELD_NAME,
    _api_create_input_params,
    _api_update_input_params,
    _encode_resource,
)
from validio_sdk.resource.channels import Channel
from validio_sdk.resource.sources import Source
from validio_sdk.validio_client import ValidioAPIClient

if TYPE_CHECKING:
    from validio_sdk.resource._diff import DiffContext


class NotificationRule(Resource):
    """
    A notification rule.

    https://docs.validio.io/docs/notifications
    """

    def __init__(
        self,
        name: str,
        channel: Channel,
        sources: list[Source] | None = None,
        notification_typenames: list[NotificationTypename] | None = None,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the window
        :param channel: The channel to attach the rule to
        :param sources: An optional list of sources to apply the rule onto.
            If none is provided, then the rule is applied to all sources.
        :param notification_typenames: The types of notifications that this
            rule applies to. If none is provided, then the rule applies to
            all notification types.
        """
        super().__init__(name, channel._resource_graph)
        self.channel_name = channel.name

        # We turn the names into a set and back to list as a means
        # to dedupe the names.
        self.source_names = list(
            {source.name for source in sources} if sources is not None else {}
        )

        typenames = (
            [
                n if isinstance(n, NotificationTypename) else NotificationTypename(n)
                for n in notification_typenames
            ]
            if notification_typenames is not None
            else []
        )
        self.notification_typenames = list(set(typenames))

        # Sort so that we can compare two lists when we look for diffs.
        self.source_names.sort()
        self.notification_typenames.sort()

        channel.add(name, self)

    def _immutable_fields(self) -> set[str]:
        return {"channel_name"}

    def _mutable_fields(self) -> set[str]:
        return {"source_names", "notification_typenames"}

    def resource_class_name(self) -> str:
        """Returns the base class name."""
        return "NotificationRule"

    def _api_create_response_field_name(self) -> str:
        return "notification_rule"

    def _api_create_input(self, namespace: str, ctx: "DiffContext") -> Any:
        return _api_create_input_params(
            self,
            namespace=namespace,
            overrides={
                "channel_id": ctx.channels[self.channel_name]._must_id(),
                "sources": self._extract_source_ids_from_ctx(ctx),
            },
        )

    def _api_update_input(self, _namespace: str, ctx: "DiffContext") -> Any:
        return _api_update_input_params(
            self,
            overrides={
                "sources": self._extract_source_ids_from_ctx(ctx),
            },
        )

    async def _api_delete(self, client: ValidioAPIClient) -> Any:
        response = await client.delete_notification_rule(
            NotificationRuleDeleteInput(id=self._must_id())
        )
        return self._check_graphql_response(
            response=response,
            method_name="delete_notification_rule",
            response_field=None,
        )

    def _extract_source_ids_from_ctx(self, ctx: "DiffContext") -> list[str]:
        ids = []
        for source_name in self.source_names:
            ids.append(ctx.sources[source_name]._must_id())

        return ids

    def _encode(self) -> dict[str, object]:
        # Drop fields here that are not part of the constructor for when
        # we deserialize back. They will be reinitialized by the constructor.
        return _encode_resource(self, skip_fields={"channel_name"})

    @staticmethod
    def _decode(
        ctx: "DiffContext", channel: Channel, obj: dict[str, Any]
    ) -> "NotificationRule":
        config_obj = obj[CONFIG_FIELD_NAME]
        sources = [
            ctx.sources[source_name] for source_name in config_obj["source_names"]
        ]
        obj = {
            # Drop fields that are not part of the constructor, we will
            # reinitialize them in the constructor.
            k: v
            for k, v in config_obj.items()
            if k not in {"source_names"}
        }

        return NotificationRule(
            **{
                **obj,
                "channel": channel,
                "sources": sources,
            }  # type: ignore
        )
