__all__ = ['JinjaAssertion']

import traceback
from typing import Optional, Tuple

from api_compose.core.events.jinja import JinjaRenderingEvent
from api_compose.core.jinja.core.context import BaseJinjaContext
from api_compose.core.jinja.core.engine import JinjaEngine
from api_compose.core.logging import get_logger
from api_compose.services.assertion_service.events import AssertionEvent
from api_compose.services.assertion_service.exceptions import JinjaTemplateNotEvaluatedToBooleanException
from api_compose.services.assertion_service.models.jinja_assertion import JinjaAssertionModel, AssertionStateEnum

logger = get_logger(__name__)


class JinjaAssertion():

    def __init__(self,
                 assertion_model: JinjaAssertionModel,
                 jinja_context: BaseJinjaContext,
                 jinja_engine: JinjaEngine,
                 ):
        self.assertion_model = assertion_model
        self.template = assertion_model.template
        self.jinja_context = jinja_context
        self.jinja_engine = jinja_engine

    def run(self):
        try:
            is_success, text, exec = self.execute()
            exec = str(exec)
        except Exception as e:
            logger.warning(traceback.format_exc(), AssertionEvent())
            is_success = False
            text = ''
            exec = str(e)

        self.assertion_model.is_success = is_success
        self.assertion_model.text = text
        self.assertion_model.exec = exec
        self.assertion_model.state = AssertionStateEnum.EXECUTED

    def execute(self) -> Tuple[bool, str, Optional[Exception]]:
        text, is_success, exec = self.jinja_engine.set_template_by_string(self.template).render_to_str(
            self.jinja_context)


        if is_success:
            cleaned_text = text.strip().lower().strip("'").strip('"')
            if cleaned_text == 'true':
                return True, text, exec
            elif cleaned_text == 'false':
                return False, text, exec
            else:
                try:
                    raise JinjaTemplateNotEvaluatedToBooleanException(self.template)
                except Exception as exec:
                    logger.warning(traceback.format_exc(), AssertionEvent())
                    return False, text, exec
        else:
            return False, text, exec
