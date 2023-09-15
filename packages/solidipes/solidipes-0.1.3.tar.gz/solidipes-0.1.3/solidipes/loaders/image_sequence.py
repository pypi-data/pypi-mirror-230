from PIL import Image as PILImage

from .. import viewers
from .file import File
from .sequence import Sequence


class ImageSequence(Sequence, File):
    """Sequence of images loaded with PIL"""

    supported_mime_types = ["image/"]

    def __init__(self, path):
        File.__init__(self, path)
        Sequence.__init__(self)

        self.add("image_sequence")
        self.add("n_frames")

        self.default_viewer = viewers.Image

    def _load_data(self, key):
        """Load image data with PIL"""

        if key == "image_sequence":
            return PILImage.open(self.file_info.path)

        elif key == "n_frames" or key == "_element_count":
            return self.image_sequence.n_frames

        else:
            return super()._load_data(key)

    def _load_element(self, n):
        """Load a single frame"""

        self.image_sequence.seek(n)
        return self.image_sequence.copy()

    def select_frame(self, frame):
        self.select_element(frame)

    @property
    def image(self):
        # cannot be defined with self.add and _load_data because it changes
        return self._current_element

    @classmethod
    def check_file_support(cls, path):
        """In addition to File class checks, also check if the file is a sequence of images"""

        if not super().check_file_support(path):
            return False

        try:
            with PILImage.open(path) as im:
                return im.is_animated  # tests whether the file contains multiple frames

        except Exception as e:
            print(f"Error while checking ImageSequence support for {path}: {e}")
            return False
