# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ GENERAL IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from enum import Enum as _Enum
from typing import Any


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ ENUM
# └─────────────────────────────────────────────────────────────────────────────────────


class Enum(_Enum):
    """A base class for enum subclasses"""

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ __EQ__
    # └─────────────────────────────────────────────────────────────────────────────────

    def __eq__(self, other: Any) -> bool:
        """Equality Method"""

        # Handle enum-enum equality
        if isinstance(other, Enum):
            return True if other.value == self.value else False

        # Call super method
        return True if other == self.value else False

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ __HASH__
    # └─────────────────────────────────────────────────────────────────────────────────

    def __hash__(self) -> int:
        """Hash Method"""

        # Return hash
        return hash(self.value)


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ HTTP METHOD
# └─────────────────────────────────────────────────────────────────────────────────────


class HTTPMethod(Enum):
    """An enum class that represents the HTTP methods"""

    # Define DELETE enum
    DELETE = "DELETE"

    # Define GET enum
    GET = "GET"

    # Define PATCH enum
    PATCH = "PATCH"

    # Define POST enum
    POST = "POST"

    # Define PUT enum
    PUT = "PUT"
