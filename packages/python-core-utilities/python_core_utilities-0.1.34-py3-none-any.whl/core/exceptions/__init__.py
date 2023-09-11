# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ ERROR
# └─────────────────────────────────────────────────────────────────────────────────────


class Error(Exception):
    """A base class for exception subclasses"""

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ __INIT__
    # └─────────────────────────────────────────────────────────────────────────────────

    def __init__(self, message: str) -> None:
        """Init Method"""

        # Set message
        self.message = message

        # Call super init
        super().__init__(message)


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ NULL ATTRIBUTE ERROR
# └─────────────────────────────────────────────────────────────────────────────────────


class NullAttributeError(Error):
    """Raised when an expected non-null attribute is null"""

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ __INIT__
    # └─────────────────────────────────────────────────────────────────────────────────

    def __init__(self, Class: type, attr: str) -> None:
        """Init Method"""

        # Set message
        self.message = f"Attribute {Class.__name__}.{attr} cannot be null."

        # Call super init
        super().__init__(self.message)
