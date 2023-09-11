# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ GENERAL IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

from typing import Any, TYPE_CHECKING

# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ PROJECT IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from core.api.classes.api import API
from core.api.classes.api_endpoint import APIEndpoint

if TYPE_CHECKING:
    from core.types import JSONSchema


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ API MIXIN
# └─────────────────────────────────────────────────────────────────────────────────────


class APIMixin:
    """A mixin for classes with API-related attributes and methods"""

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ CLASS ATTRIBUTES
    # └─────────────────────────────────────────────────────────────────────────────────

    # Declare type of API
    api: API

    # Initialize API base URL
    API_BASE_URL: str = ""

    # Initialize API endpoints
    API_ENDPOINTS: list[dict[str, str | JSONSchema]]

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ __INIT__
    # └─────────────────────────────────────────────────────────────────────────────────

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Init Method"""

        # Initialize and set API
        self.api = API(base_url=self.API_BASE_URL)

        # Initialize API endpoints
        if not hasattr(self, "API_ENDPOINTS"):
            self.API_ENDPOINTS = []

        # Iterate over API endpoints
        for api_endpoint_dict in self.API_ENDPOINTS:
            # Initialize an APIEndpoint instance
            api_endpoint = APIEndpoint.from_dict({**api_endpoint_dict, "api": self.api})

            # Push API endpoint
            api_endpoint.push()

        # Call super init method
        # NOTE: After to ensure other classes have access to api attribute
        super().__init__(*args, **kwargs)
