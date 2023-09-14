import subprocess
from pathlib import Path


def find_zit_root(start_path: Path):
    current_path = start_path
    while current_path != Path("/"):
        if (current_path / ".zit").is_dir():
            return current_path
        current_path = current_path.parent
    raise FileNotFoundError(
        "No .zit directory found in the current directory or any parent directories, are you inside a zit project?"
    )


class SubprocessError(Exception):
    def __init__(self, returncode, stderr, cmd):
        self.returncode = returncode
        self.stderr = stderr
        self.cmd = cmd
        super().__init__(f"Error running command: {' '.join(cmd)}\n{stderr}")


def run_subprocess(command, cwd=None, capture_stdout=True, shell=False, env=None, wait=True, return_stdout=False):
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE if return_stdout else None if capture_stdout else subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        cwd=cwd,
        shell=shell,
        env=env,
    )

    if not wait:
        return process

    stdout, stderr = process.communicate()

    if process.returncode:
        raise SubprocessError(process.returncode, stderr, command)

    return stdout if return_stdout else process
