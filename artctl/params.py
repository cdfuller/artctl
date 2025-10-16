"""Parameter parsing and coercion helpers."""

class ParameterError(Exception):
    """Raised when CLI overrides are invalid."""


def parse_overrides(arguments, declared_params):
    """Parse --set arguments into a mapping with type coercion."""
    declared_index = _index_params(declared_params)
    values = {}

    for raw in arguments or []:
        name, value = _split_override(raw)
        if name not in declared_index:
            raise ParameterError("Unknown parameter '{0}'.".format(name))

        param = declared_index[name]
        coerced = _coerce_value(name, value, param)
        values[name] = coerced

    for name, param in declared_index.items():
        if name not in values:
            if param["type"] == "bool":
                default = param.get("default", False)
                values[name] = bool(default)
            elif param.get("required") and param.get("default") is None:
                raise ParameterError(
                    "Parameter '{0}' is required but no value was provided.".format(name)
                )
            else:
                values[name] = param.get("default")

    return values


def _index_params(params):
    indexed = {}
    for param in params or []:
        indexed[param["name"]] = param
    return indexed


def _split_override(argument):
    if "=" not in argument:
        raise ParameterError("Overrides must use KEY=VALUE format; got '{0}'.".format(argument))
    name, value = argument.split("=", 1)
    name = name.strip()
    value = value.strip()
    if not name:
        raise ParameterError("Override key must be non-empty: '{0}'.".format(argument))
    if not value:
        raise ParameterError("Override value must be non-empty for key '{0}'.".format(name))
    return name, value


def _coerce_value(name, value, param):
    param_type = param["type"]

    if param_type == "string":
        return value
    if param_type == "int":
        return _coerce_int(name, value)
    if param_type == "float":
        return _coerce_float(name, value)
    if param_type == "bool":
        return _coerce_bool(name, value)
    if param_type == "enum":
        return _coerce_enum(name, value, param)
    if param_type in {"file", "dir"}:
        return value

    raise ParameterError("Unsupported parameter type '{0}' for '{1}'.".format(param_type, name))


def _coerce_int(name, value):
    try:
        return int(value, 10)
    except ValueError:
        raise ParameterError("Parameter '{0}' expects an integer. Received '{1}'.".format(name, value))


def _coerce_float(name, value):
    try:
        return float(value)
    except ValueError:
        raise ParameterError("Parameter '{0}' expects a float. Received '{1}'.".format(name, value))


def _coerce_bool(name, value):
    normalized = value.lower()
    if normalized in {"true", "1", "yes", "on"}:
        return True
    if normalized in {"false", "0", "no", "off"}:
        return False
    raise ParameterError("Parameter '{0}' expects a boolean. Received '{1}'.".format(name, value))


def _coerce_enum(name, value, param):
    choices = param.get("choices") or []
    if value not in choices:
        raise ParameterError(
            "Parameter '{0}' expects one of {1}. Received '{2}'.".format(
                name, choices, value
            )
        )
    return value
