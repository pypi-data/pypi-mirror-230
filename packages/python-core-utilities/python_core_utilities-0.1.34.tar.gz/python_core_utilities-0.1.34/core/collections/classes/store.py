# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ GENERAL IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from abc import ABC
from typing import Any, TYPE_CHECKING, TypeVar

# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ PROJECT IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from core.collections.classes.collection import Collection
from core.collections.dict_collection import DictCollection
from core.collections.exceptions import DoesNotExistError

if TYPE_CHECKING:
    from core.collections.classes.item import Item

# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ TYPE VARIABLES
# └─────────────────────────────────────────────────────────────────────────────────────

T = TypeVar("T", bound="Item")


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ STORE
# └─────────────────────────────────────────────────────────────────────────────────────


class Store(ABC):
    """An abstract class that represents a store that houses collections of items"""

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ CLASS ATTRIBUTES
    # └─────────────────────────────────────────────────────────────────────────────────

    # Initialize collection class
    CollectionClass: type[Collection[Any]] = DictCollection

    # Declare type of collections by key
    _collections_by_key: dict[str, Collection[Any]]

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ __INIT__
    # └─────────────────────────────────────────────────────────────────────────────────

    def __init__(self) -> None:
        """Init Method"""

        # Initialize collections by key
        self._collections_by_key = {}

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ CREATE
    # └─────────────────────────────────────────────────────────────────────────────────

    def create(
        self,
        key: str,
        CollectionClass: type[Collection[T]] | Collection[T] | None = None,
    ) -> Collection[T]:
        """Creates a collection by key"""

        # Initialize collection class
        CollectionClass = CollectionClass or self.CollectionClass

        # Initialize collection istance
        collection = (
            CollectionClass
            if isinstance(CollectionClass, Collection)
            else CollectionClass()
        )

        # Add collection to store
        self._collections_by_key[key] = collection

        # Return collection
        return collection

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ DELETE
    # └─────────────────────────────────────────────────────────────────────────────────

    def delete(self, key: str) -> None:
        """Deletes a collection by key"""

        # Delete collection
        del self._collections_by_key[key]

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ GET
    # └─────────────────────────────────────────────────────────────────────────────────

    def get(self, key: str) -> Collection[Any]:
        """Returns a collection by key"""

        # Check if collection exists
        if key in self._collections_by_key:
            # Return collection
            return self._collections_by_key[key]

        # Raise DoesNotExistError
        raise DoesNotExistError(f"A collection with key '{key}' does not exist")

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ GET OR CREATE
    # └─────────────────────────────────────────────────────────────────────────────────

    def get_or_create(
        self,
        key: str,
        CollectionClass: type[Collection[T]] | Collection[T] | None = None,
    ) -> Collection[T]:
        """Returns a collection by key, creating it if it doesn't exist"""

        # Initialize try-except block
        try:
            # Return collection
            return self.get(key=key)

        # Handle DoesNotExistError
        except DoesNotExistError:
            # Create collection
            return self.create(key=key, CollectionClass=CollectionClass)
