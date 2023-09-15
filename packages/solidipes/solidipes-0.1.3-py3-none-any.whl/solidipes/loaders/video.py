from .. import viewers
from .file import File


class Video(File):
    """Video file"""

    supported_mime_types = ["video/"]

    def __init__(self, path):
        super().__init__(path)

        self.add("video")
        self.default_viewer = viewers.Video

    def _load_data(self, key):
        """Load image data with PIL"""

        data = super()._load_data(key)
        if data is not None:
            return data

        return open(self.file_info.path, "rb")
