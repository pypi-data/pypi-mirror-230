import argparse
import os
import subprocess
import sys
from typing import Any
from urllib.parse import urlparse

from ul_py_tool.commands.cmd import Cmd


class CmdRestore(Cmd):
    uri: str
    db_dump_file_path: str
    flags: str
    clean_data: int

    @staticmethod
    def add_parser_args(parser: argparse.ArgumentParser) -> None:
        db_dump_path = os.path.join(os.getcwd(), '.tmp', 'dbdump.sql')
        parser.add_argument('--db-uri', dest='uri', type=str, required=True)
        parser.add_argument('--dump-file', dest='db_dump_file_path', type=str, default=db_dump_path, required=False)
        parser.add_argument('--clean-data', dest='clean_data', type=int, default=1, required=False)
        parser.add_argument('--flags', dest='flags', type=str, default='', required=False)

    def run(self, *args: Any, **kwargs: Any) -> None:
        parsed_db_uri = urlparse(self.uri)
        db_name = parsed_db_uri.path.strip("/")
        if not os.path.exists(self.db_dump_file_path):
            raise ValueError(f'file {self.db_dump_file_path} was not found')

        db_pref = f'-U {parsed_db_uri.username} -d {db_name} -h {parsed_db_uri.hostname} -p {parsed_db_uri.port}'
        db_pwd = f'PGPASSWORD={parsed_db_uri.password}'

        subprocess.run(
            [f'{db_pwd} psql {db_pref} -c "create user replicator; "'],
            shell=True,
            check=False,
            stderr=sys.stderr,
            stdout=sys.stdout,
        )
        subprocess.run(
            [f'{db_pwd} psql {db_pref} -c "create user postgres;"'],
            shell=True,
            check=False,
            stderr=sys.stderr,
            stdout=sys.stdout,
        )
        subprocess.run(
            [f'{db_pwd} psql {db_pref} -c "create user viewer;"'],
            shell=True,
            check=False,
            stderr=sys.stderr,
            stdout=sys.stdout,
        )
        subprocess.run(
            [f'{db_pwd} psql {db_pref} -c "create schema audit;"'],
            shell=True,
            check=False,
            stderr=sys.stderr,
            stdout=sys.stdout,
        )
        subprocess.run(
            [f'{db_pwd} psql {db_pref} -c "create schema public;"'],
            shell=True,
            check=False,
            stderr=sys.stderr,
            stdout=sys.stdout,
        )
        subprocess.run(
            [f'{db_pwd} psql {db_pref} -c "create schema cache;"'],
            shell=True,
            check=False,
            stderr=sys.stderr,
            stdout=sys.stdout,
        )
        subprocess.run(
            [f'{db_pwd} psql {db_pref} -c "drop extension timescaledb;"'],
            shell=True,
            check=False,
            stderr=sys.stderr,
            stdout=sys.stdout,
        )

        if self.clean_data:
            truncate_all_sql = (
                f"CREATE OR REPLACE FUNCTION truncate_tables(username IN VARCHAR) RETURNS void AS \\$$ "
                f"DECLARE statements CURSOR FOR SELECT tablename FROM pg_tables WHERE tableowner = username AND schemaname = 'public'; "
                f"BEGIN FOR stmt IN statements LOOP EXECUTE 'TRUNCATE TABLE ' || quote_ident(stmt.tablename) || ' CASCADE;'; END LOOP; END; "
                f"\\$$ LANGUAGE plpgsql; "
                f"SELECT truncate_tables('{parsed_db_uri.username}');"
            )

            subprocess.run(
                [f'{db_pwd} psql {db_pref} -c "{truncate_all_sql}"'],
                shell=True,
                check=True,
                stderr=sys.stderr,
                stdout=sys.stdout,
            )

        result = subprocess.run(
            [f'{db_pwd} pg_restore {db_pref} --data-only --exclude-schema=audit {self.flags} < "{self.db_dump_file_path}"'],
            shell=True,
            check=True,
            stderr=sys.stderr,
            stdout=sys.stdout,
        )
        if result.returncode == 1:
            exit(1)
