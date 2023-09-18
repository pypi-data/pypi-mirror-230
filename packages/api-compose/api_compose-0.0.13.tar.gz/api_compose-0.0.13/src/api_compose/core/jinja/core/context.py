"""
Standardize Jinja Contexts used for different purposes
"""
from __future__ import annotations

__all__ = ['BaseJinjaContext']

from pydantic import BaseModel as _BaseModel


class BaseJinjaContext(_BaseModel, extra='allow'):
    """
    Base Model which contains jinja contexts
    """
    pass
