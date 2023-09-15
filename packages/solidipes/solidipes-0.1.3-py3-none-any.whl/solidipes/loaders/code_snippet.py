from .. import viewers
from .text import Text


class CodeSnippet(Text):
    supported_extensions = ["py", "cc", "hh", "inp", "m"]

    def __init__(self, path):
        super().__init__(path)
        self.default_viewer = viewers.Code

    def _load_data(self, key):
        data = super()._load_data(key)
        if data is not None:
            return data

        text = ""
        with open(self.file_info.path, "r") as f:
            text = f.read()
        return text
