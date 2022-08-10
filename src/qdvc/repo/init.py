from dvc.repo import Repo as DvcRepo
from qdvc.config import Config
from qdvc.repo import Repo
from dvc.utils import relpath
from dvc.utils.fs import remove
from dvc.exceptions import InitError

import logging
import os

logger = logging.getLogger(__name__)


def init(root_dir=os.curdir, no_scm=False, force=False, subdir=False):
    """
    Creates an empty repo on the given directory -- basically a
    `.qdvc` directory with subdirectories for configuration and cache.
    flag to override it.
    Args:
        root_dir: Path to repo's root directory.
    Returns:
        Repo instance.
    Raises:
        KeyError: Raises an exception.
    """
    DvcRepo.init(root_dir, no_scm, force, subdir)

    root_dir = os.path.realpath(root_dir)
    qdvc_dir = os.path.join(root_dir, Repo.QDVC_DIR)

    if os.path.isdir(qdvc_dir):
        if not force:
            raise InitError(f"'{relpath(qdvc_dir)}' exists. Use `-f` to force.")

        remove(qdvc_dir)

    os.mkdir(qdvc_dir)

    _ = Config.init(qdvc_dir)

    return DvcRepo(root_dir)
