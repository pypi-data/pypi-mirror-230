from enum import Enum

from pydantic import ConfigDict, BaseModel as _BaseModel


class EventType(Enum):
    # Registration
    ProcessorRegistration = 'ProcessorRegistration'
    JinjaFunctionRegistration = 'JinjaFunctionRegistration'

    # Others
    Action = 'Action'
    Assertion = 'Assertion'
    CLI = 'Cli'
    Default = 'Default'
    Deserialisation = 'Deserialisation'
    Discovery = 'Discovery'
    Executor = 'Executor'
    ReadConfiguration = 'ReadConfiguration'
    JinjaRendering = 'JinjaRendering'
    Scheduler = 'Scheduler'
    SchemaValidator = 'SchemaValidator'
    Session = 'Session'
    Specification = 'Specification'
    Scenario = 'Scenario'
    TemplatedField = 'TemplatedField'
    TextField = 'TextField'

    def __json__(self):
        return self.value


class BaseData(_BaseModel):
    model_config = ConfigDict(extra="allow")


class BaseEvent(_BaseModel):
    event: EventType
    data: BaseData
