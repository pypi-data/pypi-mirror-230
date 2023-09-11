"""Destinations."""
from typing import TYPE_CHECKING, Any, cast

from validio_sdk.resource._resource import Resource
from validio_sdk.resource._serde import (
    CONFIG_FIELD_NAME,
    _api_create_input_params,
    _encode_resource,
)
from validio_sdk.resource.credentials import (
    AwsCredential,
    Credential,
    GcpCredential,
    SnowflakeCredential,
)

if TYPE_CHECKING:
    from validio_sdk.resource._diff import DiffContext


class Destination(Resource):
    """A destination configuration.

    https://docs.validio.io/docs/destinations
    """

    def __init__(
        self,
        name: str,
        credential: Credential,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the destination
        :param credential: The credential to attach the destination to
        """
        super().__init__(name, credential._resource_graph)
        self.credential_name: str = credential.name

        credential.add(name, self)

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return set({})

    def resource_class_name(self) -> str:
        """Returns the base class name."""
        return "Destination"

    def _encode(self) -> dict[str, object]:
        # Drop a fields here that are not part of the constructor so that.
        # we can deserialize the output back.
        return _encode_resource(self, skip_fields={"credential_name"})

    @staticmethod
    def _decode(
        _: "DiffContext",
        cls: type,
        obj: dict[str, dict[str, object]],
        credential: Credential,
    ) -> "Destination":
        return cls(
            **cast(
                dict[str, object], {**obj[CONFIG_FIELD_NAME], "credential": credential}
            )
        )

    def _api_create_input(self, namespace: str, ctx: "DiffContext") -> Any:
        return _api_create_input_params(
            self,
            namespace=namespace,
            overrides={
                "credential_id": ctx.credentials[self.credential_name]._must_id(),
            },
        )

    def _api_update_input(self, namespace: str, ctx: "DiffContext") -> Any:
        return _api_create_input_params(
            self,
            namespace=namespace,
            overrides={
                "credential_id": ctx.credentials[self.credential_name]._must_id(),
            },
        )


class GcpBigQueryDestination(Destination):
    """A BigQuery destination configuration.

    https://docs.validio.io/docs/bigquery-1
    """

    def __init__(
        self,
        name: str,
        credential: GcpCredential,
        project: str,
        dataset: str,
        table: str,
    ):
        """
        Constructor.

        :param project: GCP project where the BigQuery instance resides.
        :param dataset: Dataset containing the configured table.
        :param table: Name of table to write to.
        """
        super().__init__(name, credential)

        self.project = project
        self.dataset = dataset
        self.table = table

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._immutable_fields(),
            *{
                "project",
                "dataset",
                "table",
            },
        }


class SnowflakeDestination(Destination):
    """
    A Snowflake destination configuration.

    https://docs.validio.io/docs/snowflake-1
    """

    def __init__(
        self,
        name: str,
        credential: SnowflakeCredential,
        database: str,
        db_schema: str,
        table: str,
        role: str,
        warehouse: str,
    ):
        """
        Constructor.

        :param database: Name of the snowflake database to connect to .
        :param db_schema: Name of the schema in the database that contains the
            table to write to.
        :param table: Name of table to monitor.
        :param warehouse: Snowflake virtual warehouse to use to write to table.
        :param role: Snowflake role to assume when writing to table.
        """
        super().__init__(name, credential)

        self.database = database
        self.db_schema = db_schema
        self.table = table
        self.role = role
        self.warehouse = warehouse

    def __getattr__(self, name):
        """Getter for field aliases."""
        # schema is called db_schema
        if name == "schema":
            return self.db_schema
        raise AttributeError

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._immutable_fields(),
            *{
                "database",
                "db_schema",
                "table",
                "role",
                "warehouse",
            },
        }


class AwsKinesisDestination(Destination):
    """A Kinesis destination configuration."""

    def __init__(
        self,
        name: str,
        credential: AwsCredential,
        region: str,
        stream_name: str,
        endpoint: str | None = None,
    ):
        """
        Constructor.

        :param region: AWS region where the Kinesis stream resides.
        :param stream_name: Kinesis stream name
        :param endpoint: (Deprecated)
        """
        super().__init__(name, credential)

        self.region = region
        self.stream_name = stream_name
        self.endpoint = endpoint

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._immutable_fields(),
            *{
                "region",
                "stream_name",
                "endpoint",
            },
        }
