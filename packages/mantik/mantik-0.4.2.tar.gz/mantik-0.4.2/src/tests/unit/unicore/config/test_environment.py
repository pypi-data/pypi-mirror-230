import os
import pathlib

import pytest

import mantik.testing as testing
import mantik.unicore.config.environment as environment
import mantik.unicore.config.executable as executable
import mantik.unicore.exceptions as exceptions


class TestEnvironment:
    @pytest.mark.parametrize(
        ("env_vars", "d", "expected"),
        [
            (
                testing.config.ALL_ENV_VARS,
                {
                    "Apptainer": {
                        "Path": "image.sif",
                    },
                },
                testing.config._create_apptainer_environment(
                    path=pathlib.Path("image.sif")
                ),
            ),
            (
                testing.config.ALL_ENV_VARS,
                {"Python": "/path/to/venv"},
                testing.config._create_python_environment(
                    path=pathlib.Path("/path/to/venv")
                ),
            ),
            (
                testing.config.ALL_ENV_VARS,
                {"Python": {"Path": "/path/to/venv"}},
                testing.config._create_python_environment(
                    path=pathlib.Path("/path/to/venv")
                ),
            ),
            (
                testing.config.ALL_ENV_VARS,
                {
                    "Python": {"Path": "/path/to/venv"},
                    "PreRunCommand": {
                        "Command": "a precommand",
                        "ExecuteOnLoginNode": True,
                    },
                    "PostRunCommand": {
                        "Command": "a postcommand",
                        "ExecuteOnLoginNode": True,
                    },
                },
                testing.config._create_python_environment(
                    path=pathlib.Path("/path/to/venv"),
                    preRunCommand=environment.Command(
                        command="a precommand", executeOnLoginNode=True
                    ),
                    postRunCommand=environment.Command(
                        command="a postcommand", executeOnLoginNode=True
                    ),
                ),
            ),
        ],
    )
    def test_from_dict(
        self, monkeypatch, expect_raise_if_exception, env_vars, d, expected
    ):
        if "MLFLOW_TRACKING_TOKEN" in os.environ:
            del os.environ["MLFLOW_TRACKING_TOKEN"]
        if "MLFLOW_EXPERIMENT_ID" in os.environ:
            del os.environ["MLFLOW_EXPERIMENT_ID"]
        for key in env_vars:
            os.environ[key] = testing.config.DEFAULT_ENV_VAR_VALUE

        with expect_raise_if_exception(expected):
            result = environment.Environment.from_dict(d)

            assert result == expected

    @pytest.mark.parametrize(
        (
            "env",
            "expected",
        ),
        [
            # Test case: No execution environment
            (
                environment.Environment(),
                None,
            ),
            # Test case: Apptainer
            (
                testing.config._create_apptainer_environment(
                    path=pathlib.Path("/path/to/venv")
                ),
                "srun apptainer",
            ),
            # Test case: Python
            (
                testing.config._create_python_environment(
                    path=pathlib.Path("/path/to/venv")
                ),
                None,
            ),
        ],
    )
    def test_create_execution_command(self, env, expected):
        result = env._create_execution_command()

        assert expected == result

    @pytest.mark.parametrize(
        (
            "env",
            "expected",
        ),
        [
            # Test case: Apptainer with no modules and no precommand
            (
                testing.config._create_apptainer_environment(
                    modules=None, path=pathlib.Path("/path/to/venv")
                ),
                None,
            ),
            # Test case: Apptainer with no modules and precommand
            (
                testing.config._create_apptainer_environment(
                    modules=None,
                    path=pathlib.Path("/path/to/venv"),
                    preRunCommand=environment.Command(command="a precommand"),
                ),
                "a precommand",
            ),
            # Test case: Apptainer with 1 module and no precommand
            (
                testing.config._create_apptainer_environment(
                    modules=["Module"], path=pathlib.Path("/path/to/venv")
                ),
                "module load Module",
            ),
            # Test case: Apptainer with 1 module and precommand
            (
                testing.config._create_apptainer_environment(
                    modules=["Module"],
                    path=pathlib.Path("/path/to/venv"),
                    preRunCommand=environment.Command(command="a precommand"),
                ),
                "a precommand; module load Module",
            ),
            # Test case: Apptainer with 2 modules and no precommand
            (
                testing.config._create_apptainer_environment(
                    modules=["Module"], path=pathlib.Path("/path/to/venv")
                ),
                "module load Module",
            ),
            # Test case: Apptainer with 2 modules and precommand
            (
                testing.config._create_apptainer_environment(
                    modules=["Module1", "Module2"],
                    path=pathlib.Path("/path/to/venv"),
                    preRunCommand=environment.Command(command="a precommand"),
                ),
                "a precommand; module load Module1 Module2",
            ),
            # Test case: Python with no modules and no precommand
            (
                testing.config._create_python_environment(
                    modules=None, path=pathlib.Path("/path/to/venv")
                ),
                "source /path/to/venv/bin/activate",
            ),
            # Test case: Python with no modules and precommand
            (
                testing.config._create_python_environment(
                    modules=None,
                    path=pathlib.Path("/path/to/venv"),
                    preRunCommand=environment.Command(command="a precommand"),
                ),
                "a precommand; source /path/to/venv/bin/activate",
            ),
            # Test case: Python with 1 module and no precommand
            (
                testing.config._create_python_environment(
                    modules=["Module"],
                    path=pathlib.Path("/path/to/venv"),
                ),
                ("source /path/to/venv/bin/activate; " "module load Module"),
            ),
            # Test case: Python with 1 module and precommand
            (
                testing.config._create_python_environment(
                    modules=["Module"],
                    path=pathlib.Path("/path/to/venv"),
                    preRunCommand=environment.Command(command="a precommand"),
                ),
                (
                    "a precommand; "
                    "source /path/to/venv/bin/activate; "
                    "module load Module"
                ),
            ),
            # Test case: Python with 2 modules and no precommand
            (
                testing.config._create_python_environment(
                    modules=["Module1", "Module2"],
                    path=pathlib.Path("/path/to/venv"),
                ),
                (
                    "source /path/to/venv/bin/activate; "
                    "module load Module1 Module2"
                ),
            ),
            # Test case: Python with 2 modules and precommand
            (
                testing.config._create_python_environment(
                    modules=["Module1", "Module2"],
                    path=pathlib.Path("/path/to/venv"),
                    preRunCommand=environment.Command(command="a precommand"),
                ),
                (
                    "a precommand; "
                    "source /path/to/venv/bin/activate; "
                    "module load Module1 Module2"
                ),
            ),
            # Test case: No execution environment
            (
                environment.Environment(
                    modules=["Module1", "Module2"],
                    preRunCommand=environment.Command(command="a precommand"),
                ),
                "a precommand; module load Module1 Module2",
            ),
        ],
    )
    def test_create_precommand(self, env, expected):
        result = env._create_precommand()

        assert expected == result

    def test_create_postcommand(self):
        expected = "a postcommand"
        env = testing.config._create_python_environment(
            path=pathlib.Path("/path/to/venv"),
            postRunCommand=environment.Command(command="a postcommand"),
        )

        result = env._create_postcommand()

        assert expected == result

    @pytest.mark.parametrize(
        "env",
        [
            # Test case: Apptainer with no variables
            testing.config._create_apptainer_environment(
                modules=None,
                path=pathlib.Path("/path/to/venv"),
                include_mlflow_env_vars=False,
            ),
            # Test case: Python with no variables
            testing.config._create_python_environment(
                modules=None,
                path=pathlib.Path("/path/to/venv"),
                include_mlflow_env_vars=False,
            ),
        ],
    )
    def test_add_env_variables(self, env):
        assert env.variables is None
        expected = {"env_var": "ENV_VAR"}
        env.add_env_vars(expected)
        result = env.variables
        assert expected == result


@pytest.mark.parametrize(
    ("config", "expected", "error_message"),
    [
        # Test case: No execution environment given
        (
            {"Resources": {}},
            None,
            None,
        ),
        # Test case: One execution environment given
        (
            {"Apptainer": {"Path": "image.sif"}},
            executable.Apptainer(path=pathlib.Path("image.sif")),
            None,
        ),
        # Test case: Two execution environments given, should raise
        (
            {"Apptainer": {}, "Python": {}},
            exceptions.ConfigValidationError(),
            "Only one execution environment is allowed, "
            "but in config these have been "
            "found: 'Apptainer', 'Python'.",
        ),
    ],
)
def test_get_execution_environment(
    expect_raise_if_exception, config, expected, error_message
):
    with expect_raise_if_exception(expected) as e:
        result = environment._get_execution_environment(config)
        assert result == expected

    if error_message is not None:
        assert str(e.value) == error_message
