# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ GENERAL IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from typing import Any, Generator, TypeVar

# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ PROJECT IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from core.functions.dict import dfrom_json
from core.placeholders import Nothing
from core.types import JSONSchema

# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ TYPE VARIABLES
# └─────────────────────────────────────────────────────────────────────────────────────

T = TypeVar("T")


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ OFROM DICT
# └─────────────────────────────────────────────────────────────────────────────────────


def ofrom_dict(Class: type[T], data: dict[Any, Any]) -> T:
    """Initializes an item from a dictionary"""

    # Initialize item
    item = Class(**data)

    # Return item
    return item


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ OFROM JSON
# └─────────────────────────────────────────────────────────────────────────────────────


def ofrom_json(
    Class: type[T],
    data: Any,
    path: str | None = None,
    schema: JSONSchema | None = None,
    defaults: dict[Any, Any] | None = None,
) -> Generator[T, None, None]:
    """Initializes an item from a JSON object"""

    # Iterate over data
    for data in dfrom_json(data=data, path=path, schema=schema, defaults=defaults):
        # Yield item from data
        yield ofrom_dict(Class=Class, data=data)


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ OGET
# └─────────────────────────────────────────────────────────────────────────────────────


def oget(obj: Any, path: str, default: Any = Nothing, delimiter: str = ".") -> Any:
    """Gets a nest value from a Python object using a path string"""

    # Initialize value
    value = default

    # Iterate over attributes
    for attr in path.split(delimiter):
        # Check if object has attribute or no default is given
        if hasattr(obj, attr) or default is Nothing:
            # Get attribute and set object
            value = obj = getattr(obj, attr)

        # Otherwise return default
        else:
            return default

    # Return value
    return value
