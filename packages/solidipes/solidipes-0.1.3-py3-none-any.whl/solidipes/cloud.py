import os
import subprocess
import tempfile
import uuid

from .config import cloud_connection_timeout
from .utils import (
    get_cloud_dir_path,
    get_cloud_info,
    get_path_relative_to_root,
    get_path_relative_to_workdir,
    set_cloud_info,
)

key_names_per_mount_type = {
    "s3": ["access_key_id", "secret_access_key"],
    "smb": ["password"],
}


def check_process_return(process, fail_message):
    try:
        process.check_returncode()

    except subprocess.CalledProcessError as e:
        if e.stderr:
            raise RuntimeError(f"{fail_message}: {e.stderr.decode()}")
        else:
            raise RuntimeError(fail_message)


def get_existing_mount_info(path):
    path = get_path_relative_to_root(path)
    config = get_cloud_info()

    if path not in config:
        raise ValueError(f'Path "{path}" has not been set as mounting point.')

    mount_info = config[path]
    return mount_info


def get_mount_id(mount_info):
    """Create new unique mount_id if not already set."""

    if "mount_id" not in mount_info:
        mount_id = str(uuid.uuid4())
        mount_info["mount_id"] = mount_id
    else:
        mount_id = mount_info["mount_id"]

    return mount_id


def mount(path, mount_info, headless=False):
    if os.path.ismount(path):
        raise RuntimeError(f'"{path}" is already mounted.')

    mount_type = mount_info["type"]

    if mount_type == "s3":
        mount_system = mount_info.get("system", "juicefs")

        if mount_system == "juicefs":
            mount_s3_juicefs(path, mount_info)

        elif mount_system == "s3fs":
            mount_s3fs(path, mount_info)

    elif mount_type == "ssh":
        mount_system = mount_info.get("system", "sshfs")

        if mount_system == "sshfs":
            mount_sshfs(path, mount_info, headless=headless)

    elif mount_type == "nfs":
        mount_system = mount_info.get("system", "mount")

        if mount_system == "mount":
            mount_nfs_with_mount_command(path, mount_info, headless=headless)

    elif mount_type == "smb":
        mount_system = mount_info.get("system", "mount")

        if mount_system == "mount":
            mount_smb_with_mount_command(path, mount_info, headless=headless)

    else:
        raise ValueError(f'Unknown cloud storage type "{mount_type}".')

    wait_mount(path)


def wait_mount(path):
    import time

    wait = 0
    while not os.path.ismount(path):
        time.sleep(1)
        wait += 1
        if wait > cloud_connection_timeout:
            raise RuntimeError(f'"{path}" may not be mounted.')


def mount_s3fs(path, mount_info=None):
    if mount_info is None:
        mount_info = get_existing_mount_info(path)

    # Check that keys are available
    if "access_key_id" not in mount_info or "secret_access_key" not in mount_info:
        raise RuntimeError("Mounting failed: access_key_id and secret_access_key are not available.")

    # Create directory if it does not exist
    if not os.path.exists(path):
        os.makedirs(path)

    # Create temporary passwd file
    passwd_path = write_temp_passwd_file(mount_info["access_key_id"], mount_info["secret_access_key"])

    # Mount S3 bucket
    bucket_path = mount_info["bucket_name"]
    mount_id = get_mount_id(mount_info)
    remote_dir_name = mount_info.get("remote_dir_name", mount_id)
    if remote_dir_name != ".":
        bucket_path += f":/{remote_dir_name.rstrip('/')}"

    mount_process = subprocess.run(
        [
            "s3fs",
            bucket_path,
            path,
            "-o",
            f"passwd_file={passwd_path}",
            "-o",
            f"url={mount_info['endpoint_url']}",
            "-o",
            "nonempty",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=cloud_connection_timeout,
    )

    check_process_return(mount_process, "Mounting failed")

    # Remove temporary passwd file
    os.remove(passwd_path)


def write_temp_passwd_file(access_key_id, secret_access_key):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".passwd", delete=False) as f:
        f.write(f"{access_key_id}:{secret_access_key}\n")
        file_path = f.name

    return file_path


def mount_s3_juicefs(path, mount_info=None):
    if mount_info is None:
        mount_info = get_existing_mount_info(path)

    # Create directory if it does not exist
    if not os.path.exists(path):
        os.makedirs(path)

    # Create mount_id (if necessary), used to find database file
    mount_id = get_mount_id(mount_info)

    database_filename = f"{mount_id}.db"
    database_path = os.path.join(get_cloud_dir_path(), database_filename)
    database_url = f"sqlite3://{database_path}"
    bucket_url = f"{mount_info['endpoint_url'].rstrip('/')}/{mount_info['bucket_name']}"

    # Create database file and remote directory if first time mount
    if not os.path.exists(database_path):
        remote_dir_name = mount_info.get("remote_dir_name", mount_id)
        format_process = subprocess.run(
            [
                "juicefs",
                "format",
                "--storage",
                "s3",
                "--bucket",
                bucket_url,
                "--access-key",
                mount_info["access_key_id"],
                "--secret-key",
                mount_info["secret_access_key"],
                database_url,
                remote_dir_name,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=cloud_connection_timeout,
        )
        check_process_return(format_process, "Formatting failed")

    # Otherwise, just put keys in the database
    else:
        add_keys_process = subprocess.run(
            [
                "juicefs",
                "config",
                database_url,
                "--access-key",
                mount_info["access_key_id"],
                "--secret-key",
                mount_info["secret_access_key"],
                "--force",  # Skip keys validation
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=cloud_connection_timeout,
        )
        check_process_return(add_keys_process, "Failed to add keys to database")

    # Mount S3 bucket
    mount_process = subprocess.run(
        [
            "juicefs",
            "mount",
            "--background",
            database_url,
            path,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=cloud_connection_timeout,
    )
    check_process_return(mount_process, "Mounting failed")

    # Remove keys from database
    remove_keys_process = subprocess.run(
        [
            "juicefs",
            "config",
            database_url,
            "--access-key",
            "",
            "--secret-key",
            "",
            "--force",  # Skip keys validation
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=cloud_connection_timeout,
    )
    check_process_return(remove_keys_process, "Failed to remove keys from database")


def mount_sshfs(path, mount_info=None, headless=False):
    if mount_info is None:
        mount_info = get_existing_mount_info(path)

    # Create directory if it does not exist
    if not os.path.exists(path):
        os.makedirs(path)

    # Mount SSH file system
    endpoint = mount_info["endpoint"]
    command = [
        "sshfs",
        endpoint,
        path,
    ]

    options = []
    if headless:
        options.append("password_stdin")
    if len(options) > 0:
        command += ["-o", ",".join(options)]

    mount_process = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=cloud_connection_timeout,
        input=b"\n" if headless else None,
    )
    check_process_return(mount_process, "Mounting failed")


def mount_nfs_with_mount_command(path, mount_info=None, headless=False):
    mount_with_mount_command("nfs", path, mount_info, headless=headless)


def mount_smb_with_mount_command(path, mount_info=None, headless=False):
    mount_with_mount_command("cifs", path, mount_info, headless=headless)


def mount_with_mount_command(mount_command_type, path, mount_info, headless=False):
    if mount_info is None:
        mount_info = get_existing_mount_info(path)

    # Create directory if it does not exist
    if not os.path.exists(path):
        os.makedirs(path)

    # Mount using "mount" command
    endpoint = mount_info["endpoint"]
    command = [
        "sudo",
        "mount",
        "-t",
        mount_command_type,
        endpoint,
        path,
    ]

    if headless:
        command.insert(1, "-S")  # read password from stdin

    options = []
    if "username" in mount_info:
        options.append(f"username={mount_info['username']}")
    if "password" in mount_info:
        options.append(f"password={mount_info['password']}")
    elif headless:
        options.append("password=''")
    if "domain" in mount_info:
        options.append(f"domain={mount_info['domain']}")
    if len(options) > 0:
        command.extend(["-o", ",".join(options)])

    mount_process = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=cloud_connection_timeout,
        input=b"\n" if headless else None,
    )
    check_process_return(mount_process, "Mounting failed")


def unmount(path, headless=False):
    command = ["umount", path]

    # Check if mounting method requires sudo
    config = get_cloud_info()
    path_relative_to_root = get_path_relative_to_root(path)
    mount_system = config.get(path_relative_to_root, {}).get("system", "")
    sudo = mount_system in ["mount"]

    if sudo:
        command.insert(0, "sudo")
        if headless:
            command.insert(1, "-S")  # read password from stdin

    unmount_process = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        input=b"\n" if headless else None,
    )
    check_process_return(unmount_process, "Unmounting failed")


def convert_local_to_cloud(local_path, mount_info):
    """Copy local content to cloud, unmount temp cloud and mount at final location"""

    temp_path = tempfile.mkdtemp()
    print("Mounting to temporary location...")
    mount(temp_path, mount_info)

    print("Copying local content to cloud...")
    rsync(local_path, temp_path)
    os.system(f"rm -rf {local_path}")

    print("Unmounting temporary cloud...")
    unmount(temp_path)
    os.rmdir(temp_path)

    print("Mounting cloud at final location...")
    mount(local_path, mount_info)


def convert_cloud_to_cloud(local_path, mount_info_prev, mount_info_new):
    raise NotImplementedError("Not implemented. Please convert to local first.")


def add_keys_to_info(mount_info):
    """Use mount_id to retrieve keys from user home's .solidipes directory.

    Keys already present in mount_info are not replaced.
    If one key is not found, no error is raised. Error should happen later when trying to mount.
    """

    # Missing keys should be listed in mount_info["remote_keys"]
    missing_keys = mount_info.get("removed_keys", [])

    # Backward compatibility if "removed_keys" is not present
    if len(missing_keys) == 0:
        mount_type = mount_info["type"]

        if mount_type == "s3":
            missing_keys = key_names_per_mount_type[mount_type].copy()

            # Remove keys that are already present in mount_info
            for missing_key in missing_keys.copy():
                if missing_key in mount_info:
                    missing_keys.remove(missing_key)

    if len(missing_keys) == 0:
        return

    # Retrieve user info
    mount_id = mount_info["mount_id"]
    user_config = get_cloud_info(user=True)

    if mount_id not in user_config and len(missing_keys) > 0:
        print(f'Warning: Mount information for "{mount_id}" not found in user\'s .solidipes directory.')
        return
    user_mount_info = user_config[mount_id]

    # Replace current keys with user's keys
    for key_name in missing_keys:
        if key_name not in user_mount_info:
            print(f'Warning: Private credential "{key_name}" not found for mount "{mount_id}"')
            continue
        mount_info[key_name] = user_mount_info[key_name]


def remove_keys_from_info(mount_info):
    """Remove keys from info and generate mount_id if necessary"""

    mount_type = mount_info["type"]
    key_names = key_names_per_mount_type.get(mount_type, None)
    if key_names is None:
        return

    # Retrieve user info
    mount_id = get_mount_id(mount_info)
    user_config = get_cloud_info(user=True)

    # Remove keys from current config, and add "removed_keys" entry
    removed_keys = {}

    for key_name in key_names:
        if key_name in mount_info:
            removed_keys[key_name] = mount_info.pop(key_name)
            if "removed_keys" not in mount_info:
                mount_info["removed_keys"] = []
            mount_info["removed_keys"].append(key_name)

    # Save keys in user config (if does not already exist)
    if mount_id not in user_config and len(removed_keys) > 0:
        user_config[mount_id] = removed_keys
        set_cloud_info(user_config, user=True)


def rsync(source_dir, target_dir, delete=False):
    args = [
        "rsync",
        "-rlv",  # recursive, links, verbose, cannot use -a with juicefs
        source_dir.rstrip("/") + "/",
        target_dir,
    ]

    if delete:
        args.append("--delete")

    rsync_process = subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    check_process_return(rsync_process, "Rsync failed")


def list_mounts(only_mounted=False):
    """Get config expressed relative to working directory, with mount status"""

    config = get_cloud_info()
    mounts = {}

    for local_path, mount_info in config.items():
        local_path_relative_to_workdir = get_path_relative_to_workdir(local_path)
        mount_info["mounted"] = os.path.ismount(local_path_relative_to_workdir)
        if only_mounted and not mount_info["mounted"]:
            continue
        mounts[local_path_relative_to_workdir] = mount_info

    return mounts


def mount_all(headless=False):
    """Mount all mounts that are not already mounted"""

    mounts = list_mounts()
    for local_path, mount_info in mounts.items():
        if mount_info["mounted"]:
            continue

        print(f"Mounting {local_path}...")
        try:
            add_keys_to_info(mount_info)
            mount(local_path, mount_info, headless=headless)
        except Exception as e:
            print(f"Error: {e}")

    print("Mount All: Done!")


def unmount_all(headless=False):
    """Unmount all mounted mounts"""

    mounts = list_mounts(only_mounted=True)
    for local_path in mounts.keys():
        print(f"Unmounting {local_path}...")
        try:
            unmount(local_path, headless=headless)
        except Exception as e:
            print(f"Error: {e}")
