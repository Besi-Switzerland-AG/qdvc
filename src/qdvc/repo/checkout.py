import os
from typing import TYPE_CHECKING, Any, Optional
import logging
import importlib.util
import shutil
from pathlib import Path
import sys
from datetime import datetime

if TYPE_CHECKING:
    from qdvc.repo import Repo

logger = logging.getLogger(__name__)


def checkout(
    repo: "Repo",
    query: str,
    version: str,
    download_files: bool,
    **kwargs: Any,
):
    # Checkout the query branch
    repo.git_repo.git.checkout(repo.QUERY_SEPARATOR.join([repo.QUERY_BRANCH_PREFIX, query, repo.QUERY_INIT]))

    # Rebase on version branch
    query_branch = repo.QUERY_SEPARATOR.join([repo.QUERY_BRANCH_PREFIX, query, version])
    branch_already_exists = any(r.name == query_branch for r in repo.git_repo.heads)
    if not branch_already_exists:
        repo.git_repo.git.branch(query_branch)
    repo.git_repo.git.checkout(query_branch)
    repo.git_repo.git.rebase(version)

    # Applies filtering
    p = Path(os.path.join(repo.qdvc_dir, repo.FILTER_FILE_NAME))
    spec = importlib.util.spec_from_file_location("filter", p)
    if not spec or not spec.loader:
        raise Exception("Filter file in qdvc was not found")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["filter"] = mod
    spec.loader.exec_module(mod)
    from filter import Query
    query = Query()
    new_paths = []
    for root, subdirs, files in os.walk(repo.QDVC_DATA_DIR):
        for f in files:
            fp = os.path.join(repo.root_dir, root, f)
            if query.filter(fp):  # type: ignore
                new_path = fp[len(repo.data_qdvc_dir) + 1 :]
                new_path = os.path.join(repo.root_dir, new_path)
                new_paths.append(new_path)
                if branch_already_exists:
                    if os.path.exists(new_path):
                        continue
                    else:
                        raise Exception("The query branch was already created and is now inconsistent in the results.")

                shutil.copy(fp, new_path)
    
    #  Download file if requested
    if download_files:
        repo.dvc_repo.checkout(targets=new_paths)

    # Add files and Commits branch
    if not branch_already_exists:
        repo.git_repo.git.add(new_paths)
        repo.git_repo.git.commit('-m', f"Queried on {datetime.today().strftime('%Y-%m-%d')}")

    # notifiy that user that if he's happy, he should push the branch
