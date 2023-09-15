from enum import Enum
from typing import Callable

class NormativeAction():
    def __init__(self, name: str, action_fn: Callable, domain: Enum = 0):
        self.name = name
        self.action_fn = action_fn
        self.domain = domain

    