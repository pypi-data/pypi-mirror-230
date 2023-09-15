#!/bin/env python
################################################################
import base64
import fnmatch
import os

import streamlit as st
import streamlit.components.v1 as components
from datasize import DataSize

################################################################
from streamlit_tree_select import tree_select

# Must import explicitly from "solidipes" to work in Streamlit
from solidipes.loaders.file import File
from solidipes.loaders.file_sequence import FileSequence
from solidipes.loaders.mime_types import extension2mime_type, is_valid_extension, mime_types2extensions
from solidipes.loaders.sequence import Sequence
from solidipes.reports.widgets.custom_widgets import SpeechBubble
from solidipes.reports.widgets.gitlab_issues import GitInfos, GitlabIssues
from solidipes.reports.widgets.zenodo import ZenodoInfos, ZenodoPublish
from solidipes.scanners.scanner import Scanner, list_files
from solidipes.utils import get_git_repository, get_git_root, get_mimes, get_study_metadata, set_mimes

################################################################
command = "report"
command_help = "generate report from directory"
################################################################
jupyter_icon_filename = os.path.join(os.path.dirname(__file__), "jupyter_logo.png")
_jupyter_icon = base64.b64encode(open(jupyter_icon_filename, "rb").read()).decode("utf-8")


def transform_to_subtree(h, subtree=""):
    tree = []
    for name, f in h.items():
        if isinstance(f, dict):
            current_dir = os.path.join(subtree, name)
            s = transform_to_subtree(f, current_dir)
            if s:
                tree.append({"label": name, "value": current_dir, "children": s})
            else:
                tree.append({"label": name, "value": current_dir})
    return tree


################################################################


class StateWrapper:
    def __init__(self, f):
        self.key = "solidipes_state_GUI_" + f.unique_identifier
        self.f = f
        if self.key not in st.session_state["GUI_files"]:
            st.session_state["GUI_files"][self.key] = {}
        # self.logger = None

    def set_logger(self, foo):
        # self.logger = foo
        pass

    def __getattribute__(self, name):
        if name in ["key", "f", "logger", "set_logger"]:
            return super().__getattribute__(name)

        try:
            if name not in st.session_state["GUI_files"][self.key]:
                st.session_state["GUI_files"][self.key][name] = None
            return st.session_state["GUI_files"][self.key][name]
        except KeyError:
            return None

    def __setattr__(self, name, value):
        if name in ["key", "f", "logger", "set_logger"]:
            super().__setattr__(name, value)
            return

        try:
            if self.key not in st.session_state["GUI_files"]:
                st.session_state["GUI_files"][self.key] = {}
            st.session_state["GUI_files"][self.key][name] = value
            # print("Changing_state:", self.key, name, value)
        except KeyError:
            pass

        # if self.logger is not None:
        # self.logger(self.f.file_info.path, f"{name} -> {value}")


################################################################


class FileWrapper:
    def __init__(self, f):
        self.state = StateWrapper(f)
        self.f = f

    def __getattr__(self, name):
        if name in ["state", "f"]:
            return super().__getattr__(name)

        return getattr(self.f, name)


################################################################


class Report(GitInfos):
    def __init__(self):
        super().__init__()
        self.display_push_button = False
        self.file_wildcard = "*"
        self.file_error_checkbox = None
        self.scanner = Scanner()
        st.set_page_config(layout="wide")
        self.createLayouts()

    def createLayouts(self):
        self.progress_layout = st.sidebar.empty()

        st.sidebar.markdown("*Powered by* **Solidipes**")
        st.sidebar.markdown(
            (
                '<center><img src="https://gitlab.com/dcsm/solidipes/-/raw/main/logos/solidipes.jpg" width="60%"'
                ' style="border-radius:50%;" /><br><a style="font-size: 13px;"'
                ' href="https://gitlab.com/dcsm/solidipes">https://gitlab.com/dcsm/solidipes</a></center>'
            ),
            unsafe_allow_html=True,
        )
        st.sidebar.markdown(
            (
                '<p style="font-size: 10px"><center><em>Software funded by</em> <img width="100px"'
                ' src="https://ethrat.ch/wp-content/uploads/2021/12/ethr_en_rgb_black.svg"/>&nbsp;'
                '<a style="font-size: 10px" href="https://ethrat.ch/en/">https://ethrat.ch/en/</a></center></p>'
            ),
            unsafe_allow_html=True,
        )
        st.sidebar.markdown("---")
        st.sidebar.markdown(
            f"### <center> [View/Edit Gitlab repository]({self.git_origin}) </center>", unsafe_allow_html=True
        )
        self.jupyter_control = st.sidebar.container()
        self.update_buttons = st.sidebar.container()
        self.file_selector = st.sidebar.container()
        self.path_selector = st.sidebar.container()
        if self.git_repository is not None:
            self.git_control = st.sidebar.container()
        self.env_layout = st.sidebar.container()
        self.options = st.sidebar.expander("Options")

        self.main_layout = st.container()
        # self.modified_state = self.main_layout.empty()
        # self.logs = self.main_layout.container()
        self.global_message = self.main_layout.container()
        self.header_layout = self.main_layout.container()
        self.zenodo_publish = ZenodoPublish(self.main_layout, self.global_message, self.progress_layout)
        self.zenodo_infos = ZenodoInfos(self.main_layout)
        if self.git_origin is not None:
            self.gitlab_issues = GitlabIssues(self.main_layout)
        self.files_container = self.main_layout.container()

    def alternative_parser(self, e):
        return []

    def add_log(self, mesg):
        self.log_layout.text(mesg)

    def load_file(self, e):
        if not e.state.loaded:
            try:
                e.load_all()
            except Exception as err:
                e.errors += ["Error during import<br>" + str(err)]
            e.errors += self.alternative_parser(e)
            e.state.valid = e.valid_loading()
            e.state.errors = e.errors
            e.state.loaded = True

    def get_file_title(self, e):
        path = e.file_info.path
        if isinstance(e.f, FileSequence):
            path = e.f.path

        file_title = f"{path}"

        if e.state.valid and (not e.discussions or e.archived_discussions):
            title = ":white_check_mark: &nbsp; &nbsp;" + file_title
        else:
            title = ":no_entry_sign: &nbsp; &nbsp; " + file_title
            title += "&nbsp; &nbsp; :arrow_backward: &nbsp; &nbsp; "
            title += f"**{e.file_info.type.strip()}**"

        if e.state.view:
            title += "&nbsp; :open_book:"

        if e.discussions:
            title += "&nbsp; :e-mail:"

        return title

    def get_file_edit_link(self, e):
        _path = e.file_info.path
        while os.path.islink(_path):
            dirname = os.path.dirname(_path)
            _path = os.path.join(dirname, os.readlink(_path))

        url = self.git_origin + "/-/edit/master/data/" + _path
        return url

    def mime_type_information(self, e, layout, main_layout):
        valid_ext = is_valid_extension(e.file_info.path, e.file_info.type)
        if not e.state.valid and not valid_ext:
            type_choice_box = layout.empty()
            type_choice = type_choice_box.container()
            sel = type_choice.radio(
                "Type selection",
                options=["extension", "mime"],
                key="type_sel_" + e.unique_identifier,
                horizontal=True,
            )

            choice = None
            if sel == "mime":
                possible_types = [e for e in mime_types2extensions.keys()]
                choice = type_choice.selectbox(
                    "type",
                    ["Select type"] + possible_types,
                    key="mime_" + e.unique_identifier,
                )
            else:

                def format_types(x):
                    if x == "Select type":
                        return x
                    return f"{x} ({extension2mime_type[x]})"

                possible_types = [e for e in extension2mime_type.keys()]
                choice = type_choice.selectbox(
                    "extension",
                    ["Select type"] + possible_types,
                    format_func=format_types,
                    key="mime_" + e.unique_identifier,
                )
                if choice != "Select type":
                    choice = extension2mime_type[choice]

            if choice != "Select type":
                st.write(choice)
                confirm = main_layout.button(
                    f"Confirm change type {choice} -> {mime_types2extensions[choice]}",
                    type="primary",
                    use_container_width=True,
                )
                if confirm:
                    mimes = get_mimes()
                    mimes[e.file_info.path] = choice
                    set_mimes(mimes)
                    self.clear_session_state()
                    st.experimental_rerun()
        else:
            layout.info(e.file_info.type)

    def display_file(self, e, readme=False):
        if not fnmatch.fnmatch(e.file_info.path.lower(), self.file_wildcard):
            return

        path = e.file_info.path
        fname = os.path.basename(path).lower()
        if not readme and fname == "readme.md":
            return

        e.state.valid = e.valid_loading
        if self.file_error_checkbox and e.valid_loading():
            return

        title = self.get_file_title(e)

        button_layout = st.empty()

        if "currently_opened" not in st.session_state:
            st.session_state["currently_opened"] = []

        def switch_view():
            e.state.view = True
            st.session_state["currently_opened"].append(e.unique_identifier)

        button_layout.button(f"{title}", use_container_width=True, on_click=switch_view)

        # if e.discussions and not e.archived_discussions:
        #    switch_view()

        # force visibility of readme
        if fname == "readme.md":
            e.state.view = True

        details_layout = st.expander(
            title,
            expanded=e.unique_identifier in st.session_state["currently_opened"],
        )
        if e.state.view is True:
            button_layout.empty()
            if not e.state.valid and e.state.errors:
                for err in e.errors:
                    details_layout.warning(err)

            col1, col2, col3, col4, col5 = details_layout.columns(5)

            with details_layout:
                self.show_discussions(e)

                if e.state.adding_comment:
                    # from streamlit_quill import st_quill
                    # message = st_quill(html=True, preserve_whitespace=False,
                    #                    key=f"chat_input_{e.unique_identifier}")

                    from streamlit_ace import st_ace

                    content = st_ace(
                        theme="textmate",
                        show_gutter=False,
                        key=f"chat_input_{e.unique_identifier}",
                    )
                    if content:
                        import re

                        m = re.match(r"(\w+):(.*)", content)
                        if m:
                            e.add_message(m[1], m[2].strip())
                        else:
                            e.add_message("Unknown", content)
                        e.state.adding_comment = False
                        st.experimental_rerun()

            if isinstance(e.f, Sequence):
                sequence_switcher = details_layout.container()
                with sequence_switcher:
                    st.write(f"Sequence of {e._element_count} elements.")

                    selected_element = st.slider(
                        "Current element",
                        min_value=1,
                        max_value=e._element_count,
                        step=1,
                        key="sequence_switcher_" + e.unique_identifier,
                    )
                    e.select_element(selected_element - 1, False)

            col4.download_button(
                f"Download {os.path.basename(e.file_info.path)} ({DataSize(e.file_info.size):.2a})",
                data=open(e.file_info.path, "rb"),
                file_name=os.path.basename(e.file_info.path),
                key="download_" + e.unique_identifier,
            )
            try:
                _link = self._get_jupyter_link()
                _link += "/" + os.path.dirname(e.file_info.path)
                # im_link = self._jupyter_link(_link, "50em")
                col2.markdown(
                    f"[Edit in Jupyterlab]({_link}/)",
                    unsafe_allow_html=True,
                )
            except RuntimeError:
                pass

            #             if self.git_origin is not None:
            #                url = self.get_file_edit_link(e)
            #                col3.markdown(f"[Edit on Gitlab]({url})", unsafe_allow_html=True)

            col3.button(
                ":speech_balloon: add a comment",
                on_click=lambda: setattr(e.state, "adding_comment", True),
                key=f"add_comment_button_{e.unique_identifier}",
            )

            self.mime_type_information(e, col1, details_layout)
            with details_layout:
                try:
                    with st.spinner(f"Loading {e.file_info.path}..."):
                        e.view()
                except Exception as err:
                    st.error("Error trying to display file")
                    st.exception(err)
                    # raise err

            def close_file():
                e.state.view = False
                st.session_state["currently_opened"].remove(e.unique_identifier)

            col5.button("Close", key=f"close_button_{e.unique_identifier}", on_click=close_file)

    def show_discussions(self, e):
        if not e.discussions:
            return
        if not e.archived_discussions:
            st.markdown("### :speech_balloon: Discussions")
            for author, message in e.discussions:
                SpeechBubble(author, message)
            st.markdown("<br>", unsafe_allow_html=True)

            st.button(
                "Respond",
                on_click=lambda: setattr(e.state, "adding_comment", True),
                key=f"respond_button_{e.unique_identifier}",
            )
            st.markdown("---")

        if self.show_advanced:
            if e.discussions:
                st.markdown("---")
                if not e.archived_discussions:
                    st.button("Archive messages", on_click=e.archive_discussions())
                else:
                    st.button("Unarchive messages", on_click=e.archive_discussions(False))

                st.markdown("---")

    def scan_directories(self, dir_path):
        paths_to_explore = []
        all_paths = []
        self._open_in_jupyterlab_button()
        self._force_rescan_button()

        _st = self.file_selector.expander("File selection tool", expanded=True)
        self.file_wildcard = _st.text_input("File pattern", value=self.file_wildcard)
        self.file_error_checkbox = _st.checkbox("Show only files with errors")

        with st.spinner("Loading directories..."):
            if "scanned_files" not in st.session_state:
                st.session_state["scanned_files"] = {}
                h = self.scanner.scan(dir_path, scan_files=False)
                s_files = st.session_state["scanned_files"]
                s_files["all_paths"] = [d[0] for d in list_files(h)]
                s_files["nodes"] = transform_to_subtree(h)
            else:
                s_files = st.session_state["scanned_files"]
            nodes = s_files["nodes"]
            all_paths = s_files["all_paths"]
            _st = self.file_selector.expander("Path selection", expanded=True)
            with _st:
                return_select = tree_select(
                    nodes,
                    expanded=all_paths,
                    expand_disabled=True,
                    checked=all_paths,
                )
                paths_to_explore.clear()
                for c in return_select["checked"]:
                    paths_to_explore.append(c)

        return all_paths, paths_to_explore

    def main(self, dir_path):
        if "GUI_files" not in st.session_state:
            st.session_state["GUI_files"] = {}

        if "currently_opened" not in st.session_state:
            st.session_state["currently_opened"] = []

        self.show_advanced = self.options.checkbox("Advanced", value=False)
        show_zenodo_publish_button = self.options.checkbox("Show zenodo publish (advanced)", value=False)

        self.zenodo_infos.show()
        if show_zenodo_publish_button:
            self.zenodo_publish.show()
        self._environment_info()
        if self.git_repository is not None:
            self._git_info()

        if self.display_push_button:
            changed_files = self.git_get_changed_files()
            if changed_files:
                self.modified_state.button(
                    "Dataset in a modified state: Push Modifications ?",
                    on_click=self.git_push,
                    type="primary",
                    use_container_width=True,
                )
            else:
                self.modified_state.empty()

        if self.git_origin is not None:
            self.gitlab_issues.show()

        st.markdown(
            """
        <style>
        .css-18j515v {
          justify-content: left;
        }
        .css-1umgz6k {
          justify-content: left;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )
        st.markdown("---")
        all_paths, selected_paths = self.scan_directories(dir_path)

        if not selected_paths:
            st.markdown("#### Please select a directory on the left panel")
            return

        if "all_found_files" not in st.session_state:
            with st.spinner("Scanning files..."):
                found = self.scanner.scan_dirs([p for p in all_paths], recursive=False)
                st.session_state["all_found_files"] = found

        all_found_files = st.session_state["all_found_files"]

        if not all_found_files:
            st.markdown(f"#### Nothing in the paths: {selected_paths}")
            return

        self.display_files(all_found_files, selected_paths)

        # if show_logs:
        #     with self.logs.expander("Logs"):
        #         st.markdown("---")
        #         for k, v in reversed(st.session_state["logs"]):
        #             st.markdown(f"**{k}** -> {type(v).__name__}")
        #             st.markdown(v)
        #     with self.logs.expander("State"):
        #         st.json(st.session_state, expanded=False)

    def _get_jupyter_link(self):
        try:
            session = os.environ["SESSION_URL"]
            dir_path = os.getcwd()
            rel_path = os.path.relpath(dir_path, self.git_root)
            _link = f"{session}/lab/tree/{rel_path}"
            return _link
        except Exception:
            raise RuntimeError("Not in a renku session")

    def _jupyter_link(self, uri, size):
        _img = f'<a href="{uri}"><img height="{size}" src="data:image/png;base64,{_jupyter_icon}"></a>'
        return _img

    def _write_jupyter_link(self):
        try:
            _link = self._get_jupyter_link()
            # im_link = self._jupyter_link(_link, "50em")
            st.markdown(
                f"### <center>[View/Edit in Jupyterlab]({_link}) </center>",
                unsafe_allow_html=True,
            )
        except Exception as err:
            st.error("Jupyter not accessible: " + str(err))

    def display_files(self, found, selected_paths):
        files = list_files(found)
        bar = self.progress_layout.progress(0, text="Loading files")

        selected_files = []
        for full_path, f in files:
            if os.path.dirname(full_path) not in selected_paths and full_path not in selected_paths:
                continue
            selected_files.append((full_path, f))

        n_files = len(selected_files)

        for i, (full_path, f) in enumerate(selected_files):
            percent_complete = i * 100 // n_files
            bar.progress(percent_complete + 1, text=f"Loading {full_path}")
            if isinstance(f, File) or isinstance(f, FileSequence):
                f = FileWrapper(f)
                # f.state.set_logger(lambda key, m: self.logger(key, m))
                self.display_file(f, readme=True)
            else:
                self.display_dir(full_path, f)
        self.progress_layout.empty()

    def display_dir(self, d, content):
        found_files = False
        for k, v in content.items():
            if isinstance(v, File):
                if fnmatch.fnmatch(v.file_info.path.lower(), self.file_wildcard):
                    found_files = True

        if found_files:
            components.html(
                '<div style="'
                "padding: 0 1em;"
                "line-height: 4em;"
                "border-radius: .5em;"
                "background-color: #dbeff8;"
                "font-family: 'Source Sans Pro', sans-serif;"
                'color:black;"><h3> &#128193; &nbsp;&nbsp;'
                f"{d} </h3></div>"
            )

        for k, v in content.items():
            if not isinstance(v, File):
                continue
            # n = os.path.basename(v.file_info.path).lower()
            # if n == "readme.md":
            #     v = FileWrapper(v)
            #     # v.state.set_logger(lambda key, m: self.logger(key, m))
            #     self.display_file(v, readme=True)

    def _open_in_jupyterlab_button(self):
        with self.jupyter_control:
            self._write_jupyter_link()

    def _environment_info(self):
        with self.env_layout.expander("Environment"):
            table_env = [k for k in os.environ.items()]
            st.dataframe(table_env)

    def _git_info(self):
        with self.git_control.container():
            changed_files = self.git_get_changed_files()
            changed_files = [e for e in changed_files if not e.startswith(".solidipes/cloud/")]
            if changed_files:
                with st.expander("Modified Files", expanded=False):
                    for p in changed_files:
                        st.markdown(f"- {p}")

                    st.button(
                        "Revert Modifications",
                        type="primary",
                        use_container_width=True,
                        on_click=self.git_revert,
                    )

    def git_get_changed_files(self):
        changed_files = []
        if self.git_repository:
            changed_files = [item.a_path for item in self.git_repository.index.diff(None)]
        return changed_files

    def git_revert(self):
        repo = get_git_repository()
        ret = repo.git.reset("--hard")
        print("git revert", ret)
        print("git revert", type(ret))
        print("git revert return", ret)
        # self.logger("git revert", ret)
        # self.logger("git revert", type(ret))
        # self.logger("git revert return", ret)
        zenodo_metadata = get_study_metadata()
        import yaml

        zenodo_content = yaml.safe_dump(zenodo_metadata)
        st.session_state["zenodo_metadata_editor"] = zenodo_content
        # self.logger(
        #     "st.session_state['zenodo_metadata_editor']",
        #     st.session_state["zenodo_metadata_editor"],
        # )
        st.session_state["rewrote_zenodo_content"] = True
        self.clear_session_state()

    def git_push(self):
        import subprocess

        import git

        save_cwd = os.getcwd()
        try:
            os.chdir(get_git_root())
            changed_files = self.git_get_changed_files()
            # changed_files = [os.path.relpath(e, os.getcwd()) for e in changed_files]
            for e in changed_files:
                ret = self.git_repository.git.add(e)
            if ret != "":
                self.global_message.info(ret)

            ret = self.git_repository.git.commit('-m "Automatic update from solidipes interface"')
            if ret != "":
                self.global_message.info(ret)

        except git.GitCommandError as err:
            self.global_message.error(err)
            print(err)
            os.chdir(save_cwd)
            return

        os.chdir(save_cwd)

        p = subprocess.Popen(
            "renku dataset update --delete -c --all --no-remote",
            shell=True,
            stdout=subprocess.PIPE,
        )
        p.wait()
        out, err = p.communicate()

        if not p.returncode == 0:
            self.global_message.error("renku update failed")
            if out is not None:
                self.global_message.error(out.decode())
            if err is not None:
                self.global_message.error(err.decode())
        else:
            self.global_message.info(out.decode())

        try:
            origin = self.git_repository.remotes.origin
            origin.push("master")

        except git.GitCommandError as err:
            self.global_message.error(err)
            return

        self.global_message.success("Update repository complete")

        self.clear_session_state()

    # def logger(self, key, message):
    #     print(key, message)
    #     if "logs" not in st.session_state:
    #         st.session_state["logs"] = []
    #     import inspect
    #
    #     caller = inspect.stack()[1]
    #     # filename = caller[1]
    #     line = caller[2]
    #     func = caller[3]
    #     key = func + ":" + str(line) + ": " + key
    #     try:
    #         st.session_state["logs"].append((key, message))
    #     except KeyError:
    #         pass

    def _force_rescan_button(self):
        rescan_button = self.update_buttons.button("Force folder scan", use_container_width=True, type="primary")

        if rescan_button:
            self.clear_session_state()

    def clear_session_state(self):
        print("Clearing session state")
        keys = [k for k in st.session_state]
        for k in keys:
            del st.session_state[k]


################################################################


def make(dir_path, additional_arguments=""):
    import subprocess

    cmd = f"streamlit run {__file__} {' '.join(additional_arguments)}"
    print(cmd)
    subprocess.call(cmd, shell=True, cwd=dir_path)


################################################################
if __name__ == "__main__":
    report = Report()
    report.main("./")
