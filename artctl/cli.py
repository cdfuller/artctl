"""Command-line interface entry point for artctl."""

import argparse

from . import __version__


def build_parser():
    """Construct the top-level argument parser with stub options."""
    parser = argparse.ArgumentParser(
        prog="artctl",
        description="CLI for running generative art programs from a YAML registry.",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Display the artctl version and exit.",
    )
    return parser


def main(argv=None):
    """Main entry point used by the console script."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if getattr(args, "version", False):
        print(__version__)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
