"""Tests for nested dataclasses and collection types."""

from __future__ import annotations

from dataclasses import dataclass

from datamarshal import dataclass_json


@dataclass_json
@dataclass
class Address:
    street: str
    city: str


@dataclass_json
@dataclass
class Person:
    name: str
    address: Address


@dataclass_json
@dataclass
class Team:
    name: str
    members: list[Person]


@dataclass_json
@dataclass
class WithCollections:
    tags: list[str]
    scores: dict[str, int]
    unique_ids: set[int]
    coords: tuple[float, float]


@dataclass_json
@dataclass
class WithOptional:
    name: str
    nickname: str | None = None
    address: Address | None = None


@dataclass_json
@dataclass
class WithUnion:
    value: int | str


@dataclass_json
@dataclass
class WithVarTuple:
    values: tuple[int, ...]


class TestNestedDataclass:
    def test_encode_nested(self) -> None:
        p = Person(name="Alice", address=Address(street="123 Main", city="NYC"))
        d = p.to_dict()
        assert d == {"name": "Alice", "address": {"street": "123 Main", "city": "NYC"}}

    def test_decode_nested(self) -> None:
        p = Person.from_dict(
            {"name": "Alice", "address": {"street": "123 Main", "city": "NYC"}}
        )
        assert p.name == "Alice"
        assert p.address.street == "123 Main"
        assert p.address.city == "NYC"

    def test_round_trip_nested(self) -> None:
        orig = Person(name="Bob", address=Address(street="456 Oak", city="LA"))
        restored = Person.from_json(orig.to_json())
        assert restored == orig

    def test_deeply_nested(self) -> None:
        team = Team(
            name="Engineering",
            members=[
                Person(name="Alice", address=Address(street="1 A St", city="X")),
                Person(name="Bob", address=Address(street="2 B St", city="Y")),
            ],
        )
        d = team.to_dict()
        assert len(d["members"]) == 2
        assert d["members"][0]["address"]["city"] == "X"

        restored = Team.from_json(team.to_json())
        assert restored == team


class TestCollections:
    def test_list(self) -> None:
        obj = WithCollections(
            tags=["a", "b"], scores={"x": 1}, unique_ids={3, 1, 2}, coords=(1.0, 2.0)
        )
        d = obj.to_dict()
        assert d["tags"] == ["a", "b"]
        assert d["scores"] == {"x": 1}
        assert d["unique_ids"] == [1, 2, 3]  # sorted
        assert d["coords"] == [1.0, 2.0]

    def test_round_trip_collections(self) -> None:
        obj = WithCollections(
            tags=["a", "b"], scores={"x": 1, "y": 2}, unique_ids={10, 20}, coords=(3.0, 4.0)
        )
        d = obj.to_dict()
        restored = WithCollections.from_dict(d)
        assert restored.tags == ["a", "b"]
        assert restored.scores == {"x": 1, "y": 2}
        assert restored.unique_ids == {10, 20}
        assert restored.coords == (3.0, 4.0)


class TestOptionalUnion:
    def test_optional_none(self) -> None:
        obj = WithOptional(name="A")
        d = obj.to_dict()
        assert d["nickname"] is None
        assert d["address"] is None

    def test_optional_present(self) -> None:
        obj = WithOptional(name="A", nickname="B", address=Address(street="1", city="C"))
        d = obj.to_dict()
        assert d["nickname"] == "B"
        assert d["address"] == {"street": "1", "city": "C"}

    def test_optional_round_trip(self) -> None:
        obj = WithOptional(name="A", address=Address(street="1", city="C"))
        restored = WithOptional.from_dict(obj.to_dict())
        assert restored == obj

    def test_union(self) -> None:
        obj1 = WithUnion(value=42)
        assert obj1.to_dict() == {"value": 42}
        assert WithUnion.from_dict({"value": 42}).value == 42

        obj2 = WithUnion(value="hello")
        assert obj2.to_dict() == {"value": "hello"}
        assert WithUnion.from_dict({"value": "hello"}).value == "hello"

    def test_variable_tuple(self) -> None:
        obj = WithVarTuple(values=(1, 2, 3))
        d = obj.to_dict()
        assert d["values"] == [1, 2, 3]
        restored = WithVarTuple.from_dict(d)
        assert restored.values == (1, 2, 3)
