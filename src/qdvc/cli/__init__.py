from qdvc.exceptions import QdvcException


class QdvcParserError(QdvcException):
    """Base class for CLI parser errors."""

    def __init__(self):
        super().__init__("parser error")
