"""Command templating utilities."""

import os


class TemplateError(Exception):
    """Raised when command templating fails."""


def render_command(registry_entry, params_values, project_root=None):
    """Expand registry command template with placeholders and parameter values."""
    if project_root is None:
        project_root = os.getcwd()

    command_template = registry_entry.get("command") or []
    if not command_template:
        raise TemplateError(
            "Registry entry '{0}' has no command template.".format(
                registry_entry.get("name")
            )
        )

    resolved = []
    params_inserted = False
    for token in command_template:
        if token == "{params}":
            resolved.extend(_render_params_flags(registry_entry, params_values))
            params_inserted = True
            continue

        resolved.append(
            _expand_token(token, registry_entry, params_values, project_root)
        )

    if not params_inserted:
        resolved.extend(_render_params_flags(registry_entry, params_values))
    return resolved


def _expand_token(token, registry_entry, params_values, project_root):
    replacements = {
        "{project_root}": project_root,
        "{entrypoint}": registry_entry.get("entrypoint"),
        "{name}": registry_entry.get("name"),
        "{output}": params_values.get("output"),
    }

    for placeholder, value in replacements.items():
        if placeholder in token:
            if value is None:
                raise TemplateError(
                    "Placeholder {0} requires a value for program '{1}'.".format(
                        placeholder, registry_entry.get("name")
                    )
                )
            token = token.replace(placeholder, str(value))

    if token.startswith("{params.") and token.endswith("}"):
        param_name = token[len("{params.") : -1]
        if param_name not in params_values:
            raise TemplateError(
                "Parameter '{0}' not provided for token {1}.".format(
                    param_name, token
                )
            )
        return str(params_values[param_name])

    return token


def _render_params_flags(registry_entry, params_values):
    flags = []
    for param in registry_entry.get("params", []):
        name = param["name"]
        param_type = param["type"]
        value = params_values.get(name)

        if param_type == "bool":
            if value:
                flags.append("--{0}".format(name))
            continue

        if value is None:
            continue

        flags.append("--{0}".format(name))
        flags.append(str(value))
    return flags
