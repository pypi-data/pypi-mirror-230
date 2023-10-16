import logging
import sys

import mlflow

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    # Print, log and write to file to test all those functionalities with the
    # UNICORE backend.
    argument_string = " ".join(sys.argv[1:])
    with mlflow.start_run():
        print(argument_string)
        logger.debug(f"Printed {argument_string}.")
        mlflow.log_param("print", "Hello")
        with open("output.txt", "w") as text_file:
            text_file.write("test")
