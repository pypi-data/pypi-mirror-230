from typing import Any, cast

import pytest

from validio_sdk.graphql_client import (
    NumericDistributionMetric,
    NumericMetric,
    Role,
    UserStatus,
    WindowTimeUnit,
)
from validio_sdk.resource._diff import (
    DiffContext,
    GraphDiff,
    ResourceUpdate,
    ResourceUpdates,
    ResourceWithRepr,
    _diff_resource_graph,
)
from validio_sdk.resource._errors import ManifestConfigurationError
from validio_sdk.resource._resource import Resource, ResourceGraph
from validio_sdk.resource.channels import Channel, SlackChannel
from validio_sdk.resource.credentials import Credential, DemoCredential
from validio_sdk.resource.destinations import Destination, GcpBigQueryDestination
from validio_sdk.resource.filters import NullFilter
from validio_sdk.resource.identity_providers import (
    IdentityProvider,
    SamlIdentityProvider,
)
from validio_sdk.resource.notification_rules import NotificationRule
from validio_sdk.resource.segmentations import Segmentation
from validio_sdk.resource.sources import DemoSource, Source
from validio_sdk.resource.thresholds import DynamicThreshold
from validio_sdk.resource.users import User
from validio_sdk.resource.validators import (
    NumericDistributionValidator,
    NumericValidator,
    Reference,
    Validator,
)
from validio_sdk.resource.windows import TumblingWindow, Window


def _add_namespace(namespace: str, ctx: DiffContext):
    for f in DiffContext.fields():
        for r in getattr(ctx, f).values():
            r._namespace = namespace


def create_diff_context(
    identity_providers: dict[str, IdentityProvider] | None = None,
    users: dict[str, User] | None = None,
    credentials: dict[str, Credential] | None = None,
    channels: dict[str, Channel] | None = None,
    destinations: dict[str, Destination] | None = None,
    sources: dict[str, Source] | None = None,
    windows: dict[str, Window] | None = None,
    segmentations: dict[str, Segmentation] | None = None,
    validators: dict[str, Validator] | None = None,
    notification_rules: dict[str, NotificationRule] | None = None,
) -> DiffContext:
    return DiffContext(
        identity_providers=identity_providers or {},
        users=users or {},
        credentials=credentials or {},
        channels=channels or {},
        destinations=destinations or {},
        sources=sources or {},
        windows=windows or {},
        segmentations=segmentations or {},
        validators=validators or {},
        notification_rules=notification_rules or {},
    )


def create_resource_updates(
    identity_providers: dict[str, ResourceUpdate] | None = None,
    users: dict[str, ResourceUpdate] | None = None,
    credentials: dict[str, ResourceUpdate] | None = None,
    channels: dict[str, ResourceUpdate] | None = None,
    destinations: dict[str, ResourceUpdate] | None = None,
    sources: dict[str, ResourceUpdate] | None = None,
    windows: dict[str, ResourceUpdate] | None = None,
    segmentations: dict[str, ResourceUpdate] | None = None,
    validators: dict[str, ResourceUpdate] | None = None,
    notification_rules: dict[str, ResourceUpdate] | None = None,
) -> ResourceUpdates:
    return ResourceUpdates(
        identity_providers=identity_providers or {},
        users=users or {},
        credentials=credentials or {},
        channels=channels or {},
        destinations=destinations or {},
        sources=sources or {},
        windows=windows or {},
        segmentations=segmentations or {},
        validators=validators or {},
        notification_rules=notification_rules or {},
    )


def create_graph_diff(
    to_create: DiffContext | None = None,
    to_delete: DiffContext | None = None,
    to_update: ResourceUpdates | None = None,
) -> GraphDiff:
    return GraphDiff(
        to_create=to_create or DiffContext(),
        to_delete=to_delete or DiffContext(),
        to_update=to_update or create_resource_updates(),
    )


def collect_resource_config(manifest: Resource, server: Resource) -> ResourceUpdate:
    all_fields = manifest._all_fields()
    manifest_config = {f: getattr(manifest, f) for f in all_fields}
    server_config = {f: getattr(server, f) for f in all_fields}
    return ResourceUpdate(
        manifest=ResourceWithRepr(resource=manifest, repr=manifest_config),
        server=ResourceWithRepr(resource=server, repr=server_config),
    )


# ruff: noqa: PLR0915
def test_diff_should_detect_create_update_delete_operations_on_resources():
    namespace = "my_namespace"
    manifest_g = ResourceGraph()
    server_g = ResourceGraph()

    manifest_c1 = DemoCredential("c1", manifest_g)
    manifest_d1 = GcpBigQueryDestination("d1", cast(Any, manifest_c1), "a", "b", "c")
    manifest_d2 = GcpBigQueryDestination(
        "d2", cast(Any, manifest_c1), "e", "f", "g"
    )  # To be updated
    manifest_d3 = GcpBigQueryDestination(
        "d3", cast(Any, manifest_c1), "x", "y", "z"
    )  # To be created
    manifest_s1 = DemoSource("s1", manifest_c1)
    manifest_s2 = DemoSource("s2", manifest_c1)  # To be created
    manifest_seg1 = Segmentation("seg1", manifest_s1, ["city"])
    manifest_seg2 = Segmentation("seg2", manifest_s1, ["gender"])  # To be created
    manifest_w1 = TumblingWindow("w1", manifest_s1, "d", 1, WindowTimeUnit.DAY)
    manifest_w2 = TumblingWindow(
        "w2", manifest_s1, "d", 2, WindowTimeUnit.DAY
    )  # To be created
    manifest_w3 = TumblingWindow(
        "w3",
        manifest_s1,
        "d",
        3,
        WindowTimeUnit.DAY,
    )  # Update
    manifest_v1 = NumericValidator(
        "v1", manifest_w1, manifest_seg1, NumericMetric.MAX, "a"
    )
    manifest_v2 = NumericValidator(
        "v2",
        manifest_w1,
        manifest_seg1,
        NumericMetric.MEAN,
        "b",
    )  # To be created
    manifest_ch1 = SlackChannel("ch1", "app", "web", "tz", manifest_g)
    manifest_ch2 = SlackChannel("ch2", "app", "web", "tz", manifest_g)  # To be created
    manifest_ch3 = SlackChannel("ch3", "app", "web", None, manifest_g)  # To be updated
    manifest_r1 = NotificationRule("r1", manifest_ch1, [manifest_s1])
    manifest_r2 = NotificationRule("r2", manifest_ch1, [manifest_s1])  # To be created
    manifest_r3 = NotificationRule("r3", manifest_ch1, [manifest_s1])  # To be updated

    manifest_p1 = SamlIdentityProvider(
        "p1", "c", "e", "i", True, manifest_g
    )  # To be created
    manifest_p2 = SamlIdentityProvider(
        "p2", "c", "e", "i", True, manifest_g
    )  # To be updated

    manifest_u1 = User(
        "u1", Role.ADMIN, "d", "e", "u", "p", "f", UserStatus.ACTIVE, manifest_g
    )  # To be created
    manifest_u2 = User(
        "u2", Role.ADMIN, "d", "e", "u", "p", "f", UserStatus.ACTIVE, manifest_g
    )  # To be created

    server_c1 = DemoCredential("c1", server_g)
    server_d1 = GcpBigQueryDestination("d1", cast(Any, server_c1), "a", "b", "c")
    server_d2 = GcpBigQueryDestination("d2", cast(Any, server_c1), "d", "f", "g")
    server_d4 = GcpBigQueryDestination(
        "d4", cast(Any, server_c1), "x", "y", "z"
    )  # To be deleted
    server_s1 = DemoSource("s1", server_c1)
    server_s3 = DemoSource("s3", server_c1)  # To be deleted
    server_seg1 = Segmentation("seg1", server_s1, ["city"])
    server_seg3 = Segmentation("seg3", server_s1, ["country"])  # To be deleted
    server_w1 = TumblingWindow("w1", server_s1, "d", 1, WindowTimeUnit.DAY)
    server_w3 = TumblingWindow("w3", server_s1, "d", 4, WindowTimeUnit.DAY)
    server_w4 = TumblingWindow(
        "w4", server_s1, "d", 5, WindowTimeUnit.DAY
    )  # To be deleted
    server_v1 = NumericValidator("v1", server_w1, server_seg1, NumericMetric.MAX, "a")
    server_v3 = NumericValidator(
        "v3", server_w1, server_seg1, NumericMetric.MAX, "d"
    )  # Delete
    server_ch1 = SlackChannel("ch1", "app", "web", "tz", server_g)
    server_ch3 = SlackChannel("ch3", "app", "web", "tz", server_g)
    server_ch4 = SlackChannel("ch4", "app", "web", "tz", server_g)  # To be deleted
    server_r1 = NotificationRule("r1", server_ch1, [server_s1])
    server_r3 = NotificationRule("r3", server_ch1, [])
    server_r4 = NotificationRule("r4", server_ch1, [server_s1])  # To be deleted
    server_p3 = SamlIdentityProvider(
        "p3", "c", "e", "i", True, server_g
    )  # To be deleted
    server_p2 = SamlIdentityProvider("p2", "c", "e", "i", False, server_g)
    server_u3 = User(
        "u3", Role.ADMIN, "d", "e", "u", "p", "f", UserStatus.ACTIVE, server_g
    )  # To be deleted
    server_u2 = User(
        "u2", Role.GUEST, "d", "e", "u", "p", "f", UserStatus.ACTIVE, server_g
    )

    manifest_ctx = create_diff_context(
        credentials={manifest_c1.name: manifest_c1},
        destinations={
            manifest_d1.name: manifest_d1,
            manifest_d2.name: manifest_d2,
            manifest_d3.name: manifest_d3,
        },
        sources={
            manifest_s1.name: manifest_s1,
            manifest_s2.name: manifest_s2,
        },
        segmentations={
            manifest_seg1.name: manifest_seg1,
            manifest_seg2.name: manifest_seg2,
        },
        windows={
            manifest_w1.name: manifest_w1,
            manifest_w2.name: manifest_w2,
            manifest_w3.name: manifest_w3,
        },
        validators={
            manifest_v1.name: manifest_v1,
            manifest_v2.name: manifest_v2,
        },
        channels={
            manifest_ch1.name: manifest_ch1,
            manifest_ch2.name: manifest_ch2,
            manifest_ch3.name: manifest_ch3,
        },
        notification_rules={
            manifest_r1.name: manifest_r1,
            manifest_r2.name: manifest_r2,
            manifest_r3.name: manifest_r3,
        },
        identity_providers={
            manifest_p1.name: manifest_p1,
            manifest_p2.name: manifest_p2,
        },
        users={
            manifest_u1.name: manifest_u1,
            manifest_u2.name: manifest_u2,
        },
    )

    server_ctx = create_diff_context(
        credentials={server_c1.name: server_c1},
        destinations={
            server_d1.name: server_d1,
            server_d2.name: server_d2,
            server_d4.name: server_d4,
        },
        sources={
            server_s1.name: server_s1,
            server_s3.name: server_s3,
        },
        segmentations={
            server_seg1.name: server_seg1,
            server_seg3.name: server_seg3,
        },
        windows={
            server_w1.name: server_w1,
            server_w3.name: server_w3,
            server_w4.name: server_w4,
        },
        validators={
            server_v1.name: server_v1,
            server_v3.name: server_v3,
        },
        channels={
            server_ch1.name: server_ch1,
            server_ch3.name: server_ch3,
            server_ch4.name: server_ch4,
        },
        notification_rules={
            server_r1.name: server_r1,
            server_r3.name: server_r3,
            server_r4.name: server_r4,
        },
        identity_providers={
            server_p2.name: server_p2,
            server_p3.name: server_p3,
        },
        users={
            server_u2.name: server_u2,
            server_u3.name: server_u3,
        },
    )

    expected = create_graph_diff(
        to_create=DiffContext(
            destinations={manifest_d3.name: manifest_d3},
            sources={manifest_s2.name: manifest_s2},
            segmentations={manifest_seg2.name: manifest_seg2},
            windows={manifest_w2.name: manifest_w2},
            validators={manifest_v2.name: manifest_v2},
            channels={manifest_ch2.name: manifest_ch2},
            notification_rules={manifest_r2.name: manifest_r2},
            identity_providers={manifest_p1.name: manifest_p1},
            users={manifest_u1.name: manifest_u1},
        ),
        to_delete=DiffContext(
            destinations={server_d4.name: server_d4},
            sources={server_s3.name: server_s3},
            segmentations={server_seg3.name: server_seg3},
            windows={server_w4.name: server_w4},
            validators={server_v3.name: server_v3},
            channels={server_ch4.name: server_ch4},
            notification_rules={server_r4.name: server_r4},
            identity_providers={server_p3.name: server_p3},
            users={server_u3.name: server_u3},
        ),
        to_update=create_resource_updates(
            destinations={
                server_d2.name: collect_resource_config(
                    manifest_d2,
                    server_d2,
                )
            },
            windows={
                manifest_w3.name: collect_resource_config(
                    manifest_w3,
                    server_w3,
                )
            },
            channels={
                manifest_ch3.name: collect_resource_config(
                    manifest_ch3,
                    server_ch3,
                ),
            },
            notification_rules={
                manifest_r3.name: collect_resource_config(
                    manifest_r3,
                    server_r3,
                )
            },
            identity_providers={
                manifest_p2.name: collect_resource_config(
                    manifest_p2,
                    server_p2,
                )
            },
            users={
                manifest_u2.name: collect_resource_config(
                    manifest_u2,
                    server_u2,
                )
            },
        ),
    )

    _add_namespace(namespace, server_ctx)
    assert expected == _diff_resource_graph(namespace, manifest_ctx, server_ctx)


@pytest.mark.parametrize(
    ("filter_field", "reference_filter_field", "offset", "expect_update"),
    [
        ("age", "age10", 2, False),
        ("age2", "age10", 2, True),
        ("age", "age10", 3, True),
        ("age", "age", 2, True),
    ],
)
def test_diff_should_detect_updates_on_nested_objects(
    filter_field,
    reference_filter_field,
    offset,
    expect_update,
):
    namespace = "my_namespace"
    manifest_g = ResourceGraph()
    server_g = ResourceGraph()

    manifest_c1 = DemoCredential("c1", manifest_g)
    manifest_s1 = DemoSource("s1", manifest_c1)
    manifest_seg1 = Segmentation("seg1", manifest_s1, ["city"])
    manifest_w1 = TumblingWindow("w1", manifest_s1, "d", 1, WindowTimeUnit.DAY)

    manifest_v = NumericDistributionValidator(
        name="v1",
        window=manifest_w1,
        segmentation=manifest_seg1,
        threshold=DynamicThreshold(2),
        metric=NumericDistributionMetric.MAXIMUM_RATIO,
        source_field="a",
        reference_source_field="b",
        filter=NullFilter(field=filter_field),
        reference=Reference(
            manifest_s1,
            manifest_w1,
            1,
            offset,
            NullFilter(field=reference_filter_field),
        ),
    )

    server_c1 = DemoCredential("c1", server_g)
    server_s1 = DemoSource("s1", server_c1)
    server_seg1 = Segmentation("seg1", server_s1, ["city"])
    server_w1 = TumblingWindow("w1", server_s1, "d", 1, WindowTimeUnit.DAY)
    server_v = NumericDistributionValidator(
        name="v1",
        window=server_w1,
        segmentation=server_seg1,
        threshold=DynamicThreshold(2),
        metric=NumericDistributionMetric.MAXIMUM_RATIO,
        source_field="a",
        reference_source_field="b",
        filter=NullFilter(field="age"),
        reference=Reference(server_s1, server_w1, 1, 2, NullFilter(field="age10")),
    )

    manifest_ctx = create_diff_context(
        credentials={manifest_c1.name: manifest_c1},
        sources={manifest_s1.name: manifest_s1},
        segmentations={manifest_seg1.name: manifest_seg1},
        windows={manifest_w1.name: manifest_w1},
        validators={manifest_v.name: manifest_v},
    )
    server_ctx = create_diff_context(
        credentials={server_c1.name: server_c1},
        sources={server_s1.name: server_s1},
        segmentations={server_seg1.name: server_seg1},
        windows={server_w1.name: server_w1},
        validators={server_v.name: server_v},
    )

    expected = create_graph_diff(
        to_update=create_resource_updates(
            validators=(
                {
                    manifest_v.name: collect_resource_config(
                        manifest_v,
                        server_v,
                    ),
                }
                if expect_update
                else {}
            ),
        )
    )

    _add_namespace(namespace, server_ctx)
    assert expected == _diff_resource_graph(namespace, manifest_ctx, server_ctx)


def test_diff_should_reject_update_on_immutable_field():
    namespace = "my_namespace"
    manifest_g = ResourceGraph()
    server_g = ResourceGraph()

    manifest_c1 = DemoCredential("c1", manifest_g)
    manifest_s1 = DemoSource("s1", manifest_c1)
    manifest_s2 = DemoSource("s2", manifest_c1)

    server_c1 = DemoCredential("c1", server_g)
    server_s1 = DemoSource("s1", server_c1)
    server_s2 = DemoSource("s2", server_c1)

    # Differing sources on the same segmentation should be rejected.
    manifest_seg1 = Segmentation("seg1", manifest_s2, ["city"])
    server_seg1 = Segmentation("seg1", server_s1, ["city"])

    manifest_ctx = create_diff_context(
        credentials={manifest_c1.name: manifest_c1},
        sources={manifest_s1.name: manifest_s1, manifest_s2.name: manifest_s2},
        segmentations={manifest_seg1.name: manifest_seg1},
    )
    server_ctx = create_diff_context(
        credentials={server_c1.name: server_c1},
        sources={server_s1.name: server_s1, server_s2.name: server_s2},
        segmentations={server_seg1.name: server_seg1},
    )

    _add_namespace(namespace, server_ctx)
    with pytest.raises(ManifestConfigurationError) as err:
        _diff_resource_graph(namespace, manifest_ctx, server_ctx)

    assert "field 'source_name' is immutable" in str(err)
