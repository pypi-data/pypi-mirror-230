"""
Utility functions for microservice_shared package.
"""
import os


def create_directories(log_directories) -> None:
    """
    Creates the specified log directories if they don't exist.

    This function takes a list of directory paths as input and creates each
    directory if it doesn't already exist. The `exist_ok` parameter is set to
    True, so if the directory already exists, no error will be raised.

    Args:
        log_directories (List[str]): A list of directory paths to create.

    Returns:
        None.
    """
    for directory in log_directories:
        os.makedirs(directory, exist_ok=True)
