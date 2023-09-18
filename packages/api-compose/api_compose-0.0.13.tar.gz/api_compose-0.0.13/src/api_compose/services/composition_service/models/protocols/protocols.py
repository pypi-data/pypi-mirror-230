from enum import Enum


class ActionAPIProtocolEnum(str, Enum):
    """
    Action State as determined by the executor
    """

    UNDEFINED = 'undefined'
    HTTP = 'http'
    WEBSOCKET = 'websocket'
    GRPC = 'grpc'
    FIX = 'fix'
