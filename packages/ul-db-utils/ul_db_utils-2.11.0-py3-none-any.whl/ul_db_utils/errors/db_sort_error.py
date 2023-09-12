from ul_db_utils.errors.db_error import DbError


class DBSortError(DbError):
    """Raised when a client attempts to sort with invalid query params"""
    pass
