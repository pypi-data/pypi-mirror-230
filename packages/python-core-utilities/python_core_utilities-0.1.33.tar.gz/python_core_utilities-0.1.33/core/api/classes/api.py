# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ GENERAL IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import posixpath
import requests

from json.decoder import JSONDecodeError
from typing import Any, TYPE_CHECKING

try:
    import aiohttp
except ImportError:
    aiohttp = None  # type: ignore

# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ PROJECT IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from core.api.classes.api_endpoint import APIEndpoint
from core.api.classes.api_response import APIResponse
from core.api.classes.api_store import api_store
from core.api.classes.api_transaction import APITransaction
from core.collections.classes.item import Item
from core.enums import HTTPMethod

if TYPE_CHECKING:
    from core.collections.classes.items import Items


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ API
# └─────────────────────────────────────────────────────────────────────────────────────


class API(Item):
    """A utility class that represents API clients"""

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ CLASS ATTRIBUTES
    # └─────────────────────────────────────────────────────────────────────────────────

    # Declare type of base URL
    BASE_URL: str

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ __INIT__
    # └─────────────────────────────────────────────────────────────────────────────────

    def __init__(self, base_url: str) -> None:
        """Init Method"""

        # Set the base URL
        self.BASE_URL = base_url

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ __GETATTR__
    # └─────────────────────────────────────────────────────────────────────────────────

    def __getattr__(self, name: str) -> Items[APIEndpoint]:
        """Getattr Method"""

        # Define endpoints suffix
        endpoints_suffix = "_endpoints"

        # Check if the name ends with endpoints suffix
        if name.endswith(endpoints_suffix):
            # Return endpoints filtered by item
            return self.endpoints.filter(item=name[: -len(endpoints_suffix)])

        # Rasie an AttributeError
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ BASE URL
    # └─────────────────────────────────────────────────────────────────────────────────

    @property
    def base_url(self) -> str:
        """Returns the base URL of the API class"""
        return self.BASE_URL

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ ENDPOINTS
    # └─────────────────────────────────────────────────────────────────────────────────

    @property
    def endpoints(self) -> Items[APIEndpoint]:
        """Returns a list of endpoints of the API instance"""
        return APIEndpoint.items.filter(api=self)

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ CONSTRUCT URL
    # └─────────────────────────────────────────────────────────────────────────────────

    def construct_url(self, *route: str, base_url: str | None = None) -> str:
        """Constructs a URL from the base URL and endpoint"""

        # Get base URL
        base_url = base_url or self.base_url

        # Construct URL
        url = posixpath.join(base_url, *route)

        # Return URL
        return url

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ REQUEST
    # └─────────────────────────────────────────────────────────────────────────────────

    def request(
        self,
        method: HTTPMethod,
        *route: str,
        params: dict[str, Any] | None = None,
        base_url: str | None = None,
    ) -> APIResponse:
        """Makes a synchronous HTTP request"""

        # Initialize params
        params = params or {}

        # Construct URL
        url = self.construct_url(*route, base_url=base_url)

        # Initialize APITransaction instance
        transaction = APITransaction(url=url, method=method)

        # Get make request function
        make_request = {
            HTTPMethod.GET: requests.get,
        }.get(method, requests.get)

        # Make request
        response = make_request(url, params=params)

        # Initialize try-except block
        try:
            # Get JSON data
            json = response.json()

        # Handle JSONDecodeError
        except JSONDecodeError:
            # Set JSON data to None
            json = None

        # Initialize APIResponse instance and set transaction response
        transaction.response = APIResponse(status_code=response.status_code, json=json)

        # Return API response
        return transaction.response

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ REQUEST ASYNC
    # └─────────────────────────────────────────────────────────────────────────────────

    async def request_async(
        self,
        method: HTTPMethod,
        *route: str,
        params: dict[str, Any] | None = None,
        base_url: str | None = None,
    ) -> APIResponse:
        """Makes an asynchronous HTTP request"""

        # Check if aiohttp is not installed
        if aiohttp is None:
            # Raise ImportError
            raise ImportError("Library 'aiohttp' is not installed.")

        # Initialize params
        params = params or {}

        # Construct URL
        url = self.construct_url(*route, base_url=base_url)

        # Initialize APITransaction instance
        transaction = APITransaction(url=url, method=method)

        # Make GET request
        async with aiohttp.ClientSession() as session:
            # Get make request function
            make_request = {
                HTTPMethod.GET: session.get,
            }.get(method, session.get)

            # Get response
            async with make_request(url, params=params) as response:
                # Initialize try-except block
                try:
                    # Get JSON
                    json = await response.json(content_type=None)

                # Handle JSONDecodeError
                except JSONDecodeError:
                    # Set JSON data to None
                    json = None

        # Initialize APIResponse instance and set transaction response
        transaction.response = APIResponse(status_code=response.status, json=json)

        # Return API response
        return transaction.response

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ GET
    # └─────────────────────────────────────────────────────────────────────────────────

    def get(
        self,
        *route: str,
        params: dict[str, Any] | None = None,
        base_url: str | None = None,
    ) -> APIResponse:
        """Makes a synchronous HTTP GET request"""

        # Make GET request and return response
        return self.request(
            HTTPMethod.GET,
            *route,
            params=params,
            base_url=base_url,
        )

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ GET ASYNC
    # └─────────────────────────────────────────────────────────────────────────────────

    async def get_async(
        self,
        *route: str,
        params: dict[str, Any] | None = None,
        base_url: str | None = None,
    ) -> APIResponse:
        """Makes an asynchronous HTTP GET request"""

        # Make GET request and return response
        return await self.request_async(
            HTTPMethod.GET,
            *route,
            params=params,
            base_url=base_url,
        )

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ META
    # └─────────────────────────────────────────────────────────────────────────────────

    class Meta(Item.Meta):
        """Meta Class"""

        # Define items
        ITEMS = api_store.get_or_create("apis")
