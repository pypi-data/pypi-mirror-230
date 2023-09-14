from enum import Enum


class SlackErrors(str, Enum):
    INVALID_AUTH = 'invalid_auth'
