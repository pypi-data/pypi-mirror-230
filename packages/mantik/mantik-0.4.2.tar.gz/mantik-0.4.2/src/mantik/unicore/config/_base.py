import abc
import functools
import typing as t


class ConfigObject(abc.ABC):
    """An object contained in the config."""

    @classmethod
    def from_dict(cls, config: t.Dict) -> "ConfigObject":
        """Initialize from dict."""
        return cls._from_dict(config)

    def to_dict(self) -> t.Dict:
        """Return as dict."""
        return _exclude_none_values(self._to_dict())

    @classmethod
    @abc.abstractmethod
    def _from_dict(cls, config: t.Dict) -> "ConfigObject":
        ...

    @abc.abstractmethod
    def _to_dict(self) -> t.Dict:
        ...


def _exclude_none_values(dict_) -> t.Dict:
    """Create a dict which only contains value that are not `None`."""
    return {
        key: _to_dict_if_config_object(value)
        for key, value in dict_.items()
        if value is not None
    }


@functools.singledispatch
def _to_dict_if_config_object(value: t.Any) -> t.Any:
    return value


@_to_dict_if_config_object.register
def _(value: ConfigObject) -> t.Any:
    return value.to_dict()
