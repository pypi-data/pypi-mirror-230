import dataclasses
import typing as t

import pytest

import mantik.unicore.config._base as _base


@dataclasses.dataclass
class AnyConfigObject(_base.ConfigObject):
    test: str = "test"

    @classmethod
    def _from_dict(cls, config: t.Dict) -> "AnyConfigObject":
        pass

    def _to_dict(self) -> t.Dict:
        return dataclasses.asdict(self)


@pytest.mark.parametrize(
    ("dict_", "expected"),
    [
        (
            {"any": "value"},
            {"any": "value"},
        ),
        (
            {"any": None},
            {},
        ),
        (
            {"any": AnyConfigObject()},
            {"any": {"test": "test"}},
        ),
    ],
)
def test_exclude_none_values(dict_, expected):
    result = _base._exclude_none_values(dict_)

    assert result == expected
