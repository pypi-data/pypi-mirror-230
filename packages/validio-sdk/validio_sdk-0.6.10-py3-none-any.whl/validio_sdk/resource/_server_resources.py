import inspect
from typing import cast

from camel_converter import to_snake

# We need to import the validio_sdk module due to the `eval`
# ruff: noqa: F401
import validio_sdk
from validio_sdk.graphql_client import (
    GetIdentityProvidersIdentityProvidersSamlIdentityProvider,
    GraphQLClientHttpError,
    ListCredentialsCredentialsListAwsAthenaCredential,
    ListCredentialsCredentialsListAwsCredential,
    ListCredentialsCredentialsListAwsRedshiftCredential,
    ListCredentialsCredentialsListKafkaSaslSslPlainCredential,
    ListCredentialsCredentialsListKafkaSslCredential,
    ListCredentialsCredentialsListPostgreSqlCredential,
    ListCredentialsCredentialsListSnowflakeCredential,
    ReferenceSourceConfigDetails,
    UserDetails,
)
from validio_sdk.resource._diff import (
    DiffContext,
    GraphDiff,
    ResourceUpdates,
    expand_validator_field_selectors,
    infer_schema_for_source,
)
from validio_sdk.resource._diff_util import (
    must_find_channel,
    must_find_credential,
    must_find_destination,
    must_find_segmentation,
    must_find_source,
    must_find_window,
)
from validio_sdk.resource._resource import Resource, ResourceGraph
from validio_sdk.resource._util import _sanitize_error
from validio_sdk.resource.credentials import (
    AwsAthenaCredential,
    AwsCredential,
    AwsRedshiftCredential,
    Credential,
    DemoCredential,
    GcpCredential,
    KafkaSaslSslPlainCredential,
    KafkaSslCredential,
    PostgreSqlCredential,
    SnowflakeCredential,
)
from validio_sdk.resource.destinations import Destination
from validio_sdk.resource.identity_providers import (
    IdentityProvider,
    SamlIdentityProvider,
)
from validio_sdk.resource.segmentations import Segmentation
from validio_sdk.resource.sources import Source
from validio_sdk.resource.thresholds import (
    THRESHOLD_CLASSES,
    Threshold,
)
from validio_sdk.resource.users import User
from validio_sdk.resource.validators import VALIDATOR_CLASSES, Reference
from validio_sdk.resource.windows import WINDOW_CLASSES, Window
from validio_sdk.validio_client import ValidioAPIClient


async def load_resources(namespace: str, client: ValidioAPIClient) -> DiffContext:
    g = ResourceGraph()
    ctx = DiffContext()

    # Ordering matters here - we need to load parent resources before children
    await load_credentials(namespace, client, g, ctx)
    await load_channels(namespace, client, g, ctx)
    # await load_identity_providers(namespace, client, g, ctx)
    await load_users(namespace, client, g, ctx)
    await load_destinations(namespace, client, ctx)
    await load_sources(namespace, client, ctx)
    await load_segmentations(namespace, client, ctx)
    await load_windows(namespace, client, ctx)
    await load_validators(namespace, client, ctx)
    await load_notification_rules(namespace, client, ctx)

    return ctx


async def load_credentials(
    # ruff: noqa: ARG001
    namespace: str,
    client: ValidioAPIClient,
    g: ResourceGraph,
    ctx: DiffContext,
):
    credentials = await client.list_credentials()

    for c in credentials:
        if c.resource_namespace != namespace:
            continue

        name = c.resource_name

        # The 'secret' parts of a credential are left unset since they are not
        # provided by the API. We check for changes to them specially.
        match c.typename__:
            case "DemoCredential":
                credential: Credential = DemoCredential(name=name, __internal__=g)
            case "GcpCredential":
                credential = GcpCredential(
                    name=name, credential="UNSET", __internal__=g
                )
            case "AwsCredential":
                c = cast(ListCredentialsCredentialsListAwsCredential, c)
                credential = AwsCredential(
                    name=name,
                    access_key=c.config.access_key,
                    secret_key="UNSET",
                    __internal__=g,
                )
            case "PostgreSqlCredential":
                c = cast(ListCredentialsCredentialsListPostgreSqlCredential, c)
                credential = PostgreSqlCredential(
                    name=name,
                    host=c.config.host,
                    port=c.config.port,
                    user=c.config.user,
                    password="UNSET",
                    default_database=c.config.default_database,
                    __internal__=g,
                )
            case "AwsRedshiftCredential":
                c = cast(ListCredentialsCredentialsListAwsRedshiftCredential, c)
                credential = AwsRedshiftCredential(
                    name=name,
                    host=c.config.host,
                    port=c.config.port,
                    user=c.config.user,
                    password="UNSET",
                    default_database=c.config.default_database,
                    __internal__=g,
                )
            case "AwsAthenaCredential":
                c = cast(ListCredentialsCredentialsListAwsAthenaCredential, c)
                credential = AwsAthenaCredential(
                    name=name,
                    access_key=c.config.access_key,
                    secret_key="UNSET",
                    region=c.config.region,
                    query_result_location=c.config.query_result_location,
                    __internal__=g,
                )
            case "SnowflakeCredential":
                c = cast(ListCredentialsCredentialsListSnowflakeCredential, c)
                credential = SnowflakeCredential(
                    name=name,
                    account=c.config.account,
                    user=c.config.user,
                    password="UNSET",
                    __internal__=g,
                )
            case "KafkaSslCredential":
                c = cast(ListCredentialsCredentialsListKafkaSslCredential, c)
                credential = KafkaSslCredential(
                    name=name,
                    bootstrap_servers=c.config.bootstrap_servers,
                    ca_certificate=c.config.ca_certificate,
                    client_certificate="UNSET",
                    client_private_key="UNSET",
                    client_private_key_password="UNSET",
                    __internal__=g,
                )
            case "KafkaSaSlSslCredential":
                c = cast(ListCredentialsCredentialsListKafkaSaslSslPlainCredential, c)
                credential = KafkaSaslSslPlainCredential(
                    name=name,
                    bootstrap_servers=c.config.bootstrap_servers,
                    username="UNSET",
                    password="UNSET",
                    __internal__=g,
                )
            case _:
                raise RuntimeError(
                    f"unsupported credential '{name}' of type '{type(c)}'"
                )

        credential._id.value = c.id
        credential._namespace = c.resource_namespace

        ctx.credentials[name] = credential


async def load_channels(
    namespace: str,
    client: ValidioAPIClient,
    g: ResourceGraph,
    ctx: DiffContext,
):
    # We need to import the module due to the `eval`
    # ruff: noqa: F401
    from validio_sdk.resource import channels

    server_channels = await client.get_channels()

    for ch in server_channels:
        if ch.resource_namespace != namespace:
            continue

        name = ch.resource_name

        cls = eval(f"validio_sdk.resource.channels.{ch.typename__}")
        channel = cls(
            **{
                **ch.config.__dict__,  # type: ignore
                "name": name,
                "__internal__": g,
            }
        )
        channel._id.value = ch.id
        channel._namespace = ch.resource_namespace
        ctx.channels[name] = channel


async def load_identity_providers(
    # ruff: noqa: ARG001
    namespace: str,
    client: ValidioAPIClient,
    g: ResourceGraph,
    ctx: DiffContext,
):
    identity_providers = await client.get_identity_providers()
    if identity_providers is None:
        return

    for p in identity_providers:
        if p is None or p.resource_namespace != namespace:
            continue

        name = p.resource_name

        match p.typename__:
            case "SamlIdentityProvider":
                sp = cast(GetIdentityProvidersIdentityProvidersSamlIdentityProvider, p)
                provider: IdentityProvider = SamlIdentityProvider(
                    name=name,
                    cert=sp.config.cert,
                    entry_point=sp.config.entry_point,
                    entity_id=sp.config.entity_id,
                    disabled=sp.disabled,
                    __internal__=g,
                )
            case _:
                raise RuntimeError(
                    f"unsupported identity provider '{name}' of type '{type(p)}'"
                )

        provider._id.value = p.id
        provider._namespace = p.resource_namespace

        ctx.identity_providers[name] = provider


async def load_users(
    # ruff: noqa: ARG001
    namespace: str,
    client: ValidioAPIClient,
    g: ResourceGraph,
    ctx: DiffContext,
):
    users = await client.get_users()
    if users is None:
        return

    for u in users:
        if u is None or u.resource_namespace != namespace:
            continue

        name = u.resource_name

        server_field_names = {
            to_snake(f) for f in inspect.signature(UserDetails).parameters
        }
        manifest_field_names = set(inspect.signature(User).parameters)
        field_names = set.intersection(server_field_names, manifest_field_names)
        args = {
            "name": name,
            "__internal__": g,
            **{field: getattr(u, field) for field in field_names},
        }
        user = User(**args)  # type: ignore

        user._id.value = u.id
        user._namespace = u.resource_namespace

        ctx.users[name] = user


async def load_notification_rules(
    namespace: str,
    client: ValidioAPIClient,
    ctx: DiffContext,
):
    # We need to import the module due to the `eval`
    # ruff: noqa: F401
    from validio_sdk.resource import notification_rules

    rules = await client.get_notification_rules()

    source_lookup_by_id = {s._must_id(): s for s in ctx.sources.values()}
    for r in rules:
        if r.resource_namespace != namespace:
            continue

        name = r.resource_name

        cls = eval(f"validio_sdk.resource.notification_rules.{r.typename__}")
        fields = list(inspect.signature(cls).parameters)
        rule = cls(
            **{
                **{
                    f: getattr(r, f)
                    for f in fields
                    if f not in {"name", "channel", "sources"}
                },
                "name": name,
                "channel": must_find_channel(ctx, r.channel.resource_name),
                "sources": [
                    source_lookup_by_id[sid]
                    for sid in r.sources
                    if sid and sid in source_lookup_by_id
                ],
            }
        )
        rule._id.value = r.id
        rule._namespace = r.resource_namespace
        ctx.notification_rules[name] = rule


async def load_destinations(
    namespace: str,
    client: ValidioAPIClient,
    ctx: DiffContext,
):
    # We need to import the module due to the `eval`
    # ruff: noqa: F401
    from validio_sdk.resource import destinations

    server_destinations = await client.list_destinations()

    for d in server_destinations:
        if d.resource_namespace != namespace:
            continue

        name = d.resource_name

        cls = eval(f"validio_sdk.resource.destinations.{d.typename__}")
        destination = cls(
            **{
                **d.config.__dict__,  # type: ignore
                "name": name,
                "credential": must_find_credential(ctx, d.credential.resource_name),
            }
        )
        destination._id.value = d.id
        destination._namespace = d.resource_namespace
        ctx.destinations[name] = destination


async def load_sources(
    namespace: str,
    client: ValidioAPIClient,
    ctx: DiffContext,
):
    # We need to import the module due to the `eval`
    # ruff: noqa: F401
    from validio_sdk.resource import sources

    server_sources = await client.list_sources()

    for s in server_sources:
        if s.resource_namespace != namespace:
            continue

        name = s.resource_name

        cls = eval(f"validio_sdk.resource.sources.{s.typename__}")
        params = s.config.__dict__ if hasattr(s, "config") else {}
        source = cls(
            **{
                **params,
                "name": name,
                "credential": must_find_credential(ctx, s.credential.resource_name),
                "jtd_schema": s.jtd_schema,
            }
        )
        source._id.value = s.id
        source._namespace = s.resource_namespace
        ctx.sources[name] = source


async def load_segmentations(
    namespace: str,
    client: ValidioAPIClient,
    ctx: DiffContext,
):
    # We need to import the module due to the `eval`
    # ruff: noqa: F401
    from validio_sdk.resource import segmentations

    server_segmentations = await client.list_segmentations()

    for s in server_segmentations:
        if s.resource_namespace != namespace:
            continue

        name = s.resource_name

        segmentation = Segmentation(
            name=name,
            source=must_find_source(ctx, s.source.resource_name),
            fields=s.fields,
        )

        segmentation._id.value = s.id
        segmentation._namespace = s.resource_namespace
        ctx.segmentations[name] = segmentation


async def load_windows(
    namespace: str,
    client: ValidioAPIClient,
    ctx: DiffContext,
):
    # We need to import the module due to the `eval`
    # ruff: noqa: F401
    from validio_sdk.resource import windows

    server_windows = await client.list_windows()

    for w in server_windows:
        if w.resource_namespace != namespace:
            continue

        name = w.resource_name

        cls = None
        for c in WINDOW_CLASSES:
            if w.typename__ == c.__name__:
                cls = c
                break

        if cls is None:
            raise RuntimeError(
                f"missing implementation for Window type {w.__class__.__name__}"
            )

        window = cls(
            **{
                **(w.config.__dict__ if hasattr(w, "config") else {}),  # type:ignore
                "name": name,
                "source": must_find_source(ctx, w.source.resource_name),
                "data_time_field": w.data_time_field,
            }
        )

        window._id.value = w.id
        window._namespace = w.resource_namespace
        ctx.windows[name] = window


# Takes in a graphql Threshold type
def convert_threshold(t: object) -> Threshold:
    graphql_class_name: str = t.__class__.__name__
    cls = None
    for c in THRESHOLD_CLASSES:
        if graphql_class_name.endswith(c.__name__):
            cls = c
            break

    if cls is None:
        raise RuntimeError(
            f"missing implementation for threshold type {graphql_class_name}"
        )

    # Threshold parameters map 1-1 with resources, so
    # we call the constructor directly.
    return cls(**{k: v for k, v in t.__dict__.items() if k != "typename__"})


# Takes in a graphql ReferenceSourceConfig type
def convert_reference(ctx: DiffContext, r: ReferenceSourceConfigDetails) -> Reference:
    source = must_find_source(ctx, r.source.resource_name)
    window = must_find_window(ctx, r.window.resource_name)

    return Reference(
        source=source,
        window=window,
        history=r.history,
        offset=r.offset,
        filter=r.filter,
    )


async def load_validators(
    namespace: str,
    client: ValidioAPIClient,
    ctx: DiffContext,
):
    for source in ctx.sources.values():
        validators = await client.list_validators(source._must_id())

        for v in validators:
            if v.resource_namespace != namespace:
                continue

            name = v.resource_name

            cls = None
            for c in VALIDATOR_CLASSES:
                if v.typename__ == c.__name__:
                    cls = c
                    break

            if cls is None:
                raise RuntimeError(
                    f"missing implementation for Validator type {v.typename__}"
                )

            window = must_find_window(ctx, v.source_config.window.resource_name)
            segmentation = must_find_segmentation(
                ctx, v.source_config.segmentation.resource_name
            )
            maybe_destination = (
                must_find_destination(ctx, v.destination.name)
                if hasattr(v, "destination") and v.destination
                else None
            )

            threshold = convert_threshold(v.config.threshold)  # type:ignore
            maybe_reference = (
                {
                    "reference": convert_reference(
                        ctx, v.reference_source_config  # type: ignore
                    )
                }
                if hasattr(v, "reference_source_config")
                else {}
            )
            maybe_filter = (
                {"filter": v.source_config.filter}
                if hasattr(v.source_config, "filter")
                else {}
            )

            # These are named inconsistently in the list apis, so we treat
            # them specially.
            metric_names = {
                "metric",
                "relative_volume_metric",
                "volume_metric",
                "distribution_metric",
                "numeric_anomaly_metric",
                "relative_time_metric",
                "categorical_distribution_metric",
            }

            config = {}
            for f, config_value in v.config.__dict__.items():  # type: ignore
                if f == "threshold":
                    continue
                if f in metric_names:
                    config["metric"] = config_value
                else:
                    config[f] = config_value

            validator = cls(
                **{
                    **config,
                    **maybe_reference,
                    **maybe_filter,
                    "threshold": threshold,
                    "name": name,
                    "window": window,
                    "segmentation": segmentation,
                    **({"destination": maybe_destination} if maybe_destination else {}),
                }
            )
            validator._id.value = v.id
            validator._namespace = v.resource_namespace
            ctx.validators[name] = validator


async def apply_updates_on_server(
    namespace: str,
    ctx: DiffContext,
    diff: GraphDiff,
    client: ValidioAPIClient,
    show_secrets: bool,
):
    try:
        await apply_deletes(namespace=namespace, deletes=diff.to_delete, client=client)

        # We perform create operations in two batches. First here creates top
        # level resources, then after performing updates, we create any remaining
        # resources. We do this due to a couple scenarios
        # - A resource potentially depends on the parent to be created first before
        #   it can be updated. Example is a validator being updated to use a
        #   destination that is to be created. Another is a notification rule that
        #   is being updated to reference a Source that is to be created. In such
        #   cases, we need to apply the create on parent resource before the update
        #   on child resource.
        # - Conversely, in some cases, a parent resource needs to be updated before
        #   the child resource can be created. e.g a validator that is referencing a
        #   new field in a schema needs the source to be updated first otherwise diver
        #   will reject the validator as invalid because the field does not yet exist.
        #
        # So, here we create the top level resources first - ensuring that any child
        # resource that relies on them are resolved properly.
        # We start with creating credentials only. Since sources need them to infer
        # schema.
        await apply_creates(
            namespace=namespace,
            manifest_ctx=ctx,
            creates=DiffContext(
                credentials=diff.to_create.credentials,
                identity_providers=diff.to_create.identity_providers,
                users=diff.to_create.users,
            ),
            client=client,
            show_secrets=show_secrets,
        )

        # Resolve any pending source schemas now that we have their credential.
        for source in diff.to_create.sources.values():
            if source.jtd_schema is None:
                await infer_schema_for_source(
                    manifest_ctx=ctx, source=source, client=client
                )

        # Create the remaining top level resources.
        await apply_creates(
            namespace=namespace,
            manifest_ctx=ctx,
            creates=DiffContext(
                sources=diff.to_create.sources,
                destinations=diff.to_create.destinations,
                channels=diff.to_create.channels,
            ),
            client=client,
            show_secrets=show_secrets,
        )

        # Now we should have all source schemas available. We can expand
        # field selectors.
        expand_validator_field_selectors(ctx)

        # Then apply updates.
        await apply_updates(
            namespace=namespace, manifest_ctx=ctx, updates=diff.to_update, client=client
        )

        # Then apply remaining creates. Resources that have been created in
        # the previous steps are marked as _applied, so they will be skipped this
        # time around.
        await apply_creates(
            namespace=namespace,
            manifest_ctx=ctx,
            creates=diff.to_create,
            client=client,
            show_secrets=show_secrets,
        )
    except GraphQLClientHttpError as e:
        raise RuntimeError(f"API error: ({e.status_code}: {e.response.json()})")


# ruff: noqa: PLR0912
async def apply_deletes(namespace: str, deletes: DiffContext, client: ValidioAPIClient):
    # Delete notification rules first These reference sources so we
    # remove them before removing the sources they reference.
    for r in deletes.notification_rules.values():
        await _delete_resource(r, client)

    # For pipeline resources, start with sources (This cascades deletes,
    # so we don't have to individually delete child resources).
    for s in deletes.sources.values():
        await _delete_resource(s, client)

    # For child resources, we only need to delete them if their parent
    # haven't been deleted.
    for w in deletes.windows.values():
        if w.source_name not in deletes.sources:
            await _delete_resource(w, client)

    for sg in deletes.segmentations.values():
        if sg.source_name not in deletes.sources:
            await _delete_resource(sg, client)

    for v in deletes.validators.values():
        if v.source_name not in deletes.sources:
            await _delete_resource(v, client)

    # Next, delete destinations. Validators are deleted before we
    # delete potentially attached destinations.
    for d in deletes.destinations.values():
        await _delete_resource(d, client)

    # Finally delete credentials - these do not cascade so the api rejects any
    # delete requests if there are existing child resources attached to a credential.
    for c in deletes.credentials.values():
        await _delete_resource(c, client)

    for ch in deletes.channels.values():
        await _delete_resource(ch, client)

    for u in deletes.users.values():
        await _delete_resource(u, client)

    for ip in deletes.identity_providers.values():
        await _delete_resource(ip, client)


async def _delete_resource(resource: Resource, client: ValidioAPIClient):
    if resource._applied:
        return
    resource._applied = True
    await resource._api_delete(client)


async def apply_creates(
    namespace: str,
    manifest_ctx: DiffContext,
    creates: DiffContext,
    client: ValidioAPIClient,
    show_secrets: bool,
):
    # Creates must be applied top-down, parent first before child resources
    all_resources: list[list[Resource]] = [
        list(creates.identity_providers.values()),
        list(creates.users.values()),
        list(creates.credentials.values()),
        list(creates.sources.values()),
        list(creates.destinations.values()),
        list(creates.segmentations.values()),
        list(creates.windows.values()),
        list(creates.validators.values()),
        list(creates.channels.values()),
        list(creates.notification_rules.values()),
    ]
    for resources in all_resources:
        for r in resources:
            if r._applied:
                continue
            r._applied = True

            try:
                await r._api_create(namespace, client, manifest_ctx)
            except GraphQLClientHttpError as e:
                raise (
                    _sanitize_error(e, show_secrets) if isinstance(r, Credential) else e
                )


async def apply_updates(
    namespace: str,
    manifest_ctx: DiffContext,
    updates: ResourceUpdates,
    client: ValidioAPIClient,
):
    all_updates = [
        list(updates.identity_providers.values()),
        list(updates.users.values()),
        list(updates.credentials.values()),
        list(updates.destinations.values()),
        list(updates.sources.values()),
        list(updates.segmentations.values()),
        list(updates.windows.values()),
        list(updates.validators.values()),
        list(updates.channels.values()),
        list(updates.notification_rules.values()),
    ]

    for up in all_updates:
        for u in up:
            if u.manifest.resource._applied:
                continue
            u.manifest.resource._applied = True

            await u.manifest.resource._api_update(namespace, client, manifest_ctx)
