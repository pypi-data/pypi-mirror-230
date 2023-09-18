from pathlib import Path

from api_compose.services.common.env import get_env_vars_context
from api_compose.core.settings.settings import GlobalSettingsModelSingleton
from api_compose.core.utils.dict import merge_dict
from api_compose.core.utils.string import normalise_sentence
from api_compose.services.common.deserialiser import get_models_description
from api_compose.services.common.deserialiser.deserialiser import deserialise_manifest_to_model
from api_compose.services.common.exceptions import ManifestDescriptionNotFoundException
from api_compose.services.common.models.base import BaseModel
from api_compose.services.common.models.ref_resolver import RefResolverModel
from api_compose.services.common.processors.base import BaseProcessor
from api_compose.services.common.registry.processor_registry import ProcessorRegistry, ProcessorCategory


@ProcessorRegistry.set(
    processor_category=ProcessorCategory.RefResolver,
    models=[
        RefResolverModel(
            model_name='RefResolverModel',
            id='some_ref',
            description='',
            ref='actions/action_one.yaml',
            context=dict(
                execution_id='action_one_exec_one',
                url='http://abc.com',
                limit='12',
            ),
        ),
    ]
)
class RefResolver(BaseProcessor):
    """Resolve the reference"""

    def __init__(
            self,
            ref_resolver_model: RefResolverModel,
    ):
        super().__init__()
        self.ref_resolver_model = ref_resolver_model
        self.ref_resolver_model.description = normalise_sentence(self.ref_resolver_model.description)
        self.manifests_folder_path = ref_resolver_model.manifests_folder_path

        if len(ref_resolver_model.description) != 0:
            self.set_id()

    def set_id(self):
        """Based on Description - id mapping, resolve description to id"""
        mapping = get_models_description(self.manifests_folder_path)
        id = mapping.get(self.ref_resolver_model.description)
        if id is None:
            raise ManifestDescriptionNotFoundException(
                manifest_folder_path=self.manifests_folder_path,
                manifest_description=self.ref_resolver_model.description,
                mapping={key: str(val) for key, val in mapping.items()}
            )
        else:
            self.ref_resolver_model.id = id

    def resolve(
            self,
    ) -> BaseModel:
        # merged_context = merge_dict(
        #     self.ref_resolver_model.env_vars_context,
        #     self.ref_resolver_model.context
        # )
        # merged_context = merge_dict(
        #     merged_context,
        #     self.ref_resolver_model.cli_context,
        # )

        model: BaseModel = deserialise_manifest_to_model(
            manifest_file_path=Path(self.ref_resolver_model.id),
            manifests_folder_path=self.manifests_folder_path,
            env_vars_context=self.ref_resolver_model.env_vars_context,
            extra_context=self.ref_resolver_model.extra_context,

        )
        return model
