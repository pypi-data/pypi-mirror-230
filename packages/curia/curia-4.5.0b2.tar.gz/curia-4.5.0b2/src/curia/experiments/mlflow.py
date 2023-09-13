import functools
from typing import Callable, Dict, Any

import mlflow


class MLFlowLogger:
    def __init__(self, run_name=None, tags=None, autolog=False, is_nested=False):
        self.run_name = run_name
        self.tags = tags
        self.autolog = autolog
        self.is_nested = is_nested

    @staticmethod
    def log_dict(dict_to_log):
        for key, value in dict_to_log.items():
            mlflow.log_metric(key, value)

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if self.autolog:
                mlflow.autolog(log_datasets=False, log_models=True)
            with mlflow.start_run(
                nested=self.is_nested, run_name=self.run_name, tags=self.tags
            ):
                result = func(*args, **kwargs)

                # If the function returns a dictionary, log it.
                if isinstance(result, dict):
                    self.log_dict(result)

            return result

        return wrapper


def using_mlflow_logging(
    run_name: str = None,
    tags: Dict[str, Any] = None,
    autolog: bool = False,
    is_nested: bool = False,
) -> Callable:
    """
    A convenience function for using the MLFlowLogger class as a decorator.

    Args:
        run_name (str, optional): The name of the run. Defaults to None.
        tags (Dict[str, Any], optional): A dictionary of tags to add to the run. Defaults to None.
        autolog (bool, optional): Whether to use MLFlow's autologging feature. Defaults to False.
        is_nested (bool, optional): Whether the run is nested within another run. Defaults to False.

    Returns:
        Callable: A decorator for logging MLFlow runs.
    """

    logger = MLFlowLogger(run_name, tags, autolog, is_nested)

    def decorator(func: Callable) -> Callable:
        return logger(func)

    return decorator
