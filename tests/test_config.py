"""Tests for field configuration: rename, exclude, letter case, custom encoders/decoders."""

from __future__ import annotations

from dataclasses import dataclass, field

from fieldmarshal import FieldConfig, LetterCase, dataclass_json


@dataclass_json
@dataclass
class WithRename:
    user_name: str = field(
        metadata={"fieldmarshal": FieldConfig(field_name="userName")}
    )
    email: str = ""


@dataclass_json
@dataclass
class WithExclude:
    name: str
    password: str = field(
        metadata={"fieldmarshal": FieldConfig(exclude=True, default="secret")}
    )


@dataclass_json
@dataclass
class WithExcludeNoFcDefault:
    name: str
    internal: str = field(
        default="fallback",
        metadata={"fieldmarshal": FieldConfig(exclude=True)},
    )


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CamelModel:
    first_name: str
    last_name: str
    is_active: bool = True


@dataclass_json(letter_case=LetterCase.KEBAB)
@dataclass
class KebabModel:
    first_name: str
    last_name: str


@dataclass_json
@dataclass
class WithCustomEncoder:
    value: int = field(
        metadata={
            "fieldmarshal": FieldConfig(
                encoder=lambda v: v * 2,
                decoder=lambda v: v // 2,
            )
        }
    )


class TestFieldRename:
    def test_to_dict_uses_renamed_key(self) -> None:
        obj = WithRename(user_name="alice", email="a@b.com")
        d = obj.to_dict()
        assert "userName" in d
        assert "user_name" not in d
        assert d["userName"] == "alice"

    def test_from_dict_uses_renamed_key(self) -> None:
        obj = WithRename.from_dict({"userName": "alice", "email": "a@b.com"})
        assert obj.user_name == "alice"


class TestFieldExclude:
    def test_to_dict_excludes_field(self) -> None:
        obj = WithExclude(name="alice", password="secret123")
        d = obj.to_dict()
        assert "password" not in d
        assert d == {"name": "alice"}

    def test_from_dict_uses_default(self) -> None:
        obj = WithExclude.from_dict({"name": "alice"})
        assert obj.name == "alice"
        assert obj.password == "secret"

    def test_from_dict_exclude_without_fc_default(self) -> None:
        obj = WithExcludeNoFcDefault.from_dict({"name": "test"})
        assert obj.name == "test"
        assert obj.internal == "fallback"


class TestLetterCase:
    def test_camel_case_to_dict(self) -> None:
        obj = CamelModel(first_name="Alice", last_name="Smith")
        d = obj.to_dict()
        assert d == {"firstName": "Alice", "lastName": "Smith", "isActive": True}

    def test_camel_case_from_dict(self) -> None:
        obj = CamelModel.from_dict(
            {"firstName": "Alice", "lastName": "Smith", "isActive": False}
        )
        assert obj.first_name == "Alice"
        assert obj.last_name == "Smith"
        assert obj.is_active is False

    def test_camel_case_round_trip(self) -> None:
        orig = CamelModel(first_name="Bob", last_name="Jones", is_active=False)
        restored = CamelModel.from_json(orig.to_json())
        assert restored == orig

    def test_kebab_case(self) -> None:
        obj = KebabModel(first_name="Alice", last_name="Smith")
        d = obj.to_dict()
        assert d == {"first-name": "Alice", "last-name": "Smith"}

    def test_kebab_case_from_dict(self) -> None:
        obj = KebabModel.from_dict({"first-name": "Alice", "last-name": "Smith"})
        assert obj.first_name == "Alice"


class TestCustomEncoderDecoder:
    def test_custom_encoder(self) -> None:
        obj = WithCustomEncoder(value=5)
        d = obj.to_dict()
        assert d["value"] == 10  # doubled

    def test_custom_decoder(self) -> None:
        obj = WithCustomEncoder.from_dict({"value": 10})
        assert obj.value == 5  # halved

    def test_round_trip(self) -> None:
        orig = WithCustomEncoder(value=7)
        restored = WithCustomEncoder.from_dict(orig.to_dict())
        assert restored == orig
