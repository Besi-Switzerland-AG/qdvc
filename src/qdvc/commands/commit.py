import argparse
import logging
from qdvc.cli.command import CmdBase


logger = logging.getLogger(__name__)


class CmdCommit(CmdBase):
    def run(self):
        try:
            self.repo.commit(
                self.args.message,
            )

        except Exception:
            logger.exception("")
            return 1
        return 0


def add_parser(subparsers, parent_parser):
    ADD_HELP = "Commits the new query"

    parser = subparsers.add_parser(
        "commit",
        parents=[parent_parser],
        description=ADD_HELP,
        help=ADD_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-m",
        "--message",
        nargs="?",
        dest="message",
        help="message to associate with the query commit",
    )
    parser.set_defaults(func=CmdCommit)
