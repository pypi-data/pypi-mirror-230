import os

from ..utils import load_file
from .cached_metadata import CachedMetadata
from .sequence import Sequence


class FileSequence(Sequence, CachedMetadata):
    """Sequence of files"""

    # Format is { key in metadata.yaml : attribute path }
    cached_metadata_fields = {
        "modified_time": "file_info.modified_time",
    }

    def __init__(self, pattern, paths):
        Sequence.__init__(self)
        self.path = os.path.join(os.path.dirname(paths[0]), pattern)
        self.unique_identifier = self.path
        self._paths = paths
        self._element_count = len(paths)
        CachedMetadata.__init__(self)
        del self.default_viewer  # Use files' viewers

    @property
    def _modified_time(self):
        return self.file_info.modified_time

    def _load_element(self, n):
        if n < 0 or n >= self._element_count:
            raise KeyError(f"File {n} does not exist")

        path = self._paths[n]
        return load_file(path)

    def select_file(self, n):
        self.select_element(n, update_default_viewer=True)
