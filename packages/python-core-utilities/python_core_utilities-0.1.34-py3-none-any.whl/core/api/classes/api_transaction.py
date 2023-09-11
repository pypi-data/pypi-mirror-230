# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ GENERAL IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

from typing import TYPE_CHECKING

# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ PROJECT IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from core.api.classes.api_request import APIRequest

if TYPE_CHECKING:
    from core.api.classes.api_response import APIResponse
    from core.enums import HTTPMethod


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ API TRANSACTION
# └─────────────────────────────────────────────────────────────────────────────────────


class APITransaction:
    """A utility class that represents API requests"""

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ CLASS ATTRIBUTES
    # └─────────────────────────────────────────────────────────────────────────────────

    # Declare type of request
    request: APIRequest | None

    # Declare type of response
    response: APIResponse | None

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ __INIT__
    # └─────────────────────────────────────────────────────────────────────────────────

    def __init__(
        self,
        request: APIRequest | None = None,
        response: APIResponse | None = None,
        url: str | None = None,
        method: HTTPMethod | None = None,
    ) -> None:
        """Init Method"""

        # Check if request is None and should be initialized
        if request is None and url is not None and method is not None:
            # Create request
            request = APIRequest(method=method, url=url)

        # Set request
        self.request = request

        # Set response
        self.response = response

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ __STR__
    # └─────────────────────────────────────────────────────────────────────────────────

    def __str__(self) -> str:
        """String Method"""

        # Initialize string to method
        string = self.method.value if self.method is not None else "PENDING"

        # Check if URL is available
        if self.url is not None:
            # Append URL to string
            string += f" | {self.url} "

        # Return string representation
        return string

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ IS COMPLETE
    # └─────────────────────────────────────────────────────────────────────────────────

    @property
    def is_complete(self) -> bool:
        """Returns a boolean indicating if the transaction is complete"""

        # Return whether both request and response are complete
        return self.request is not None and self.response is not None

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ METHOD
    # └─────────────────────────────────────────────────────────────────────────────────

    @property
    def method(self) -> HTTPMethod | None:
        """Returns the method of the request"""

        # Return request method
        return self.request.method if self.request is not None else None

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ URL
    # └─────────────────────────────────────────────────────────────────────────────────

    @property
    def url(self) -> str | None:
        """Returns the URL of the request"""

        # Return request URL
        return self.request.url if self.request is not None else None
