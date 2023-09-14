import os

from sqlalchemy import text, inspect

from ul_db_utils.modules.db import db

AUDIT_SQL_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audit.sql')


def add_table_to_audit(table_name: str) -> None:
    sql_command = f"SELECT audit.audit_table('public.{table_name}');"
    with db.engine.connect().execution_options(autocommit=True) as conn:
        conn.execute(text(sql_command))


def add_current_tables_to_audit() -> None:
    for table_name in db.engine.table_names():
        add_table_to_audit(table_name)


def exclude_audit_from_table(table_name: str) -> None:
    db.engine.execute(f"DROP TRIGGER IF EXISTS audit_trigger_row on public.{table_name}")
    db.engine.execute(f"DROP TRIGGER IF EXISTS audit_trigger_stm on public.{table_name}")


def exculde_audit_scheme() -> None:
    db.engine.execute('DROP SCHEMA IF EXISTS audit CASCADE;')


def exclude_audit_from_current_tables() -> None:
    for table_name in db.engine.table_names():
        exclude_audit_from_table(table_name)


def enable_audit() -> None:
    with open(AUDIT_SQL_FILE_PATH, 'r') as f:
        assert '/*' not in f.read(), 'comments with /* */ not supported in SQL file python interface'

    with open(AUDIT_SQL_FILE_PATH, 'r') as f:
        queries = [line.strip() for line in f.readlines()]

    queries = [cut_comment(q) for q in queries]
    sql_command = ' '.join(queries)
    db.engine.execute(text(sql_command))
    add_current_tables_to_audit()


def drop_audit() -> None:
    exclude_audit_from_current_tables()
    exculde_audit_scheme()


def cut_comment(query: str) -> str:
    idx = query.find('--')
    if idx >= 0:
        query = query[:idx]
    return query
