__all__ = ["Runner"]

from api_compose.root.processors.specification import SpecificationProcessor

"""
Composition Root
"""
import datetime

from api_compose.core.logging import get_logger
from api_compose.core.settings.settings import GlobalSettingsModelSingleton
from api_compose.core.jinja.core.engine import JinjaEngine

from api_compose.services.reporting_service.processors.base_report import BaseReport
from api_compose.services.persistence_service.processors.base_backend import BaseBackend
from api_compose.root.models.session import SessionModel
from api_compose.root.models.specification import SpecificationModel
from api_compose.services.common.registry.processor_registry import ProcessorRegistry

logger = get_logger(name=__name__)


class Runner:

    def __init__(self,
                 session_model: SessionModel,
                 jinja_engine: JinjaEngine,
                 ):
        self.session_model = session_model
        self.session_model.set_parent_ids()

        self.backend: BaseBackend = ProcessorRegistry.create_processor_by_name(
            class_name=GlobalSettingsModelSingleton.get().backend.processor.value,
            config={},
        )
        self.jinja_engine: JinjaEngine = jinja_engine

    def _execute_specification(self, specification_model: SpecificationModel):
        # Parallel Execution of Specifications??
        print(specification_model.fqn)

        specification_processor = SpecificationProcessor(
            specification_model,
            backend=self.backend,
            jinja_engine=self.jinja_engine,
        )

        specification_processor.run()

    def _execute_report_renderer(self):
        # Generate report(s)
        output_folder = GlobalSettingsModelSingleton.get().reporting.reports_folder

        report: BaseReport = ProcessorRegistry.create_processor_by_name(
            class_name=GlobalSettingsModelSingleton.get().reporting.processor.value,
            config=dict(
                model=self.session_model,
                model_template_path='session.html.j2',
                output_folder=output_folder,
                registry=ProcessorRegistry(),
            )
        )
        report.run()

    def run(self):
        for idx, scenario_group_model in enumerate(self.session_model.specifications):
            self._execute_specification(scenario_group_model)
            if idx != len(self.session_model.specifications) - 1:
                # don't sleep for last group at the end
                logger.debug(
                    f"Specification Model {scenario_group_model.id} done..... going to sleep for {self.session_model}"
                )

        self._execute_report_renderer()
