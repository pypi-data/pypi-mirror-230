import uuid
from typing import List

from flask_sqlalchemy import BaseQuery
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_serializer import SerializerMixin

from ul_db_utils.modules.db import db, DbModel
from ul_db_utils.utils.ensure.ensure_list import ensure_list
from ul_db_utils.utils.remove_duplicated_spaces_of_string import remove_duplicated_spaces_of_string


class BaseMaterializedPGView(DbModel, SerializerMixin):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="Идентификатор записи")
    last_refresh_date = db.Column(db.DateTime(), nullable=False, comment="Дата последнего обновления")

    sql = ''
    refresh_by_tables: List[str] = []
    indexing_fields: List[str] = []

    query_class = BaseQuery

    __table_args__ = {'info': {'skip_autogenerate': True}}

    _index_format = '{table}_{field}_index'
    _pkey_format = '{table}_pkey'

    __abstract__ = True

    @classmethod
    def create_view(cls) -> str:
        assert isinstance(cls.sql, str)
        sql_string = cls.sql.strip()

        sql_create = f'CREATE MATERIALIZED VIEW IF NOT EXISTS {cls.__tablename__} AS ' + sql_string
        pref = ('' if sql_create[-1] == ';' else ';')
        sql_index = pref + f'CREATE UNIQUE INDEX IF NOT EXISTS {cls._pkey_format.format(table=cls.__tablename__)} ON {cls.__tablename__}(id);'

        return remove_duplicated_spaces_of_string(sql_create + sql_index)

    @classmethod
    def create_index(cls, field_names: List[str]) -> str:
        ensure_list(field_names, str)
        create_index_sql = ''
        for field_name in set(field_names):
            create_index_sql += f'CREATE INDEX IF NOT EXISTS {cls._index_format.format(table=cls.__tablename__, field=field_name)} ON {cls.__tablename__} ({field_name});'
        return create_index_sql

    @classmethod
    def drop_index(cls, field_names: List[str]) -> None:
        ensure_list(field_names, str)
        create_index_sql = ''
        for field_name in set(field_names):
            create_index_sql += f'DROP INDEX IF EXISTS {cls._index_format.format(table=cls.__tablename__, field=field_name)};'
        db.engine.execute(text(create_index_sql))

    @classmethod
    def refresh_view(cls) -> None:
        db.engine.execute(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {cls.__tablename__};")

    @classmethod
    def recreate_view(cls) -> None:
        db.engine.execute(text(''.join(cls.drop_view())))
        db.engine.execute(text(''.join(cls.create_view())))
        if cls.indexing_fields:
            db.engine.execute(text(''.join(cls.create_index(cls.indexing_fields))))
        db.engine.execute(text(''.join(cls.create_sql_triggers())))

    @classmethod
    def recreate_view_with_cron(cls) -> None:
        db.engine.execute(text(''.join(cls.drop_view())))
        db.engine.execute(text(''.join(cls.create_view())))
        if cls.indexing_fields:
            db.engine.execute(text(''.join(cls.create_index(cls.indexing_fields))))
        db.engine.execute(text(''.join(cls.create_sql_triggers_for_cron())))

    @classmethod
    def drop_view(cls) -> str:
        return f"{cls.drop_triggers()}" + f"DROP MATERIALIZED VIEW IF EXISTS {cls.__tablename__} CASCADE;"

    @classmethod
    def drop_triggers(cls) -> str:
        commands = list()
        for table_name in cls.refresh_by_tables:
            commands.append(f"DROP TRIGGER IF EXISTS refresh_{cls.__tablename__}_by_{table_name} ON {table_name} CASCADE;")
        return ''.join(commands)

    @classmethod
    def create_sql_triggers(cls) -> str:
        create_trigger_func_sql = (
            f"CREATE OR REPLACE FUNCTION refresh_{cls.__tablename__}()"
            f" RETURNS TRIGGER LANGUAGE plpgsql"
            f" AS $$ "
            f"BEGIN "
            f"REFRESH MATERIALIZED VIEW CONCURRENTLY {cls.__tablename__}; "
            f"RETURN NULL; "
            f"END $$;"
        )
        create_triggers_sql = ''
        for table_name in cls.refresh_by_tables:
            create_triggers_sql += (
                f"CREATE TRIGGER refresh_{cls.__tablename__}_by_{table_name} "
                f"AFTER INSERT OR UPDATE OR DELETE OR TRUNCATE "
                f"ON {table_name} "
                f"FOR EACH STATEMENT "
                f"EXECUTE PROCEDURE refresh_{cls.__tablename__}();"
            )
        return remove_duplicated_spaces_of_string(create_trigger_func_sql + create_triggers_sql)

    @classmethod
    def create_sql_triggers_for_cron(cls) -> str:
        create_trigger_func_sql = (
            f"CREATE OR REPLACE FUNCTION refresh_{cls.__tablename__}()"
            f" RETURNS TRIGGER LANGUAGE plpgsql"
            f" AS $$ "
            f"BEGIN "
            f"UPDATE public.updating_materialized_view_cron SET date_changes = now() WHERE name_materialized_view = '{cls.__tablename__}'; "
            f"RETURN NULL; "
            f"END $$;"
        )
        create_triggers_sql = ''
        for table_name in cls.refresh_by_tables:
            create_triggers_sql += (
                f"CREATE TRIGGER refresh_{cls.__tablename__}_by_{table_name} "
                f"AFTER INSERT OR UPDATE OR DELETE OR TRUNCATE "
                f"ON {table_name} "
                f"FOR EACH STATEMENT "
                f"EXECUTE PROCEDURE refresh_{cls.__tablename__}();"
            )
        return remove_duplicated_spaces_of_string(create_trigger_func_sql + create_triggers_sql)

    @classmethod
    def add_view_refresh_cron(cls, id: UUID, priority: int) -> str:
        return f"INSERT INTO public.updating_materialized_view_cron " \
               f"(id, name_materialized_view, date_changes, date_update, priority) " \
               f"VALUES ('{id}', '{cls.__tablename__}', null, null, {priority});"
