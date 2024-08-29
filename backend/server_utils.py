from enum import Enum


class Privilege(Enum):
    ADMIN = 1
    UPLOADER = 2
    USER = 3


class Responses(Enum):
    SUCCESS = 1
    EMPTY_NAME = 2
    PRIVILEGE_ERROR = 3
    TAKEN_FILE_NAME = 4
    FILE_NOT_EXISTS = 5


def createResp(resp_c: Responses) -> dict[str, str]:
    """
    Creates a dictionary representing the stringified response code.
    """
    return {"RESP_CODE": resp_c.name}


def checkPrivilege(priv: Privilege, needed_priv: Privilege) -> bool:
    """
    Checks the privilege against the needed privilege.
    """

    if not priv or not needed_priv:
        return False

    if priv.value > needed_priv.value:
        return False

    return True
