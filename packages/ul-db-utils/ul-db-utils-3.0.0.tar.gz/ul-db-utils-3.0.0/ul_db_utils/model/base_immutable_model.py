import uuid
from datetime import datetime
from typing import Optional

from flask_sqlalchemy import BaseQuery
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.engine.base import Connection
from sqlalchemy_serializer import SerializerMixin

from ul_db_utils.errors.deletion_not_allowed import DeletionNotAllowedError
from ul_db_utils.errors.update_not_allowed import UpdateNotAllowedError
from ul_db_utils.modules import transaction_commit
from ul_db_utils.modules.db import db, DbModel, DbMapper


class BaseImmutableModel(DbModel, SerializerMixin):
    __abstract__ = True

    query_class = BaseQuery

    id = db.Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="Идентификатор записи")
    date_created = db.Column(db.DateTime(), default=datetime.utcnow(), nullable=False, comment="Дата и время создания записи")
    user_created_id = db.Column(PG_UUID(as_uuid=True), nullable=False, comment="Идентификатор пользователя, создавшего запись")

    def mark_as_created(self, user_created_id: uuid.UUID, date_created: Optional[datetime] = None) -> None:
        """Util for set user_created_id and date_created"""
        assert transaction_commit.transaction_context, \
            f'database insert must be in {transaction_commit} context manager'
        assert 'user_created_id' in [column.name for column in self.__table__.columns], \
            f"model {self.__repr__()} must have user_created_id foreign key"
        assert isinstance(user_created_id, uuid.UUID), f"user_created_id must be type of {uuid.UUID}"
        self.user_created_id = user_created_id
        if date_created:
            assert isinstance(date_created, datetime), f"date_created must be type of {datetime}"
            self.date_created = date_created
        else:
            self.date_created = datetime.utcnow()

    def mark_as_modified(self, user_modified_id: uuid.UUID, date_modified: Optional[datetime] = None) -> None:
        """Util for set user_modified_id and date_modified"""
        raise UpdateNotAllowedError()

    def __repr__(self) -> str:
        return self.__class__.__name__

    def mark_as_deleted(
        self,
        user_modified_id: uuid.UUID,
        date_modified: Optional[datetime] = None,
    ) -> None:
        raise DeletionNotAllowedError()


@db.event.listens_for(DbMapper, 'before_insert')
def receive_before_create(mapper: DbMapper, connection: Connection, target: BaseImmutableModel) -> None:
    if issubclass(target.__class__, BaseImmutableModel):
        assert transaction_commit.transaction_context, \
            f'database updates must be in {transaction_commit} context manager'

        assert isinstance(target.date_created, datetime), \
            f"date_created must be type of {datetime}, but {type(target.date_created)} is given"


@db.event.listens_for(db.Mapper, 'before_update')
def receive_before_update(mapper: DbMapper, connection: Connection, target: BaseImmutableModel) -> None:
    if issubclass(target.__class__, BaseImmutableModel):
        raise UpdateNotAllowedError()
