import os
import subprocess
import sys
from argparse import ArgumentParser
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

from ul_py_tool.commands.cmd import Cmd


class CmdDump(Cmd):
    uri: str
    dest_path: str

    @staticmethod
    def add_parser_args(parser: ArgumentParser) -> None:
        def_file = os.path.join(os.getcwd(), '.tmp', f'dbdump_{datetime.now().isoformat()}.sql')
        parser.add_argument('--db-uri', dest='uri', type=str, required=True)
        parser.add_argument('--dest', dest='dest_path', type=str, default=def_file, required=False)

    def run(self, *args: Any, **kwargs: Any) -> None:
        parsed_db_uri = urlparse(self.uri)
        db_name = parsed_db_uri.path.strip("/")
        assert len(db_name) > 0
        os.makedirs(os.path.dirname(self.dest_path), exist_ok=True)
        result = subprocess.run(
            [(
                f'PGPASSWORD={parsed_db_uri.password} pg_dump --schema=public --data-only -Fc '
                f'-h {parsed_db_uri.hostname} '
                f'-p {parsed_db_uri.port} '
                f'-U {parsed_db_uri.username} '
                f'-d {db_name} '
                f'-f {self.dest_path} '
            )],
            shell=True,
            check=True,
            stderr=sys.stderr,
            stdout=sys.stdout,
        )
        if result.returncode == 1:
            exit(1)
