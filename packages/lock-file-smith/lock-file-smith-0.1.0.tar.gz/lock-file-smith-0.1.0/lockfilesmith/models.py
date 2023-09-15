from dataclasses import dataclass


@dataclass
class LockFile:
    """LockFile data class

    The input line should be from `git lfs locks` and looks like this:
    'Content/Foobar.uasset\tTheUserNameorUsername\tID:1234567\n'

    """
    name: str
    author: str
    id: int

    def __init__(self, line: str):
        name_, author_, id_ = line.split("\t")
        id_ = id_[3:]  # Strips off "ID:" prefix
        self.name = name_.strip()
        self.author = author_.strip()
        self.id = int(id_)
