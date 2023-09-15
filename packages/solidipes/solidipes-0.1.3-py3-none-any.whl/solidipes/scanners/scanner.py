import os
import re
from pathlib import Path

from ..config import default_ignore_patterns
from ..loaders.file_sequence import FileSequence
from ..utils import get_ignore, load_file


def split_all_path(path):
    head, tail = os.path.split(path)
    _split = [tail]
    path = head
    while path:
        head, tail = os.path.split(path)
        _split.insert(0, tail)
        path = head
    return _split


################################################################


class Scanner:
    def __init__(self):
        try:
            # Get ignored patterns from .solidipes
            self.excluded_patterns = get_ignore()
        except FileNotFoundError:
            self.excluded_patterns = default_ignore_patterns.copy()

    def scan_dirs(self, paths, recursive=True):
        """
        Scans all the paths provided (possibly recursively)
        Returns a directory tree with loaded files
        """

        res = {}
        for p in paths:
            split_p = split_all_path(p)
            _res = res
            for _dir in split_p:
                if _dir not in _res:
                    _res[_dir] = {}
                _res = _res[_dir]
            s = self.scan_dir(p, recursive=recursive)
            _res.update(s)
        return res

    def scan_dir_filenames(self, path, recursive=True, scan_files=True):
        """
        Scans the provided path (possibly recursively)
        Returns a directory tree with the filenames
        """

        found_files = {}

        for f in sorted(os.listdir(path)):
            fname = os.path.join(path, f)
            if self.is_excluded(fname):
                continue

            if os.path.isdir(fname):
                if recursive:
                    scan = self.scan_dir_filenames(os.path.join(path, f), scan_files=scan_files)
                    found_files.update({f: scan})
                continue

            if not scan_files:
                continue

            found_files.update({f: fname})

        return found_files

    def scan_dir(self, path, recursive=True, scan_files=True):
        """
        Scans the provided path (possibly recursively)
        Returns a directory tree with loaded files
        """

        found_filenames = self.scan_dir_filenames(path, recursive, scan_files)
        found_files = for_each_dir(found_filenames, load_files)

        return found_files

    def is_excluded(self, path):
        p = Path(path)

        for pattern in self.excluded_patterns:
            # If the pattern ends with a trailing slash, test whether the path
            # is a directory
            if pattern.endswith("/"):
                if p.match(pattern) and p.is_dir():
                    return True

            # Otherwise, only test whether the path matches the pattern
            else:
                if p.match(pattern):
                    return True

        return False

    def scan(self, uri, scan_files=True):
        return self.scan_dir(uri, scan_files=scan_files)


################################################################


def list_files(found, current_dir=""):
    items = []
    for k, v in found.items():
        full_dir = os.path.join(current_dir, k)
        items.append((full_dir, v))
        if isinstance(v, dict):
            items += list_files(v, current_dir=full_dir)
    return items


################################################################


def for_each_filename(found, f, current_dir=""):
    items = {}
    for k, v in found.items():
        full_dir = os.path.join(current_dir, k)
        if os.path.isdir(full_dir):
            items[k] = for_each_filename(v, f, current_dir=full_dir)
            continue

        items[k] = f(v)
    return items


################################################################


def for_each_dir(found, f, current_dir=""):
    """
    For each directory structure,
    applies a provided function (f) to
    all files.

    If there is a returned value, store
    the result in a structure similar
    to the provided input
    """
    items = {}
    files = []
    for k, v in found.items():
        if isinstance(v, dict):
            items[k] = for_each_dir(v, f)
        else:
            files.append((k, v))
    files = f(files, current_dir=current_dir)
    if files is not None:
        for k, v in files.items():
            items[k] = v
    return items


################################################################


def load_files(file_list, current_dir=None):
    """
    Loading files from provided filename list
    Returns a dictionary mapping filenames with loaded files
    """

    sequences = {}
    normal_files = []
    for name, path in file_list:
        m = re.match("([^0-9]*)([0-9]+)(.*)", name)
        if m:
            # num = m[2]
            base = m[1] + "*" + m[3]
            # print(f"detected series: {name} {path} {base} {num}")
            if base not in sequences:
                sequences[base] = []
            sequences[base].append((name, path))
        else:
            normal_files.append((name, path))

    # Remove sequences with only one file and add them to normal files
    for k, v in list(sequences.items()):
        if len(v) == 1:
            normal_files.append(v[0])
            del sequences[k]

    loaded_files = []
    for name, path in normal_files:
        loaded_files.append((name, load_file(path)))

    for base, paths in sequences.items():
        p = [e[1] for e in paths]
        loaded_files.append((base, FileSequence(base, p)))

    return dict(loaded_files)
