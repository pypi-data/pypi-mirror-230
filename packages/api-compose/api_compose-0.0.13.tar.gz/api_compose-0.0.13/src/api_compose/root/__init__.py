from api_compose.core.jinja.core.engine import JinjaEngine
from api_compose.core.logging import get_logger
from api_compose.root.events import SessionEvent
from api_compose.root.models.session import SessionModel
from api_compose.root.models.session import SessionModel
from api_compose.root.runner import Runner
from api_compose.services.common.jinja import build_runtime_jinja_engine

logger = get_logger(__name__)


def run_session_model(
        session_model: SessionModel,
) -> SessionModel:
    logger.info(f'Running Session {session_model.id=}', SessionEvent())
    jinja_engine: JinjaEngine = build_runtime_jinja_engine()
    runner = Runner(session_model, jinja_engine)
    runner.run()
    return runner.session_model


