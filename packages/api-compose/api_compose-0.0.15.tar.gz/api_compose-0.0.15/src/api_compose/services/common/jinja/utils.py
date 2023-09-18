import jinja2
import yaml

from api_compose import FunctionsRegistry, FunctionType
from api_compose.core.utils.json_path import parse_json_with_jsonpath


@FunctionsRegistry.set(
    name='acp.utils.double_quote',
    func_type=FunctionType.JinjaFilter,
    alias=['double_quote']
)
def add_double_quote(value):
    """
    Add double quotations to a string. Similar to Helm `quote`.
    Example Usage in Jinja: {{ value | acp.utils.double_quote }}
    """
    return f'"{value}"'


@FunctionsRegistry.set(
    name='acp.utils.single_quote',
    func_type=FunctionType.JinjaFilter,
    alias=['single_quote']
)
def add_single_quote(value):
    """
    Add single quotations to a string. Similar to Helm `quote`.
    Example Usage in Jinja: {{ value | acp.utils.single_quote }}
    """
    return f"'{value}'"


@FunctionsRegistry.set(
    name='acp.utils.tpl',
    func_type=FunctionType.JinjaGlobal,
    alias=['tpl']
)
@jinja2.pass_context
def render_template_in_yaml_template(
        context: jinja2.runtime.Context,
        json_path: str,
):
    """
    Evaluate a template inside a yaml template. See Helm `tpl`.

    Example Usage in Jinja: {{ acp.utils.tpl('$.path.to.variable') }}
    """
    template: str = dict(context).get('template')
    dict_ = yaml.load(template, Loader=yaml.FullLoader)

    return parse_json_with_jsonpath(dict_, json_path, get_all_matches=False)
