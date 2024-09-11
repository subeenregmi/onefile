from enum import Enum


class Privilege(Enum):
    ADMIN = 1
    UPLOADER = 2
    USER = 3
    UNKNOWN = 99

    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN


class Responses(Enum):
    SUCCESS = 1
    EMPTY_NAME = 2
    PRIVILEGE_ERROR = 3
    TAKEN_FILE_NAME = 4
    FILE_NOT_EXISTS = 5
    EMPTY_USERNAME = 6
    TAKEN_USERNAME = 7
    EMPTY_PASSWORD = 8
    UNSPECIFIED_PRIVILEGE = 9
    USER_NOT_FOUND = 10
    EMPTY_PAGE_NAME = 11
    PAGE_NOT_FOUND = 12
    PARAMETER_ERROR = 13
    FILE_NOT_UPLOADED = 14


def createResp(resp_c: Responses) -> dict[str, str]:
    """
    Creates a dictionary representing the stringified response code.
    """

    resp = {"RESP_CODE": resp_c.name}

    if resp_c is Responses.SUCCESS:
        return resp, 200

    return resp, 403


def checkPrivilege(priv: Privilege, needed_priv: Privilege) -> bool:
    """
    Checks the privilege against the needed privilege.
    """

    if not priv or not needed_priv:
        return False

    if priv.value > needed_priv.value:
        return False

    return True
