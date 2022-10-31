import argparse
import logging
from qdvc.cli.command import CmdBase


logger = logging.getLogger(__name__)


class CmdCheckout(CmdBase):
    def run(self):
        try:
            self.repo.checkout(
                self.args.query_name[0],
                self.args.data_version[0],
                self.args.download_files,
            )

        except Exception:
            logger.exception("")
            return 1
        return 0


def add_parser(subparsers, parent_parser):
    ADD_HELP = "Checks out a specific query and version"

    parser = subparsers.add_parser(
        "checkout",
        parents=[parent_parser],
        description=ADD_HELP,
        help=ADD_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("query_name", nargs=1, help="Name of the already created query")
    parser.add_argument("data_version", nargs=1, help="Version tag or hash on main branch")
    parser.add_argument(
        "--download_files",
        action=argparse.BooleanOptionalAction,
        help="Option to download the files after filtering them",
    )
    parser.set_defaults(func=CmdCheckout)
