# lock-file-smith

Simple wrapper for Git LFS (Large File Storage) commands.

## Quickstart

As there is no API for interacting with Git LFS, this wrapper provides function that
you can use in your Python application for querying, lock/unlock Git LFS files etc.

The `LockFile` dataclass stores the name, author and ID of a locked file.

Take note that the speed of this library depends on Git. This has not been tested on
a Git repository with a large number of locked files.

## Usage

```python
from lockfilesmith.cmds import lock, query

# Use this to verify if Git/Git LFS is presence
query.is_git_installed()
query.verify_git_lfs()

# Query for locked files.
locked_files = query.locked_files()  # Will return empty list if no locked files 

# Lock a file (ensure the file format is tracked as LFS)
lock.lock_file("foo/bar.uasset")  # True

# Unlock file (you can retrieve the locked object ID using query.locked_files)
bar = query.locked_files()[0]  # assume bar.uasset is the only locked file
lock.unlock_file(bar.id)
```

## Further reading

[https://git-lfs.com/](https://git-lfs.com/)

[https://www.atlassian.com/git/tutorials/git-lfs](https://www.atlassian.com/git/tutorials/git-lfs)
