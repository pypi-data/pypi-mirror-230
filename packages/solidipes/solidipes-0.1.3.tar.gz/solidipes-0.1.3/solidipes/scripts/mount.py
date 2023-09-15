import argparse

command = "mount"
command_help = "Mount cloud storage"


def main(args):
    from ..cloud import (
        add_keys_to_info,
        convert_cloud_to_cloud,
        convert_local_to_cloud,
        list_mounts,
        mount,
        mount_all,
        remove_keys_from_info,
    )
    from ..utils import bcolors, get_cloud_info, get_path_relative_to_root, set_cloud_info

    config = get_cloud_info()

    # --all: mount all existing mount points
    if args.all:
        mount_all()
        return

    # --list-existing: show existing mount points
    if args.list_existing:
        mounts = list_mounts()
        print("Existing mount points:")

        for local_path, mount_info in mounts.items():
            mounted_message = " mounted" if mount_info["mounted"] else ""
            print(
                f"    {local_path} {bcolors.OKGREEN}({mount_info['type']},"
                f" {mount_info['system']}){mounted_message}{bcolors.ENDC}"
            )

        return

    # Mount or convert, depending on provided and saved configuration
    local_path_relative_to_root = get_path_relative_to_root(args.local_path)
    mount_info_saved = config.get(local_path_relative_to_root, None)
    mount_info_provided = get_mount_info_from_args(args)

    if mount_info_saved is not None:
        if mount_info_provided is not None:
            if args.convert:
                if not args.force:
                    print(f'Mount info for "{args.local_path}" already exists. Use --force to convert. Aborting...')
                    return
                add_keys_to_info(mount_info_saved)
                convert_cloud_to_cloud(args.local_path, mount_info_saved, mount_info_provided)

            else:
                if not args.force:
                    print(f'Mount info for "{args.local_path}" already exists. Use --force to replace it. Aborting...')
                    return
                print("Mounting...")
                mount(args.local_path, mount_info_provided)

        else:  # Mount info not provided
            if args.convert:
                print(f'No mount info provided for converting "{args.local_path}". Aborting...')
                return

            else:
                add_keys_to_info(mount_info_saved)
                print("Mounting...")
                mount(args.local_path, mount_info_saved)

    else:  # Mount info not saved
        if mount_info_provided is not None:
            if args.convert:
                convert_local_to_cloud(args.local_path, mount_info_provided)

            else:
                print("Mounting...")
                mount(args.local_path, mount_info_provided)

        else:  # Mount info not provided
            print("No mount info provided and no mount info saved for this directory.")
            return

    # Save config info if mount is successful
    if local_path_relative_to_root not in config or args.force:
        if not args.public_keys:
            remove_keys_from_info(mount_info_provided)
        config[local_path_relative_to_root] = mount_info_provided
        set_cloud_info(config)

    print("Mount: Done!")


def get_mount_info_from_args(args):
    if args.type == "s3":
        mount_info = {
            "type": "s3",
            "system": args.system,
            "endpoint_url": args.endpoint_url.rstrip("/"),
            "bucket_name": args.bucket_name,
            "access_key_id": args.access_key_id,
            "secret_access_key": args.secret_access_key,
        }

        if args.remote_dir_name is not None:
            mount_info["remote_dir_name"] = args.remote_dir_name.rstrip("/")

        return mount_info

    elif args.type in ["ssh", "nfs", "smb"]:
        mount_info = {
            "type": args.type,
            "system": args.system,
            "endpoint": args.endpoint.rstrip("/"),
        }
        if getattr(args, "username", ""):
            mount_info["username"] = args.username
        if getattr(args, "password", ""):
            mount_info["password"] = args.password
        if getattr(args, "domain", ""):
            mount_info["domain"] = args.domain

        return mount_info

    elif args.type is None:
        return None

    else:
        raise ValueError(f'Unknown cloud storage type "{args.type}".')


def populate_arg_parser(parser):
    parser.description = command_help

    paths = parser.add_mutually_exclusive_group(required=True)

    paths.add_argument(
        "-p",
        "--local-path",
        help=(
            "Path to the directory to mount. If the directory has already been mounted before, there is no need to"
            " indicate other mounting parameters. If not specified, the command shows existing mounting points."
        ),
    )

    paths.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Mount all existing mounting points (not already mounted).",
    )

    paths.add_argument(
        "-l",
        "--list-existing",
        action="store_true",
        help="List existing mount points.",
    )

    parser.add_argument(
        "-f",
        "--force",
        help="Replace the currently saved configuration for this directory",
        action="store_true",
    )

    parser.add_argument(
        "-c",
        "--convert",
        action="store_true",
        help="Send the contents of the local directory to the cloud storage (convert it to cloud storage).",
    )

    parser.add_argument(
        "-k",
        "--public-keys",
        action="store_true",
        help=(
            "Save all access keys publicly in local .solidipes directory. WARNING: when published, everyone will be"
            " able to see your keys and will have full access (possibly write access) to your mounted directory."
        ),
    )

    # Cloud types subparsers
    type_parsers = parser.add_subparsers(dest="type", help="Type of cloud storage to mount")

    s3_parser = type_parsers.add_parser("s3", help="S3 bucket")
    populate_s3_parser(s3_parser)

    ssh_parser = type_parsers.add_parser("ssh", help="remote file system through ssh")
    populate_ssh_parser(ssh_parser)

    nfs_parser = type_parsers.add_parser("nfs", help="nfs file system")
    populate_nfs_parser(nfs_parser)

    smb_parser = type_parsers.add_parser("smb", help="smb file system")
    populate_smb_parser(smb_parser)


def populate_s3_parser(parser):
    parser.description = "Mount an S3 bucket"

    parser.add_argument(
        "endpoint_url",
        metavar="endpoint-url",
        help="URL of the S3 endpoint",
    )

    parser.add_argument(
        "bucket_name",
        metavar="bucket-name",
        help="Name of the S3 bucket",
    )

    parser.add_argument(
        "access_key_id",
        metavar="access-key-id",
        help="Access key ID",
    )

    parser.add_argument(
        "secret_access_key",
        metavar="secret-access-key",
        help="Secret access key",
    )

    parser.add_argument(
        "-s",
        "--system",
        choices=["juicefs", "s3fs"],
        default="juicefs",
        help="System to use for mounting. Default: juicefs",
    )

    parser.add_argument(
        "-n",
        "--remote-dir-name",
        help="Name of the mounted directory in the bucket. If not specified, a random unique name is attributed.",
    )


def populate_ssh_parser(parser):
    parser.description = "Mount a remote file system through ssh"

    parser.add_argument(
        "endpoint",
        help="[user@]host[:path]",
    )

    parser.add_argument(
        "-s",
        "--system",
        choices=["sshfs"],
        default="sshfs",
        help="System to use for mounting. Default: sshfs",
    )


def populate_nfs_parser(parser):
    parser.description = "Mount an nfs file system"

    parser.add_argument(
        "endpoint",
        help="host:path",
    )

    parser.add_argument(
        "-s",
        "--system",
        choices=["mount"],
        default="mount",
        help="System to use for mounting. Default: mount command",
    )


def populate_smb_parser(parser):
    parser.description = "Mount an smb file system"

    parser.add_argument(
        "endpoint",
        help="//host/path",
    )

    parser.add_argument(
        "-u",
        "--username",
        default="",
        help="Username",
    )

    parser.add_argument(
        "-s",
        "--system",
        choices=["mount"],
        default="mount",
        help="System to use for mounting. Default: mount command",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    populate_arg_parser(parser)
    args = parser.parse_args()
    main(args)
