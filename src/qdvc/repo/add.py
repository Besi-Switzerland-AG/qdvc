from typing import TYPE_CHECKING, Any, List
from .githelper import checkout_master
import os
from dvc.stage import Stage

if TYPE_CHECKING:
    from qdvc.repo import Repo
    from qdvc.types import TargetType


def add(
    repo: "Repo",
    targets: "TargetType",
    recursive: bool = False,
    no_commit: bool = False,
    fname: str = ".",
    to_remote: bool = False,
    **kwargs: Any,
) -> List[str]:
    checkout_master(repo.git_repo)
    staged = repo.dvc_repo.add(targets, recursive, no_commit, fname, to_remote, **kwargs)

    new_paths = []
    for staged_file in staged:
        staged_file: Stage
        if staged_file.path[: len(repo.root_dir)] != repo.root_dir:
            raise Exception("Cannot add a file outside repository, please try again.")
        new_path = os.path.join(repo.data_qdvc_dir, staged_file.path[len(repo.root_dir) + 1 :])
        dir_name = os.path.dirname(new_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        os.rename(staged_file.path, new_path)
        new_paths.append(new_path)

    repo.git_repo.git.add(new_paths)
    return new_paths
