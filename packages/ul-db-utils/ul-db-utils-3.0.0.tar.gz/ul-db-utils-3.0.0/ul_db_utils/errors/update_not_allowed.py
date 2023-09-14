from ul_db_utils.errors.db_error import DbError


class UpdateNotAllowedError(DbError):
    """Raised when db table update not allowed.
    """
    pass
