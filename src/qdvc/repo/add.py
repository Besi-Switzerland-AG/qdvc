from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from qdvc.repo import Repo
    from qdvc.types import TargetType


def add(
    repo: "Repo",
    targets: "TargetType",
    recursive: bool = False,
    no_commit: bool = False,
    fname: str = None,
    to_remote: bool = False,
    **kwargs: Any,
):
    pass
