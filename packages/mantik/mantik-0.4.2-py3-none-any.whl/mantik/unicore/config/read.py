import json
import pathlib
import typing as t

import yaml

import mantik.unicore.exceptions as exceptions

_ALLOWED_FILE_EXTENSIONS = {"json": [".json"], "yaml": [".yml", ".yaml"]}


def read_config(path: pathlib.Path) -> t.Dict:
    try:
        if path.suffix in _ALLOWED_FILE_EXTENSIONS["json"]:
            return _read_json_config(path)
        elif path.suffix in _ALLOWED_FILE_EXTENSIONS["yaml"]:
            return _read_yaml_config(path)
    except FileNotFoundError:
        raise exceptions.ConfigValidationError(f"No such config: '{path.name}'")
    allowed_file_types = exceptions.iterable_to_string(
        item
        for sublist in _ALLOWED_FILE_EXTENSIONS.values()
        for item in sublist
    )
    raise exceptions.ConfigValidationError(
        f"The given file type {path.suffix!r} "
        "is not supported for the config, "
        "the supported ones are: "
        f"{allowed_file_types}."
    )


def _read_yaml_config(backend_config_path: pathlib.Path) -> t.Dict:
    with open(backend_config_path) as f:
        return yaml.safe_load(f)


def _read_json_config(backend_config_path: pathlib.Path) -> t.Dict:
    with open(backend_config_path) as f:
        return json.load(f)
