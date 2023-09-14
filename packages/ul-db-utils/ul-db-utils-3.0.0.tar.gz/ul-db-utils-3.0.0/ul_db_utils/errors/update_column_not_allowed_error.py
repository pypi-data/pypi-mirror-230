from ul_db_utils.errors.db_error import DbError


class UpdateColumnNotAllowedError(DbError):
    """Raised when db table column update not allowed.
    """
    pass
