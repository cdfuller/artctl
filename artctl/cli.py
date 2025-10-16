"""Command-line interface entry point for artctl."""

import argparse
import sys

from . import __version__
from . import output_manager
from . import params
from . import registry
from . import templater
from . import runner

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
    """List available registry entries."""
    try:
        entries = registry.load_registry(args.registry_path)
    except registry.RegistryError as exc:
        print("Registry error: {0}".format(exc), file=sys.stderr)
        return EXIT_VALIDATION_ERROR

    if not entries:
        print("No registry entries found in {0}.".format(args.registry_path))
        return EXIT_SUCCESS

    for name in sorted(entries):
        entry = entries[name]
        description = entry.get("description", "").strip()
        print("- {0}: {1}".format(name, description))
    return EXIT_SUCCESS


def handle_help(args):
    """Show details for a specific registry entry."""
    try:
        entries = registry.load_registry(args.registry_path)
    except registry.RegistryError as exc:
        print("Registry error: {0}".format(exc), file=sys.stderr)
        return EXIT_VALIDATION_ERROR

    program = args.program
    entry = entries.get(program)
    if not entry:
        print("Program '{0}' not found in registry.".format(program), file=sys.stderr)
        return EXIT_VALIDATION_ERROR

    print("Name: {0}".format(entry["name"]))
    print("Description: {0}".format(entry["description"]))
    print("Runtime: {0}".format(entry["runtime"]))
    print("Entrypoint: {0}".format(entry["entrypoint"]))
    print("Command template:")
    print("  {0}".format(" ".join(entry["command"])))

    params = entry.get("params", [])
    if params:
        print("Parameters:")
        for param in params:
            default = param.get("default")
            required = "required" if param.get("required") else "optional"
            summary = "{0} ({1}, {2})".format(param["name"], param["type"], required)
            if default is not None:
                summary += ", default={0}".format(default)
            if param.get("choices"):
                summary += ", choices={0}".format(param["choices"])
            if param.get("help"):
                summary += " - {0}".format(param["help"])
            print("  - {0}".format(summary))
    else:
        print("Parameters: none")

    output = entry.get("output")
    if output:
        print("Output expectations:")
        if output.get("required"):
            print("  - Output is required.")
        if output.get("path_template"):
            print("  - Path template: {0}".format(output["path_template"]))
        if output.get("extension"):
            print("  - Extension: .{0}".format(output["extension"]))
    else:
        print("Output expectations: none")

    tags = entry.get("tags") or []
    if tags:
        print("Tags: {0}".format(", ".join(tags)))
    else:
        print("Tags: none")

    print("Source: {0}".format(entry.get("source_path")))
    return EXIT_SUCCESS


def handle_run(args):
    """Validate registry entry prior to execution (implementation pending)."""
    try:
        entries = registry.load_registry(args.registry_path)
    except registry.RegistryError as exc:
        print("Registry error: {0}".format(exc), file=sys.stderr)
        return EXIT_VALIDATION_ERROR

    program = args.program
    entry = entries.get(program)
    if not entry:
        print("Program '{0}' not found in registry.".format(program), file=sys.stderr)
        return EXIT_VALIDATION_ERROR

    try:
        override_map = params.parse_overrides(args.overrides, entry.get("params", []))
    except params.ParameterError as exc:
        print("Parameter error: {0}".format(exc), file=sys.stderr)
        return EXIT_VALIDATION_ERROR

    try:
        output_path = output_manager.build_output_path(entry, params_values=override_map)
    except output_manager.OutputError as exc:
        print("Output error: {0}".format(exc), file=sys.stderr)
        return EXIT_VALIDATION_ERROR
    override_map["output"] = output_path

    print("Execution pipeline for '{0}' is not implemented yet.".format(program))
    print("Resolved parameters:")
    for name in entry.get("params", []):
        param_name = name["name"]
        value = override_map.get(param_name)
        print("  - {0}: {1}".format(param_name, value))
    print("  - output: {0}".format(output_path))
    try:
        rendered_command = templater.render_command(
            entry,
            override_map,
        )
    except templater.TemplateError as exc:
        print("Template error: {0}".format(exc), file=sys.stderr)
        return EXIT_VALIDATION_ERROR

    print("Command preview:")
    print("  {0}".format(" ".join(rendered_command)))
    print("Output path:")
    print("  {0}".format(output_path))

    if args.dry_run:
        print("Dry run requested; command will not execute until Milestone M6.")
        return EXIT_SUCCESS

    try:
        exit_status = runner.execute(rendered_command)
    except runner.RunnerError as exc:
        print("Execution error: {0}".format(exc), file=sys.stderr)
        return EXIT_INTERNAL_ERROR

    if exit_status != 0:
        print("Generator exited with status {0}.".format(exit_status), file=sys.stderr)
        return EXIT_INTERNAL_ERROR

    print("Run completed successfully.")
    return EXIT_SUCCESS
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
