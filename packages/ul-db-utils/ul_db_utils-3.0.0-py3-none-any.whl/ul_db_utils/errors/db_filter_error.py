from ul_db_utils.errors.db_error import DbError


class DBFiltersError(DbError):
    """Raised when a client attempts to filters with invalid query params"""
    pass
