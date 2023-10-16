import pathlib

import pytest

import mantik.testing as testing
import mantik.unicore.config as _config
import mantik.unicore.config.executable as executable
import mantik.unicore.exceptions as exceptions


class TestConfig:
    @pytest.mark.parametrize(
        ("env_vars", "d", "expected"),
        [
            # Test cases: environment variables not set.
            ([], {}, exceptions.ConfigValidationError()),
            (
                testing.config.ALL_ENV_VARS[:1],
                {},
                exceptions.ConfigValidationError(),
            ),
            (
                testing.config.ALL_ENV_VARS[:2],
                {},
                exceptions.ConfigValidationError(),
            ),
            (
                testing.config.ALL_ENV_VARS,
                {},
                exceptions.ConfigValidationError(),
            ),
            # Test case: backend config missing Resources section.
            (
                testing.config.ALL_ENV_VARS,
                {"Queue": "batch"},
                exceptions.ConfigValidationError(),
            ),
            # Test case: Everything correct.
            (
                testing.config.ALL_ENV_VARS,
                {
                    "UnicoreApiUrl": "test-url",
                    "Environment": {
                        "Apptainer": {
                            "Path": "image.sif",
                        },
                    },
                    "Resources": {"Queue": "batch"},
                },
                testing.config._create_config(
                    resources=_config.resources.Resources(queue="batch"),
                    env=_config.environment.Environment(
                        execution=executable.Apptainer(
                            path=pathlib.Path("image.sif"),
                        ),
                    ),
                ),
            ),
            # Test case: No environment given
            (
                testing.config.ALL_ENV_VARS,
                {
                    "UnicoreApiUrl": "test-url",
                    "Resources": {"Queue": "batch"},
                },
                testing.config._create_config(
                    resources=_config.resources.Resources(queue="batch"),
                ),
            ),
            # Test case: No environment given, but resources
            (
                testing.config.ALL_ENV_VARS,
                {
                    "UnicoreApiUrl": "test-url",
                    "Resources": {
                        "Queue": "batch",
                        "Runtime": "2h",
                        "Nodes": 1,
                        "TotalCPUs": 2,
                        "CPUsPerNode": 3,
                        "GPUsPerNode": 4,
                        "MemoryPerNode": "10G",
                        "Reservation": "test-reservation",
                        "NodeConstraints": "mem192",
                        "QoS": "test-qos",
                    },
                },
                testing.config._create_config(
                    resources=_config.resources.Resources(
                        queue="batch",
                        runtime="2h",
                        nodes=1,
                        total_cpus=2,
                        cpus_per_node=3,
                        gpus_per_node=4,
                        memory_per_node="10G",
                        reservation="test-reservation",
                        node_constraints="mem192",
                        qos="test-qos",
                    ),
                ),
            ),
            # Test case: Only modules given in environment
            (
                testing.config.ALL_ENV_VARS,
                {
                    "UnicoreApiUrl": "test-url",
                    "Environment": {
                        "Modules": ["module"],
                    },
                    "Resources": {"Queue": "batch"},
                },
                testing.config._create_config(
                    resources=_config.resources.Resources(queue="batch"),
                    env=_config.environment.Environment(
                        modules=["module"],
                    ),
                ),
            ),
            # Test case: Local Apptainer image given.
            (
                testing.config.ALL_ENV_VARS,
                {
                    "UnicoreApiUrl": "test-url",
                    "Resources": {"Queue": "batch"},
                    "Environment": {
                        "Apptainer": {
                            "Path": "image.sif",
                        },
                    },
                },
                testing.config._create_config(
                    resources=_config.resources.Resources(queue="batch"),
                    env=_config.environment.Environment(
                        execution=executable.Apptainer(
                            path=pathlib.Path("image.sif"),
                        ),
                    ),
                ),
            ),
            # Test case: Local Apptainer image given with additional options
            # as list of strings
            (
                testing.config.ALL_ENV_VARS,
                {
                    "UnicoreApiUrl": "test-url",
                    "Resources": {"Queue": "batch"},
                    "Environment": {
                        "Apptainer": {
                            "Path": "image.sif",
                            "Options": ["--nv", "-B /data:/data"],
                        },
                    },
                },
                testing.config._create_config(
                    resources=_config.resources.Resources(queue="batch"),
                    env=_config.environment.Environment(
                        execution=executable.Apptainer(
                            path=pathlib.Path("image.sif"),
                            options=["--nv", "-B /data:/data"],
                        )
                    ),
                ),
            ),
            # Test case: Local Apptainer image given with additional options
            # as string
            (
                testing.config.ALL_ENV_VARS,
                {
                    "UnicoreApiUrl": "test-url",
                    "Resources": {"Queue": "batch"},
                    "Environment": {
                        "Apptainer": {
                            "Path": "image.sif",
                            "Options": "--nv -B /data:/data",
                        },
                    },
                },
                testing.config._create_config(
                    resources=_config.resources.Resources(queue="batch"),
                    env=_config.environment.Environment(
                        execution=executable.Apptainer(
                            path=pathlib.Path("image.sif"),
                            options=["--nv -B /data:/data"],
                        )
                    ),
                ),
            ),
            # Test case: Remote Apptainer image given.
            (
                testing.config.ALL_ENV_VARS,
                {
                    "UnicoreApiUrl": "test-url",
                    "Resources": {"Queue": "batch"},
                    "Environment": {
                        "Apptainer": {
                            "Path": "/absolute/path/to/image.sif",
                            "Type": "remote",
                        },
                    },
                },
                testing.config._create_config(
                    resources=_config.resources.Resources(queue="batch"),
                    env=_config.environment.Environment(
                        execution=executable.Apptainer(
                            path=pathlib.Path("/absolute/path/to/image.sif"),
                            type="remote",
                        ),
                    ),
                ),
            ),
            # Test case: More variables and modules given.
            (
                testing.config.ALL_ENV_VARS,
                {
                    "UnicoreApiUrl": "test-url",
                    "Resources": {"Queue": "batch"},
                    "Environment": {
                        "Apptainer": {
                            "Path": "/absolute/path/to/image.sif",
                            "Type": "remote",
                        },
                        "Variables": {"TEST_ENV_VAR": "value"},
                        "Modules": [
                            "TensorFlow/2.5.0-Python-3.8.5",
                            "Horovod/0.23.0-Python-3.8.5",
                            "PyTorch/1.8.1-Python-3.8.5",
                        ],
                    },
                },
                testing.config._create_config(
                    resources=_config.resources.Resources(queue="batch"),
                    env=_config.environment.Environment(
                        execution=executable.Apptainer(
                            path=pathlib.Path("/absolute/path/to/image.sif"),
                            type="remote",
                        ),
                        modules=[
                            "TensorFlow/2.5.0-Python-3.8.5",
                            "Horovod/0.23.0-Python-3.8.5",
                            "PyTorch/1.8.1-Python-3.8.5",
                        ],
                        variables={"TEST_ENV_VAR": "value"},
                    ),
                ),
            ),
            # Test case: Remote Apptainer image given but relative path.
            (
                testing.config.ALL_ENV_VARS,
                {
                    "UnicoreApiUrl": "test-url",
                    "Resources": {"Queue": "batch"},
                    "Environment": {
                        "Apptainer": {
                            "Path": "../relative/path/to/image.sif",
                            "Type": "remote",
                        },
                    },
                },
                exceptions.ConfigValidationError(),
            ),
            # Test case: Config entry has incorrect type.
            (
                testing.config.ALL_ENV_VARS,
                {
                    "UnicoreApiUrl": "test-url",
                    "Resources": {"Queue": "batch", "Nodes": "incorrect type"},
                },
                exceptions.ConfigValidationError(),
            ),
        ],
    )
    @pytest.mark.usefixtures("unset_tracking_token_env_var_before_execution")
    def test_from_dict(
        self, expect_raise_if_exception, env_vars_set, env_vars, d, expected
    ):
        env_vars = {
            var: testing.config.DEFAULT_ENV_VAR_VALUE for var in env_vars
        }

        with env_vars_set(env_vars), expect_raise_if_exception(expected):
            result = _config.core.Config.from_dict(d)

            assert result == expected

    @pytest.mark.parametrize(
        ("config", "expected"),
        [
            # Test case: Only project, resources and
            # environment are included in the returned dict.
            (
                _config.core.Config(
                    api_url="not_included",
                    user="not_included",
                    password="not_included",
                    project="test-project",
                    resources=_config.resources.Resources(
                        queue="batch",
                    ),
                    environment=_config.environment.Environment(
                        execution=executable.Apptainer(
                            path=pathlib.Path("test-image")
                        ),
                    ),
                ),
                {
                    "Project": "test-project",
                    "Resources": {"Queue": "batch"},
                    "Executable": "srun apptainer",
                    "Arguments": [
                        "run",
                        "--cleanenv",
                        "--env MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI:-file://$PWD/mlruns}",  # noqa: E501
                        "${MLFLOW_TRACKING_TOKEN:+--env MLFLOW_TRACKING_TOKEN=$MLFLOW_TRACKING_TOKEN}",  # noqa: E501
                        "${MLFLOW_EXPERIMENT_NAME:+--env MLFLOW_EXPERIMENT_NAME=$MLFLOW_EXPERIMENT_NAME}",  # noqa: E501
                        "${MLFLOW_EXPERIMENT_ID:+--env MLFLOW_EXPERIMENT_ID=$MLFLOW_EXPERIMENT_ID}",  # noqa: E501
                        "test-image",
                    ],
                    "RunUserPrecommandOnLoginNode": False,
                    "RunUserPostcommandOnLoginNode": False,
                    "Stdout": "mantik.log",
                    "Stderr": "mantik.log",
                },
            ),
            # Test case: All given values included.
            (
                _config.core.Config(
                    api_url="not_included",
                    user="not_included",
                    password="not_included",
                    project="test-project",
                    resources=_config.resources.Resources(
                        queue="batch",
                        runtime="1h",
                        nodes=2,
                        total_cpus=48,
                        cpus_per_node=24,
                        memory_per_node="10G",
                        gpus_per_node=1,
                        reservation="test-reservation",
                        node_constraints="test-node-constraints",
                        qos="test-qos",
                    ),
                    environment=_config.environment.Environment(
                        execution=executable.Apptainer(
                            path=pathlib.Path("test-image"),
                        ),
                        variables={"TEST": "test"},
                    ),
                ),
                {
                    "Project": "test-project",
                    "Resources": {
                        "Queue": "batch",
                        "Runtime": "1h",
                        "Nodes": 2,
                        "TotalCPUs": 48,
                        "CPUsPerNode": 24,
                        "GPUS": 1,
                        "MemoryPerNode": "10G",
                        "Reservation": "test-reservation",
                        "NodeConstraints": "test-node-constraints",
                        "QoS": "test-qos",
                    },
                    "Environment": {"TEST": "test", "SRUN_CPUS_PER_TASK": "24"},
                    "Executable": "srun apptainer",
                    "Arguments": [
                        "run",
                        "--cleanenv",
                        "--env MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI:-file://$PWD/mlruns}",  # noqa: E501
                        "${MLFLOW_TRACKING_TOKEN:+--env MLFLOW_TRACKING_TOKEN=$MLFLOW_TRACKING_TOKEN}",  # noqa: E501
                        "${MLFLOW_EXPERIMENT_NAME:+--env MLFLOW_EXPERIMENT_NAME=$MLFLOW_EXPERIMENT_NAME}",  # noqa: E501
                        "${MLFLOW_EXPERIMENT_ID:+--env MLFLOW_EXPERIMENT_ID=$MLFLOW_EXPERIMENT_ID}",  # noqa: E501
                        "test-image",
                    ],
                    "RunUserPrecommandOnLoginNode": False,
                    "RunUserPostcommandOnLoginNode": False,
                    "Stdout": "mantik.log",
                    "Stderr": "mantik.log",
                },
            ),
        ],
    )
    def test_to_dict(self, config, expected):
        result = config.to_dict()

        assert result == expected

    @pytest.mark.parametrize(
        ("config", "expected"),
        [
            # Test case: No environment section, and cpus_per_node unset
            (
                _config.core.Config(
                    api_url="not_included",
                    user="not_included",
                    password="not_included",
                    project="test-project",
                    resources=_config.resources.Resources(
                        queue="batch",
                    ),
                ),
                None,
            ),
            # Test case: Environment section, but no Variables, and
            # cpus_per_node unset
            (
                _config.core.Config(
                    api_url="not_included",
                    user="not_included",
                    password="not_included",
                    project="test-project",
                    resources=_config.resources.Resources(
                        queue="batch",
                    ),
                    environment=_config.environment.Environment(),
                ),
                None,
            ),
            # Test case: Environment section with Variables, and
            # cpus_per_node unset
            (
                _config.core.Config(
                    api_url="not_included",
                    user="not_included",
                    password="not_included",
                    project="test-project",
                    resources=_config.resources.Resources(
                        queue="batch",
                    ),
                    environment=_config.environment.Environment(
                        variables={"TEST_VAR": "test_value"}
                    ),
                ),
                {"TEST_VAR": "test_value"},
            ),
            # Test case: SRUN_CPUS_PER_TASK set explicitly by user,
            # and cpus_per_node unset
            (
                _config.core.Config(
                    api_url="not_included",
                    user="not_included",
                    password="not_included",
                    project="test-project",
                    resources=_config.resources.Resources(
                        queue="batch",
                    ),
                    environment=_config.environment.Environment(
                        variables={"SRUN_CPUS_PER_TASK": "2"},
                    ),
                ),
                {"SRUN_CPUS_PER_TASK": "2"},
            ),
            # Test case: No environment section, and cpus_per_node set
            (
                _config.core.Config(
                    api_url="not_included",
                    user="not_included",
                    password="not_included",
                    project="test-project",
                    resources=_config.resources.Resources(
                        queue="batch",
                        cpus_per_node=2,
                    ),
                ),
                {"SRUN_CPUS_PER_TASK": "2"},
            ),
            # Test case: Environment section, but no Variables, and
            # cpus_per_node set
            (
                _config.core.Config(
                    api_url="not_included",
                    user="not_included",
                    password="not_included",
                    project="test-project",
                    resources=_config.resources.Resources(
                        queue="batch",
                        cpus_per_node=2,
                    ),
                    environment=_config.environment.Environment(),
                ),
                {"SRUN_CPUS_PER_TASK": "2"},
            ),
            # Test case: Environment section with Variables, and
            # cpus_per_node set
            (
                _config.core.Config(
                    api_url="not_included",
                    user="not_included",
                    password="not_included",
                    project="test-project",
                    resources=_config.resources.Resources(
                        queue="batch",
                        cpus_per_node=2,
                    ),
                    environment=_config.environment.Environment(
                        variables={"TEST_VAR": "test_value"},
                    ),
                ),
                {"TEST_VAR": "test_value", "SRUN_CPUS_PER_TASK": "2"},
            ),
            # Test case: SRUN_CPUS_PER_TASK set explicitly by user, and
            # cpus_per_node set
            (
                _config.core.Config(
                    api_url="not_included",
                    user="not_included",
                    password="not_included",
                    project="test-project",
                    resources=_config.resources.Resources(
                        queue="batch",
                        cpus_per_node=1,
                    ),
                    environment=_config.environment.Environment(
                        variables={
                            "TEST_VAR": "test_value",
                            "SRUN_CPUS_PER_TASK": "2",
                        }
                    ),
                ),
                {"TEST_VAR": "test_value", "SRUN_CPUS_PER_TASK": "2"},
            ),
        ],
    )
    def test_with_optional_add_srun_cpus_per_task_to_environment(
        self, config, expected
    ) -> None:
        result = config.environment.variables

        assert result == expected
