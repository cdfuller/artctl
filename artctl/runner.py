"""Subprocess execution for artctl."""

import subprocess


class RunnerError(Exception):
    """Raised when execution of a generator fails."""


def execute(command, working_dir=None):
    """Execute the given command list and stream output."""
    try:
        result = subprocess.run(
            command,
            cwd=working_dir,
            check=False,
        )
    except FileNotFoundError:
        executable = command[0] if command else ""
        raise RunnerError(
            "Executable not found: {0}. Install the required runtime.".format(executable)
        )
    except OSError as exc:
        raise RunnerError("Failed to execute command: {0}".format(exc))

    if result.returncode != 0:
        raise RunnerError("Command exited with status {0}".format(result.returncode))

    return result.returncode
