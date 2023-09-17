from enum import Enum
from typing import Callable, List, Optional

from pydantic import Field, BaseModel as _BaseModel

from api_compose.core.logging import get_logger
from api_compose.services.common.events.jinja_function_registration import JinjaFunctionRegistrationEvent

logger = get_logger(__name__)


class JinjaFunctionType(Enum):
    Global: str = 'Global'
    Filter: str = 'Filter'
    Test: str = 'Test'


class JinjaFunctionModel(_BaseModel):
    name: str = Field(description='dot-separated name. Dot indicates Namespace')
    func_type: JinjaFunctionType
    func: Callable
    alias: List[str]

    @property
    def all_names(self) -> List[str]:
        return [self.name] + self.alias


class JinjaFunctionsRegistry:
    """
    - Use Decorator to Register Jinja Functions

    Lazy evaluation of Calculated Field.
    Only evaluate when `render()` is called
    """

    registry: List[JinjaFunctionModel] = []

    @classmethod
    def set(cls,
            name: str,
            func_type: JinjaFunctionType = JinjaFunctionType.Global,
            alias: Optional[List] = None,
            ):
        """
        Parameters
        ----------
        name: How the jinja function is accessed in the template
        func_type: One of the JinjaFunctionType
        alias: Other names of the function
        Returns
        -------

        """
        assert name not in [model.name for model in cls.registry], f'Jinja Function Name {name} is already taken!!!'

        if alias is None:
            alias = []

        if alias is not None:
            assert type(alias) == list, "Alias must be a list of string"

        def decorator(func: Callable):
            cls.registry.append(
                JinjaFunctionModel(
                    name=name,
                    func_type=func_type,
                    func=func,
                    alias=alias
                )
            )
            # logger.info("Registering Jinja %s -  %s " % (func_type.value, ', '.join([name] + alias)),
            #             JinjaFunctionRegistrationEvent())
            return func

        return decorator
