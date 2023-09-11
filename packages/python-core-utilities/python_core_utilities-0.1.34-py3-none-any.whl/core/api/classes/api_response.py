# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ GENERAL IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

from typing import TYPE_CHECKING

# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ PROJECT IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

if TYPE_CHECKING:
    from core.types import JSON, JSONDict, JSONList, JSONValue


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ API RESPONSE
# └─────────────────────────────────────────────────────────────────────────────────────


class APIResponse:
    """A utility class that represents API responses"""

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ CLASS ATTRIBUTES
    # └─────────────────────────────────────────────────────────────────────────────────

    # Declare type of status code
    status_code: int

    # Declare type of JSON
    json: JSON

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ __INIT__
    # └─────────────────────────────────────────────────────────────────────────────────

    def __init__(self, status_code: int, json: JSON = None) -> None:
        """Init Method"""

        # Set status code
        self.status_code = status_code

        # Set JSON
        self.json = json

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ JSON DICT
    # └─────────────────────────────────────────────────────────────────────────────────

    @property
    def json_dict(self) -> JSONDict:
        """Return the JSON response as a dictionary"""

        # Return JSON as dict
        return self.json if isinstance(self.json, dict) else {}

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ JSON LIST
    # └─────────────────────────────────────────────────────────────────────────────────

    @property
    def json_list(self) -> JSONList:
        """Return the JSON response as a list"""

        # Return JSON as list
        return self.json if isinstance(self.json, list) else []

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ JSON VALUE
    # └─────────────────────────────────────────────────────────────────────────────────

    @property
    def json_value(self) -> JSONValue:
        """Return the JSON response as a value"""

        # Return JSON as value
        return self.json if not isinstance(self.json, (dict, list)) else None
