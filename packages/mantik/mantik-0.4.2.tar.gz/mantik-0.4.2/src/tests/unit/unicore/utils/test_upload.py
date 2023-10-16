import pathlib

import pytest

import mantik.unicore.config.environment as _environment
import mantik.unicore.config.executable as executable
import mantik.unicore.utils.upload as upload_files


@pytest.mark.parametrize(
    ("environment", "expect_image_is_included"),
    [
        # Test case: No environment given
        (
            None,
            False,
        ),
        # Test case: No execution environment given
        (
            _environment.Environment(),
            False,
        ),
        # Test case: upload local image
        (
            _environment.Environment(
                execution=executable.Apptainer(
                    path=pathlib.Path("mantik-test.sif"),
                    type="local",
                ),
            ),
            True,
        ),
        # Test case: use remote image, don't upload a local image
        (
            _environment.Environment(
                execution=executable.Apptainer(
                    path=pathlib.Path("/absolute/path/to/remote/image.sif"),
                    type="remote",
                ),
            ),
            False,
        ),
    ],
)
def test_get_files_to_upload(
    example_project_path,
    example_config,
    environment,
    expect_image_is_included,
):
    example_config.environment = environment
    files = upload_files.get_files_to_upload(
        project_dir=example_project_path, config=example_config
    )
    if expect_image_is_included:
        assert example_project_path / "mantik-test.sif" in files
    else:
        assert example_project_path / "mantik-test.sif" not in files


@pytest.mark.parametrize(
    ("exclude", "expected"),
    [
        # Test case: exclude all files
        (["*"], []),
        # Test case: exclude all Python files
        (
            [
                # pycache folder might be added when executing any file
                # in the project dir manually.
                "__pycache__/",
                "*.py",
            ],
            [
                "Dockerfile",
                "MLproject",
                "recipe.def",
                "compute-backend-config.json",
                "compute-backend-config.yaml",
                "mantik-test.sif",
                "config-with-errors.yaml",
            ],
        ),
        # Test case: exclude all except main.py and test_subfolder/test.py
        (
            [
                "__pycache__/",
                "Dockerfile",
                "MLproject",
                "recipe.def",
                "compute-backend-config.json",
                "compute-backend-config.yaml",
                "mantik-test.sif",
                "config-with-errors.yaml",
            ],
            ["main.py", "run.py", "test_subfolder/test.py"],
        ),
        # Test case: exclude all except main.py
        (
            [
                "__pycache__/",
                "Dockerfile",
                "MLproject",
                "recipe.def",
                "compute-backend-config.json",
                "compute-backend-config.yaml",
                "mantik-test.sif",
                "test_subfolder/",
                "config-with-errors.yaml",
            ],
            ["main.py", "run.py"],
        ),
        # Test case: exclude all except test_subfolder/test.py
        (
            [
                "__pycache__/",
                "Dockerfile",
                "MLproject",
                "recipe.def",
                "compute-backend-config.json",
                "compute-backend-config.yaml",
                "mantik-test.sif",
                "config-with-errors.yaml",
                "main.py",
                "run.py",
            ],
            ["test_subfolder/test.py"],
        ),
    ],
)
def test_recursively_list_files_in_directory(
    example_project_path, exclude, expected
):
    for i, element in enumerate(expected):
        expected[i] = example_project_path / element
    result = upload_files._recursively_list_files_in_directory(
        example_project_path, exclude
    )

    assert sorted(result) == sorted(expected)


@pytest.mark.parametrize(
    ("file_name", "exclude", "expected"),
    [
        ("main.py", ["*.py"], True),
        ("main.py", ["*.yaml"], False),
    ],
)
def test_file_matches_exclude_entry(
    file_name, example_project_path, exclude, expected
):
    filepath = example_project_path / file_name
    assert expected == upload_files._file_matches_exclude_entry(
        filepath, exclude
    )


@pytest.mark.parametrize(
    ("pattern", "expected"),
    [
        ("*.py", ["run.py", "main.py"]),
        ("**/*.py", ["run.py", "main.py", "test.py"]),
    ],
)
def test_files_matching_pattern(example_project_path, pattern, expected):
    result = upload_files._files_matching_pattern(example_project_path, pattern)

    assert sorted(result) == sorted(expected)


@pytest.mark.parametrize(
    ("element_relative_path", "exclude", "expected"),
    [
        (pathlib.Path("subfolder/test.py"), ["subfolder/"], True),
    ],
)
def test_file_in_excluded_subdirectory(
    element_relative_path, exclude, expected
):
    assert expected == upload_files._file_in_excluded_subdirectory(
        element_relative_path, exclude
    )
