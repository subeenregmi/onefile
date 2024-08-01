import yaml
import secrets


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

    # If secret_key is not in the yaml file
    if "secret_key" not in data or data["secret_key"] is None:
        data["secret_key"] = secrets.token_hex()

    return data
