"""Credentials configuration."""
from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Optional, Union, cast

from validio_sdk.resource._resource import Resource, ResourceGraph
from validio_sdk.resource._resource_graph import RESOURCE_GRAPH
from validio_sdk.resource._serde import (
    CONFIG_FIELD_NAME,
    NODE_TYPE_FIELD_NAME,
    ImportValue,
    _encode_resource,
    _import_resource_params,
    get_children_node,
    with_resource_graph_info,
)

if TYPE_CHECKING:
    from validio_sdk.resource._diff import DiffContext


class Credential(Resource):
    """
    Base class for a credential resource.

    https://docs.validio.io/docs/credentials
    """

    def __init__(self, name: str, __internal__=None):
        """
        Constructor.

        :param name: Unique resource name assigned to the credential
        :param __internal__: Should be left ignored. This is for internal usage only.
        """
        # Credentials are at the root sub-graphs.
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

    @abstractmethod
    def _secret_fields(self) -> set[str] | None:
        pass

    def resource_class_name(self) -> str:
        """Returns the base class name."""
        return "Credential"

    def _encode(self) -> dict[str, object]:
        return _encode_resource(self)

    @staticmethod
    def _decode(
        ctx: "DiffContext",
        cls: type,
        obj: dict[str, dict[str, object]],
        g: ResourceGraph,
    ) -> "Credential":
        from validio_sdk.resource.destinations import Destination
        from validio_sdk.resource.sources import Source

        credential = cls(**with_resource_graph_info(obj[CONFIG_FIELD_NAME], g))
        children_obj = cast(
            dict[str, dict[str, dict[str, Any]]], get_children_node(obj)
        )

        Credential._decode_children(ctx, children_obj, credential, Source, "sources")
        Credential._decode_children(
            ctx, children_obj, credential, Destination, "destinations"
        )

        return credential

    @staticmethod
    def _decode_children(
        ctx: "DiffContext",
        children_obj: dict[str, dict[str, dict[str, object]]],
        credential: "Credential",
        resource_cls: type,
        resource_module: str,
    ):
        # We need to import the validio_sdk module due to the `eval`
        # ruff: noqa: F401
        import validio_sdk

        resources_obj = (
            children_obj[resource_cls.__name__]
            if resource_cls.__name__ in children_obj
            else {}
        )
        resources = {}
        for resource_name, value in resources_obj.items():
            cls = eval(
                f"validio_sdk.resource.{resource_module}.{value[NODE_TYPE_FIELD_NAME]}"
            )
            r = cast(Any, resource_cls)._decode(ctx, cls, value, credential)
            resources[resource_name] = r
            ctx.__getattribute__(resource_module)[resource_name] = r

        if len(resources) > 0:
            credential._children[resource_cls.__name__] = resources

    def _import_params(self) -> dict[str, ImportValue]:
        secret_fields = {
            field: ImportValue(value="UNSET", comment="FIXME: Add secret value")
            for field in (self._secret_fields() or set({}))
        }
        return {
            **_import_resource_params(
                resource=self,
                skip_fields=self._secret_fields(),
            ),
            **secret_fields,
        }


class DemoCredential(Credential):
    """A demo credential resource."""

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return set({})

    def _secret_fields(self) -> set[str] | None:
        return None


class GcpCredential(Credential):
    """
    A credential resource that can be used to authenticate against
    Google Cloud Platform services.
    """

    def __init__(
        self,
        name: str,
        credential: str,
        __internal__=None,
    ):
        """
        Constructor.

        :param credential: Service account JSON credential
        """
        super().__init__(name, __internal__)
        self.credential = credential

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return set({})

    def _secret_fields(self) -> set[str] | None:
        return {"credential"}


class AwsCredential(Credential):
    """A credential resource that can be used to authenticate against AWS services."""

    def __init__(
        self,
        name: str,
        access_key: str,
        secret_key: str,
        __internal__=None,
    ):
        """
        Constructor.

        :param access_key: Access key for the IAM user
            https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html
        :param secret_key: Secret key for the IAM user
            https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html
        """
        super().__init__(name, __internal__)
        self.access_key = access_key
        self.secret_key = secret_key

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {"access_key"}

    def _secret_fields(self) -> set[str] | None:
        return {"secret_key"}


class SnowflakeCredential(Credential):
    """A credential resource that can be used to connect to a Snowflake table."""

    def __init__(
        self,
        name: str,
        account: str,
        user: str,
        password: str,
        __internal__=None,
    ):
        """
        Constructor.

        :param account: Snowflake account identifier
        :param user: Username having read access to the desired table.
        :param password: Password of the specified user.
        """
        super().__init__(name, __internal__)
        self.account = account
        self.user = user
        self.password = password

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {"account", "user"}

    def _secret_fields(self) -> set[str] | None:
        return {"password"}


class PostgresLikeCredential(Credential):
    """
    A credential resource that can be used to connect to
    a Postgres-compatible table.
    """

    def __init__(
        self,
        name: str,
        host: str,
        port: int,
        user: str,
        password: str,
        default_database: str,
        __internal__=None,
    ):
        """
        Constructor.

        :param host: DNS hostname or IP address at which to reach the database server.
        :param port: Port number of the database server.
        :param user: Username having read access to the desired table.
        :param password: Password of the specified user.
        :param default_database: Name of the default database to use this
            credential with. This can be overridden e.g. in a Source configuration.
        """
        super().__init__(name, __internal__)
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.default_database = default_database

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {"host", "port", "user", "default_database"}

    def _secret_fields(self) -> set[str] | None:
        return {"password"}


class PostgreSqlCredential(PostgresLikeCredential):
    """
    A credential resource that can be used to connect to a Postgres table.

    https://docs.validio.io/docs/postgresql
    """


class AwsRedshiftCredential(PostgresLikeCredential):
    """
    A credential resource that can be used to connect to a Redshift table.

    https://docs.validio.io/docs/redshift
    """


class AwsAthenaCredential(Credential):
    """Athena credential resource."""

    def __init__(
        self,
        name: str,
        access_key: str,
        secret_key: str,
        region: str,
        query_result_location: str,
        __internal__=None,
    ):
        """
        Constructor.

        :param access_key: Access key for the IAM user
            https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html
        :param secret_key: Secret key for the IAM user
            https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html
        :param region: Region where the Athena service resides. e.g. eu-central-1
        :param query_result_location: S3 bucket to store query results
            e.g s3://myathenabucket/results
        """
        super().__init__(name, __internal__)
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.query_result_location = query_result_location

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {"access_key", "region", "query_result_location"}

    def _secret_fields(self) -> set[str] | None:
        return {"secret_key"}


class KafkaSslCredential(Credential):
    """
    A Kafka TLS credential.

    Security protocol: SSL

    https://docs.validio.io/docs/kafka#authentication-methods-for-source-config
    """

    def __init__(
        self,
        name: str,
        bootstrap_servers: list[str],
        ca_certificate: str,
        client_certificate: str,
        client_private_key: str,
        client_private_key_password: str,
        __internal__=None,
    ):
        """
        Constructor.

        :param bootstrap_servers: List of Kafka server addresses to connect to.
            example: ['localhost:9092']
        :param ca_certificate: Certificate of the Certificate authority (CA)
            in CRT format.
        :param client_certificate: Client SSL certificate in PEM format.
        :param client_private_key: Client private key certificate in PEM format.
        :param client_private_key_password: Password or passphrase of
            client_private_key.
        """
        super().__init__(name, __internal__)
        self.bootstrap_servers = bootstrap_servers
        self.ca_certificate = ca_certificate
        self.client_certificate = client_certificate
        self.client_private_key = client_private_key
        self.client_private_key_password = client_private_key_password

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {"bootstrap_servers"}

    def _secret_fields(self) -> set[str] | None:
        return {
            "ca_certificate",
            "client_certificate",
            "client_private_key",
            "client_private_key_password",
        }


class KafkaSaslSslPlainCredential(Credential):
    """
    A Kafka SASL SSL credential.

    Security protocol: SASL_SSL
    Sasl mechanism: PLAIN

    https://docs.validio.io/docs/kafka#authentication-methods-for-source-config
    """

    def __init__(
        self,
        name: str,
        bootstrap_servers: list[str],
        username: str,
        password: str,
        __internal__=None,
    ):
        """
        Constructor.

        :param bootstrap_servers: List of Kafka server addresses to connect to.
            example: ['localhost:9092']
        :param username: Username for the credential
        :param password: Password for the credential
        """
        super().__init__(name, __internal__)
        self.bootstrap_servers = bootstrap_servers
        self.username = username
        self.password = password

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {"bootstrap_servers"}

    def _secret_fields(self) -> set[str] | None:
        return {"username", "password"}


KafkaCredential = Union[KafkaSslCredential, KafkaSaslSslPlainCredential]
