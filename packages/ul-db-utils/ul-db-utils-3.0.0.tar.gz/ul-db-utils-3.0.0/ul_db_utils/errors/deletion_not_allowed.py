from ul_db_utils.errors.db_error import DbError


class DeletionNotAllowedError(DbError):
    """Raised when db obj deletion not allowed.
    """
    pass
