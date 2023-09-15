import subprocess

from lockfilesmith.exceptions import LockFileSmithException


def install_git_lfs() -> bool:
    # This initialized Git LFS, not installing Git LFS binaries. Refer to
    #  https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage
    commands = [
        "git",
        "lfs",
        "install",
    ]
    result = subprocess.run(
        commands,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode:
        raise LockFileSmithException(f"Fail to install Git LFS. Error: {result.stderr}")

    return True
