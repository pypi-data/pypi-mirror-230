import tempfile
import typing as t


def use_temp_dir(func: t.Callable):
    """

    Parameters
    ----------
    func : a function that has temp_dir_name as argument

    Returns
    -------
    It returns what func returns, but it provides
    a temporary directory throughout execution to func,
    and that directory name is passed to func
    through the temp_dir_name argument.
    The directory is deleted when func ends.
    """

    def wrapper(*args, **kwargs):
        with tempfile.TemporaryDirectory() as temp_dir:
            return func(*args, temp_dir_name=temp_dir, **kwargs)

    return wrapper
