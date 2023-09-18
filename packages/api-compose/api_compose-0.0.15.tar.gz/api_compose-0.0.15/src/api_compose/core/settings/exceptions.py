from pathlib import Path


class IncludeExcludeBothSetException(Exception):
    def __init__(
            self,
            include_manifest_file_paths,
            include_tags,
            include_models,
            exclude_manifest_file_paths,
            exclude_tags,
            exclude_models,
    ):
        self.include_manifest_file_paths = include_manifest_file_paths
        self.include_tags = include_tags
        self.include_models = include_models
        self.exclude_manifest_file_paths = exclude_manifest_file_paths
        self.exclude_tags = exclude_tags
        self.exclude_models = exclude_models

    def __str__(self):
        return ('Both include and exclude cannot be set at the same time. \n'
                f'{self.include_manifest_file_paths=} \n'
                f'{self.include_tags=} \n'
                f'{self.include_models=} \n'
                f'{self.exclude_manifest_file_paths=} \n'
                f'{self.exclude_tags=} \n'
                f'{self.exclude_models=}')


class ConfigurationFileException(Exception):

    def __init__(
            self,
            config_file_path: Path,
    ):
        self.config_file_path = config_file_path

    def __str__(self):
        return f"""Error: Configuration File {self.config_file_path.absolute()} error"""
