from typing import TypeVar



class BaseProcessor:

    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

BaseProcessorSubclass = TypeVar('BaseProcessorSubclass', bound=BaseProcessor)
