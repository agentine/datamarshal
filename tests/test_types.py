"""Tests for built-in type handlers and strict/lenient modes."""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from pathlib import Path
from uuid import UUID

import pytest

from fieldmarshal import dataclass_json


class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


@dataclass_json
@dataclass
class WithDatetime:
    created: datetime.datetime
    birthday: datetime.date
    alarm: datetime.time


@dataclass_json
@dataclass
class WithUUID:
    id: UUID


@dataclass_json
@dataclass
class WithDecimal:
    amount: Decimal


@dataclass_json
@dataclass
class WithEnum:
    color: Color


@dataclass_json
@dataclass
class WithPath:
    location: Path


@dataclass_json
@dataclass
class WithBytes:
    data: bytes


@dataclass_json(strict=False)
@dataclass
class Lenient:
    name: str
    age: int
    score: float


@dataclass_json(strict=True)
@dataclass
class Strict:
    name: str
    age: int


class TestDatetime:
    def test_encode(self) -> None:
        obj = WithDatetime(
            created=datetime.datetime(2024, 1, 15, 10, 30, 0),
            birthday=datetime.date(1990, 5, 20),
            alarm=datetime.time(7, 30),
        )
        d = obj.to_dict()
        assert d["created"] == "2024-01-15T10:30:00"
        assert d["birthday"] == "1990-05-20"
        assert d["alarm"] == "07:30:00"

    def test_decode(self) -> None:
        obj = WithDatetime.from_dict(
            {
                "created": "2024-01-15T10:30:00",
                "birthday": "1990-05-20",
                "alarm": "07:30:00",
            }
        )
        assert obj.created == datetime.datetime(2024, 1, 15, 10, 30, 0)
        assert obj.birthday == datetime.date(1990, 5, 20)
        assert obj.alarm == datetime.time(7, 30)

    def test_round_trip(self) -> None:
        orig = WithDatetime(
            created=datetime.datetime(2024, 6, 1, 12, 0, 0),
            birthday=datetime.date(2000, 1, 1),
            alarm=datetime.time(23, 59, 59),
        )
        restored = WithDatetime.from_json(orig.to_json())
        assert restored == orig


class TestUUID:
    def test_encode(self) -> None:
        uid = UUID("12345678-1234-5678-1234-567812345678")
        obj = WithUUID(id=uid)
        d = obj.to_dict()
        assert d["id"] == "12345678-1234-5678-1234-567812345678"

    def test_decode(self) -> None:
        obj = WithUUID.from_dict({"id": "12345678-1234-5678-1234-567812345678"})
        assert obj.id == UUID("12345678-1234-5678-1234-567812345678")

    def test_round_trip(self) -> None:
        orig = WithUUID(id=UUID("abcdef01-2345-6789-abcd-ef0123456789"))
        assert WithUUID.from_json(orig.to_json()) == orig


class TestDecimal:
    def test_encode(self) -> None:
        obj = WithDecimal(amount=Decimal("19.99"))
        assert obj.to_dict()["amount"] == "19.99"

    def test_decode(self) -> None:
        obj = WithDecimal.from_dict({"amount": "19.99"})
        assert obj.amount == Decimal("19.99")

    def test_round_trip(self) -> None:
        orig = WithDecimal(amount=Decimal("100.005"))
        assert WithDecimal.from_json(orig.to_json()) == orig


class TestEnum:
    def test_encode(self) -> None:
        obj = WithEnum(color=Color.RED)
        assert obj.to_dict()["color"] == "red"

    def test_decode(self) -> None:
        obj = WithEnum.from_dict({"color": "green"})
        assert obj.color is Color.GREEN

    def test_round_trip(self) -> None:
        orig = WithEnum(color=Color.BLUE)
        assert WithEnum.from_json(orig.to_json()) == orig


class TestPath:
    def test_encode(self) -> None:
        obj = WithPath(location=Path("/usr/local/bin"))
        assert obj.to_dict()["location"] == "/usr/local/bin"

    def test_decode(self) -> None:
        obj = WithPath.from_dict({"location": "/usr/local/bin"})
        assert obj.location == Path("/usr/local/bin")

    def test_round_trip(self) -> None:
        orig = WithPath(location=Path("relative/path"))
        assert WithPath.from_json(orig.to_json()) == orig


class TestBytes:
    def test_encode(self) -> None:
        obj = WithBytes(data=b"hello")
        assert obj.to_dict()["data"] == "aGVsbG8="

    def test_decode(self) -> None:
        obj = WithBytes.from_dict({"data": "aGVsbG8="})
        assert obj.data == b"hello"

    def test_round_trip(self) -> None:
        orig = WithBytes(data=b"\x00\x01\x02\xff")
        assert WithBytes.from_json(orig.to_json()) == orig


class TestStrictMode:
    def test_strict_rejects_unknown(self) -> None:
        with pytest.raises(ValueError, match="Unknown fields"):
            Strict.from_dict({"name": "A", "age": 1, "extra": True})

    def test_strict_type_mismatch(self) -> None:
        with pytest.raises(TypeError, match="Expected int"):
            Strict.from_dict({"name": "A", "age": "not_an_int"})


class TestLenientMode:
    def test_lenient_ignores_unknown(self) -> None:
        obj = Lenient.from_dict({"name": "A", "age": 1, "score": 2.0, "extra": True})
        assert obj.name == "A"

    def test_lenient_coerces_types(self) -> None:
        obj = Lenient.from_dict({"name": "A", "age": "42", "score": "3.14"})
        assert obj.age == 42
        assert obj.score == 3.14
