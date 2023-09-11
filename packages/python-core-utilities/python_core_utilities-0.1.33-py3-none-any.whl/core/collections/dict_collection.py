# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ GENERAL IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

from copy import deepcopy
from typing import Any, Generator, Iterable, TYPE_CHECKING, TypeVar

# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ PROJECT IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from core.collections.classes.collection import Collection
from core.collections.exceptions import DuplicateKeyError
from core.functions.object import oget

if TYPE_CHECKING:
    from core.collections.classes.item import Item
    from core.collections.classes.items import Items

# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ TYPE VARIABLES
# └─────────────────────────────────────────────────────────────────────────────────────

T = TypeVar("T", bound="Item")


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ DICT COLLECTION
# └─────────────────────────────────────────────────────────────────────────────────────


class DictCollection(Collection[T]):
    """A utility class that represents a dictionary collection of items"""

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ INSTANCE ATTRIBUTES
    # └─────────────────────────────────────────────────────────────────────────────────

    # Initialize item ID
    _item_id: int

    # Declare type of items by ID
    _items_by_id: dict[int, T]

    # Declare type of item IDs by key
    _item_ids_by_key: dict[Any, int]

    # Declare type of keys by item ID
    _keys_by_item_id: dict[int, set[Any]]

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ __INIT__
    # └─────────────────────────────────────────────────────────────────────────────────

    def __init__(self) -> None:
        """Init Method"""

        # Initialize item ID
        self._item_id = 0

        # Initialize items by ID
        self._items_by_id = {}

        # Initialize item IDs by key
        self._item_ids_by_key = {}

        # Initialize keys by item ID
        self._keys_by_item_id = {}

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ _COMPARE
    # └─────────────────────────────────────────────────────────────────────────────────

    def _compare(self, left: Any, right: Any, operator: str) -> bool | None:
        """Returns a boolean comparison of two values based on an operator"""

        # Initialize try-except block
        try:
            # Handle case of equal to
            if operator == "equals":
                return left == right  # type: ignore

            # Otherwise, handle case of less than
            if operator == "lt":
                return left < right  # type: ignore

            # Otherwise handle case of less than or equal to
            elif operator == "lte":
                return left <= right  # type: ignore

            # Otherwise handle case of greater than
            elif operator == "gt":
                return left > right  # type: ignore

            # Otherwise handle case of greater than or equal to
            elif operator == "gte":
                return left >= right  # type: ignore

        # Handle TypeError
        except TypeError:
            pass

        # Return None by default
        return None

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ _EXPOSE ITEM
    # └─────────────────────────────────────────────────────────────────────────────────

    def _expose_item(self, item: T) -> T:
        """Exposes an item from the collection"""

        # Check if item has an ID
        if item._imeta.id is not None:
            # Get item ID
            item_id = int(item._imeta.id)

            # Check if item ID is in items by ID
            if item_id in self._items_by_id:
                # Return item
                return self._items_by_id[item_id]

        # Return item
        return item

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ COLLECT
    # └─────────────────────────────────────────────────────────────────────────────────

    def collect(
        self, operations: tuple[Any, ...] = (), expose: bool = False
    ) -> Generator[T, None, None]:
        """Yields items in the collection"""

        # Initialize collected items
        collected = iter(self._items_by_id.values())

        # Iterate over operations
        for operation in operations:
            # Check if callable
            if callable(operation):
                # Apply operation to collected
                collected = operation(collected)

        # Iterate over collected items
        for item in collected:
            # Deepcopy and yield item
            yield item if expose else deepcopy(item)

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ COUNT
    # └─────────────────────────────────────────────────────────────────────────────────

    def count(self, operations: tuple[Any, ...] = ()) -> int:
        """Returns a count of items in the collection"""

        # Return the number of items in the collection
        return sum(1 for _ in self.collect(operations=operations, expose=True))

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ FILTER
    # └─────────────────────────────────────────────────────────────────────────────────

    def filter(
        self,
        conditions: tuple[tuple[str, str, Any], ...],
        items: Items[T] | None = None,
    ) -> Items[T]:
        """Returns a filtered collection of items"""

        def operation(items: Generator[T, None, None]) -> Generator[T, None, None]:
            """Yields items filtered from the collection"""

            # Iterate over items
            for item in items:
                # Iterate over kwargs
                for attr, operator, expected in conditions:
                    # Get actual value
                    actual = oget(item, attr, delimiter="__")

                    # Handle case of equals
                    if operator in ("equals", "iequals"):
                        # Check if case-insensitive equals
                        if (
                            operator == "iequals"
                            and isinstance(actual, str)
                            and isinstance(expected, str)
                        ):
                            # Set actual and expected to lowercase
                            actual = actual.lower()
                            expected = expected.lower()

                        # Break if actual does not equal expected
                        if actual != expected:
                            break

                    # Otherwise handle case of less than
                    elif operator in ("lt", "lte", "gt", "gte"):
                        # Break if item comparison evaluates to False
                        if not self._compare(
                            left=actual, right=expected, operator=operator
                        ):
                            break

                    # Otherwise handle case of in
                    elif operator in ("in", "iin"):
                        # Check if case-insensitive in
                        if operator == "iin" and isinstance(actual, str):
                            # Set actual to lowercase
                            actual = actual.lower()

                            # Check if expected is a string
                            if isinstance(expected, str):
                                # Set expected to lowercase
                                expected = expected.lower()

                            # Otherwise check if expected is an iterable
                            elif isinstance(expected, Iterable):
                                # Lowercase each item in expected
                                expected = set(
                                    x.lower() if isinstance(x, str) else x
                                    for x in expected
                                )

                        # Break if actual not in expected
                        if actual not in expected:
                            break

                    # Otherwise handle case of contains
                    elif operator in ("contains", "icontains"):
                        # Check if case-insensitive contains
                        if operator == "icontains" and isinstance(expected, str):
                            # Set expected to lowercase
                            expected = expected.lower()

                            # Check if actual is a string
                            if isinstance(actual, str):
                                # Set actual to lowercase
                                actual = actual.lower()

                            # Otherwise check if actual is an iterable
                            elif isinstance(actual, Iterable):
                                # Lowercase each item in actual
                                actual = set(
                                    x.lower() if isinstance(x, str) else x
                                    for x in actual
                                )

                        # Break if expected not in actual
                        if expected not in actual:
                            break

                # Otherwise yield item
                else:
                    yield item

        # Apply filter operation to items
        return self.apply(items, lambda x: operation(x))

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ HEAD
    # └─────────────────────────────────────────────────────────────────────────────────

    def _head(
        self, n: int, items: Generator[T, None, None]
    ) -> Generator[T, None, None]:
        """Yields the first n items in the collection"""

        # Iterate over items
        for i, item in enumerate(items):
            # Check if i is greater than or equal to n
            if i >= n:
                # Break
                break
            # Yield item
            yield item

    def head(self, n: int, operations: tuple[Any, ...] = ()) -> Items[T]:
        """Returns the first n items in the collection"""

        # Apply head operation to items
        return self.apply(*operations, lambda items: self._head(n=n, items=items))

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ KEYS
    # └─────────────────────────────────────────────────────────────────────────────────

    def _keys(
        self, keys: tuple[Any, ...], items: Generator[T, None, None]
    ) -> Generator[T, None, None]:
        """Yields items in the collection by key lookup"""

        # Iterate over keys
        for key in keys:
            # Continue if key is not in item IDs by key
            if key not in self._item_ids_by_key:
                continue

            # Get item ID
            item_id = self._item_ids_by_key[key]

            # Yield item
            yield self._items_by_id[item_id]

    def keys(self, keys: tuple[Any, ...], operations: tuple[Any, ...] = ()) -> Items[T]:
        """Returns items in the collection by key lookup"""

        # Apply keys operation to items
        return self.apply(lambda items: self._keys(keys=keys, items=items), *operations)

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ PUSH
    # └─────────────────────────────────────────────────────────────────────────────────

    def push(self, item: T) -> None:
        """Pushes an item to the collection"""

        # Check if item already has an ID
        if item._imeta.id is not None:
            # Set creating to False
            is_creating = False

            # Get item ID
            item_id = int(item._imeta.id)

            # Iterate over values
            for value in self._keys_by_item_id.pop(item_id, []):
                # Remove item ID from item IDs by key
                del self._item_ids_by_key[value]

        # Otherwise, handle case of new item
        else:
            # Set creating to True
            is_creating = True

            # Increment item ID
            self._item_id += 1

            # Return item ID
            item_id = self._item_id

        # Initialize keys
        keys = []

        # Iterate over key attriubutes
        for attr in item._cmeta.KEYS:
            # Get key
            key = (
                tuple([getattr(item, a, None) for a in attr])
                if isinstance(attr, tuple)
                else getattr(item, attr, None)
            )

            # Check if key is in item IDs by key
            if key in self._item_ids_by_key:
                # Raise a duplicate key error
                raise DuplicateKeyError(f"An item with the key '{key}' already exists.")

            # Append key to keys
            keys.append(key)

        # Iterate over keys
        for key in keys:
            # Add item ID to item IDs by key
            self._item_ids_by_key[key] = item_id

            # Add value to keys by item ID
            self._keys_by_item_id.setdefault(item_id, set()).add(key)

        # Update item ID
        item._imeta.id = str(item_id)

        # Check if creating
        if is_creating:
            # Deepcopy item
            item = deepcopy(item)

        # Otherwise, handle case of updating
        else:
            # Get item dict
            item_dict = item.__dict__

            # Expose item
            item = self._expose_item(item)

            # Update item dict
            item.__dict__.update(deepcopy(item_dict))

        # Add item to items by ID
        self._items_by_id[item_id] = item
