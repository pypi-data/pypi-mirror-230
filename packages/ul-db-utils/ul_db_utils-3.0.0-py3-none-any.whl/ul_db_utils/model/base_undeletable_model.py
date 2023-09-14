import uuid
from datetime import datetime
from typing import Optional

from flask_sqlalchemy import BaseQuery
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.engine.base import Connection
from sqlalchemy.inspection import inspect
from sqlalchemy_serializer import SerializerMixin

from ul_db_utils.errors.deletion_not_allowed import DeletionNotAllowedError
from ul_db_utils.modules import transaction_commit
from ul_db_utils.modules.db import db, DbModel, DbMapper


class BaseUndeletableModel(DbModel, SerializerMixin):

    __abstract__ = True

    query_class = BaseQuery

    id = db.Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="Идентификатор записи")
    date_created = db.Column(db.DateTime(), default=datetime.utcnow(), nullable=False, comment="Дата и время создания записи")
    date_modified = db.Column(db.DateTime(), default=datetime.utcnow(), nullable=False, comment="Дата и время изменения записи")

    def mark_as_created(self, date_created: Optional[datetime] = None) -> None:
        """Util for set date_created"""
        assert transaction_commit.transaction_context, \
            'database insert must be in transaction_commit context manager'
        if date_created:
            assert isinstance(date_created, datetime), \
                f"date_created must be type of {PG_UUID}, but {type(date_created)} is given"
            self.date_created = date_created
            self.date_modified = date_created
        else:
            self.date_created = datetime.utcnow()
            self.date_modified = datetime.utcnow()

    def mark_as_modified(
        self,
        date_modified: Optional[datetime] = None,
    ) -> None:
        """Util for set user_modified_id and date_modified"""
        assert transaction_commit.transaction_context, \
            'database update must be in transaction_commit context manager'
        if date_modified is not None:
            assert isinstance(date_modified, datetime), \
                f"date_modified must be type of {datetime}, but {type(date_modified)} is given"
            self.date_modified = date_modified
        else:
            self.date_modified = datetime.utcnow()

    def __repr__(self) -> str:
        return self.__class__.__name__

    def mark_as_deleted(
        self,
        date_modified: Optional[datetime] = None,
    ) -> None:
        raise DeletionNotAllowedError()


@db.event.listens_for(db.Mapper, 'before_update')
def receive_before_update(mapper: DbMapper, connection: Connection, target: BaseUndeletableModel) -> None:
    if issubclass(target.__class__, BaseUndeletableModel):
        assert transaction_commit.transaction_context,\
            f'database updates must be in {transaction_commit} context manager'

        unchanged_keys = inspect(target).attrs.get('id').state.unmodified

        assert 'date_modified' not in unchanged_keys, \
            "date_modified must be set on model update"

        assert isinstance(target.date_modified, datetime), \
            f"date_modified must be type of {datetime}, but {type(target.date_modified)} is given"


@db.event.listens_for(DbModel, 'before_insert')
def receive_before_create(mapper: DbMapper, connection: Connection, target: BaseUndeletableModel) -> None:
    if issubclass(target.__class__, BaseUndeletableModel):
        assert transaction_commit.transaction_context,\
            f'database updates must be in {transaction_commit} context manager'

        assert isinstance(target.date_created, datetime), \
            f"date_created must be type of {datetime}, but {type(target.date_created)} is given"

        assert isinstance(target.date_modified, datetime), \
            f"date_modified must be type of {datetime}, but {type(target.date_modified)} is given"
