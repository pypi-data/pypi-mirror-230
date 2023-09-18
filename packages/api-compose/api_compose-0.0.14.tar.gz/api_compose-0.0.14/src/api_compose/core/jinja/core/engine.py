"""
Jinja is rendered in the below order


1. User's template value files rendered with env var, before put into the pydantic models
2. Pydantic models' templates are rendered with user's template value files.
3. Inside an action's adapter, field value(s) in the action root is rendered with value from a previous action

- Env Var in .env file >> template value files >> pydantic root template files >> action models

"""
from __future__ import annotations

__all__ = ['JinjaEngine']

import traceback
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Callable, Type

from jinja2 import BaseLoader, Environment, TemplateNotFound, Template, meta, StrictUndefined, Undefined, \
    FileSystemLoader, ChoiceLoader

from api_compose.core.events.jinja import JinjaRenderingEvent
from api_compose.core.jinja.core.context import BaseJinjaContext
from api_compose.core.jinja.core.loader import PrependingLoader
from api_compose.core.jinja.exceptions import TemplateNotFoundByPathException
from api_compose.core.logging import get_logger

logger = get_logger(__name__)


class JinjaTemplateSyntax(Enum):
    CURLY_BRACES = 'curly_braces'
    SQUARE_BRACKETS = 'square_braces'


class JinjaEngine:
    """
    Render templates all or nothing

    >>> JinjaEngine().set_template_by_string('hello').render_to_str(BaseJinjaContext())
    ('hello', True, None)

    >>> JinjaEngine().set_template_by_string('{{ var }}').render_to_str(BaseJinjaContext())
    ('{{ var }}', False, UndefinedError("'var' is undefined"))

    >>> JinjaEngine().set_template_by_string("key1={{ val1 }}, key2={{ val2 }}").render_to_str(BaseJinjaContext(**dict(val1=12)))
    ('key1={{ val1 }}, key2={{ val2 }}', False, UndefinedError("'val2' is undefined"))


    """

    def __init__(self,
                 templates_search_paths: Optional[List[Path]] = None,
                 macro_template_paths: Optional[List[str]] = None,
                 undefined: Type[Undefined] = StrictUndefined,
                 jinja_template_syntax: JinjaTemplateSyntax = JinjaTemplateSyntax.CURLY_BRACES,
                 globals: Optional[Dict] = None,
                 filters: Optional[Dict] = None,
                 tests: Optional[Dict] = None,
                 ):
        # Internal
        self._template_search_paths = templates_search_paths
        self._macro_template_paths = macro_template_paths
        self._jinja_template_syntax = jinja_template_syntax
        self.undefined = undefined

        # Persistent
        self._loader: BaseLoader = _build_loader(templates_search_paths, macro_template_paths)
        self._custom_globals = globals
        self._environment: Environment = _build_template_env(
            loader=self._loader,
            jinja_template_syntax=jinja_template_syntax,
            undefined=self.undefined,
            globals=globals if globals is not None else {},
            filters=filters if filters is not None else {},
            tests=tests if tests is not None else {},
        )

        # Current
        self.can_strip: bool = False
        self.required_template_file_path: Optional[str] = None
        self.current_template: Optional[Template] = None
        self.current_source: Optional[str] = None

    @property
    def _custom_global_keys(self) -> List[str]:
        return [key for key in self._custom_globals.keys()]

    def _unset(self):
        # unset current values
        self.required_template_file_path: Optional[str] = None
        self.current_template: Optional[Template] = None
        self.current_source: Optional[str] = None

    def set_template_by_file_path(self,
                                  template_file_path: str,
                                  can_strip: bool = True
                                  ) -> JinjaEngine:
        self.can_strip = can_strip
        self.required_template_file_path = template_file_path

        if self._template_search_paths:
            try:
                self.current_template = self._environment.get_template(template_file_path)
            except TemplateNotFound as e:
                logger.error(f'Available Templates are {self.get_available_templates()}')
            except Exception as e:
                # Raise Exception. Programmatic error
                logger.error(traceback.format_exc())
                self._unset()
                raise
            else:
                with open(self.current_template.filename, 'r') as file:
                    self.current_source = file.read()
        else:
            logger.warning(f'Template Search Path not set. Not looking up for file {template_file_path=}')

        return self

    def set_template_by_string(self,
                               template_str: str,
                               can_strip: bool = True,
                               ) -> JinjaEngine:
        self.can_strip = can_strip
        self.current_template = self._environment.from_string(template_str)
        self.current_source = template_str
        return self

    def get_available_templates(self) -> List[Path]:
        """
        Return all available templates in templates_search_paths
        -------

        """
        if self._template_search_paths is not None:
            return [Path(template_path) for template_path in self._environment.list_templates()]
        else:
            return []

    def render_to_str(self, jinja_context: Optional[BaseJinjaContext] = None) -> Tuple[str, bool, Optional[Exception]]:
        """

        Parameters
        ----------
        jinja_context

        Returns
        -------
        Tuple of

        1. rendered str is successful, or the original template if failed
        2. boolean if it is successful or not

        """
        if jinja_context is None:
            jinja_context = BaseJinjaContext()
        else:
            assert isinstance(jinja_context,
                              BaseJinjaContext), f"Please pass in a jinjaContext object! You passed in a {type(jinja_context)}"

        if self.current_template is not None:
            try:
                result, is_success, exec = self.current_template.render(dict(jinja_context)), True, None
                result = result.strip() if self._jinja_template_syntax else result
            except Exception as e:
                logger.warning(traceback.format_exc(), JinjaRenderingEvent())
                result, is_success, exec = self.current_source, False, e
            self._unset()
            return result, is_success, exec
        else:
            try:
                raise TemplateNotFoundByPathException(
                    template_search_paths=self._template_search_paths,
                    required_template_path=self.required_template_file_path,
                    available_template_paths=self.get_available_templates()
                )
            except Exception as exec:
                logger.warning(traceback.format_exc(), JinjaRenderingEvent())
                self._unset()
                return "", False, exec

    def get_template_variables(self, recursive=False) -> List[str]:
        """
        Return all variables used in current template
        Returns
        -------

        """
        variables = []

        if self.current_template is not None and self.current_source is not None:
            parsed_content = self._environment.parse(self.current_source)
            variables += [var for var in meta.find_undeclared_variables(parsed_content)]

            if recursive:
                for referenced_template in meta.find_referenced_templates(parsed_content):
                    variables += self.__class__(
                        templates_search_paths=self._template_search_paths,
                        macro_template_paths=self._macro_template_paths,
                        jinja_template_syntax=self._jinja_template_syntax).set_template_by_file_path(
                        referenced_template).get_template_variables()

        return variables


def _build_template_env(
        loader: BaseLoader,
        jinja_template_syntax=JinjaTemplateSyntax.CURLY_BRACES,
        undefined=Undefined,
        globals: Dict[str, Callable] = None,
        filters: Dict[str, Callable] = None,
        tests: Dict[str, Callable] = None,
) -> Environment:
    """

    Parameters
    ----------
    jinja_template_syntax: What syntax to use in the jinja template. Can be used to render same template for different purposes.

    Returns
    -------
    """
    if jinja_template_syntax == JinjaTemplateSyntax.CURLY_BRACES:
        env = Environment(
            loader=loader,
            undefined=undefined,
            extensions=['jinja2.ext.do'],
            autoescape=False,
            block_start_string='{%',
            block_end_string='%}',
            variable_start_string='{{',
            variable_end_string='}}',
            comment_start_string='{#',
            comment_end_string='#}',
        )
    elif jinja_template_syntax == JinjaTemplateSyntax.SQUARE_BRACKETS:
        env = Environment(
            loader=loader,
            undefined=undefined,
            extensions=['jinja2.ext.do'],
            autoescape=False,
            block_start_string='[%',
            block_end_string='%]',
            variable_start_string='[[',
            variable_end_string=']]',
            comment_start_string='[#',
            comment_end_string='#]',
        )
    else:
        raise ValueError(f'Unhandled jinja template syntax: {jinja_template_syntax}')

    env.globals.update({} if globals is None else globals)
    env.filters.update({} if filters is None else filters)
    env.tests.update({} if tests is None else tests)
    return env


def _build_loader(
        templates_search_paths: Optional[List[Path]] = None,
        macro_template_paths: Optional[List[str]] = None,
) -> BaseLoader:
    if templates_search_paths is None:
        if macro_template_paths is not None:
            logger.error(
                f'ignoring macro template paths {macro_template_paths} as template search path is None. Impossible to search...')
        return BaseLoader()
    else:
        file_system_loaders: List[FileSystemLoader] = [FileSystemLoader(searchpath=templates_search_path) for
                                                       templates_search_path in templates_search_paths]
        if macro_template_paths is None:
            return ChoiceLoader(file_system_loaders)
        else:
            return PrependingLoader(delegate=ChoiceLoader(file_system_loaders),
                                    prepend_template_paths=macro_template_paths)
