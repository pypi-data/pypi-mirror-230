from typing import Any


class DirectResponseException(Exception):
    def __init__(self, message: Any):
        self.message = message
