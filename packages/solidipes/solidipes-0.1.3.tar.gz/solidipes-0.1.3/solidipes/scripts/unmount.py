import argparse

command = "unmount"
command_help = "Unmount cloud storage"


def main(args):
    import os

    from ..cloud import list_mounts, unmount
    from ..utils import bcolors, get_cloud_info, get_path_relative_to_root, set_cloud_info

    mounts = list_mounts(only_mounted=not args.forget)

    # --list-mounted: show mounted directories
    if args.list_mounted:
        print("Currently mounted directories:")

        for local_path, mount_info in mounts.items():
            if not mount_info.get("mounted"):
                continue
            print(f"    {local_path} {bcolors.OKGREEN}({mount_info['type']}, {mount_info['system']}){bcolors.ENDC}")

        return

    # --local-path: unmount specified directory, otherwise unmount all
    if args.local_path:
        local_path = args.local_path.rstrip(os.sep)
        if local_path not in mounts:
            print(f'"{local_path}" has not been mounted with "solidipes mount".')
            return
        paths_to_unmount = [local_path]
    else:
        paths_to_unmount = list(mounts.keys())

    if len(paths_to_unmount) == 0:
        print("Nothing to unmount.")
        return

    if args.forget:
        config = get_cloud_info()

    for path in paths_to_unmount:  # path relative working directory
        try:
            if os.path.ismount(path):
                unmount(path)
                print(f'Unmounted "{path}"')

        except RuntimeError as e:
            print(f"Error unmounting {path}: {e}")
            continue

        if args.forget:
            path_relative_to_root = get_path_relative_to_root(path)
            if path_relative_to_root in config:
                del config[path_relative_to_root]
                print(f'Forgot mount info for "{path}"')

    if args.forget:
        set_cloud_info(config)


def populate_arg_parser(parser):
    parser.description = command_help

    parser.add_argument(
        "-p",
        "--local-path",
        nargs="?",
        default="",
        help="Path of the directory to unmount. If not specified, all mounted directories are unmounted.",
    )

    parser.add_argument(
        "-f",
        "--forget",
        help="Also delete mount info from saved configuration",
        action="store_true",
    )

    parser.add_argument(
        "-l",
        "--list-mounted",
        help="List currently mounted directories",
        action="store_true",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    populate_arg_parser(parser)
    args = parser.parse_args()
    main(args)
