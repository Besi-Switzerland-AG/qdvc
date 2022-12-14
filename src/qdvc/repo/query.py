from typing import TYPE_CHECKING, Any
from .githelper import checkout_master
from gitdb.exc import BadName
import os
import shutil


if TYPE_CHECKING:
    from qdvc.repo import Repo


def query(
    repo: "Repo",
    name: str,
    **kwargs: Any,
) -> str:
    checkout_master(repo.git_repo)

    # Branch from master
    try:
        new_branch = repo.git_repo.create_head(repo.QUERY_SEPARATOR.join([repo.QUERY_BRANCH_PREFIX, name, repo.QUERY_INIT]))
    except BadName:
        raise Exception(
            "Please create a first commit on master branch, " "e.g. by commiting config files or adding new data."
        )
    new_branch.checkout()

    # Create a filter.py file
    filter_path = os.path.join(repo.qdvc_dir, repo.FILTER_FILE_NAME)
    if os.path.exists(filter_path):
        raise Exception(f"{filter_path} already exists. Please remove it from Master.")

    base_filter_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "resources",
        "filter_skeletton.py",
    )
    shutil.copyfile(base_filter_path, filter_path)
    return name
