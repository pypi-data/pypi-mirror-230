from pathlib import Path
from typing import Any, List, Optional, Set, Literal

from pydantic import BaseModel as _BaseModel
from pydantic import field_validator, model_validator, Field, ConfigDict

from api_compose.core.utils.string import split_pascal_case_string


class BaseModel(_BaseModel):
    model_config = ConfigDict(
        protected_namespaces=()
    )

    id: str = Field(
        description='Identifier of the Model. Have to be unique in the repository',
    )

    @field_validator('id', mode="before")
    @classmethod
    def validate_id(cls, value):
        if not value:
            raise ValueError(f'id must not be empty. {value=}')
        return value

    model_name: Literal['BaseModel'] = Field(
        description='Model Name. Used for Internal model lookup',
    )

    # @model_validator(mode="before")
    # @classmethod
    # def set_model_name(cls, values):
    #     values['model_name'] = cls.__name__
    #     return values

    class_name: str = Field(
        description='Class which the model corresponds to. User for Internal class lookup',
    )

    @model_validator(mode="before")
    @classmethod
    def set_class_name(cls, values):
        values['class_name'] = ''.join(split_pascal_case_string(cls.__name__)[:-1])
        return values

    description: str = Field(
        "",
        description='Description of the Model',

    )

    manifest_file_path: Optional[Path] = Field(
        None,
        description='Relative Path to Manifest which defines the model'
    )

    tags: Set[str] = Field(
        set(),
        description='Tags which identify the Model'
    )

    # To be set programmatically. Don't set manually
    parent_ids: List[str] = Field(
        [],
        description='A list of parents of the model. Internally set to construct model hierarchy.',

    )

    @property
    def is_parent_ids_set(self) -> bool:
        return len(self.parent_ids) != 0

    def set_parent_ids(self):
        # add the id of the parent to the children
        for field in self.model_fields.keys():
            obj = getattr(self, field)
            if type(obj) in (list, tuple):
                for o in obj:
                    conditionally_set_parent_ids(o, self)
            elif type(obj) == dict:
                for val in obj.values():
                    conditionally_set_parent_ids(val, self)
            else:
                conditionally_set_parent_ids(obj, self)

    @property
    def ancestry(self):
        # Used to judge if a component belongs to the same parent. Useful for scoped component (e.g. Scenario-scoped Action)
        return '.'.join(self.parent_ids)

    @property
    def uid(self):
        """
        Unique Id.
        """
        return self.id

    @property
    def fqn(self):
        return '.'.join([self.ancestry, self.uid])

    @field_validator("id")
    @classmethod
    def replace_whitespace(cls, value):
        return value.replace(" ", "_")

    def __hash__(self):
        return hash(self.fqn)

    def __eq__(self, other):
        if isinstance(other, BaseModel) and other.fqn == self.fqn:
            return True
        else:
            return False


def conditionally_set_parent_ids(child: Any, parent: BaseModel):
    parent_execution_id = getattr(parent, 'execution_id', None)
    parent_id = parent_execution_id if parent_execution_id is not None else parent.id
    if isinstance(child, BaseModel) and not child.is_parent_ids_set:
        child.parent_ids += parent.parent_ids + [parent_id]
        child.set_parent_ids()
