from enum import Enum


class Responses(Enum):
    SUCCESS = 1
    EMPTY_NAME = 2
    PRIVILEGE_ERROR = 3
    TAKEN_FILE_NAME = 4
    FILE_NOT_EXISTS = 5


def create_resp(resp_c: Responses) -> dict[str, str]:
    """
    Creates a dictionary representing the stringified response code.
    """
    return {"RESP_CODE": resp_c.name}
