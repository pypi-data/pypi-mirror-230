import importlib
import traceback
from pathlib import Path
from api_compose.core.logging import get_logger

logger = get_logger(__name__)


def safe_import_module(
        path_to_module: Path,
):
    module = None

    # Get absolute in case relative path is used
    path_to_module = path_to_module.absolute()

    if path_to_module.exists():
        try:
            relative_path = str(path_to_module.relative_to(Path.cwd()))
            relative_path = relative_path.replace('/', '.')
            # Import the module dynamically
            module = importlib.import_module(relative_path)
        except Exception as e:
            logger.error(traceback.format_exc())

    return module
