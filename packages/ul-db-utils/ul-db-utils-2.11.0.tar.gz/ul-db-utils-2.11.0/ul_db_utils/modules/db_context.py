from functools import wraps
from typing import Any, Callable, cast, TypeVar

from ul_db_utils.modules import db

TFn = TypeVar("TFn", bound=Callable[..., Any])


def db_app_context(fn: TFn) -> TFn:
    assert db.initialized_sdk is not None, 'you must initialize db-config'

    @wraps(fn)
    def new_fn(*args: Any, **kwargs: Any) -> Any:
        assert db.initialized_sdk is not None
        assert db.initialized_sdk._flask_app is not None
        with db.initialized_sdk._flask_app.app_context():
            return fn(*args, **kwargs)
    return cast(TFn, new_fn)
