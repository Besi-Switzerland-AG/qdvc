import os
from qdvc.config import Config
from dvc.repo import Repo as DvcRepo


class Repo:
    QDVC_DIR = ".qdvc"

    from dvc.repo.add import add  # type: ignore[misc]

    def __init__(
        self,
        root_dir=".",
        uninitialized=False,
        config=None,
    ):
        self._uninitialized = uninitialized
        dvcRepo = DvcRepo(root_dir=root_dir, uninitialized=uninitialized)
        self.root_dir, self.dvc_dir, self.tmp_dir = dvcRepo._get_repo_dirs(
            root_dir=root_dir,
            fs=dvcRepo.fs,
            uninitialized=uninitialized,
            scm=dvcRepo.scm(),
        )
        self.qdvc_dir = os.path.join(self.root_dir, self.QDVC_DIR)
        self.git_dir = os.path.join(self.root_dir, ".git")
        self.config = Config(self.qdvc_dir, config=config)

    @staticmethod
    def init(root_dir=os.curdir, no_scm=False, force=False, subdir=False):
        from qdvc.repo.init import init

        return init(root_dir=root_dir, no_scm=no_scm, force=force, subdir=subdir)

    def __enter__(self) -> "Repo":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @classmethod
    def find_qdvc_dir(cls, root=None):
        root_dir = DvcRepo.find_root(root)
        return os.path.join(root_dir, cls.QDVC_DIR)
