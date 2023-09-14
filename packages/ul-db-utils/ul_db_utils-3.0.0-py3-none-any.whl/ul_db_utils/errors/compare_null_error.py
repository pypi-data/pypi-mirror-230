from ul_db_utils.errors.db_error import DbError


class ComparisonToNullError(DbError):
    """Raised when a client attempts to use a filter object that compares a
    resource's attribute to ``NULL`` using the ``==`` operator instead of using
    ``is_null``.
    """
    pass
