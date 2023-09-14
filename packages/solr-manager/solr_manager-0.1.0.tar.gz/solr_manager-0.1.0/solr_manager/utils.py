from humps import decamelize


def decamelize_keys(data: dict) -> dict:
    """Decamelize keys of a dictionary.

    Humps `decamelize` does not support setting the depth of the decamelization, so we
    have to do it manually."""
    return {decamelize(key): value for key, value in data.items()}
