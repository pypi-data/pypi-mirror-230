from PIL import Image as PILImage

from .. import viewers
from .file import File


class SVGWrapper:
    def __init__(self, filename):
        self.src = open(filename, "r").read()

    def _repr_svg_(self):
        return self.src

    def show(self):
        from io import BytesIO

        import cairosvg
        import matplotlib.pyplot as plt
        from PIL import Image

        img_png = cairosvg.svg2png(self.src)
        img = Image.open(BytesIO(img_png))
        plt.imshow(img)


class Image(File):
    """Image loaded with PIL"""

    supported_mime_types = ["image/"]

    def __init__(self, path):
        super().__init__(path)

        self.add("image")
        self.default_viewer = viewers.Image

    def _load_data(self, key):
        """Load image data with PIL"""

        data = super()._load_data(key)
        if data is not None:
            return data

        if self.file_info.type == "image/svg+xml":
            return SVGWrapper(self.file_info.path)
        return PILImage.open(self.file_info.path)
