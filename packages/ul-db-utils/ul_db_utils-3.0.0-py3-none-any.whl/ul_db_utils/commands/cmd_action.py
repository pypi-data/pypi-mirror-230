import os
import subprocess
import sys
from argparse import ArgumentParser
from typing import Any

from ul_py_tool.commands.cmd import Cmd


class CmdAction(Cmd):
    app_dir: str
    app_migration_dir_name: str
    app_file_name: str

    @property
    def app_rel_dir(self) -> str:
        return os.path.relpath(self.app_dir, os.getcwd())

    @staticmethod
    def add_parser_args(parser: ArgumentParser) -> None:
        parser.add_argument('--app-dir', dest='app_dir', type=str, required=True)
        parser.add_argument('--app-migration-dir-name', dest='app_migration_dir_name', type=str, default='migrations', required=False)
        parser.add_argument('--app-flask-file-name', dest='app_file_name', type=str, default='main.py', required=False)

    def run(self, *args: Any, **kwargs: Any) -> None:
        migration_dir = os.path.join(self.app_dir, self.app_migration_dir_name)
        flask_app_path = os.path.join(self.app_dir, self.app_file_name)
        additional_args = ' '.join([f'{key}={value}' for key, value in kwargs.items()])

        result = subprocess.run(
            [f'FLASK_APP="{flask_app_path}" flask db {self.cmd} {additional_args} --directory "{migration_dir}"'],
            shell=True,
            stderr=sys.stderr,
            stdout=sys.stdout,
        )
        if result.returncode == 1:
            exit(1)
