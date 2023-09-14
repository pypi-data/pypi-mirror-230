import argparse
import os
import re
from contextlib import closing
from typing import Any
from urllib.parse import urlparse

import psycopg2
from pydantic import PostgresDsn
from sqlalchemy import text
from ul_py_tool.commands.cmd import Cmd


class CmdDocs(Cmd):
    uri: PostgresDsn
    dest_path: str
    schema_db: str

    @staticmethod
    def add_parser_args(parser: argparse.ArgumentParser) -> None:
        def_dir = os.path.join(os.getcwd(), 'docs/db')
        parser.add_argument('--db-uri', dest='uri', type=str, required=True)
        parser.add_argument('--dest', dest='dest_path', type=str, default=def_dir, required=False)
        parser.add_argument('--schema_db', dest='schema_db', type=str, default='public', required=False)

    def run(self, *args: Any, **kwargs: Any) -> None:
        parsed_db_uri = urlparse(self.uri)
        db_name = parsed_db_uri.path.strip("/")
        assert len(db_name) > 0

        with open(os.path.join(os.path.dirname(__file__), 'doc_request_sql.sql'), 'rt') as sql_file:
            doc_request_sql = sql_file.read()

        doc_request_sql = text(doc_request_sql.format(
            schema_db=self.schema_db,
        ))

        with closing(psycopg2.connect(self.uri)) as conn:
            with conn.cursor() as cursor:
                cursor.execute(str(doc_request_sql))
                doc_data = cursor.fetchall()

        for item in doc_data:
            db_name = item[0]
            schema_name = item[1]
            table_name = item[2]
            table_description = item[3]
            file_path = os.path.join(self.dest_path, self.clean_slug(db_name), f"{self.clean_slug(schema_name)}__{self.clean_slug(table_name)}.md")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w+") as file:
                file.write(f"# {db_name} \"{schema_name}.{table_name}\"\n\n"
                           f"{table_description}\n\n"
                           f"## Описание колонок\n\n"
                           f"| Название | Тип | Описание |\n"
                           f"| -------- | --- | -------- |\n")
                for table_field_name, table_field_type, table_field_description in zip(item[4], item[5], item[6]):
                    file.write(f"| {table_field_name} | {table_field_type} | {table_field_description} |\n")

    def clean_slug(self, text: str) -> str:
        return re.sub(r"[^\w\d]+", "_", text)
