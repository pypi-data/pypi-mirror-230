from ul_db_utils.errors.db_error import DbError


class UnknownFieldError(DbError):
    """Raised when the user attempts to reference a field that does not
    exist on a model in a search.

    """

    def __init__(self, field: str) -> None:

        #: The name of the unknown attribute.
        self.field = field
