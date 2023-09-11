# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ GENERAL IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

from typing import Any, Generator, TYPE_CHECKING

# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ PROJECT IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from core.placeholders import Nothing

if TYPE_CHECKING:
    from core.types import JSONDict, JSONSchema


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ DFROM JSON
# └─────────────────────────────────────────────────────────────────────────────────────


def dfrom_json(
    data: Any,
    path: str | None = None,
    schema: JSONSchema | None = None,
    defaults: dict[Any, Any] | None = None,
) -> Generator[JSONDict, None, None]:
    """Initializes an item from a JSON object"""

    # Check if should get data from path
    if isinstance(data, dict) and path is not None:
        # Get data from path
        data = dget(data, path, delimiter=".")

    # Check if data is a dictionary
    if isinstance(data, dict):
        # Convert to list
        data = [data]

    # Check if data is a list
    if isinstance(data, list):
        # Iterate over data
        for item in data:
            # Check if schema is not None
            if schema is not None:
                # Get item from schema
                item = dfrom_schema(item, schema=schema, defaults=defaults)

            # Yield item
            yield item


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ DFROM SCHEMA
# └─────────────────────────────────────────────────────────────────────────────────────


def dfrom_schema(
    data: dict[Any, Any], schema: JSONSchema, defaults: dict[Any, Any] | None = None
) -> dict[Any, Any]:
    """Remaps a dictionary using a schema"""

    # Initialize root data
    root_data = data

    # Initialize mapped data
    mapped_data: dict[Any, Any] = defaults or {}

    # Check if schema is not None
    if schema is not None:
        # Iterate over schema
        for setter, getter in (schema or {}).items():
            # Check if getter is callable
            if callable(getter):
                # Get value to set
                value_to_set = getter(root_data, data)

            # Otherwise handle case of string path
            else:
                # Get value to set
                value_to_set = dget(data, getter, delimiter=".")

            # Set value to set to mapped data
            dset(mapped_data, setter, value_to_set)

    # Return mapped data
    return mapped_data


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ DGET
# └─────────────────────────────────────────────────────────────────────────────────────


def dget(
    dictionary: dict[Any, Any], path: str, default: Any = Nothing, delimiter: str = "."
) -> Any:
    """Gets a value from a nested dictionary using a path string"""

    # Initialize value
    value = default

    # Iterate over keys
    for key in path.split(delimiter):
        # Check if key exists or no default is given
        if key in dictionary or default is Nothing:
            # Get value by key and set dictionary
            value = dictionary = dictionary[key]

        # Otherwise return default
        else:
            return default

    # Return value
    return value


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ DPOP
# └─────────────────────────────────────────────────────────────────────────────────────


def dpop(
    dictionary: dict[Any, Any], path: str, default: Any = Nothing, delimiter: str = "."
) -> Any:
    """Pops a value from a nested dictionary using a path string"""

    # Split the path into keys
    keys = path.split(delimiter)

    # Initialize value
    value = default

    # Iterate over keys
    for key in keys[:-1]:
        # Check if key exists or no default is given
        if key in dictionary or default is Nothing:
            # Get value by key and set dictionary
            dictionary = dictionary[key]

        # Otherwise return default
        else:
            return default

    # Check if key exists or no default is given
    if keys[-1] in dictionary or default is Nothing:
        # Pop value by last key
        value = dictionary.pop(keys[-1])

    # Return value
    return value


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ DSET
# └─────────────────────────────────────────────────────────────────────────────────────


def dset(
    dictionary: dict[Any, Any], path: Any, value: Any, delimiter: str = "."
) -> None:
    """Sets a value in a nested dictionary using a path string"""

    # Check if the path is a tuple
    if isinstance(path, tuple):
        # Check if the value to set is not a tuple or list
        if not isinstance(value, (tuple, list)):
            # Convert value to set to a list
            value = [value] * len(path)

        # Iterate over zip of path and value to set
        for path_i, value_i in zip(path, value):
            # Remap data
            dset(dictionary, path_i, value_i)

    # Otherwise, handle case of string path
    elif isinstance(path, str):
        # Split the path into keys
        keys = path.split(delimiter)

        # Iterate over keys
        for key in keys[:-1]:
            # Check if key exists
            if key not in dictionary:
                # Set key to empty dictionary
                dictionary[key] = {}

            # Get value by key
            dictionary = dictionary[key]

        # Set value by last key
        dictionary[keys[-1]] = value

    # Otherwise, handle general case
    else:
        # Set value by path
        dictionary[path] = value
