# imports
import os
import fnmatch

from netsky.tools import tool


# helpers
def read_gitignore(gitignore_path):
    with open(gitignore_path, "r") as f:
        lines = f.readlines()
    return [line.strip() for line in lines if not line.startswith("#")]


def is_ignored(path, ignore_patterns):
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(path, pattern):
            return True
    return False


# tools
@tool
def read_file(path: str) -> str:
    """
    Reads a file and returns its content.
    """
    # TODO: fix hack
    if path.startswith("https://") or path.startswith("http://"):
        from netsky.tools.internet import webpage_to_str

        return webpage_to_str(path)
    path = os.path.expanduser(path)
    with open(path, "r") as f:
        return f.read()


@tool
def list_files(path: str = ".", depth: int = 2, additional_ignore_dirs: list = []):
    """
    Lists all files in a directory.
    """
    path = os.path.expanduser(path)
    files_list = []
    home = os.path.expanduser("~")
    gitignore_path = os.path.join(home, ".gitignore")

    if os.path.exists(gitignore_path):
        gitignore_patterns = read_gitignore(gitignore_path)
    else:
        gitignore_patterns = []

    ignore_dirs = [".git"] + additional_ignore_dirs

    for root, dirs, files in os.walk(path):
        if root.count(os.sep) >= depth:
            dirs.clear()  # Clear directories list to prevent further depth traversal.

        dirs[:] = [
            d
            for d in dirs
            if not is_ignored(d, ignore_dirs) and not is_ignored(d, gitignore_patterns)
        ]

        for file in files:
            file_path = os.path.join(root, file)
            if not is_ignored(file_path, gitignore_patterns):
                files_list.append(file_path)
    return files_list


@tool
def write_file(path: str, content: str):
    """
    Writes a file.
    """
    path = os.path.expanduser(path)
    with open(path, "w") as f:
        f.write(content)
