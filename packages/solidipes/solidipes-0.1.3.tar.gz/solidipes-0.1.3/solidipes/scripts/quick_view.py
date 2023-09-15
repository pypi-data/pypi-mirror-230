import argparse

command = "view"
command_help = "generate a view from a file"

################################################################


def main(args):
    """Generate a .py report for the given directory."""
    from .. import viewer_backends
    from ..loaders.sequence import Sequence
    from ..utils import load_file

    path = args.path
    _file = load_file(path)
    print(_file)

    if viewer_backends.current_backend == "streamlit":
        import streamlit as st

        st.set_page_config(layout="wide")

    if args.item > 0 and isinstance(_file, Sequence):
        _file.select_element(args.item)
    _file.view()


def populate_arg_parser(parser):
    parser.description = """Generate view for the given file."""

    parser.add_argument("path", help="Path to file to be viewed")
    parser.add_argument(
        "--item", type=int, default=0, help="In case the object is a sequence helpful to select the correct item"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    populate_arg_parser(parser)
    args = parser.parse_args()
    main(args)
