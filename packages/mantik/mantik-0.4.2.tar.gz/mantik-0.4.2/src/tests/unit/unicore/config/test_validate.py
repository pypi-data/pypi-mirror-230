import pathlib
import shutil

import mlflow.exceptions
import pytest
import yaml

import mantik.unicore.config.environment as environment
import mantik.unicore.config.validate as project_config
import mantik.unicore.exceptions as exceptions


@pytest.fixture(autouse=True)
def set_required_env_vars(env_vars_set, required_config_env_vars) -> None:
    with env_vars_set(required_config_env_vars):
        yield


class TestConfigValidator:
    @pytest.mark.parametrize(
        ("mlproject_path", "config_path", "expected"),
        [
            # Test case: config path is not absolute
            (
                "/absolute/path",
                "relative/path",
                pathlib.Path("/absolute/path/relative/path"),
            ),
            # Test case: both paths are absolute
            (
                "/absolute/path",
                "/absolute/path/config",
                pathlib.Path("/absolute/path/config"),
            ),
        ],
    )
    def test_config_absolute_path(self, mlproject_path, config_path, expected):
        config = project_config.ProjectValidator(
            mlproject_path, config_path, {}, "main"
        )
        assert config.config_absolute_path == expected

    @pytest.mark.parametrize(
        ("mlproject_path", "config_path", "expected"),
        [
            # Test case: config path is not absolute
            ("/absolute/path", "relative/path", pathlib.Path("relative/path")),
            # Test case: both paths are absolute
            ("/absolute/path", "/absolute/path/config", pathlib.Path("config")),
        ],
    )
    def test_config_relative_path(self, mlproject_path, config_path, expected):
        config = project_config.ProjectValidator(
            mlproject_path, config_path, {}, "main"
        )
        assert config.config_relative_path == expected

    @pytest.mark.parametrize(
        ("fake_mlproject_path", "config_path", "expected"),
        [
            # Test case: MLproject path is not absolute
            (
                "absolute/path",
                "relative/path",
                "ML project path must be an absolute path, "
                "but 'absolute/path' was given.",
            ),
            # Test case: MLproject path does not exist
            (
                "/absolute/path",
                "relative/path",
                "ML project path not found at '/absolute/path', "
                "check that the given path is correct.",
            ),
            # Test case: config path does not exist
            (
                "ml_project_resource",
                "false/path/to/config.yml",
                "Config not found at "
                "'ml_project_resource/false/path/to/config.yml', "
                "check that the given path is correct.",
            ),
            # Test case: config path is from another project
            (
                "ml_project_resource",
                "invalid_config_type",
                "Config file is not in the ML project directory, "
                "check that the given paths "
                "are correct:\nConfig file: "
                "'invalid_config_type'\nML project directory: "
                "'ml_project_resource'",
            ),
            # Test case: config with errors
            (
                "ml_project_resource",
                "config_with_errors",
                "Config is missing entry for key 'UnicoreApiUrl'",
            ),
            # Test case: config without Environment section validation
            # successful
            (
                "ml_project_resource",
                "compute_backend_config_yaml",
                None,
            ),
            # Test case: config with Environment section validation successful
            (
                "ml_project_resource",
                "compute_backend_config_json",
                None,
            ),
        ],
    )
    def test_validate(
        self,
        expect_raise_if_exception,
        fake_mlproject_path,
        config_path,
        expected,
        mlproject_path,
        invalid_config_type,
        config_with_errors,
        compute_backend_config_yaml,
        compute_backend_config_json,
    ):
        expected_error = (
            exceptions.ConfigValidationError() if expected is not None else None
        )

        with expect_raise_if_exception(expected_error) as e:
            final_mlproject_path = fake_mlproject_path
            if fake_mlproject_path == "ml_project_resource":
                final_mlproject_path = mlproject_path

            if config_path == "invalid_config_type":
                config_path = invalid_config_type
            elif config_path == "config_with_errors":
                config_path = config_with_errors
            elif config_path == "compute_backend_config_yaml":
                config_path = compute_backend_config_yaml
            elif config_path == "compute_backend_config_json":
                config_path = compute_backend_config_json

            mlproject_config = project_config.ProjectValidator(
                final_mlproject_path, config_path, {}, "main"
            )
            mlproject_config.validate()

        if expected is not None:
            expected = (
                expected.replace(
                    "ml_project_resource", mlproject_path.as_posix()
                )
                .replace("invalid_config_type", invalid_config_type.as_posix())
                .replace("config_with_errors", config_with_errors.as_posix())
            )

            result = str(e.value)

            assert result == expected

    @pytest.mark.parametrize(
        ("execution_dict", "expected", "error_message"),
        [
            # Test case: local apptainer path does not exist
            (
                {
                    "Apptainer": {
                        "Path": "non-existent-image",
                        "Type": "local",
                    }
                },
                exceptions.ConfigValidationError(),
                "The path '"
                "mlproject_path/non-existent-image' "
                "given as execution environment was not found, "
                "check that the given path is correct. "
                "The path must be relative to the ML project path.",
            ),
            # Test case: image exists
            (
                {"Apptainer": {"Path": "mantik-test.sif", "Type": "local"}},
                None,
                None,
            ),
            # Test case: image is remote and path absolute
            (
                {
                    "Apptainer": {
                        "Path": "/absolute/remote/image",
                        "Type": "remote",
                    }
                },
                None,
                None,
            ),
            # Test case: image is remote and path relative
            (
                {
                    "Apptainer": {
                        "Path": "relative/remote/image",
                        "Type": "remote",
                    }
                },
                exceptions.ConfigValidationError(),
                "If image type 'remote' is given for an Apptainer image, "
                "the given path must be absolute. "
                "The given path is: 'relative/remote/image'.",
            ),
            # Test case: python venv has relative path
            (
                {
                    "Python": {
                        "Path": "relative/remote/image",
                    }
                },
                exceptions.ConfigValidationError(),
                "The given path to the Python Venv must be absolute. "
                "The given path is: 'relative/remote/image'.",
            ),
        ],
    )
    def test_validate_execution_path(
        self,
        expect_raise_if_exception,
        mlproject_path,
        execution_dict,
        expected,
        error_message,
    ):
        with expect_raise_if_exception(expected) as e:
            config = project_config.ProjectValidator(
                mlproject_path, "config_path", {}, "main"
            )
            execution = environment._get_execution_environment(execution_dict)

            result = config._validate_execution_path(execution)
            assert result is expected

        if error_message is not None:
            expected_error = error_message.replace(
                "mlproject_path", mlproject_path.as_posix()
            )
            result_error = str(e.value)
            assert result_error == expected_error

    @pytest.mark.parametrize(
        ("entry_point", "parameters", "expected"),
        [
            (
                "this-entry-point-does-not-exist",
                {},
                mlflow.exceptions.ExecutionException(
                    "Could not find this-entry-point-does-not-exist "
                    "among entry points ['main'] "
                    "or interpret this-entry-point-does-not-exist "
                    "as a runnable script. "
                    "Supported script file extensions: ['.py', '.sh']"
                ),
            ),
            ("main", {}, None),
        ],
    )
    def test_validate_ml_project_file(
        self,
        expect_raise_if_exception,
        mlproject_path,
        entry_point,
        parameters,
        expected,
    ):
        with expect_raise_if_exception(expected) as e:
            config = project_config.ProjectValidator(
                mlproject_path,
                "compute-backend-config.yaml",
                parameters,
                entry_point,
            )
            config.validate()
            if expected is not None:
                assert str(e.value) == expected.message

    def test_validate_config_not_in_exclude(
        self,
        mlproject_path,
        tmp_path,
        expect_raise_if_exception,
    ):
        config_file_name = "compute-backend-config.yaml"
        path = _copy_mlproject_and_add_exclude_to_config(
            tmp_path=tmp_path,
            mlproject_path=mlproject_path,
            name=config_file_name,
        )

        with expect_raise_if_exception(exceptions.ConfigValidationError()) as e:
            config = project_config.ProjectValidator(
                path, config_file_name, {}, "main"
            )
            config.validate()

        assert f"Config file '{config_file_name}' cannot be excluded" in str(
            e.value
        )


def _copy_mlproject_and_add_exclude_to_config(
    tmp_path: pathlib.Path, mlproject_path: pathlib.Path, name: str
) -> pathlib.Path:
    target = tmp_path / "mlproject"
    shutil.copytree(mlproject_path, target)

    with open(mlproject_path / name) as f:
        config = yaml.safe_load(f.read())
        config["Exclude"] = [name]

    with open(target / name, "w") as f:
        yaml.safe_dump(config, stream=f, indent=4)

    return target
