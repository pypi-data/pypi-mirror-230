import subprocess
from typing import List

from lockfilesmith.exceptions import LockFileSmithException
from lockfilesmith.models import LockFile


def is_git_installed() -> bool:
    try:
        subprocess.check_output(
            "git --version",
            shell=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def verify_git_lfs() -> bool:
    commands = [
        "git",
        "lfs",
        "--version",
    ]
    result = subprocess.run(
        commands,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode:
        print("Warning! Git LFS is not installed.")
        return False

    return True


def locked_files() -> List[LockFile]:
    commands = [
        "git",
        "lfs",
        "locks",
    ]
    result = subprocess.run(
        commands,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode:
        raise LockFileSmithException(f"Fail to query locked files. Error: {result.stderr}")

    if not result.stdout:
        return []

    locked = []
    lines = result.stdout.split("\n")
    for line in lines:
        if not line:
            continue

        lock_file = LockFile(line)
        locked.append(lock_file)

    return locked
