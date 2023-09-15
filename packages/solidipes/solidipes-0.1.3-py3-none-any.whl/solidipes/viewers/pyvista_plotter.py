import pyvista as pv

from .. import loaders, viewer_backends
from .viewer import Viewer


class PyvistaPlotter(Viewer):
    """Viewer for pyvista meshes

    Args:
        **kwargs: keyword arguments passed to the pyvista.Plotter constructor
    """

    def __init__(self, data_container=None, add_kwargs={}, show_kwargs={}, **kwargs):
        self.compatible_data_types = [loaders.PyvistaMesh]

        #: keeps track of whether the plotter has already been shown
        self.shown = False

        #: Pyvista plotter
        self.plotter = None
        if viewer_backends.current_backend == "streamlit":
            self.plotter = pv.Plotter(off_screen=True, **kwargs)
        else:  # python or jupyter notebook
            self.plotter = pv.Plotter(**kwargs)

        self.plotter.background_color = "black"
        self.meshes = []
        self.points = []

        super().__init__(data_container, add_kwargs=add_kwargs, show_kwargs=show_kwargs)

    def add(self, data_container, **kwargs):
        """Add mesh to the viewer

        Args:
            **kwargs: keyword arguments passed to the pyvista.Plotter.add_mesh
                method
        """
        self.check_data_compatibility(data_container)

        if isinstance(data_container, loaders.DataContainer):
            self.add_mesh(data_container, **kwargs)

    def add_mesh(self, data_container, **kwargs):
        """Add mesh to the viewer

        Args:
            **kwargs: keyword arguments passed to the pyvista.Plotter.add_mesh
                method
        """
        data = data_container.mesh
        self.meshes.append((data, kwargs))

    def add_points(self, data_container, **kwargs):
        """Add mesh as points to the viewer

        Args:
            **kwargs: keyword arguments passed to the
                pyvista.Plotter.add_points method
        """
        data = data_container.mesh
        self.points.append((data, kwargs))

    def show(self, auto_close=False, **kwargs):
        """Show the viewer

        Args:
            auto_close: whether to close the viewer after showing it
            **kwargs: keyword arguments passed to the pyvista.Plotter.show
                method
        """
        if viewer_backends.current_backend == "streamlit":
            if self.data_container is not None:
                path = self.data_container.file_info.path
            else:
                path = "Unknown"
            key = f"pyvista_ploter_{path}"
            import streamlit as st
            from stpyvista import stpyvista

            wireframe = st.checkbox(
                "wireframe",
                value=True,
                key=key + "_wireframe",
            )

            for p, _ in self.points:
                st.write(p)

            for i, (m, kw) in enumerate(self.meshes):
                options_key = key + f"mesh_{i}_options"
                if options_key not in st.session_state:
                    st.session_state[options_key] = ["None"] + m.array_names

                st.write(m)
                col1, col2 = st.columns(2)
                if len(st.session_state[options_key]) > 1:
                    active_field = col1.selectbox(
                        "active field",
                        key=key + f"active_field_mesh_{i}",
                        options=st.session_state[options_key],
                    )
                else:
                    active_field = None

                warp = col2.number_input("warp", value=0.0, key=key + f"warp_fiels_mesh_{i}")
                if active_field == "None":
                    active_field = None

                if warp != 0:
                    m = m.warp_by_vector(active_field, factor=warp)
                    self.meshes[i] = (m, kw)

                m.set_active_scalars(active_field)

            for p, _ in self.points:
                self.plotter.add_points(p)

            kwargs_plot = {}
            if wireframe:
                kwargs_plot["style"] = "wireframe"

            for m, _ in self.meshes:
                self.plotter.add_mesh(m, **kwargs_plot)

            self.plotter.reset_camera()
            self.plotter.add_scalar_bar()
            stpyvista(self.plotter)

        else:  # python or jupyter notebook
            for p, _kwargs in self.points:
                self.plotter.add_points(p, **_kwargs)

            for m, _kwargs in self.meshes:
                self.plotter.add_mesh(m, **_kwargs)

            self.plotter.show(auto_close, **kwargs)
            self.shown = True

    def save(self, path, **kwargs):
        """Save the view to a file

        Args:
            path: path to the file
            **kwargs: keyword arguments passed to the
                pyvista.Plotter.screenshot method
        """
        # Pyvista Plotter must be shown before saving
        if not self.shown:
            self.plotter.show(auto_close=False)  # also for streamlit backend
            self.shown = True
        self.plotter.screenshot(path, **kwargs)
