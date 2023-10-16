import pathlib
import typing as t

import mantik.unicore.config.core as core
import mantik.unicore.config.executable as executable


def get_files_to_upload(
    project_dir: pathlib.Path,
    config: core.Config,
) -> t.List[pathlib.Path]:
    """Get all files to be uploaded via UNICORE.

    Notes
    -----
    Since MLflow docker backend mounts the MLflow project directory, all
    directory contents are uploaded here as well.

    """
    exclude_list = config.files_to_exclude
    files = _recursively_list_files_in_directory(project_dir, exclude_list)
    if (
        config.execution_environment_given()
        and isinstance(config.environment.execution, executable.Apptainer)
        and config.environment.execution.is_local
    ):
        files.append(
            config.environment.execution.path_as_absolute_to(project_dir)
        )
    return list(set(files))


def _recursively_list_files_in_directory(
    project_dir: pathlib.Path, exclude: t.List[str]
) -> t.List[pathlib.Path]:
    files = [
        path
        for path in project_dir.rglob("*")
        if path.is_file()
        and not file_matches_exclude_pattern(
            path, project_dir=project_dir, exclude=exclude
        )
    ]
    return files


def file_matches_exclude_pattern(
    path: pathlib.Path, project_dir: pathlib.Path, exclude: t.List[str]
) -> bool:
    return _file_matches_exclude_entry(
        path, exclude=exclude
    ) or _file_in_excluded_subdirectory(
        path.relative_to(project_dir), exclude=exclude
    )


def _file_matches_exclude_entry(path: pathlib.Path, exclude: t.List) -> bool:
    return any(
        path.name in _files_matching_pattern(path.parent, pattern)
        for pattern in exclude
    )


def _files_matching_pattern(path: pathlib.Path, pattern: str) -> t.List[str]:
    return [file.name for file in path.glob(pattern)]


def _file_in_excluded_subdirectory(
    element_relative_path: pathlib.Path, exclude: t.List[str]
) -> bool:
    return any(f"{part}/" in exclude for part in element_relative_path.parts)
