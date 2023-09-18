from __future__ import annotations

from pydantic import BaseModel as _BaseModel, Field


class BaseActionConfigModel(_BaseModel, extra='allow'):
    pass
