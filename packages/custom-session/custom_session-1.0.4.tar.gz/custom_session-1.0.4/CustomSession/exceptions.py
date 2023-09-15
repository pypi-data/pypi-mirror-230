from typing import *


class RetriesExceeded(Exception):
    """
    Custom exception for handling cases where the maximum number of retries is exceeded during HTTP requests.

    This exception is raised when the `SyncSession` class encounters exceptions during HTTP requests. It handles retries
    based on the specified criteria and raises this exception if the maximum number of retries is exceeded.

    Attributes:
        message (str): A descriptive error message indicating the reason for the exception.
        retries_attempted (int): The number of retry attempts made before this exception was raised.
        ignored_exceptions (List[Type[Exception]]): A list of exception types that are ignored and trigger retries
            when encountered.

    Example usage:
    ```
    try:
        # Code that may raise exceptions
    except RetriesExceeded as e:
        print(f"Retries exceeded after {e.retries_attempted} attempts: {e}")
    ```
    """
    def __init__(self, message: str, retries_attempted: int, ignored_exceptions: List[Type[Exception]]):
        super().__init__(message)
        self.retries_attempted = retries_attempted
        self.ignored_exceptions = ignored_exceptions
