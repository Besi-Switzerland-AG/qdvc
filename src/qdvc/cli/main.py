import logging
import sys

logger = logging.getLogger("qdvc")


class DvcParserError(Exception):
    """Base class for CLI parser errors."""

    def __init__(self):
        super().__init__("parser error")


def parse_args(argv=None):
    """Parses CLI arguments.
    Args:
        argv: optional list of arguments to parse. sys.argv is used by default.
    Raises:
        DvcParserError: raised for argument parsing errors.
    """
    from .parser import get_main_parser

    parser = get_main_parser()
    args = parser.parse_args(argv)
    args.parser = parser
    return args


def main(argv=None):  # noqa: C901
    """Main entry point for dvc CLI.
    Args:
        argv: optional list of arguments to parse. sys.argv is used by default.
    Returns:
        int: command's return code.
    """
    from dvc._debug import debugtools
    from dvc.config import ConfigError
    from dvc.exceptions import DvcException, NotDvcRepoError
    from dvc.logger import disable_other_loggers, set_loggers_level

    # NOTE: stderr/stdout may be closed if we are running from dvc.daemon.
    # On Linux we directly call cli.main after double forking and closing
    # the copied parent's standard file descriptors. If we make any logging
    # calls in this state it will cause an exception due to writing to a closed
    # file descriptor.
    if sys.stderr.closed:  # pylint: disable=using-constant-test
        logging.disable()
    elif sys.stdout.closed:  # pylint: disable=using-constant-test
        logging.disable(logging.INFO)

    args = None
    disable_other_loggers()

    outerLogLevel = logger.level
    try:
        args = parse_args(argv)

        level = None
        if args.quiet:
            level = logging.CRITICAL
        elif args.verbose == 1:
            level = logging.DEBUG
        elif args.verbose > 1:
            level = logging.TRACE

        if level is not None:
            set_loggers_level(level)

        logger.trace(args)

        if not sys.stdout.closed and not args.quiet:
            from dvc.ui import ui

            ui.enable()

        with debugtools(args):
            cmd = args.func(args)
            ret = cmd.do_run()
    except ConfigError:
        logger.exception("configuration error")
        ret = 251
    except KeyboardInterrupt:
        logger.exception("interrupted by the user")
        ret = 252
    except BrokenPipeError:
        import os

        # Python flushes standard streams on exit; redirect remaining output
        # to devnull to avoid another BrokenPipeError at shutdown
        # See: https://docs.python.org/3/library/signal.html#note-on-sigpipe
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        ret = 141  # 128 + 13 (SIGPIPE)
    except NotDvcRepoError:
        logger.exception("")
        ret = 253
    except DvcException:
        ret = 255
        logger.exception("")
    except DvcParserError:
        ret = 254
    except Exception as exc:  # noqa, pylint: disable=broad-except
        # pylint: disable=no-member
        ret = logger.exception(exc) or 255
        raise exc

    try:
        from dvc import analytics

        if analytics.is_enabled():
            analytics.collect_and_send_report(args, ret)

        return ret
    finally:
        logger.setLevel(outerLogLevel)

        from dvc.external_repo import clean_repos

        # Remove cached repos in the end of the call, these are anonymous
        # so won't be reused by any other subsequent run anyway.
        clean_repos()
