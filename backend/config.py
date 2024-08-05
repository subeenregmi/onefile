import yaml
import secrets
import socket


def getConfig(filename: str) -> dict[str, str]:
    """ Gets the config.yaml file and turns it into a python
    dictionary.

    Args:
        filename: the filename for the config.yaml

    Returns:
        A  dictionary consisting of the config.yaml file
    """
    with open(filename, "r") as f:
        data = yaml.load(f, yaml.Loader)

    data = checkSecret(data)
    data = checkHost(data)

    return data


def checkSecret(data: dict[str, str]) -> dict[str, str]:
    """ Checks if secret is present in data, if not it will generate it

    Args:
        data: The current yaml file as a dictionary

    Returns:
        The 'data' dictionary with the secret_key
    """
    if "secret_key" not in data or data["secret_key"] is None:
        data["secret_key"] = secrets.token_hex()

    return data


def checkHost(data: dict[str, str]) -> dict[str, str]:
    """ Checks if host is present in data, if not will use localhost

    Args:
        data: The current yaml file as a dictionary

    Returns:
        The 'data' dictionary with the host
    """

    if "host" not in data or data["host"] is None:
        data["host"] = "localhost"

    return data


def checkRefreshFiles(data: dict[str, str]) -> dict[str, str]:
    """ Checks if refresh_files is present in the config file, if
    not will user 300 seconds or 5 minutes.

    Args:
        data: The current yaml file as a dictionary

    Returns:
        The 'data' dictionary with the refreshfile value

    """

    if "refresh_files" not in data or data["refresh_files"] is None:
        data["host"] = 300

    return data
