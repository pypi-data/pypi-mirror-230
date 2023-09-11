"""Window configuration."""
from abc import abstractmethod
from typing import TYPE_CHECKING, Any

from validio_sdk.graphql_client.enums import WindowTimeUnit
from validio_sdk.resource._resource import Resource
from validio_sdk.resource._serde import (
    CONFIG_FIELD_NAME,
    NODE_TYPE_FIELD_NAME,
    _api_create_input_params,
    _encode_resource,
)
from validio_sdk.resource.sources import Source

if TYPE_CHECKING:
    from validio_sdk.resource._diff import DiffContext


class Window(Resource):
    """
    Base class for a window resource.

    https://docs.validio.io/docs/windows
    """

    def __init__(self, name: str, source: Source):
        """
        Constructor.

        :param name: Unique resource name assigned to the window
        :param source: The source to attach the window to
        """
        super().__init__(name, source._resource_graph)
        self.source_name: str = source.name

        source.add(name, self)

    def _immutable_fields(self) -> set[str]:
        return {"source_name", "data_time_field"}

    @abstractmethod
    def _mutable_fields(self) -> set[str]:
        pass

    def resource_class_name(self) -> str:
        """Returns the base class name."""
        return "Window"

    def _api_create_input(self, namespace: str, ctx: "DiffContext") -> Any:
        return _api_create_input_params(
            self,
            namespace=namespace,
            overrides={"source_id": ctx.sources[self.source_name]._must_id()},
        )

    def _encode(self) -> dict[str, object]:
        # Drop fields here that are not part of the constructor for when
        # we deserialize back. They will be reinitialized by the constructor.
        return _encode_resource(self, skip_fields={"source_name"})

    @staticmethod
    def _decode(obj: dict[str, Any], source: Source) -> "Window":
        cls = eval(obj[NODE_TYPE_FIELD_NAME])
        return cls(**{**obj[CONFIG_FIELD_NAME], "source": source})


class TumblingWindow(Window):
    """A Tumbling window resource."""

    def __init__(
        self,
        name: str,
        source: Source,
        data_time_field: str,
        window_size: int,
        time_unit: WindowTimeUnit,
    ):
        """
        Constructor.

        :param data_time_field: Data time field for the window
        :param window_size: Size of the tumbling window
        :param time_unit: Unit of the specified window_size.
            (minimum window size is 30 minutes)
        """
        super().__init__(name=name, source=source)

        self.data_time_field: str = data_time_field
        self.window_size: int = window_size
        self.time_unit: WindowTimeUnit = (
            # When we decode, enums are passed in a strings
            time_unit
            if isinstance(time_unit, WindowTimeUnit)
            else WindowTimeUnit(time_unit)
        )

    def _mutable_fields(self) -> set[str]:
        return {"time_unit", "window_size"}


class FixedBatchWindow(Window):
    """
    A FixedBatch window resource.

    https://docs.validio.io/docs/windows-configuration#31-fixed-batch-window
    """

    def __init__(
        self,
        name: str,
        source: Source,
        data_time_field: str,
        batch_size: int,
        segmented_batching: bool = False,
        batch_timeout_secs: int | None = None,
    ):
        """
        Constructor.

        :param data_time_field: Data time field for the window
        :param batch_size: Number of datapoints that form a Window
        :param segmented_batching: If True, each segment gets a separate
            Window of batch_size length.
        :param batch_timeout_secs: If segmented_batching is True, applies a timeout
            after which any collected datapoints for a segment will be force-processed
        """
        super().__init__(name=name, source=source)

        self.data_time_field: str = data_time_field
        self.batch_size = batch_size
        self.segmented_batching = segmented_batching
        self.batch_timeout_secs = batch_timeout_secs

    def _immutable_fields(self) -> set[str]:
        return {
            *super()._immutable_fields(),
            *{
                "segmented_batching",
            },
        }

    def _mutable_fields(self) -> set[str]:
        return {"batch_size", "batch_timeout_secs"}


class SessionizedWindow(Window):
    """
    A Sessionized window resource.

    https://docs.validio.io/docs/windows-configuration#33-sessionized-window
    """

    def __init__(
        self,
        name: str,
        source: Source,
        data_time_field: str,
        timeout: int,
        timeout_unit: WindowTimeUnit,
    ):
        """
        Constructor.

        :param data_time_field: Data time field for the window
        :param timeout: Session gap length in the selected time unit
        :param timeout_unit: Time-unit of timeout
        """
        super().__init__(name=name, source=source)

        self.data_time_field: str = data_time_field
        self.timeout = timeout
        self.timeout_unit: WindowTimeUnit = (
            # When we decode, enums are passed in a strings
            timeout_unit
            if isinstance(timeout_unit, WindowTimeUnit)
            else WindowTimeUnit(timeout_unit)
        )

    def _mutable_fields(self) -> set[str]:
        return {"timeout", "timeout_unit"}


class FileWindow(Window):
    """
    A File window resource.

    https://docs.validio.io/docs/windows-configuration#34-file-window
    """

    def __init__(
        self,
        name: str,
        source: Source,
        data_time_field: str,
    ):
        """
        Constructor.

        :param data_time_field: Data time field for the window
        """
        super().__init__(name=name, source=source)

        self.data_time_field: str = data_time_field

    def _mutable_fields(self) -> set[str]:
        return set({})


WINDOW_CLASSES: set[type] = {
    TumblingWindow,
    FixedBatchWindow,
    SessionizedWindow,
    FileWindow,
}
