import os
from typing import TYPE_CHECKING, Any, Optional
import logging


if TYPE_CHECKING:
    from qdvc.repo import Repo

logger = logging.getLogger(__name__)


def commit(
    repo: "Repo",
    message: Optional[str] = None,
    **kwargs: Any,
) -> str:

    # Check if we are on a query branch
    if not repo.is_query_branch():
        raise Exception("You tried to commit a query but you are not on a query branch. Please create a new query")
    filter_path = os.path.join(repo.qdvc_dir, repo.FILTER_FILE_NAME)
    # Check if only the filter.py was modified, and there is nothing else than things in .data folder
    diff = repo.git_repo.index.diff("HEAD")
    found_filter_file = False
    for file_diff in diff:
        abs_path = os.path.abspath(file_diff.a_blob.path)
        if abs_path != filter_path:
            raise Exception(
                f"You tried to create a query branch by adding files others than {filter_path}. " f"Namely: {abs_path}"
            )
        found_filter_file = True

    if not found_filter_file:
        raise Exception(f"You need to modify and `git add {filter_path}` to create your query")

    # Commit it. Print a message to remind to checkout with master data.
    message = message if message else "Query commit"
    repo.git_repo.git.commit("-m", message)

    logger.info("Successfuly commited query. Remember to push the branch and start using by `qdvc checkout`.")
    return message
