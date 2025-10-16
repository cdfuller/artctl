"""Registry loading utilities."""

import glob
import os

import yaml


class RegistryError(Exception):
    """Raised when registry files are missing or invalid."""


REQUIRED_TOP_LEVEL_FIELDS = {
    "name",
    "description",
    "runtime",
    "entrypoint",
    "command",
}

ALLOWED_TOP_LEVEL_FIELDS = REQUIRED_TOP_LEVEL_FIELDS.union(
    {"params", "output", "tags"}
)

ALLOWED_RUNTIMES = {"python", "node", "binary", "custom"}

ALLOWED_PARAM_KEYS = {"name", "type", "default", "choices", "help", "required"}
REQUIRED_PARAM_KEYS = {"name", "type"}
ALLOWED_PARAM_TYPES = {"string", "int", "float", "bool", "enum", "file", "dir"}

ALLOWED_OUTPUT_KEYS = {"required", "path_template", "extension"}


def load_registry(path):
    """Load and validate registry entries from the given directory."""
    registry_path = os.path.abspath(path or "registry")
    if not os.path.isdir(registry_path):
        raise RegistryError("Registry directory not found: {0}".format(registry_path))

    entries = {}
    source_map = {}
    for file_path in _discover_registry_files(registry_path):
        data = _load_registry_file(file_path)
        name = data["name"]
        if name in entries:
            conflict = source_map[name]
            message = (
                "Duplicate registry name '{0}' in {1} (already defined in {2})."
            ).format(name, file_path, conflict)
            raise RegistryError(message)
        data["source_path"] = file_path
        entries[name] = data
        source_map[name] = file_path

    return entries


def _discover_registry_files(registry_path):
    pattern_yaml = os.path.join(registry_path, "**", "*.yaml")
    pattern_yml = os.path.join(registry_path, "**", "*.yml")
    files = glob.glob(pattern_yaml, recursive=True)
    files.extend(glob.glob(pattern_yml, recursive=True))
    files = [f for f in files if os.path.isfile(f)]
    files.sort()
    return files


def _load_registry_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as handle:
            content = handle.read()
    except OSError as exc:
        raise RegistryError("Failed to read registry file {0}: {1}".format(file_path, exc))

    if not content.strip():
        raise RegistryError("Registry file is empty: {0}".format(file_path))

    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as exc:
        raise RegistryError("Failed to parse YAML in {0}: {1}".format(file_path, exc))

    if not isinstance(data, dict):
        raise RegistryError("Registry file must contain a mapping: {0}".format(file_path))

    _validate_top_level(file_path, data)
    _validate_command(file_path, data["command"])
    params = _validate_params(file_path, data.get("params", []))
    output = _validate_output(file_path, data.get("output"))
    tags = _validate_tags(file_path, data.get("tags"))

    data["params"] = params
    if output is not None:
        data["output"] = output
    if tags is not None:
        data["tags"] = tags
    return data


def _validate_top_level(file_path, data):
    missing = REQUIRED_TOP_LEVEL_FIELDS.difference(data)
    if missing:
        raise RegistryError(
            "Missing required fields {0} in {1}".format(sorted(missing), file_path)
        )

    unknown = set(data).difference(ALLOWED_TOP_LEVEL_FIELDS)
    if unknown:
        raise RegistryError(
            "Unknown fields {0} found in {1}".format(sorted(unknown), file_path)
        )

    runtime = data["runtime"]
    if runtime not in ALLOWED_RUNTIMES:
        raise RegistryError(
            "Invalid runtime '{0}' in {1}; expected one of {2}".format(
                runtime, file_path, sorted(ALLOWED_RUNTIMES)
            )
        )

    if not data["name"] or not isinstance(data["name"], str):
        raise RegistryError("Registry name must be a non-empty string in {0}".format(file_path))
    if not data["description"] or not isinstance(data["description"], str):
        raise RegistryError("Description must be a non-empty string in {0}".format(file_path))

    entrypoint = data["entrypoint"]
    if not isinstance(entrypoint, str) or not entrypoint:
        raise RegistryError("Entrypoint must be a non-empty string in {0}".format(file_path))


def _validate_command(file_path, command):
    if not isinstance(command, list) or not command:
        raise RegistryError("Command must be a non-empty list in {0}".format(file_path))
    for token in command:
        if not isinstance(token, str):
            raise RegistryError(
                "Command entries must be strings in {0}".format(file_path)
            )


def _validate_params(file_path, params):
    if params is None:
        return []
    if not isinstance(params, list):
        raise RegistryError("Params must be a list in {0}".format(file_path))

    seen_names = set()
    cleaned = []
    for index, param in enumerate(params):
        if not isinstance(param, dict):
            raise RegistryError(
                "Param at index {0} must be a mapping in {1}".format(index, file_path)
            )
        missing = REQUIRED_PARAM_KEYS.difference(param)
        if missing:
            raise RegistryError(
                "Param at index {0} missing fields {1} in {2}".format(
                    index, sorted(missing), file_path
                )
            )
        unknown = set(param).difference(ALLOWED_PARAM_KEYS)
        if unknown:
            raise RegistryError(
                "Param '{0}' has unknown fields {1} in {2}".format(
                    param.get("name"), sorted(unknown), file_path
                )
            )

        name = param["name"]
        if not isinstance(name, str) or not name:
            raise RegistryError("Param name must be non-empty string in {0}".format(file_path))
        if name in seen_names:
            raise RegistryError(
                "Duplicate param name '{0}' in {1}".format(name, file_path)
            )
        seen_names.add(name)

        param_type = param["type"]
        if param_type not in ALLOWED_PARAM_TYPES:
            raise RegistryError(
                "Param '{0}' has invalid type '{1}' in {2}".format(name, param_type, file_path)
            )

        if param_type == "enum":
            choices = param.get("choices")
            if not isinstance(choices, list) or not choices:
                raise RegistryError(
                    "Param '{0}' must define non-empty choices for enum type in {1}".format(
                        name, file_path
                    )
                )
        cleaned.append(
            {
                "name": name,
                "type": param_type,
                "default": param.get("default"),
                "choices": param.get("choices"),
                "help": param.get("help"),
                "required": bool(param.get("required", False)),
            }
        )
    return cleaned


def _validate_output(file_path, output):
    if output is None:
        return None
    if not isinstance(output, dict):
        raise RegistryError("Output block must be a mapping in {0}".format(file_path))
    unknown = set(output).difference(ALLOWED_OUTPUT_KEYS)
    if unknown:
        raise RegistryError(
            "Output block has unknown fields {0} in {1}".format(sorted(unknown), file_path)
        )
    result = {}
    if "required" in output:
        result["required"] = bool(output["required"])
    if "path_template" in output:
        template = output["path_template"]
        if not isinstance(template, str) or not template:
            raise RegistryError(
                "Output path_template must be a non-empty string in {0}".format(file_path)
            )
        result["path_template"] = template
    if "extension" in output:
        extension = output["extension"]
        if not isinstance(extension, str) or not extension:
            raise RegistryError(
                "Output extension must be a non-empty string in {0}".format(file_path)
            )
        result["extension"] = extension
    return result


def _validate_tags(file_path, tags):
    if tags is None:
        return None
    if not isinstance(tags, list):
        raise RegistryError("Tags must be a list in {0}".format(file_path))
    cleaned = []
    for tag in tags:
        if not isinstance(tag, str) or not tag:
            raise RegistryError("Tags must be non-empty strings in {0}".format(file_path))
        cleaned.append(tag)
    return cleaned
