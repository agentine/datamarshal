"""A modern, lightweight dataclass serialization library for Python — the better alternative to dataclasses-json"""

from datamarshal.config import FieldConfig, GlobalConfig, LetterCase
from datamarshal.core import dataclass_json

__all__ = [
    "dataclass_json",
    "FieldConfig",
    "GlobalConfig",
    "LetterCase",
]
