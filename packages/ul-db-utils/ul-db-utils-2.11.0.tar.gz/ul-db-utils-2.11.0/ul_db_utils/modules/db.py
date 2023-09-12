import importlib
import logging
import os
import time
from enum import Enum
from glob import glob
from typing import Optional, TYPE_CHECKING, Callable, TypeVar, Any, Union

import flask_sqlalchemy
from flask import Flask, current_app, _app_ctx_stack

from ul_db_utils.conf import APPLICATION__DB_URI

if TYPE_CHECKING:
    from api_utils.modules.api_sdk import ApiSdk  # type: ignore
    from api_utils.modules.worker_sdk import WorkerSdk  # type: ignore


class Wrap_EngineDebuggingSignalEvents(flask_sqlalchemy._EngineDebuggingSignalEvents):  # type: ignore  # noqa: N801
    def after_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):  # type: ignore
        if current_app:
            try:
                statement = getattr(cursor, 'query', None).decode('utf-8')  # type: ignore
                parameters = tuple()
            except Exception:  # noqa: B902
                pass
            try:
                queries = _app_ctx_stack.top.sqlalchemy_queries  # type: ignore
            except AttributeError:
                queries = _app_ctx_stack.top.sqlalchemy_queries = []  # type: ignore

            queries.append(flask_sqlalchemy._DebugQueryTuple((  # type: ignore
                statement, parameters, context._query_start_time, time.time(),
                flask_sqlalchemy._calling_context(self.app_package),  # type: ignore
            )))


flask_sqlalchemy._EngineDebuggingSignalEvents = Wrap_EngineDebuggingSignalEvents  # type: ignore


class DbWrapper(object):
    def __init__(self) -> None:
        self._wrappee = flask_sqlalchemy.SQLAlchemy()

    def __getattr__(self, attr: str) -> Any:
        if attr == 'session':
            assert initialized_sdk, 'must initialize db'
        return getattr(self._wrappee, attr)


db: 'flask_sqlalchemy.SQLAlchemy' = DbWrapper()  # type: ignore


DbModel = db.Model
DbMapper = db.Mapper
DbColumn = db.Column


logger = logging.getLogger(__name__)


TFn = TypeVar("TFn", bound=Callable)  # type: ignore


initialized_sdk: Optional['DbConfig'] = None


class TransactionIsolationLvl(Enum):
    READ_COMMITTED = 'READ COMMITTED'
    READ_UNCOMMITTED = 'READ UNCOMMITTED'
    REPEATABLE_READ = 'REPEATABLE READ'
    SERIALIZABLE = 'SERIALIZABLE'


class DbConfig:

    def __init__(
        self,
        *,
        models_path: str,
        uri: Optional[str] = APPLICATION__DB_URI,
        track_mod: bool = False,
        pool_pre_ping: int = True,
        pool_recycle: int = 60,
        debug: bool = False,
    ) -> None:
        assert uri
        self.models_path = models_path
        self.uri = uri
        self.track_mod = track_mod
        self.pool_pre_ping = pool_pre_ping
        self.pool_recycle = pool_recycle
        self.debug = debug

        self._flask_app: Optional[Flask] = None

        assert os.path.exists(models_path), f'path of models {models_path} is not exists'

    def _load_route_modules(self, dir: str, file_pref: str = '') -> None:
        suf = '.py'
        files = set()
        for route in glob(os.path.join(dir, f'{file_pref}*{suf}')):
            files.add(str(route))
        for route in glob(os.path.join(dir, f'**/{file_pref}*{suf}')):
            files.add(str(route))
        for file in files:
            file_rel = os.path.relpath(file, os.getcwd())
            mdl = file_rel[:-len(suf)].replace('\\', '/').strip('/').replace('/', '.')
            if self.debug:
                logger.info('loading module %s', mdl)
            importlib.import_module(mdl)

    def _load_models(self) -> None:
        self._load_route_modules(self.models_path)

    def _init_from_sdk_with_flask(  # PRIVATE. ONLY FOR INTERNAL API-UTILS USAGE
        self,
        sdk: Union['ApiSdk', 'WorkerSdk'],
        default_isolation_lvl: TransactionIsolationLvl = TransactionIsolationLvl.SERIALIZABLE,
    ) -> None:
        global initialized_sdk
        if initialized_sdk is not None:
            raise OverflowError('initialized DbConfig must be only one! Db has already initialized')
        initialized_sdk = self

        if self._flask_app is not None:
            raise OverflowError()
        self._flask_app = sdk._flask_app  # noqa

        self._attach_to_flask_app(self._flask_app, db, default_isolation_lvl)

        self._load_models()

    def init_with_flask(self, app_name: str, *, migrate: bool, default_isolation_lvl: TransactionIsolationLvl = TransactionIsolationLvl.SERIALIZABLE) -> Flask:
        global initialized_sdk
        if initialized_sdk is not None:
            raise OverflowError('initialized DbConfig must be only one! Db has already initialized')
        initialized_sdk = self

        if self._flask_app is not None:
            raise OverflowError()
        self._flask_app = Flask(app_name)

        self._flask_app.app_context().push()  # FUCKING HACK

        self._attach_to_flask_app(self._flask_app, db, default_isolation_lvl)

        self._load_models()

        if migrate:
            from flask_migrate import Migrate  # type: ignore
            migrator = Migrate(compare_type=True)
            migrator.init_app(self._flask_app, db)

        return self._flask_app

    def _attach_to_flask_app(self, app: Flask, db_instance: 'flask_sqlalchemy.SQLAlchemy', default_isolation_lvl: TransactionIsolationLvl) -> None:
        app.config['SQLALCHEMY_DATABASE_URI'] = self.uri
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = self.track_mod
        app.config['SQLALCHEMY_POOL_RECYCLE'] = self.pool_recycle
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            "pool_pre_ping": self.pool_pre_ping,
            # "isolation_level": default_isolation_lvl.value,
        }
        app.config['SQLALCHEMY_RECORD_QUERIES'] = True
        # TODO: add some config options
        db_instance.init_app(app)
