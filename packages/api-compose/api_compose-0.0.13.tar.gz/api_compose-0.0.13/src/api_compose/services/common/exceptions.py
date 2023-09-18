import json
from pathlib import Path
from typing import List, Dict, Set

from api_compose.core.utils.files import get_file_paths_relative_to, get_file_names_in
from api_compose.core.utils.list import get_duplicates_in_list


class ProcessorNonUniqueException(Exception):
    def __init__(
            self,
            target_processor: str,
    ):
        self.target_processor = target_processor

    def __str__(self):
        return f'Processor {self.target_processor} is registered Twice!'


class ProcessorNotFoundException(Exception):
    def __init__(
            self,
            target_processor: str,
            available_processors: List[str],
    ):
        self.target_processor = target_processor
        self.available_processors = available_processors

    def __str__(self):
        return f'No processor is found with {self.target_processor}. {self.available_processors=}'


class TagNotFoundException(Exception):
    def __init__(
            self,
            target_tag: str,
            available_tags: Set[str],
    ):
        self.target_tag = target_tag
        self.available_tags = available_tags

    def __str__(self):
        return f'No tag is found with name {self.target_tag}. {self.available_tags=}'


class ModelNotFoundException(Exception):
    def __init__(
            self,
            target_model: str,
            available_models: List[str],
    ):
        self.target_model = target_model
        self.available_models = available_models

    def __str__(self):
        return f'No model is found with name {self.target_model}. {self.available_models=}'


# Manifest Folder Exception
class ManifestFolderNotFoundException(Exception):
    def __init__(self,
                 manifest_folder_path: Path,
                 ):
        self.manifest_folder_path = manifest_folder_path

    def __str__(self):
        return (f"Manifests folder does not exist {self.manifest_folder_path.absolute()} \n"
                f"Is the location of the manifests folder correctly specified?")


# Manifest Folder Exception
class ManifestFolderEmptyException(Exception):
    def __init__(self,
                 manifest_folder_path: Path,
                 ):
        self.manifest_folder_path = manifest_folder_path

    def __str__(self):
        return (f"No manifests are found in the folder {self.manifest_folder_path.absolute()}. \n")


# Manifest Model Exception
class ManifestModelNotSpecifiedException(Exception):
    def __init__(self,
                 manifest_file_path: Path,
                 manifest_content: Dict,
                 available_model_names: List[str],
                 ):
        self.manifest_file_path = manifest_file_path
        self.manifest_content = manifest_content
        self.available_model_names = available_model_names

    def __str__(self):
        return (f"Missing Key ***model_name*** in manifest {self.manifest_file_path=} with content \n"
                f"{json.dumps(self.manifest_content, indent=4)} \n"
                f"Please add a key-value pair with key **model_name**. {self.available_model_names=}")


# Manifest Id Exception
class ManifestIdNonUniqueException(Exception):
    def __init__(self,
                 manifest_folder_path: Path,
                 ):
        self.manifest_folder_path = manifest_folder_path

        self.file_paths_with_identifical_file_names = {
            f: get_file_paths_relative_to(manifest_folder_path, f) for f in get_duplicates_in_list(
                get_file_names_in(manifest_folder_path)
            )
        }

    def __str__(self):
        return (f"Path {self.manifest_folder_path} has the below file paths with identical file names \n"
                f"{self.file_paths_with_identifical_file_names}. \n"
                f"Please eliminate identical files \n"
                )


class ManifestIdNotFoundException(Exception):
    def __init__(self,
                 manifest_folder_path: Path,
                 target_manifest_id: str,
                 ):
        self.manifest_folder_path = manifest_folder_path
        self.target_manifest_id = target_manifest_id

    def __str__(self):
        return f"No manifest with id **{self.target_manifest_id}** is found in Path **{self.manifest_folder_path.absolute()}**"


# Manifest Description Exception
class ManifestDescriptionNotFoundException(Exception):
    def __init__(self,
                 manifest_folder_path: Path,
                 manifest_description: str,
                 mapping: Dict[str, str],
                 ):
        self.manifest_folder_path = manifest_folder_path
        self.manifest_description = manifest_description
        self.mapping = mapping

    def __str__(self):
        return (
            f"No manifest with description **{self.manifest_description}** is found in Path **{self.manifest_folder_path}**. \n"
            f"Mapping of description against manifest path is {json.dumps(self.mapping, indent=4)}")


class ManifestDescriptionNonUniqueException(Exception):
    def __init__(self,
                 offending_description: str,
                 offending_manifest_file_paths: List[Path],
                 ):
        self.offending_description = offending_description
        self.offending_manifest_file_paths = offending_manifest_file_paths

    def __str__(self):
        return (f"Below Manifest File Paths share the same Description {self.offending_description}! \n",
                f"{self.offending_manifest_file_paths}")


class ManifestRenderException(Exception):
    def __init__(self,
                 manifest_file_path: Path,
                 context: Dict,
                 ):
        self.manifest_file_path = manifest_file_path
        self.context = context

    def __str__(self):
        return (f"Error - Cannot render manifest at path {self.manifest_file_path} with context \n"
                f"{json.dumps(self.context, indent=4)}")


class ManifestDeserialisationException(Exception):
    def __init__(self,
                 manifest_file_path: Path,
                 model_name: str,
                 content: Dict
                 ):
        self.manifest_file_path = manifest_file_path
        self.model_name = model_name
        self.content = content

    def __str__(self):
        return (f"Error - Cannot deserialise manifest at path {self.manifest_file_path} \n"
                f" to {self.model_name} with content \n"
                f"{self.content}"
                )
