from datetime import datetime
from typing import Any, Callable, Dict

from validio_sdk.scalars import (
    BooleanFilter,
    EnumFilter,
    NullFilter,
    StringFilter,
    ThresholdFilter,
    serialize_json_filter_expression,
    serialize_rfc3339_datetime,
)

SCALARS_PARSE_FUNCTIONS: Dict[Any, Callable[[Any], Any]] = {}
SCALARS_SERIALIZE_FUNCTIONS: Dict[Any, Callable[[Any], Any]] = {
    datetime: serialize_rfc3339_datetime,
    BooleanFilter: serialize_json_filter_expression,
    EnumFilter: serialize_json_filter_expression,
    NullFilter: serialize_json_filter_expression,
    StringFilter: serialize_json_filter_expression,
    ThresholdFilter: serialize_json_filter_expression,
}
