# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ GENERAL IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generator, Generic, TYPE_CHECKING, TypeVar

# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ PROJECT IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from core.collections.classes.items import Items

if TYPE_CHECKING:
    from core.collections.classes.item import Item

# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ TYPE VARIABLES
# └─────────────────────────────────────────────────────────────────────────────────────

T = TypeVar("T", bound="Item")


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ COLLECTION
# └─────────────────────────────────────────────────────────────────────────────────────


class Collection(Generic[T], ABC):
    """An abstract class that represents a collection of items"""

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ ALL
    # └─────────────────────────────────────────────────────────────────────────────────

    def all(self) -> Items[T]:
        """Returns all items in the collection"""

        # Return all items
        return Items(collection=self)

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ APPLY
    # └─────────────────────────────────────────────────────────────────────────────────

    def apply(self, *operations: Any) -> Items[T]:
        """Applies operations to the collection"""

        # Return items
        return self.all().apply(*operations)

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ COLLECT
    # └─────────────────────────────────────────────────────────────────────────────────

    @abstractmethod
    def collect(
        self, operations: tuple[Any, ...] = (), expose: bool = False
    ) -> Generator[T, None, None]:
        """Yields items in the collection"""

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ COUNT
    # └─────────────────────────────────────────────────────────────────────────────────

    @abstractmethod
    def count(self, operations: tuple[Any, ...] = ()) -> int:
        """Returns a count of items in the collection"""

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ FILTER
    # └─────────────────────────────────────────────────────────────────────────────────

    @abstractmethod
    def filter(
        self,
        conditions: tuple[tuple[str, str, Any], ...],
        items: Items[T] | None = None,
    ) -> Items[T]:
        """Filters items in the collection"""

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ HEAD
    # └─────────────────────────────────────────────────────────────────────────────────

    @abstractmethod
    def head(self, n: int, operations: tuple[Any, ...] = ()) -> Items[T]:
        """Returns the first n items in the collection"""

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ KEYS
    # └─────────────────────────────────────────────────────────────────────────────────

    @abstractmethod
    def keys(self, keys: tuple[Any, ...], operations: tuple[Any, ...] = ()) -> Items[T]:
        """Returns items in the collection by key lookup"""

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ PUSH
    # └─────────────────────────────────────────────────────────────────────────────────

    @abstractmethod
    def push(self, item: T) -> None:
        """Pushes an item to the collection"""
