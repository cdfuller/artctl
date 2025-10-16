"""Command-line interface entry point for artctl."""

import argparse
import sys

from . import __version__

EXIT_SUCCESS = 0
EXIT_INTERNAL_ERROR = 1
EXIT_VALIDATION_ERROR = 2


def build_parser():
    """Construct the top-level argument parser and subcommands."""
    parser = argparse.ArgumentParser(
        prog="artctl",
        description="CLI for running generative art programs from a YAML registry.",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Display the artctl version and exit.",
    )
    parser.add_argument(
        "--registry-path",
        default="registry",
        help="Override the registry directory path (default: registry/).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging for troubleshooting.",
    )

    subparsers = parser.add_subparsers(dest="command")

    list_parser = subparsers.add_parser(
        "list",
        help="List all registry programs.",
    )
    list_parser.set_defaults(handler=handle_list)

    help_parser = subparsers.add_parser(
        "help",
        help="Show detailed information for a registry program.",
    )
    help_parser.add_argument(
        "program",
        help="Registry program name to describe.",
    )
    help_parser.set_defaults(handler=handle_help)

    run_parser = subparsers.add_parser(
        "run",
        help="Execute a registry program.",
    )
    run_parser.add_argument(
        "program",
        help="Registry program name to execute.",
    )
    run_parser.add_argument(
        "--set",
        dest="overrides",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Override a parameter value (repeat for multiple overrides).",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Render the command without executing it.",
    )
    run_parser.set_defaults(handler=handle_run)

    return parser


def handle_list(args):
    """Placeholder list handler for early milestones."""
    print("list is not implemented yet. Stay tuned for milestone M2.")
    return EXIT_SUCCESS


def handle_help(args):
    """Placeholder help handler for early milestones."""
    program = args.program
    print("help for '{0}' is not implemented yet. Coming with registry loader.".format(program))
    return EXIT_SUCCESS


def handle_run(args):
    """Placeholder run handler for early milestones."""
    program = args.program
    if args.dry_run:
        prefix = "Dry run"
    else:
        prefix = "Run"
    print("{0} for '{1}' is not implemented yet. Execution arrives in later milestones.".format(prefix, program))
    return EXIT_SUCCESS


def main(argv=None):
    """Main entry point used by the console script."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if getattr(args, "version", False):
        print(__version__)
        return EXIT_SUCCESS

    if not getattr(args, "command", None):
        parser.print_help()
        return EXIT_SUCCESS

    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return EXIT_VALIDATION_ERROR

    try:
        return handler(args)
    except KeyboardInterrupt:
        if getattr(args, "verbose", False):
            raise
        print("Aborted by user.")
        return EXIT_INTERNAL_ERROR
    except Exception as exc:  # noqa: BLE001
        if getattr(args, "verbose", False):
            raise
        print("Unexpected error: {0}".format(exc), file=sys.stderr)
        return EXIT_INTERNAL_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
