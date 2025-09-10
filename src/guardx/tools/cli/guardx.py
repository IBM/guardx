"""GuardX Command Line Interpreter."""
import argparse
import logging
import sys

from guardx import __version__
from guardx.tools import init


def print_version():
    print(f"Library version: {__version__}")  # noqa: T201


def main():
    """GuardX CLI entrypoint."""
    parser = argparse.ArgumentParser(description="GuardX command line interpreter.")
    parser.add_argument('--version', help="print library version", action='store_true', required=False)
    parser.add_argument(
        '--log', help="set log level", choices=["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL", "FATAL"], required=False
    )
    parser.add_argument(
        "command",
        help="command",
        nargs='?',
        choices=["init", "analyze", "execute", "version", "help"],
        default="help",
    )
    parser.add_argument("options", nargs=argparse.REMAINDER, help="options", default=[])
    # parse args and configuration
    args = parser.parse_args()

    # setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s]\t%(message)s')

    # run
    try:
        if args.command == "init":
            init.run(args=args.options)
        elif args.command == "analyze":
            print("not implemented")  # noqa: T201
        elif args.command == "execute":
            print("not implemented")  # noqa: T201
        elif args.command == "version" or args.version:
            print_version()
        elif args.command == "help":
            parser.print_help()
        else:
            logging.warn(f"Command {args.command} not implemented")
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        logging.error(f'Caught unhandled error while executing the GuardX cli: {e}')
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
