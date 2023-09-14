from ul_db_utils.errors.db_error import DbError


class MultipleObjectsReturnedError(DbError):
    """Raised when db returned multiple objects.
    """
    pass
