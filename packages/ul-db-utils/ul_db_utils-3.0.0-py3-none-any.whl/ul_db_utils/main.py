import logging

from ul_py_tool.commands.cmd import Cmd

from ul_db_utils.commands.cmd_action import CmdAction
from ul_db_utils.commands.cmd_docs import CmdDocs
from ul_db_utils.commands.cmd_dump import CmdDump
from ul_db_utils.commands.cmd_restore import CmdRestore
from ul_db_utils.commands.cmd_waiting import CmdWaiting

logger = logging.getLogger(__name__)


def main() -> None:
    Cmd.main({
        'waiting': CmdWaiting,
        'dump': CmdDump,
        'restore': CmdRestore,
        'migrate': CmdAction,
        'upgrade': CmdAction,
        'downgrade': CmdAction,
        'init': CmdAction,
        'revision': CmdAction,
        'history': CmdAction,
        'branches': CmdAction,
        'current': CmdAction,
        'merge': CmdAction,
        'gen_docs': CmdDocs,
    })


if __name__ == '__main__':
    main()
