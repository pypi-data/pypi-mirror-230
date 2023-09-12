import argparse
import logging

import sys

import sensenova
from sensenova import version
from sensenova.cli import tools_register, api_register, display_error

logger = logging.getLogger()
formatter = logging.Formatter("[%(asctime)s] %(message)s")
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(formatter)
logger.addHandler(handler)


def main():
    parser = argparse.ArgumentParser(description=None)
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version="%(prog)s " + version.VERSION,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        dest="verbosity",
        default=0,
        help="Set verbosity.",
    )
    parser.add_argument("-a", "--access-key-id", help="What access key ID to use.")
    parser.add_argument("-s", "--secret-access-key", help="What secret access Key to use.")
    parser.add_argument("-b", "--api-base", help="What API base url to use.")

    def help(args):
        parser.print_help()

    parser.set_defaults(func=help)

    subparsers = parser.add_subparsers()
    sub_api = subparsers.add_parser("api", help="Direct API calls")
    sub_tools = subparsers.add_parser("tools", help="Client side tools for convenience")

    api_register(sub_api)
    tools_register(sub_tools)

    args = parser.parse_args()
    if args.verbosity == 1:
        logger.setLevel(logging.INFO)
    elif args.verbosity >= 2:
        logger.setLevel(logging.DEBUG)

    sensenova.debug = True
    if args.access_key_id is not None:
        sensenova.access_key_id = args.access_key_id
    if args.secret_access_key is not None:
        sensenova.secret_access_key = args.secret_access_key
    if args.api_base is not None:
        sensenova.api_base = args.api_base

    try:
        args.func(args)
    except sensenova.error.SensenovaError as e:
        display_error(e)
        return 1
    except KeyboardInterrupt:
        sys.stderr.write("\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
