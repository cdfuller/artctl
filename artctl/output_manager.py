"""Utilities for determining output directories and file paths."""

import os
from datetime import datetime


class OutputError(Exception):
    """Raised when an output path cannot be determined."""


DEFAULT_BASE_DIR = "outputs"
DEFAULT_EXTENSION = "png"


def build_output_path(entry, base_dir=None, now=None, params_values=None):
    """Create an output path for a registry entry and ensure directories exist."""
    if base_dir is None:
        base_dir = DEFAULT_BASE_DIR
    if not base_dir:
        raise OutputError("Base output directory must be provided.")

    if now is None:
        now = datetime.now()
    if params_values is None:
        params_values = {}

    output_config = entry.get("output") or {}
    extension = output_config.get("extension", DEFAULT_EXTENSION)
    extension = extension.lstrip(".")

    name = entry.get("name")
    if not name:
        raise OutputError("Registry entry missing name for output path computation.")

    dated_segments = [
        now.strftime("%Y"),
        now.strftime("%m"),
        now.strftime("%d"),
    ]
    dated_dir = os.path.join(base_dir, *dated_segments)
    if not os.path.isdir(dated_dir):
        os.makedirs(dated_dir, exist_ok=True)

    if output_config.get("path_template"):
        template_path = _render_output_template(
            output_config["path_template"],
            entry,
            params_values,
            now,
        )
        final_path = template_path
        if not os.path.isabs(final_path):
            final_path = os.path.join(base_dir, final_path)
    else:
        timestamp = now.strftime("%H%M%S")
        filename = "{0}-{1}.{2}".format(name, timestamp, extension)
        final_path = os.path.join(dated_dir, filename)

    final_dir = os.path.dirname(final_path)
    if final_dir and not os.path.isdir(final_dir):
        os.makedirs(final_dir, exist_ok=True)

    return final_path


def _render_output_template(template, entry, params_values, now):
    output = template
    replacements = {
        "{name}": entry.get("name"),
        "{entrypoint}": entry.get("entrypoint"),
        "{project_root}": os.getcwd(),
        "{date}": now.strftime("%Y-%m-%d"),
        "{date_path}": os.path.join(
            now.strftime("%Y"), now.strftime("%m"), now.strftime("%d")
        ),
        "{timestamp}": now.strftime("%H%M%S"),
    }
    for placeholder, value in replacements.items():
        if placeholder in output:
            if value is None:
                raise OutputError(
                    "Placeholder {0} requires a value in output template for '{1}'.".format(
                        placeholder, entry.get("name")
                    )
                )
            output = output.replace(placeholder, str(value))

    while True:
        start = output.find("{params.")
        if start == -1:
            break
        end = output.find("}", start)
        if end == -1:
            break
        token = output[start : end + 1]
        param_name = token[len("{params.") : -1]
        if param_name not in params_values:
            raise OutputError(
                "Parameter '{0}' not provided for output template in '{1}'.".format(
                    param_name, entry.get("name")
                )
            )
        output = output.replace(token, str(params_values[param_name]))

    return output


def output_is_required(entry):
    output_config = entry.get("output") or {}
    return bool(output_config.get("required"))


def verify_output(entry, path):
    if not output_is_required(entry):
        return True
    return os.path.exists(path)
