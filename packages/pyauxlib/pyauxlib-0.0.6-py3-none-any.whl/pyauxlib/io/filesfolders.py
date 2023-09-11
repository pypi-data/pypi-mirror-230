import re
import time
from collections.abc import Generator
from fnmatch import fnmatch
from pathlib import Path
from typing import NamedTuple

from pyauxlib.io.utils import clean_file_extension


class FileRelPath(NamedTuple):
    # Named tuple with the path of a file and the relative path to a parent path
    file: Path
    rel_path: Path


def iterate_files(pathobject: Path, file_extensions: list[str] | None = None) -> Generator[FileRelPath, None, None]:
    """Given a Path object, it returns an iterable of files
        - If the Path is a file, the only file is itself
        - If the Path is folder, returns all the files in the folder with a given
        extension. It doesn't recurse subfolders.

    Parameters
    ----------
    pathobject : Path
        Path object to look for files
    file_extensions : list[str], optional
        Extension of the files to be returned, by default None (all the extensions).
        It doesn't work if ``pathobject`` is a file.

    Returns
    -------
    Generator
        Generator with a FileRelPath class, including the found files with their path
        relative to the parent_path.
        If ``pathobject`` is a file, yields only the values for the file itself.

    Raises
    ------
    Warning
        file/folder doesn't exist
    """

    # File or files to be tested
    if pathobject.is_file():
        yield FileRelPath(pathobject, pathobject.relative_to(pathobject))
    elif pathobject.is_dir():
        yield from iterate_folder(
            folder=pathobject,
            file_extensions=file_extensions,
            subfolders=False,
            parent_path=pathobject,
        )
    else:
        raise Warning("Verify that the file or folder exists.")


def iterate_folder(
    folder: str | Path,
    file_extensions: list[str] | None = None,
    file_patterns: list[str] | None = None,
    exclude_patterns: bool = False,
    subfolders: bool = True,
    parent_path: Path | None = None,
) -> Generator[FileRelPath, None, None]:
    """Iterate through a folder and its subfolders looking for files with a given
    extension

    Parameters
    ----------
    folder : str | Path
        parent folder in which the search will start
    file_extensions : list[str], optional
        list of extensions of the files that will be looked for. By default None.
        If not passed, it returns all the files.
    file_patterns : list[str], optional
        list of patterns that the file names should match. By default None.
        If not passed, it returns all the files. If multiple patterns are provided,
        a file will be returned if its name matches any of the patterns (i.e., the
        patterns are combined using a logical 'OR').
        The patterns can include wildcards, such as '*' and '?', to match multiple
        characters or a single character, respectively. For example:
            - ["*before*"]: matches all files that have the word "before" in their name.
            - ["*.txt"]: matches all files with the '.txt' extension.
            - ["file_?.txt"]: matches all files with names like 'file_1.txt', 'file_2.txt', etc.
            - ["file_[0-9].txt"]: equivalent to the previous example, but uses a character set
              to match any digit between 0 and 9.
    exclude_patterns : bool, optional
        When 'True', it will return files that do not match 'file_patterns'
    subfolders : bool, optional
        include or not subfolders, by default True
    parent_path : Path, optional
        path of the parent, used to return the relative paths to reconstruct the folder hierarchy

    Yields
    ------
    _type_
        generator with a FileRelPath class, including the found files with their path
        relative to the parent_path
    """

    current_folder = Path(folder).parent if Path(folder).is_file() else Path(folder)

    file_extensions = [".*"] if file_extensions is None else file_extensions
    file_extensions = [clean_file_extension(ext) for ext in file_extensions]

    parent_path = parent_path or current_folder

    for entry in current_folder.iterdir():
        # Only returns files, not folders
        if entry.is_file() and any(re.match(ext, entry.suffix.lower()) for ext in file_extensions):
            if file_patterns is None or any(fnmatch(entry.name, pattern) for pattern in file_patterns) != exclude_patterns:
                yield FileRelPath(entry, current_folder.relative_to(parent_path))
        # Check the subfolders
        elif entry.is_dir() and subfolders:
            yield from iterate_folder(
                folder=entry,
                subfolders=True,
                file_extensions=file_extensions,
                file_patterns=file_patterns,
                exclude_patterns=exclude_patterns,
                parent_path=parent_path,
            )


def create_folder(path: Path, includes_file=False):
    """Creates the folder passed in the path (if it doesn't exist).
    Useful to be sure that a folder exists before saving a file.

    Parameters
    ----------
    path : Path
        Path object for the folder (can also include the file)
    includes_file : bool, optional
        The path includes a file at the end, by default False.
    """

    # NOTE: see also os.makedirs

    path = path.parent if includes_file else path

    try:
        path.mkdir(parents=True)
    except FileExistsError:
        # Defeats race condition when another thread created the path
        pass


def clean_filename(filename: str, replacement: str = "_") -> str:
    """Removes illegal characters from a filename

    Parameters
    ----------
    filename : str
        name of the file

    replacement : str
        character to replace the illegal characters

    Returns
    -------
    str
        clean name
    """

    illegal_characters = "!@#$%^&*()[]{};:,/<>?'\\'|`~-=_+"

    replacement = "_" if replacement in illegal_characters else replacement

    filename = filename.translate({ord(c): replacement for c in illegal_characters})
    return filename


def add_folder_timestamp(rootdir: str | Path, fmt: str = "run_%Y_%m_%d-%H_%M_%S") -> Path:
    """Adds a folder with timestamp to the given path

    Parameters
    ----------
    rootdir : str | Path
        path of the original folder in which the new folder will be added

    fmt : str, optional
        format of the timestamp, by default "run_%Y_%m_%d-%H_%M_%S"

    Returns
    -------
    Path
        new path
    """

    run_id = time.strftime(fmt)
    return Path(rootdir, run_id)
