import contextlib
import logging
import pathlib
import os

log = logging.getLogger(__name__)


@contextlib.contextmanager
def cwd(path: pathlib.Path):
    """Change working directory and return to previous directory on exit."""
    current = pathlib.Path.cwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(current)
