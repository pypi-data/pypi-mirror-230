from asyncio import Event
from typing import Any

from sqlalchemy.util import symbol

from ul_db_utils.errors.update_column_not_allowed_error import UpdateColumnNotAllowedError
from ul_db_utils.modules.db import DbColumn, DbModel, db


def make_immutable_column(col: DbColumn) -> None:
    @db.event.listens_for(col, 'set')
    def immutable_column_set_listener(target: DbModel, value: Any, old_value: Any, initiator: Event) -> None:
        if old_value != symbol('NEVER_SET') and old_value != symbol('NO_VALUE') and old_value != value:
            raise UpdateColumnNotAllowedError(f'Cannot update column {col.name} on model {col.class_.__name__} from {old_value} to {value}: column is non-updatable.')
