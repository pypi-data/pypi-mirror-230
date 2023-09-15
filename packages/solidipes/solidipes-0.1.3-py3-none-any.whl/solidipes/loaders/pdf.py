import base64

from .. import viewers
from .file import File


class PDF(File):
    """Image loaded as base64"""

    supported_mime_types = ["application/pdf"]

    def __init__(self, path):
        super().__init__(path)

        self.add("pdf")
        self.default_viewer = viewers.PDF

    def _load_data(self, key):
        """Load pdf as base64"""

        data = super()._load_data(key)
        if data is not None:
            return data

        with open(self.file_info.path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode("utf-8")
            return base64_pdf
        raise RuntimeError(f"could not load file {self.file_info.path}")
