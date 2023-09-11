# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ GENERAL IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

from typing import Any, Generator, TYPE_CHECKING, TypeVar

# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ PROJECT IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from core.collections.classes.item_meta import ClassMeta
from core.collections.classes.item_metaclass import ItemMetaclass
from core.functions.object import ofrom_dict, ofrom_json

if TYPE_CHECKING:
    from core.collections.classes.collection import Collection
    from core.collections.classes.item_meta import InstanceMeta
    from core.collections.classes.items import Items
    from core.types import JSONSchema

# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ TYPE VARIABLES
# └─────────────────────────────────────────────────────────────────────────────────────

T = TypeVar("T", bound="Item")


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ ITEM
# └─────────────────────────────────────────────────────────────────────────────────────


class Item(metaclass=ItemMetaclass):
    """A utility class that represents an arbitrary Python object"""

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ INSTANCE ATTRIBUTES
    # └─────────────────────────────────────────────────────────────────────────────────

    # Declare type of class meta
    _cmeta: ClassMeta

    # Declare type of instance meta
    _imeta: InstanceMeta

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ __EQ__
    # └─────────────────────────────────────────────────────────────────────────────────

    def __eq__(self, other: Any) -> bool:
        """Equality Method"""

        # Check if other is an item
        if isinstance(other, self.__class__):
            # Check if items have the same ID
            if (
                self._imeta.id is not None
                and other._imeta.id is not None
                and self._imeta.id == other._imeta.id
            ):
                return True

        # Call super method
        return False

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ __HASH__
    # └─────────────────────────────────────────────────────────────────────────────────

    def __hash__(self) -> int:
        """Hash Method"""

        # Check if item has an ID
        if self._imeta.id is not None:
            # Return hash of ID
            return hash(self.__class__) ^ hash(self._imeta.id)

        # Otherwise return hash of item ID in memory
        return hash(id(self))

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ __REPR__
    # └─────────────────────────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        """Representation Method"""

        # Get representation
        representation = self.__class__.__name__

        # Add angle brackets to representation
        representation = f"<{representation}: {str(self)}>"

        # Return representation
        return representation

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ __STR__
    # └─────────────────────────────────────────────────────────────────────────────────

    def __str__(self) -> str:
        """String Method"""

        # Check if string attribute is defined
        if self._cmeta.STR is not None and hasattr(self, self._cmeta.STR):
            # Get value
            value = getattr(self, self._cmeta.STR)

            # Return the string of the value
            return str(value)

        # Iterate over keys
        for key in self._cmeta.KEYS:
            # Check if key is a string
            if isinstance(key, str):
                # Continue if item does not have key
                if not hasattr(self, key):
                    continue

                # Get value
                value = getattr(self, key)

                # Continue if value is null
                if value in (None, ""):
                    continue

                # Return the string of the value
                return str(value)

            # Otherwise check if key is a tuple
            elif isinstance(key, tuple):
                # Get values
                values = tuple(getattr(self, k, None) for k in key)

                # Return the string of the values
                return "(" + ", ".join(str(value) for value in values) + ")"

        # Return the hex ID of the item
        return hex(id(self))

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ FROM DICT
    # └─────────────────────────────────────────────────────────────────────────────────

    @classmethod
    def from_dict(cls: type[T], data: dict[Any, Any]) -> T:
        """Initializes an item from a dictionary"""

        # Initialize and return item
        return ofrom_dict(Class=cls, data=data)

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ FROM JSON
    # └─────────────────────────────────────────────────────────────────────────────────

    @classmethod
    def from_json(
        cls: type[T],
        data: Any,
        path: str | None = None,
        schema: JSONSchema | None = None,
        defaults: dict[Any, Any] | None = None,
    ) -> Generator[T, None, None]:
        """Yields items from a list of dictionaries"""

        # Yield from JSON object
        yield from ofrom_json(
            Class=cls, data=data, path=path, schema=schema, defaults=defaults
        )

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ PUSH
    # └─────────────────────────────────────────────────────────────────────────────────

    def push(self) -> None:
        """Pushes an item to the collection"""

        # TODO: Handle recursion where two instances point to each other

        # Iterate over attributes
        for val in self.__dict__.values():
            # Check if value is an item
            if isinstance(val, Item) and val._imeta.id is None:
                # Push item
                val.push()

        # Push item to items collection
        self.__class__.items.push(self)

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ META
    # └─────────────────────────────────────────────────────────────────────────────────

    class Meta(ClassMeta):
        """Meta Class"""

        # ┌─────────────────────────────────────────────────────────────────────────────
        # │ CLASS ATTRIBUTES
        # └─────────────────────────────────────────────────────────────────────────────

        # Declare type of abstract
        ABSTRACT: bool

        # Declare type of concrete attributes
        CONCRETE_ATTRIBUTES: tuple[str, ...]

        # Declare type of string
        STR: str | None

        # Declare type of keys
        KEYS: tuple[str | tuple[str, ...], ...]

        # Declare type of indexes
        INDEXES: tuple[str | tuple[str, ...], ...]

        # Declare type of items
        ITEMS: Collection[Any] | Items[Any] | None

        # ┌─────────────────────────────────────────────────────────────────────────────
        # │ CLEAN KEYS
        # └─────────────────────────────────────────────────────────────────────────────

        def clean_keys(self, keys: tuple[Any, ...]) -> tuple[Any, ...]:
            """Cleans a series of key lookups"""

            # Return keys
            return keys
