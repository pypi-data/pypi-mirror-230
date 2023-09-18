from api_compose.core.jinja.core.engine import JinjaEngine
from api_compose.core.logging import get_logger
from api_compose.root.events import SpecificationEvent
from api_compose.root.models.specification import SpecificationModel
from api_compose.root.processors.scenario import ScenarioProcessor
from api_compose.services.common.processors.base import BaseProcessor
from api_compose.services.common.registry.processor_registry import ProcessorRegistry, ProcessorCategory
from api_compose.services.persistence_service.processors.base_backend import BaseBackend

logger = get_logger(__name__)


@ProcessorRegistry.set(

    processor_category=ProcessorCategory.Backend,
    models=[
        SpecificationModel(
            model_name='SpecificationModel',
            id='example_scenario_group',
            description='example specification',
            scenarios=[],
        )
    ]
)
class SpecificationProcessor(BaseProcessor):

    def __init__(self,
                 specification_model: SpecificationModel,
                 backend: BaseBackend,
                 jinja_engine: JinjaEngine,
                 ):
        super().__init__()
        self.specification_model = specification_model
        self.jinja_engine = jinja_engine
        self.backend = backend

    def run(self):
        logger.info(f'Running Specification {self.specification_model.id}', SpecificationEvent())
        for idx, scenario_model in enumerate(self.specification_model.scenarios):
            scenario_controller = ScenarioProcessor(
                scenario_model=scenario_model,
                backend=self.backend,
                jinja_engine=self.jinja_engine,
            )

            scenario_controller.run()

        self.backend.add(self.specification_model)
