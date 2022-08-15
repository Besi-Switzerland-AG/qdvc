import argparse
import logging

from qdvc.cli.command import CmdBase
from qdvc.cli.utils import append_doc_link

logger = logging.getLogger(__name__)


class CmdAdd(CmdBase):
    def run(self):
        try:
            self.repo.query(
                self.args.name[0],
            )

        except Exception:
            logger.exception("")
            return 1
        return 0


def add_parser(subparsers, parent_parser):
    ADD_HELP = "Creates a new query"

    parser = subparsers.add_parser(
        "query",
        parents=[parent_parser],
        description=append_doc_link(ADD_HELP, "query"),
        help=ADD_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("name", nargs=1, help="Name of the new query")
    parser.set_defaults(func=CmdAdd)
