# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ GENERAL IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

from typing import Any, AsyncGenerator, Generator, TYPE_CHECKING, TypeVar
from urllib.parse import urlparse

# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ PROJECT IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from core.api.classes.api_store import api_store
from core.collections.classes.item import Item
from core.enums import HTTPMethod
from core.functions.dict import dfrom_json
from core.functions.object import ofrom_json

if TYPE_CHECKING:
    from core.api.classes.api import API
    from core.api.classes.api_response import APIResponse
    from core.types import JSON, JSONDict, JSONSchema

# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ TYPE VARIABLES
# └─────────────────────────────────────────────────────────────────────────────────────

T = TypeVar("T")


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ API ENDPOINT
# └─────────────────────────────────────────────────────────────────────────────────────


class APIEndpoint(Item):
    """A utility class that represents API endpoints"""

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ CLASS ATTRIBUTES
    # └─────────────────────────────────────────────────────────────────────────────────

    # Declare type of API
    api: API

    # Declare type of item
    item: str

    # Declare type of item class
    item_class: type | None = None

    # Declare type of method
    method: HTTPMethod

    # Declare type of route
    route: str

    # Declare type of base URL
    _base_url: str | None = None

    # Declare type of JSON path
    json_path: str | None = None

    # Declare type of JSONschema
    json_schema: JSONSchema | None

    # Declare type of JSON defaults
    json_defaults: dict[Any, Any] | None = None

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ __INIT__
    # └─────────────────────────────────────────────────────────────────────────────────

    def __init__(
        self,
        api: API,
        item: str,
        method: HTTPMethod | str,
        url: str | None = None,
        route: str | None = None,
        base_url: str | None = None,
        json_path: str | None = None,
        json_schema: JSONSchema | None = None,
        json_defaults: dict[Any, Any] | None = None,
        item_class: type | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialize the API endpoint"""

        # Check if no URL or route was provided
        if url is None and route is None:
            # Get class name
            class_name = self.__class__.__name__

            # Raise TypeError
            raise TypeError(f"{class_name}.__init__() requires either a URL or a route")

        # Call super init method
        super().__init__(*args, **kwargs)

        # Set API
        self.api = api

        # Set item
        self.item = item.lower().strip()

        # Set method
        self.method = HTTPMethod(method.upper()) if isinstance(method, str) else method

        # Check if URL is not null
        if url:
            # Lowercase and strip URL
            url = url.strip()

            # Parse the URL
            url_parsed = urlparse(url)

            # Extract the base URL
            base_url = f"{url_parsed.scheme}://{url_parsed.netloc}"

            # Extract the route
            route = url_parsed.path[1:]

        # Set route
        self.route = route.lower().strip() if route else ""

        # Set base URL
        self._base_url = base_url

        # Set JSON path
        self.json_path = json_path

        # Set JSON schema
        self.json_schema = json_schema

        # Set JSON defaults
        self.json_defaults = json_defaults

        # Set item class
        self.item_class = item_class

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ __STR__
    # └─────────────────────────────────────────────────────────────────────────────────

    def __str__(self) -> str:
        """String Method"""

        # Return the endpoint route
        return self.route

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ URL
    # └─────────────────────────────────────────────────────────────────────────────────

    @property
    def url(self) -> str:
        """Returns the URL for the endpoint"""

        # Construct and return the URL
        return self.api.construct_url(self.route, base_url=self.base_url)

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ BASE URL
    # └─────────────────────────────────────────────────────────────────────────────────

    @property
    def base_url(self) -> str:
        """Returns the base URL for the endpoint"""

        # Return the base URL
        return self._base_url if self._base_url is not None else self.api.base_url

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ FETCH ITEM DICTS
    # └─────────────────────────────────────────────────────────────────────────────────

    def fetch_item_dicts(
        self, path: Any = 0, schema: Any = 0, defaults: Any = 0
    ) -> Generator[JSONDict, None, None]:
        """Fetches item dicts from the endpoint"""

        # Get data
        data = self.request().json

        # Yield from request JSON
        yield from dfrom_json(
            data=data,
            path=path if path is None or isinstance(path, str) else self.json_path,
            schema=schema
            if schema is None or isinstance(schema, dict)
            else self.json_schema,
            defaults=defaults
            if defaults is None or isinstance(defaults, dict)
            else self.json_defaults,
        )

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ FETCH ITEM DICTS ASYNC
    # └─────────────────────────────────────────────────────────────────────────────────

    async def fetch_item_dicts_async(
        self, path: Any = 0, schema: Any = 0, defaults: Any = 0
    ) -> AsyncGenerator[JSONDict, None]:
        """Fetches item dicts from the endpoint"""

        # Get data
        data = await self.request_json_async()

        # Iterate over data
        for item in dfrom_json(
            data=data,
            path=path if path is None or isinstance(path, str) else self.json_path,
            schema=schema
            if schema is None or isinstance(schema, dict)
            else self.json_schema,
            defaults=defaults
            if defaults is None or isinstance(defaults, dict)
            else self.json_defaults,
        ):
            # Yield item
            yield item

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ FETCH ITEMS
    # └─────────────────────────────────────────────────────────────────────────────────

    def fetch_items(
        self,
        Class: type[T] | None = None,
        path: Any = 0,
        schema: Any = 0,
        defaults: Any = 0,
    ) -> Generator[T, None, None]:
        """Fetches items from the endpoint"""

        # Get item class
        Class = Class if Class is not None else self.item_class

        # Check if item class is null
        if Class is None:
            # Raise TypeError
            raise TypeError("APIEndpoint.item_class is not defined.")

        # Get data
        data = self.request_json()

        # Yield from request JSON
        yield from ofrom_json(
            Class=Class,
            data=data,
            path=path if path is None or isinstance(path, str) else self.json_path,
            schema=schema
            if schema is None or isinstance(schema, dict)
            else self.json_schema,
            defaults=defaults
            if defaults is None or isinstance(defaults, dict)
            else self.json_defaults,
        )

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ FETCH ITEMS ASYNC
    # └─────────────────────────────────────────────────────────────────────────────────

    async def fetch_items_async(
        self,
        Class: type[T] | None = None,
        path: Any = 0,
        schema: Any = 0,
        defaults: Any = 0,
    ) -> AsyncGenerator[T, None]:
        """Fetches items from the endpoint"""

        # Get item class
        Class = Class if Class is not None else self.item_class

        # Check if item class is null
        if Class is None:
            # Raise TypeError
            raise TypeError("APIEndpoint.item_class is not defined.")

        # Get data
        data = await self.request_json_async()

        # Iterate over data
        for item in ofrom_json(
            Class=Class,
            data=data,
            path=path if path is None or isinstance(path, str) else self.json_path,
            schema=schema
            if schema is None or isinstance(schema, dict)
            else self.json_schema,
            defaults=defaults
            if defaults is None or isinstance(defaults, dict)
            else self.json_defaults,
        ):
            # Yield item
            yield item

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ REQUEST
    # └─────────────────────────────────────────────────────────────────────────────────

    def request(self) -> APIResponse:
        """Make a synchronous HTTP request to the endpoint"""

        # Make request and return response
        return self.api.request(self.method, self.route, base_url=self.base_url)

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ REQUEST ASYNC
    # └─────────────────────────────────────────────────────────────────────────────────

    async def request_async(self) -> APIResponse:
        """Make an asynchronous HTTP request to the endpoint"""

        # Make request and return response
        return await self.api.request_async(
            self.method, self.route, base_url=self.base_url
        )

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ REQUEST JSON
    # └─────────────────────────────────────────────────────────────────────────────────

    def request_json(self) -> JSON:
        """Make a synchronous HTTP request to the endpoint and return JSON"""

        # Return request JSON
        return self.request().json

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ REQUEST JSON ASYNC
    # └─────────────────────────────────────────────────────────────────────────────────

    async def request_json_async(self) -> JSON:
        """Make an asynchronous HTTP request to the endpoint and return JSON"""

        # Return request JSON
        return (await self.request_async()).json

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ META
    # └─────────────────────────────────────────────────────────────────────────────────

    class Meta(Item.Meta):
        """Meta Class"""

        # Define items
        ITEMS = api_store.get_or_create("api_endpoints")
