from pathlib import Path
from typing import Annotated

from pydantic import PlainSerializer

JsonSerialisablePathAnnotation = Annotated[
    Path,
    PlainSerializer(lambda x: str(x), return_type=str, when_used='always')
]
