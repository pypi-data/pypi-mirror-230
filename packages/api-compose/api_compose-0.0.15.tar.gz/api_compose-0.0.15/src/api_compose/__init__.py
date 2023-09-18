""" Init Core Programme"""
__all__ = ['FunctionsRegistry',  # exposed to lib users
           'get_logger']

import os  # noqa - for debugging
import sys
from pathlib import Path

from api_compose.cli.events import DiscoveryEvent
from api_compose.core.settings.settings import GlobalSettingsModelSingleton
from api_compose.services.common.events.jinja_function_registration import JinjaFunctionRegistrationEvent

# read into global settings
GlobalSettingsModelSingleton.set()

from api_compose.services.common.registry.jinja_function_registry import FunctionsRegistry, \
    FunctionType  ## For lib users

# Get logger after settings are set
# Help with import from CLI
sys.path.append(str(Path.cwd()))
from api_compose.services.common.env import get_env_vars_context
from api_compose.core.logging import get_logger
from api_compose.core.utils.dynamic_import import safe_import_module

# Import for side effect (Controller Registration)
## Register Jinja Functions
from api_compose.services.composition_service.jinja import *  # noqa - registery jinja functions

## Register Processor
from api_compose.services.common.processors.ref_resolver import RefResolver  # noqa - register ref processor to Registry

from api_compose.services.persistence_service.processors.base_backend import \
    BaseBackend  # noqa - register backend to Registry
from api_compose.services.persistence_service.processors.simple_backend import \
    SimpleBackend  # noqa - register backend to Registry

from api_compose.services.composition_service.processors.actions import Action  # noqa - register action to Registry
from api_compose.services.composition_service.processors.adapters.dummy_adapter import \
    DummyAdapter  # noqa - register adapter to Registry
from api_compose.services.composition_service.processors.adapters.http_adapter.json_http_adapter import \
    JsonHttpAdapter  # noqa - register adapter to Registry
from api_compose.services.composition_service.processors.adapters.http_adapter.xml_http_adapter import \
    XmlHttpAdapter  # noqa - register adapter to Registry
from api_compose.services.composition_service.processors.adapters.websocket_adapter import \
    JsonRpcWebSocketAdapter  # noqa - register adapter to Registry
from api_compose.services.composition_service.processors.executors.local_executor import \
    LocalExecutor  # noqa - register executors to Registry

from api_compose.services.composition_service.processors.schema_validators.json_schema_validator import \
    JsonSchemaValidator  # noqa - register Schema Validator to Registry
from api_compose.services.composition_service.processors.schema_validators.xml_schema_validator import \
    XmlSchemaValidator  # noqa - register executors to Registry

from api_compose.services.reporting_service.processors.html_report import \
    HtmlReport  # noqa - register report_renderers to Registry
