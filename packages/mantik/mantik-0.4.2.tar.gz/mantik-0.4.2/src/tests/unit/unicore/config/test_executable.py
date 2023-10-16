import pathlib

import pytest

import mantik.unicore.config.executable as executable
import mantik.unicore.exceptions as exceptions


def _create_apptainer_run_command(options: str = "") -> str:
    if options:
        options = f"{options} "
    return (
        "srun apptainer run "
        "--cleanenv "
        "--env MLFLOW_TRACKING_URI="
        "${MLFLOW_TRACKING_URI:-file://$PWD/mlruns} "
        "${MLFLOW_TRACKING_TOKEN:"
        "+--env MLFLOW_TRACKING_TOKEN=$MLFLOW_TRACKING_TOKEN} "
        "${MLFLOW_EXPERIMENT_NAME:"
        "+--env MLFLOW_EXPERIMENT_NAME=$MLFLOW_EXPERIMENT_NAME} "
        "${MLFLOW_EXPERIMENT_ID:"
        "+--env MLFLOW_EXPERIMENT_ID=$MLFLOW_EXPERIMENT_ID} "
        f"{options}"
        "image.sif"
    )


class TestApptainer:
    def test_invalid_image_type(self, expect_raise_if_exception):
        expected = (
            "The given Apptainer image type "
            "'unsupported' is not supported, the supported ones are: "
            "'local', 'remote'."
        )
        with expect_raise_if_exception(exceptions.ConfigValidationError()) as e:
            executable.Apptainer(
                path=pathlib.Path("image.sif"),
                type="unsupported",
            )

        result = str(e.value)

        assert result == expected

    @pytest.mark.parametrize(
        ("apptainer", "expected"),
        [
            (
                executable.Apptainer(
                    path=pathlib.Path("/remote/path/to/image.sif"),
                    type="remote",
                ),
                True,
            ),
            (
                executable.Apptainer(
                    path=pathlib.Path("local/path/to/image.sif"),
                    type="local",
                ),
                False,
            ),
        ],
    )
    def test_is_remote(self, apptainer, expected):
        result = apptainer.is_remote

        assert result == expected

    @pytest.mark.parametrize(
        ("apptainer", "absolute_to", "expected"),
        [
            (
                executable.Apptainer(
                    path=pathlib.Path("/remote/path/to/image.sif"),
                    type="remote",
                ),
                pathlib.Path("/path"),
                pathlib.Path("/remote/path/to/image.sif"),
            ),
            (
                executable.Apptainer(
                    path=pathlib.Path("local/path/to/image.sif"),
                    type="local",
                ),
                pathlib.Path("/path"),
                pathlib.Path("/path/local/path/to/image.sif"),
            ),
        ],
    )
    def test_path_as_absolute_to(self, apptainer, absolute_to, expected):
        result = apptainer.path_as_absolute_to(absolute_to)

        assert result == expected

    @pytest.mark.parametrize(
        (
            "environment",
            "expected",
        ),
        [
            # Test Case: Execution command with Apptainer executable
            (
                executable.Apptainer(path=pathlib.Path("image.sif")),
                _create_apptainer_run_command(),
            ),
            # Test Case: Execution command with Apptainer executable
            # and one option as list
            (
                executable.Apptainer(
                    path=pathlib.Path("image.sif"),
                    options=["--B $PWD/data:/data"],
                ),
                _create_apptainer_run_command(options="--B $PWD/data:/data"),
            ),
            # Test Case: Execution command with Apptainer executable
            # and two options
            (
                executable.Apptainer(
                    path=pathlib.Path("image.sif"),
                    options=["--nv", "--B $PWD/data:/data"],
                ),
                _create_apptainer_run_command(
                    options="--nv --B $PWD/data:/data"
                ),
            ),
        ],
    )
    def test_create_run_command(self, environment, expected):
        result = " ".join(
            [environment.get_execution_command(), *environment.get_arguments()]
        )

        assert result == expected

    @pytest.mark.parametrize(
        (
            "apptainer_image",
            "expected",
        ),
        [
            (executable.Apptainer(path=pathlib.Path("image.sif")), "image.sif"),
            (
                executable.Apptainer(
                    path=pathlib.Path("/absolute/path/to/image.sif"),
                    type="local",
                ),
                "image.sif",
            ),
            (
                executable.Apptainer(
                    path=pathlib.Path("/absolute/path/to/image.sif"),
                    type="remote",
                ),
                "/absolute/path/to/image.sif",
            ),
        ],
    )
    def test_get_image_path(
        self,
        apptainer_image,
        example_config,
        expected,
    ):
        assert expected == apptainer_image._get_image_path()


class TestPython:
    def test_path_has_to_be_checked(self):
        python = executable.Python(path=pathlib.Path("/path/to/python/env"))
        expected = False

        result = python.path_has_to_be_checked

        assert result == expected

    def test_create_run_command(self):
        environment = executable.Python(
            path=pathlib.Path("/path/to/python/env")
        )
        expected = None

        result = environment.get_execution_command()

        assert result == expected
