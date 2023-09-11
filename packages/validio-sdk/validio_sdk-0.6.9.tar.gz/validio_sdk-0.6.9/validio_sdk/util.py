"""Utilities for Validio."""

import dataclasses
import json
import pathlib
from datetime import date, datetime
from enum import Enum

from validio_sdk.resource._errors import ManifestConfigurationError
from validio_sdk.scalars import JsonTypeDefinition


def load_jtd_schema(filepath: pathlib.Path) -> JsonTypeDefinition:
    """
    Reads a jtd schema from a file on disk.

    :param filepath: Path to the file containing the schema contents.
    """
    with pathlib.Path.open(filepath) as f:
        jtd_schema = json.load(f)
        if jtd_schema == {}:
            raise ManifestConfigurationError(
                f"invalid jtd_schema in file {filepath.absolute()}: "
                "schema cannot be empty"
            )

        # TODO: https://linear.app/validio/issue/VR-2073 Fix licence issue with jtd lib
        # try:
        #     jtd.Schema.from_dict(jtd_schema).validate()
        # except Exception as e:
        #     raise ManifestConfigurationError(
        #         f"invalid jtd_schema in file {filepath.absolute()}: {e}"
        #     )

        return jtd_schema


class ClassJSONEncoder(json.JSONEncoder):
    """Encoder for classes."""

    # ruff: noqa: PLR0911
    def default(self, o):
        """
        Default encoder implementation.

        :param o: The dataclass object

        :returns: JSON encoded data
        """
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)

        if isinstance(o, Enum):
            return o.value

        if isinstance(o, datetime | date):
            return o.isoformat()

        if hasattr(o, "asdict"):
            return o.asdict()

        if hasattr(o, "__dict__"):
            return o.__dict__

        try:
            return super().default(o)
        except TypeError:
            return str(o)
