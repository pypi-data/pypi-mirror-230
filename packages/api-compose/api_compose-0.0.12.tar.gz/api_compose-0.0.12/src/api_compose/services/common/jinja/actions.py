""" Jinja Globals """

from typing import List

import jinja2

from api_compose.core.utils.exceptions import NoMatchesFoundWithFilter
from api_compose.services.common.models.text_field.templated_text_field import BaseTemplatedTextField
from api_compose.services.common.registry.jinja_function_registry import JinjaFunctionType
from api_compose.services.common.registry.jinja_function_registry import JinjaFunctionsRegistry
from api_compose.services.composition_service.models.actions.actions.base_action import ReservedExecutionId, \
    BaseActionModel


@JinjaFunctionsRegistry.set(
    name='acp.actions.actions',
    func_type=JinjaFunctionType.Global,
    alias=['actions']
)
@jinja2.pass_context
def get_actions(context: jinja2.runtime.Context) -> List[BaseActionModel]:
    """
    Example Usage in Jinja: {{ acp.actions.actions() }}
    """
    return dict(context).get('action_models')


@JinjaFunctionsRegistry.set(
    name='acp.actions.action',
    func_type=JinjaFunctionType.Global,
    alias=['action']
)
@jinja2.pass_context
def get_action(context: jinja2.runtime.Context,
               execution_id: str,
               ) -> BaseActionModel:
    """
    Example Usage in Jinja: {{ acp.actions.action('execution_id') }}
    """
    action_model = None
    if execution_id == ReservedExecutionId.Self.value:
        action_model = dict(context).get('current_action_model')
    else:
        action_models = get_actions(context)
        for candidate_action_model in action_models:
            if candidate_action_model.execution_id == execution_id:
                action_model = candidate_action_model

        if action_model is None:
            raise NoMatchesFoundWithFilter(
                filter={'execution_id': execution_id},
                collection=action_models)

    return action_model


@JinjaFunctionsRegistry.set(
    name='acp.actions.config_headers',
    func_type=JinjaFunctionType.Filter,
    alias=['config_headers']
)
@jinja2.pass_context
def get_action_config_headers_new(
        context: jinja2.runtime.Context,
        action_model: BaseActionModel,
):
    """
    Example Usage in Jinja: {{ acp.actions.action('execution_id') | acp.actions.config_method }}
    """
    templated_text_field: BaseTemplatedTextField = get_action_attribute(
        action_model,
        ['config', 'headers'],
    )
    return render_templated_text_field(context, templated_text_field=templated_text_field)


@JinjaFunctionsRegistry.set(
    name='acp.actions.config_method',
    func_type=JinjaFunctionType.Filter,
    alias=['config_method'],
)
@jinja2.pass_context
def get_action_config_method(
        context: jinja2.runtime.Context,
        action_model: BaseActionModel,
):
    """
    Example Usage in Jinja: {{ acp.actions.action('execution_id') | acp.actions.config_method }}
    """

    templated_text_field: BaseTemplatedTextField = get_action_attribute(
        action_model,
        ['config', 'method'],
    )
    return render_templated_text_field(context, templated_text_field=templated_text_field)


@JinjaFunctionsRegistry.set(
    name='acp.actions.config_params',
    func_type=JinjaFunctionType.Filter,
    alias=['config_params'],
)
@jinja2.pass_context
def get_action_config_params(
        context: jinja2.runtime.Context,
        action_model: BaseActionModel,
):
    """
    Example Usage in Jinja: {{ acp.actions.action('execution_id') | acp.actions.config_params }}
    """
    templated_text_field: BaseTemplatedTextField = get_action_attribute(
        action_model,
        ['config', 'params'],
    )
    return render_templated_text_field(context, templated_text_field=templated_text_field)


@JinjaFunctionsRegistry.set(
    name='acp.actions.config_body',
    func_type=JinjaFunctionType.Filter,
    alias=['config_body'],
)
@jinja2.pass_context
def get_action_config_body(
        context: jinja2.runtime.Context,
        action_model: BaseActionModel,
):
    """
    Example Usage in Jinja: {{ acp.actions.action('execution_id') | acp.actions.config_body }}
    """
    templated_text_field: BaseTemplatedTextField = get_action_attribute(
        action_model,
        ['config', 'body'],
    )
    return render_templated_text_field(context, templated_text_field=templated_text_field)


@JinjaFunctionsRegistry.set(
    name='acp.actions.input_url',
    func_type=JinjaFunctionType.Filter,
    alias=['input_url'],
)
def get_action_input_url(
        action_model: BaseActionModel,
):
    """
    Example Usage in Jinja: {{ acp.actions.action('execution_id') | acp.actions.input_url }}
    """
    return get_action_attribute(
        action_model,
        ['input', 'url'],
    )


@JinjaFunctionsRegistry.set(
    name='acp.actions.input_body',
    func_type=JinjaFunctionType.Filter,
    alias=['input_body'],
)
def get_action_input_body(
        action_model: BaseActionModel,
):
    """
    Example Usage in Jinja: {{ acp.actions.action('execution_id') | acp.actions.input_body }}
    """
    return get_action_attribute(
        action_model,
        ['input', 'body'],
    )


@JinjaFunctionsRegistry.set(
    name='acp.actions.output_body',
    func_type=JinjaFunctionType.Filter,
    alias=['output_body'],
)
def get_action_output_body(
        action_model: BaseActionModel,
):
    """
    Example Usage in Jinja: {{ acp.actions.action('execution_id') | acp.actions.output_body }}
    """
    return get_action_attribute(
        action_model,
        ['output', 'body'],
    )


@JinjaFunctionsRegistry.set(
    name='acp.actions.output_headers',
    func_type=JinjaFunctionType.Filter,
    alias=['output_headers'],
)
def get_action_output_headers(
        action_model: BaseActionModel,
):
    """
    Example Usage in Jinja: {{ acp.actions.action('execution_id') | acp.actions.output_headers }}
    """
    return get_action_attribute(
        action_model,
        ['output', 'headers'],
    )


@JinjaFunctionsRegistry.set(
    name='acp.actions.output_status_code',
    func_type=JinjaFunctionType.Filter,
    alias=['output_status_code'],
)
def get_action_output_status_code(
        action_model: BaseActionModel,
):
    """
    Example Usage in Jinja: {{ acp.actions.action('execution_id') | acp.actions.status_code }}
    """
    return get_action_attribute(
        action_model,
        ['output', 'status_code'],
    )


def render_templated_text_field(
        context: jinja2.runtime.Context,
        templated_text_field: BaseTemplatedTextField,
):
    """
    """
    # Context has all the global functions already
    environmnent = context.environment
    str_ = environmnent.from_string(templated_text_field.template).render(context)
    return templated_text_field.serde.deserialise(str_)


def get_action_attribute(
        action_model: BaseActionModel,
        action_attrs: List[str],
):
    """

    Parameters
    ----------
    action_model: Base Action Model
    action_attrs: a list of attributes
    Returns
    -------

    """
    for action_attr in action_attrs:
        action_attr = action_attr.strip()
        action_model = getattr(action_model, action_attr)

    return action_model
