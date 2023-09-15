import os

from .config import solidipes_dirname


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def load_file(path):
    """Load a file from path into the appropriate object type"""

    import os

    from .loaders.binary import Binary
    from .loaders.code_snippet import CodeSnippet
    from .loaders.geof_mesh import GeofMesh
    from .loaders.image import Image
    from .loaders.image_sequence import ImageSequence
    from .loaders.pdf import PDF
    from .loaders.pyvista_mesh import PyvistaMesh
    from .loaders.table import Table
    from .loaders.text import Markdown, Text
    from .loaders.video import Video

    # Note: the first matching type is used
    loader_list = [
        Table,
        PyvistaMesh,
        ImageSequence,
        Image,
        Markdown,
        Text,
        CodeSnippet,
        GeofMesh,
        Video,
        PDF,
    ]

    if not os.path.isfile(path):
        raise FileNotFoundError(f'File "{path}" does not exist')

    for loader in loader_list:
        if loader.check_file_support(path):
            return loader(path)

    # if no extension or unknown extension, assume binary
    file = Binary(path)

    return file


def find_config_directory(initial_path="", dir_name=solidipes_dirname):
    """Find a directory in the current path or any of its parents"""

    import os

    current_path = os.path.abspath(initial_path)

    while True:
        # Check if current path contains the directory
        test_path = os.path.join(current_path, dir_name)
        if os.path.isdir(test_path):
            return test_path

        # Check if current path is the root
        if current_path == os.path.dirname(current_path):
            break

        # Move up to the parent directory
        current_path = os.path.dirname(current_path)

    raise FileNotFoundError(f'The directory "{dir_name}" was not found in {initial_path} or any of its parents')


def get_solidipes_directory(initial_path=""):
    """Get the path to the .solidipes directory"""

    import os

    try:
        solidipes_directory = find_config_directory(initial_path, solidipes_dirname)

        # If parent directory is user's home, it is invalid (user_solidipes_directory)
        if os.path.dirname(solidipes_directory) == os.path.expanduser("~"):
            raise FileNotFoundError

        return solidipes_directory

    except FileNotFoundError as e:
        raise FileNotFoundError(f'{e}. Please run "solidipes init" at the root directory of your study.')


def get_user_solidipes_directory():
    import os

    path = os.path.join(os.path.expanduser("~"), solidipes_dirname)

    if not os.path.isdir(path):
        if os.path.exists(path):
            raise FileExistsError(f'"{path}" exists but is not a directory. Please remove it.')
        os.mkdir(path)

    return path


def get_study_root_path(initial_path="", **kwargs):
    import os

    return os.path.dirname(get_solidipes_directory(initial_path))


def get_path_relative_to_root(path):
    """Express path relative to study root"""

    path = os.path.abspath(path)  # Also strips trailing slash
    path = os.path.relpath(path, get_study_root_path())

    return path


def get_path_relative_to_workdir(path):
    """Convert path expressed relative to study root to path expressed relative to current working directory"""

    path = os.path.join(get_study_root_path(), path)
    path = os.path.relpath(path, os.getcwd())

    return path


def get_git_repository(initial_path=""):
    import os

    from git import Repo

    current_path = os.path.abspath(initial_path)
    git_repository = Repo(current_path, search_parent_directories=True)
    return git_repository


def get_git_root(initial_path=""):
    repo = get_git_repository(initial_path)
    git_root = repo.git.rev_parse("--show-toplevel")
    return git_root


def get_config_path(filename_var, initial_path="", check_existence=False, user=False):
    import os

    from . import config

    filename = getattr(config, filename_var)

    if user:
        config_directory = get_user_solidipes_directory()
    else:
        config_directory = get_solidipes_directory(initial_path)
    path = os.path.join(config_directory, filename)

    if check_existence and not os.path.isfile(path):
        raise FileNotFoundError(
            f'The file "{path}" does not exist. Please run "solidipes init" at the root directory of your study.'
        )

    return path


def load_yaml(filename):
    import yaml

    with open(filename) as f:
        config = yaml.safe_load(f.read())
    if config is None:
        config = {}
    return config


def save_yaml(filename, config):
    import yaml

    with open(filename, "w") as f:
        f.write(yaml.safe_dump(config))

    return config


def get_study_metadata_path(*args, **kwargs):
    return get_config_path("study_metadata_filename", *args, **kwargs)


def get_readme_path(*args, **kwargs):
    from .config import readme_filename

    return os.path.join(get_study_root_path(*args, **kwargs), readme_filename)


def get_study_description_path(*args, **kwargs):
    from .config import study_description_filename

    return os.path.join(get_study_root_path(*args, **kwargs), study_description_filename)


def get_mimes_path(*args, **kwargs):
    return get_config_path("mimes_filename", *args, **kwargs)


def get_config(filename_var, *args, **kwargs):
    path = get_config_path(filename_var, *args, **kwargs)
    if not os.path.exists(path):
        return {}
    return load_yaml(path)


def set_config(filename_var, config, *args, **kwargs):
    path = get_config_path(filename_var, *args, **kwargs)
    save_yaml(path, config)


def populate_metadata_mandatory_fields(metadata):
    from .config import study_medatada_mandatory_fields as mandatory_fields

    for field in mandatory_fields.keys():
        if field not in metadata:
            metadata[field] = mandatory_fields[field]


def separate_metadata_description(metadata, html_to_md=False, **kwargs):
    """Remove description from saved yml and put it in a separate file"""

    from markdownify import markdownify

    from .config import description_warning
    from .utils import get_study_description_path

    description = metadata.pop("description", "")  # can be html or md
    if html_to_md:
        description_md = markdownify(description)
    else:
        description_md = description

    description_path = get_study_description_path(**kwargs)
    with open(description_path, "w", encoding="UTF-8") as f:
        f.write(description_md)

    metadata["description"] = description_warning


def include_metadata_description(metadata, use_readme=False, md_to_html=False, **kwargs):
    """Update metadata description field with DESCRIPTION.md file"""

    import os

    from markdown import markdown

    from .config import study_description_filename
    from .utils import get_study_description_path

    description_path = get_study_description_path(**kwargs)

    if use_readme:
        generate_readme(with_title=False, **kwargs)
        description_path = get_readme_path(**kwargs)

    # If DESCRIPTION.md does not exist, create it by parsing current description
    if not os.path.isfile(description_path):
        separate_metadata_description(metadata, html_to_md=True, **kwargs)

    # Update metadata
    with open(description_path, "r", encoding="UTF-8") as f:
        description_md = f.read()

        if md_to_html:
            try:
                description = markdown(description_md, tab_length=2)
            except Exception as e:
                raise ValueError(f"Error parsing {study_description_filename}: {e}")
        else:
            description = description_md

        metadata["description"] = description

    # Re-generate readme
    if use_readme:
        generate_readme(**kwargs)

    return metadata


def get_study_metadata(*args, md_to_html=False, **kwargs):
    metadata = get_config("study_metadata_filename", *args, **kwargs)

    include_metadata_description(metadata, md_to_html=md_to_html, **kwargs)
    populate_metadata_mandatory_fields(metadata)

    return metadata


def generate_readme(*args, with_title=True, **kwargs):
    from .metadata import lang, licenses
    from .utils import get_readme_path

    readme_path = get_readme_path(**kwargs)
    metadata = get_study_metadata(*args, **kwargs)
    with open(readme_path, "w", encoding="UTF-8") as f:
        if with_title:
            f.write(f"# {metadata['title']}\n\n<br>\n\n")
        f.write("## Links\n\n")
        if "DOI" in metadata:
            doi = metadata["DOI"]
            f.write(f"- Data DOI: [{doi}](https://doi.org/{doi})")
        if "related_identifiers" in metadata:
            rels = metadata["related_identifiers"]
            for r in rels:
                if "resource_type" not in r:
                    continue
                f.write(f'- {r["relation"]} *{r["resource_type"]}* [{r["identifier"]}]({r["identifier"]})\n')
            f.write("\n")
        f.write("## Authors\n\n")
        if "creators" in metadata:
            authors = metadata["creators"]
            for a in authors:
                f.write(f'- **{a["name"]}**')
                if "affiliation" in a:
                    f.write(f', {a["affiliation"]}')
                if "orcid" in a:
                    f.write(f', ORCID: [{a["orcid"]}](https:://orcid.org/{a["orcid"]})')
                f.write("\n")
            f.write("\n")

        f.write("## Language\n\n")
        if "language" in metadata:
            _lang = dict(lang)[metadata["language"]]
            f.write(f"- {_lang}\n\n")

        f.write("## License\n\n")
        if "license" in metadata:
            lic = metadata["license"]
            if isinstance(lic, dict):
                lic = lic["id"]
            _lic = dict(licenses)[lic.lower()]
            f.write(f"- {_lic}\n\n")

        f.write(metadata["description"])


def set_study_metadata(config, *args, html_to_md=False, **kwargs):
    config = config.copy()
    separate_metadata_description(
        config, *args, html_to_md=html_to_md, **kwargs
    )  # keep descpription field empty when saving
    set_config("study_metadata_filename", config, *args, **kwargs)
    generate_readme(*args, **kwargs)


def get_zenodo_infos(*args, **kwargs):
    return get_config("zenodo_infos_filename", *args, **kwargs)


def set_zenodo_infos(config, *args, **kwargs):
    set_config("zenodo_infos_filename", config, *args, **kwargs)


def get_mimes(*args, **kwargs):
    try:
        return get_config("mimes_filename", *args, **kwargs)
    except FileNotFoundError:
        return {}


def set_mimes(config, *args, **kwargs):
    set_config("mimes_filename", config, *args, **kwargs)


def get_ignore(*args, **kwargs):
    from .config import default_ignore_patterns

    ignore = get_config("ignore_filename", *args, **kwargs)
    if not ignore:
        ignore = default_ignore_patterns

    return ignore


def set_ignore(config, *args, **kwargs):
    set_config("ignore_filename", config, *args, **kwargs)


def get_cloud_info(*args, **kwargs):
    return get_config("cloud_info_filename", *args, **kwargs)


def set_cloud_info(config, *args, **kwargs):
    set_config("cloud_info_filename", config, *args, **kwargs)


def get_cloud_dir_path(*args, **kwargs):
    cloud_dir_path = get_config_path("cloud_dir_name", *args, **kwargs)

    if not os.path.isdir(cloud_dir_path):
        os.makedirs(cloud_dir_path)

    return cloud_dir_path


def transform_dict_to_data_containers(data):
    from .loaders.data_container import DataContainer

    if isinstance(data, dict):
        data_res = {}
        for k, v in data.items():
            data_res[k] = transform_dict_to_data_containers(v)
        return DataContainer(data_res)

    return data


def get_cached_metadata(initial_path="."):
    # Find cached metadata from closest .solidipes directory
    metadata_all_files = get_config("cached_metadata_filename", initial_path=initial_path)
    for file_path in metadata_all_files:
        m = metadata_all_files[file_path]
        for k in m:
            m[k] = transform_dict_to_data_containers(m[k])
    return metadata_all_files


def transform_data_containers_to_dict(data):
    from .loaders.data_container import DataContainer

    if isinstance(data, DataContainer):
        data = data._data_collection
    if isinstance(data, dict):
        data_res = {}
        for k, v in data.items():
            data_res[k] = transform_data_containers_to_dict(v)
        data = data_res
    # print('transform_data_containers_to_dict:', type(data), data)
    return data


def set_cached_metadata(config, initial_path="."):
    # Set cached metadata in closest .solidipes directory
    set_config("cached_metadata_filename", transform_data_containers_to_dict(config), initial_path=initial_path)
