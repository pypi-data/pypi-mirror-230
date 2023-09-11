# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ GENERAL IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, Iterator, TYPE_CHECKING, TypeVar

# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ PROJECT IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from core.collections.exceptions import DoesNotExistError, DuplicateKeyError
from core.functions.datetime import utc_now

if TYPE_CHECKING:
    from core.collections.classes.collection import Collection
    from core.collections.classes.item import Item

# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ TYPE VARIABLES
# └─────────────────────────────────────────────────────────────────────────────────────

T = TypeVar("T", bound="Item")


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ ITEMS
# └─────────────────────────────────────────────────────────────────────────────────────


class Items(Generic[T]):
    """A utility class that represents a collection of Item instances"""

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ CLASS ATTRIBUTES
    # └─────────────────────────────────────────────────────────────────────────────────

    # Declare type of children
    _children: tuple[Items[T], ...]

    # Declare type of collection
    _collection: Collection[T]

    # Declare type of operations
    _operations: tuple[Any, ...]

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ __INIT__
    # └─────────────────────────────────────────────────────────────────────────────────

    def __init__(self, collection: Collection[T]):
        """Init Method"""

        # Initialize children
        self._children = ()

        # Set collection
        self._collection = collection

        # Initialize operations
        self._operations = ()

    # ┌────────────────────────────────────────────────────────────────────────────────
    # │ __ITER__
    # └─────────────────────────────────────────────────────────────────────────────────

    def __iter__(self) -> Iterator[T]:
        """Iter Method"""

        # Yield from collection
        yield from self._collect()

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ __REPR__
    # └─────────────────────────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        """Representation Method"""

        # Initialize representation to class name
        representation = self.__class__.__name__

        # Get item count
        count = self.count()

        # Add count to representation
        representation += f": {count}"

        # Define n
        n = 20

        # Get head
        head = self.head(n=n)

        # Get items
        items = [item.__repr__() for item in head._expose()]

        # Check if there are more than n items total
        if count > n:
            # Add truncation message to items list
            items.append("...(remaining items truncated)... ")

        # Add items to representation
        representation = f"{representation} {'[' + ', '.join(items) + ']'}"

        # Add angle brackets to the representation
        representation = f"<{representation}>"

        # Return representation
        return representation

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ _CLEAN KEYS
    # └─────────────────────────────────────────────────────────────────────────────────

    def _clean_keys(self, keys: tuple[Any, ...]) -> tuple[Any, ...]:
        """Cleans a series of key lookups"""

        # Return keys
        return keys

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ _COLLECT
    # └─────────────────────────────────────────────────────────────────────────────────

    def _collect(
        self, pulled_at: datetime | None = None, expose: bool = False
    ) -> Iterator[T]:
        """Returns an iterator of items"""

        # Get pulled at
        pulled_at = pulled_at if pulled_at is not None else utc_now()

        # Iterate over collectio
        for item in self._collection.collect(
            operations=self._operations, expose=expose
        ):
            # Set pulled at
            item._imeta.pulled_at = pulled_at

            # Yield item
            yield item

        # Iterate over children
        for child in self._children:
            # Yield from child
            yield from child._collect(pulled_at=pulled_at, expose=expose)

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ _EXPOSE
    # └─────────────────────────────────────────────────────────────────────────────────

    def _expose(self) -> Iterator[T]:
        """Returns an iterator of items"""

        # Yield from collection
        yield from self._collect(expose=True)

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ APPLY
    # └─────────────────────────────────────────────────────────────────────────────────

    def apply(self, *operations: Any) -> Items[T]:
        """Applies a series of operations to a collection of items"""

        # Apply operations
        self._operations += operations

        # Return self
        return self

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ COUNT
    # └─────────────────────────────────────────────────────────────────────────────────

    def count(self) -> int:
        """Returns a count of items in the collection"""

        # Initialize count
        count = self._collection.count(operations=self._operations)

        # Iterate over children
        for child in self._children:
            # Increment count
            count += child.count()

        # Return count
        return count

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ FILTER
    # └─────────────────────────────────────────────────────────────────────────────────

    def filter(self, **kwargs: Any) -> Items[T]:
        """Returns a filtered collection of items"""

        # Define operators
        operators = {
            "contains": "contains",
            "icontains": "icontains",
            "eq": "equals",
            "ieq": "iequals",
            "equals": "equals",
            "iequals": "iequals",
            "exact": "equals",
            "iexact": "iequals",
            "gt": "gt",
            "gte": "gte",
            "in": "in",
            "iin": "iin",
            "lt": "lt",
            "lte": "lte",
        }

        # Initialize conditions
        conditions = []

        # Iterate over kwargs
        for key, value in kwargs.items():
            # Split key
            key_split = key.split("__")

            # Get operator
            operator = key_split[-1]

            # Check if operator is in operators
            if operator in operators:
                # Remove operator suffix from key
                key = key.removesuffix(f"__{operator}")

                # Append condition to conditions and break
                conditions.append((key, operators[operator], value))

            # Otherwise set default operator
            else:
                # Append condition to conditions
                conditions.append((key, "equals", value))

        # Initialize and return a filtered collection of items
        return self._collection.filter(tuple(conditions), items=self)

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ HEAD
    # └─────────────────────────────────────────────────────────────────────────────────

    def head(self, n: int = 10) -> Items[T]:
        """Returns the first n items in the collection"""

        # Get head
        head = self._collection.head(n=n, operations=self._operations)

        # Decrement n
        n -= head._collection.count(operations=head._operations)

        # Get children
        children = []

        # Iterate over children
        for child in self._children:
            # Break if n is less than or equal to 0
            if n <= 0:
                break

            # Get child head
            child = child.head(n=n)

            # Decrement n
            n -= child.count()

            # Append child to children
            children.append(child)

        # Set children
        head._children = tuple(children)

        # Return head
        return head

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ KEY
    # └─────────────────────────────────────────────────────────────────────────────────

    def key(self, key: Any) -> T:
        """Returns an item int the collection by key lookup"""

        # Initialize item to None
        item = None

        # Iterate over items
        for _item in self.keys(key):
            # Check if item is not None
            if item is not None:
                # Raise DuplicateKeyError
                raise DuplicateKeyError(f"Multiple items with the key '{key}' found.")

            # Set item
            item = _item

        # Check if item is None
        if item is None:
            # Raise DoesNotExistError
            raise DoesNotExistError(f"No item with the key '{key}' found.")

        # Return item
        return item

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ KEYS
    # └─────────────────────────────────────────────────────────────────────────────────

    def keys(self, *keys: Any) -> Items[T]:
        """Returns items in the collection by key lookup"""

        # Clean keys
        keys = self._clean_keys(keys)

        # Get items
        items = self._collection.keys(keys=keys, operations=self._operations)

        # Get children
        children = []

        # Iterate over children
        for child in self._children:
            # Get child items by key
            child = child.keys(*keys)

            # Append child to children
            children.append(child)

        # Set children
        items._children = tuple(children)

        # Return items
        return items

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ PUSH
    # └─────────────────────────────────────────────────────────────────────────────────

    def push(self, item: T) -> None:
        """Pushes an item to the collection"""

        # Push item to collection
        self._collection.push(item=item)

        # Update pushed at timestamp
        item._imeta.pushed_at = utc_now()
