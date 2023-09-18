from typing import Union

from api_compose.core.jinja.core.context import BaseJinjaContext
from api_compose.core.jinja.core.engine import JinjaEngine
from api_compose.core.jinja.exceptions import TemplateRenderFailureException
from api_compose.core.logging import get_logger
from api_compose.services.common.events.templated_field import TemplatedFieldEvent
from api_compose.services.common.models.text_field.text_field import BaseTextField, StringTextField, \
    IntegerTextField, YamlTextField, JsonTextField, XmlTextField

logger = get_logger(__name__)


class BaseTemplatedTextField(BaseTextField):
    template: str = ""

    # Setters
    def render_to_text(self, jinja_engine: JinjaEngine, jinja_context: BaseJinjaContext) -> 'BaseTemplatedTextField':
        # Step 1: render string
        logger.debug(f"template is {self.template=}", TemplatedFieldEvent())

        rendered, is_success, exec = jinja_engine.set_template_by_string(self.template).render_to_str(
            jinja_context)

        if not is_success:
            # raise instead?
            logger.error(f"Cannot render template {self.template=}", TemplatedFieldEvent())
            logger.error(f"{is_success=}", TemplatedFieldEvent())
            logger.error(f"Exception Message={str(exec)}", TemplatedFieldEvent())
            logger.error(f"Available Globals {jinja_engine._custom_global_keys=}", TemplatedFieldEvent())
            raise TemplateRenderFailureException(
                template=self.template,
                exec=exec,
                jinja_globals=jinja_engine._environment.globals) from exec

        self.text = rendered
        logger.debug(f"rendered to {self.text=}")
        return self


class StringTemplatedTextField(StringTextField, BaseTemplatedTextField):
    pass


class IntegerTemplatedTextField(IntegerTextField, BaseTemplatedTextField):
    pass


class YamlTemplatedTextField(YamlTextField, BaseTemplatedTextField):
    pass


class JsonTemplatedTextField(JsonTextField, BaseTemplatedTextField):
    pass


class XmlTemplatedTextField(XmlTextField, BaseTemplatedTextField):
    pass


JsonLikeTemplatedTextField = Union[JsonTemplatedTextField, YamlTemplatedTextField]


