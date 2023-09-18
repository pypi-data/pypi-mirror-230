import webbrowser
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from api_compose import GlobalSettingsModelSingleton, get_env_vars_context
from api_compose.core.logging import get_logger
from api_compose.root import SessionModel
from api_compose.services.common.registry.processor_registry import ProcessorRegistry, ProcessorCategory
from api_compose.services.composition_service.models.actions.states import ActionStateEnum
from api_compose.services.reporting_service.processors.base_report import BaseReport
from api_compose.services.reporting_service.utils.plots import dump_actions_duration_graph

HTML_FILE_TEMPLATE_FOLDER = Path(__file__).parent.joinpath("html_templates")

logger = get_logger(__name__)


@ProcessorRegistry.set(

    processor_category=ProcessorCategory.Executor,
    models=[
        # No model required
    ]
)
class HtmlReport(BaseReport):
    """
    Implementation for rendering reports in HTML
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def render(self):
        env = Environment(
            loader=FileSystemLoader(HTML_FILE_TEMPLATE_FOLDER),
            # When there are HTML tags (e.g. failed JsonHttp body or expected XmlHttp body)
            autoescape=True
        )
        env.globals["set"] = set
        env.globals["vars"] = vars
        env.globals["enumerate"] = enumerate

        try:
            template = env.get_template(self.model_template_path)
        except TemplateNotFound as e:
            logger.error(f'Available templates: {env.list_templates(extensions="j2")}')
            raise ValueError(
                f'Template Not Found: {self.model_template_path}. Available Templates: {env.list_templates("j2")}')
        else:
            self.report = template.render(
                settings=GlobalSettingsModelSingleton.get(),
                env_vars_context = get_env_vars_context([path for path in GlobalSettingsModelSingleton.get().current_env_files_pack.paths]),
                model=self.model,
                model_template_path=self.model_template_path,
                registered_entries=self.registry.registry,
                action_state=ActionStateEnum,
            )

    def write(self):
        # Dump Graph
        if type(self.model) == SessionModel:
            # Actions Duration Graph
            scenario_actions_mapping = {scenario.actions_duration_file_name: scenario.actions for specification in
                                        self.model.specifications for scenario in specification.scenarios}
            for actions_duration_file_name, actions in scenario_actions_mapping.items():
                dump_actions_duration_graph(actions, self.output_folder_path.joinpath(actions_duration_file_name))

        # Write HTML
        self.path_to_output = self.output_folder_path.joinpath(
            f"{self.model.__class__.__name__}_report.html"
        )
        with open(self.path_to_output, "w") as f:
            logger.info(f'Dumping HTML report - {self.path_to_output=}')
            f.write(self.report)

            if GlobalSettingsModelSingleton.get().cli_options.is_interactive:
                webbrowser.open(str(self.path_to_output))
