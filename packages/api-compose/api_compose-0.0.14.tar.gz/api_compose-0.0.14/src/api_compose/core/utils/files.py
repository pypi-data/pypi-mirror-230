from pathlib import Path
from typing import List

from api_compose.core.logging import get_logger

logger = get_logger(__name__)


def is_folder_populated(
        folder_path: Path
) -> bool:
    files: List[str] = get_file_names_in(folder_path)

    if len(files) == 0:
        return False
    else:
        return True


def are_files_unique_in(
        folder_path: Path
) -> bool:
    files: List[str] = get_file_names_in(folder_path)
    is_unique = len(set(files)) == len(files)
    if not is_unique:
        logger.error(f'Files with identical names found in {files}')

    return is_unique


def get_file_paths_relative_to(
        folder_path: Path,
        file_name: str
) -> List[Path]:
    file_paths: List[Path] = []

    if folder_path.exists() and folder_path.is_dir():
        for file in folder_path.glob('**/*'):
            if file.stem == file_name:
                file_paths.append(file.relative_to(folder_path))
    else:
        logger.warning(f'Path {folder_path} either does not exist or is not a directory.')

    return file_paths


def get_file_names_in(
        folder_path: Path
) -> List[str]:
    if folder_path.exists() and folder_path.is_dir():
        return [file.stem for file in folder_path.glob('**/*') if file.is_file()]
    else:
        return []
