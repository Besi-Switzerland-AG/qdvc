"""Exceptions raised by the qdvc."""


class QdvcException(Exception):
    """Base class for all dvc exceptions."""

    def __init__(self, msg, *args):
        assert msg
        self.msg = msg
        super().__init__(msg, *args)


class NotQdvcRepoError(QdvcException):
    """Thrown if a directory is not a QDVC repo"""
