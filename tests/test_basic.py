"""Tests for basic serialization: simple types, round-trips."""

from __future__ import annotations

import json
from dataclasses import dataclass

from datamarshal import dataclass_json


@dataclass_json
@dataclass
class Simple:
    name: str
    age: int
    score: float
    active: bool


@dataclass_json
@dataclass
class WithNone:
    name: str
    value: int | None = None


class TestToDict:
    def test_simple(self) -> None:
        obj = Simple(name="Alice", age=30, score=9.5, active=True)
        d = obj.to_dict()
        assert d == {"name": "Alice", "age": 30, "score": 9.5, "active": True}

    def test_with_none(self) -> None:
        obj = WithNone(name="Bob", value=None)
        d = obj.to_dict()
        assert d == {"name": "Bob", "value": None}

    def test_with_value(self) -> None:
        obj = WithNone(name="Bob", value=42)
        d = obj.to_dict()
        assert d == {"name": "Bob", "value": 42}


class TestFromDict:
    def test_simple(self) -> None:
        obj = Simple.from_dict({"name": "Alice", "age": 30, "score": 9.5, "active": True})
        assert obj.name == "Alice"
        assert obj.age == 30
        assert obj.score == 9.5
        assert obj.active is True

    def test_with_none(self) -> None:
        obj = WithNone.from_dict({"name": "Bob", "value": None})
        assert obj.name == "Bob"
        assert obj.value is None

    def test_with_value(self) -> None:
        obj = WithNone.from_dict({"name": "Bob", "value": 42})
        assert obj.value == 42


class TestRoundTrip:
    def test_to_json_from_json(self) -> None:
        orig = Simple(name="Alice", age=30, score=9.5, active=True)
        s = orig.to_json()
        restored = Simple.from_json(s)
        assert restored == orig

    def test_to_dict_from_dict(self) -> None:
        orig = WithNone(name="Bob", value=7)
        restored = WithNone.from_dict(orig.to_dict())
        assert restored == orig

    def test_json_format(self) -> None:
        obj = Simple(name="Alice", age=30, score=9.5, active=True)
        s = obj.to_json()
        parsed = json.loads(s)
        assert parsed == {"name": "Alice", "age": 30, "score": 9.5, "active": True}

    def test_json_kwargs(self) -> None:
        obj = Simple(name="A", age=1, score=0.0, active=False)
        s = obj.to_json(indent=2)
        assert "\n" in s  # pretty-printed


class TestErrors:
    def test_not_a_dataclass(self) -> None:
        import pytest

        with pytest.raises(TypeError, match="dataclasses"):

            @dataclass_json
            class NotADataclass:
                pass

    def test_unknown_fields_strict(self) -> None:
        import pytest

        with pytest.raises(ValueError, match="Unknown fields"):
            Simple.from_dict(
                {"name": "A", "age": 1, "score": 0.0, "active": True, "extra": 1}
            )
