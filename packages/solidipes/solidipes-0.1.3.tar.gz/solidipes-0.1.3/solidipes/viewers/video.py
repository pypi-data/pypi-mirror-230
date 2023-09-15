import streamlit as st
from IPython.display import display

from .. import loaders, viewer_backends
from .viewer import Viewer


class Video(Viewer):
    """Viewer for videos"""

    def __init__(self, data=None):
        self.compatible_data_types = [loaders.Video]
        #: Image to display
        self.video = None
        super().__init__(data)

    def add(self, data_container):
        """Replace the viewer's image"""
        self.check_data_compatibility(data_container)
        self.video = data_container.video

    def show(self):
        if viewer_backends.current_backend == "jupyter notebook":
            display(self.image)

        elif viewer_backends.current_backend == "streamlit":
            with st.container():
                st.video(self.video)
        else:  # python
            self.image.show()
