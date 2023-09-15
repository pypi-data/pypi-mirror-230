import streamlit as st
from IPython.display import Markdown, display

from .. import loaders, viewer_backends
from .viewer import Viewer


class Text(Viewer):
    """Viewer for formatted text"""

    def __init__(self, data=None):
        self.compatible_data_types = [loaders.Text, str]
        #: Text to display
        self.text = ""
        self.max_length = 5000
        self.max_lines = 20
        super().__init__(data)

    def add(self, data_container):
        """Append text to the viewer"""
        self.check_data_compatibility(data_container)

        if isinstance(data_container, loaders.DataContainer):
            self.text += data_container.text

        elif isinstance(data_container, str):
            self.text += data_container

    def show(self):
        if viewer_backends.current_backend == "jupyter notebook":
            display(Markdown(self.text))

        elif viewer_backends.current_backend == "streamlit":
            with st.container():
                lines = self.text[: self.max_length].split("\n")
                if len(self.text) > self.max_length or len(lines) > self.max_lines:
                    text = self.text[: self.max_length]
                    lines = text.split("\n")[: self.max_lines]
                    text = "\n".join(lines)
                    st.text(text)
                    st.markdown("**more content....**")
                else:
                    st.text(self.text)
        else:  # python
            print(self.text)


class MarkdownViewer(Text):
    def __init__(self, data=None):
        super().__init__(data)
        self.compatible_data_types = [loaders.Markdown, str]

    def show(self):
        if viewer_backends.current_backend == "jupyter notebook":
            display(Markdown(self.text))

        elif viewer_backends.current_backend == "streamlit":
            st.markdown(self.text)

        else:  # pure python
            print(self.text)
