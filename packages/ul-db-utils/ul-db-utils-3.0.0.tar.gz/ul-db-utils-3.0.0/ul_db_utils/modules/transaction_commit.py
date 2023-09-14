from contextlib import contextmanager
from typing import Any

from ul_db_utils.modules import db

transaction_context: int = 0


@contextmanager
def transaction_commit() -> Any:
    assert db.initialized_sdk is not None, 'you must initialize db-config'
    global transaction_context
    try:
        transaction_context += 1
        yield
        db.db.session.commit()
        transaction_context -= 1
    except Exception:  # noqa: B902
        db.db.session.rollback()
        raise
