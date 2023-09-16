from enum import Enum

class NormType(Enum):
    PROHIBITION = 0
    PERMISSION = 1
    OBLIGATION = 2

class DeadlineType(Enum):
    BEFORE_CYCLE = 0
    AFTER_CYCLE = 1
    BEFORE_STEP = 2
    AFTER_STEP = 3
    BEFORE_TIME = 4
    AFTER_TIME = 5

class NormativeActionStatus(Enum):
    NOT_REGULATED = 0
    ALLOWED = 1
    FORBIDDEN = 2
    INVIOLABLE = 100

class NormIssuer(Enum):
    SELF = 0
    SOCIETY = 1
    ORGANIZATION = 2