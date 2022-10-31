import shutil
from dvc.repo import Repo as DvcRepo
from git.repo import Repo as GitRepo
from qdvc.repo import Repo
from qdvc.config import Config
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
    qdvc_dir = _create_dir(root_dir, Repo.QDVC_DIR, force)
    data_dir = _create_dir(root_dir, Repo.QDVC_DATA_DIR, force)

    _ = Config.init(qdvc_dir)

    base_gitignore_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "resources",
        "gitignore_skeleton",
    )
    gitignore_path = os.path.join(qdvc_dir, ".gitignore")
    shutil.copyfile(base_gitignore_path, gitignore_path)

    repo = GitRepo(root_dir)

    repo.index.add(data_dir)
    repo.index.add(qdvc_dir)
    # repo.git_repo.index.commit("Initial QDVC commit")

    return DvcRepo(root_dir)


def _create_dir(rootdir: str, sudir: str, force: bool) -> str:
    new_dir = os.path.join(rootdir, sudir)

    if os.path.isdir(new_dir):
        if not force:
            raise InitError(f"'{relpath(new_dir)}' exists. Use `-f` to force.")
        remove(new_dir)

    os.mkdir(new_dir)
    return new_dir
