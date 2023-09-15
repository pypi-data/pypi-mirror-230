import os

from ..utils import get_mimes
from .cached_metadata import CachedMetadata
from .data_container import DataContainer
from .mime_types import get_extension, get_mime_type, get_possible_extensions, is_valid_extension


class File(CachedMetadata, DataContainer):
    """Abstract container class for file metadata

    A File can be read from disk and may contain multiple DataContainer
    entries.
    """

    #: List of supported mime types. Override in subclasses.
    supported_mime_types = []
    #: List of additionally supported file extensions. Override in subclasses.
    supported_extensions = []

    # Format is { key in metadata.yaml : attribute path }
    cached_metadata_fields = {
        "modified_time": "file_info.modified_time",
        "file_info": "file_info",
        "valid_loading": "valid_loading",
        "discussions": "discussions",
        "archived_discussions": "archived_discussions",
    }

    def __init__(self, path):
        DataContainer.__init__(self)
        self.name = os.path.basename(path)
        self.path = path
        self.unique_identifier = path
        self._discussions = []
        self._archived_discussions = False
        self.add("file_info")
        self.add("valid_loading")
        self.add("discussions")
        self.add("archived_discussions")
        CachedMetadata.__init__(self)

    @property
    def _modified_time(self):
        return self.file_info.modified_time

    def add_message(self, author, msg):
        self._discussions.append((author, msg))
        self.set_cached_metadata_entry("discussions", self._discussions)

    def archive_discussions(self, flag=True):
        self._archived_discussions = flag
        self.set_cached_metadata_entry("archived_discussions", self._archived_discussions)

    def _valid_loading(self):
        return super()._valid_loading() and self._valid_extension()

    def _valid_extension(self):
        if self.file_info.path in get_mimes():
            return True

        res = is_valid_extension(self.file_info.path, self.file_info.type)
        if not res:
            self.errors.append(
                f"Mime type '{self.file_info.type}' not matching extension '{os.path.splitext(self.file_info.path)[1]}'"
            )
        return res

    def _load_data(self, key):
        """Load file_info"""

        if key == "discussions":
            return self._discussions

        if key == "archived_discussions":
            return self._archived_discussions

        if key == "valid_loading":
            return self._valid_loading()

        if key == "file_info":
            stats = os.stat(self.path)
            mime_type, charset = get_mime_type(self.path)
            return DataContainer(
                {
                    "size": stats.st_size,
                    "created_time": stats.st_ctime,
                    "modified_time": stats.st_mtime,
                    "permissions": stats.st_mode,
                    "owner": stats.st_uid,
                    "group": stats.st_gid,
                    "path": self.path,
                    "type": mime_type,
                    "charset": charset,
                    "extension": get_extension(self.path),
                }
            )

        else:
            return None

    @classmethod
    def check_file_support(cls, path):
        """Check mime type, then extension of file"""

        mime_type, _ = get_mime_type(path)

        for supported_mime_type in cls.supported_mime_types:
            if mime_type.startswith(supported_mime_type):
                return True

        extension = get_extension(path)

        if extension in cls.supported_extensions:
            return True

        extensions = get_possible_extensions(mime_type)
        for e in extensions:
            if e in cls.supported_extensions:
                return True

        return False
