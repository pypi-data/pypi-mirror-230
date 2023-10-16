import logging
import pathlib

import mlflow.projects as projects

FILE_PATH = pathlib.Path(__file__).parent

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


if __name__ == "__main__":
    uri = FILE_PATH
    entry_point = "main"
    version = None
    experiment_name = None
    experiment_id = None
    param_dict = None
    backend = "unicore"
    backend_config = FILE_PATH / "compute-backend-config.json"
    no_conda = True
    storage_dir = None
    run_id = None

    run_submitted = projects.run(
        uri.as_posix(),
        entry_point,
        version,
        experiment_name=experiment_name,
        experiment_id=experiment_id,
        parameters=param_dict,
        backend=backend,
        backend_config=backend_config.as_posix(),
        storage_dir=storage_dir,
        synchronous=True,
        run_id=run_id,
    )

    logger.debug(f"Properties: {run_submitted.properties}")
    content_output = run_submitted.read_file_from_working_directory(
        pathlib.Path("mantik.log")
    )
    logger.debug(f"UNICORE logs: {run_submitted.logs}")
    print(f"Mantik logs: {content_output}")
