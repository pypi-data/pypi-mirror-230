__all__ = ['get_yaml_with_representers']

from pathlib import Path, PosixPath
from typing import Dict, Tuple, List, Union

from lxml import etree
from lxml.etree import _Element

from api_compose.core.logging import get_logger
from api_compose.core.lxml.parser import PrintableElement
from api_compose.root.models.scenario import ExecutionIdAssignmentEnum
from api_compose.services.assertion_service.models.jinja_assertion import AssertionStateEnum
from api_compose.services.common.models.functional_testing import FunctionalTestingEnum
from api_compose.services.common.models.text_field.text_field import TextFieldFormatEnum
from api_compose.services.composition_service.models.actions.states import ActionStateEnum
from api_compose.services.composition_service.models.executors.enum import ExecutorProcessorEnum
from api_compose.services.composition_service.models.protocols.protocols import ActionAPIProtocolEnum
from api_compose.services.composition_service.models.protocols.status_enums import OtherResponseStatusEnum, \
    HttpResponseStatusEnum
from api_compose.services.persistence_service.models.enum import BackendProcessorEnum
from api_compose.services.reporting_service.models.enum import ReportProcessorEnum

logger = get_logger(__name__)


def dump_dict_to_single_yaml_file(
        dict_: Dict,
        file_path: Path
):
    output_folder = file_path.parent
    if not output_folder.exists():
        output_folder.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w') as f:
        get_yaml_with_representers().dump(dict_, f)
        logger.info(f"Model is saved at {file_path=}")


def get_yaml_with_representers():
    import yaml

    yaml.add_representer(Path, _str_path_representer)
    yaml.add_representer(PosixPath, _str_path_representer)
    yaml.add_representer(set, _str_list_representer)
    yaml.add_representer(BackendProcessorEnum, _str_enum_representer)
    yaml.add_representer(ReportProcessorEnum, _str_enum_representer)
    yaml.add_representer(TextFieldFormatEnum, _str_enum_representer)
    yaml.add_representer(ActionAPIProtocolEnum, _str_enum_representer)
    yaml.add_representer(OtherResponseStatusEnum, _int_enum_representer)
    yaml.add_representer(HttpResponseStatusEnum, _int_enum_representer)
    yaml.add_representer(ActionStateEnum, _str_enum_representer)
    yaml.add_representer(ExecutorProcessorEnum, _str_enum_representer)
    yaml.add_representer(ExecutionIdAssignmentEnum, _str_enum_representer)
    yaml.add_representer(AssertionStateEnum, _str_enum_representer)
    yaml.add_representer(FunctionalTestingEnum, _str_enum_representer)
    yaml.add_representer(_Element, _lxml_element_representer)
    yaml.add_representer(PrintableElement, _lxml_element_representer)
    return yaml


def _str_list_representer(dumper, data):
    return dumper.represent_sequence('tag:yaml.org,2002:seq', list(data))


def _str_path_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', str(data))


def _str_enum_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data.value)


def _int_enum_representer(dumper, data):
    return dumper.represent_int(data.value)


def _lxml_element_representer(dumper, data):
    # Need flexibility
    return dumper.represent_scalar('tag:yaml.org,2002:str', etree.tostring(data, encoding='unicode'))
