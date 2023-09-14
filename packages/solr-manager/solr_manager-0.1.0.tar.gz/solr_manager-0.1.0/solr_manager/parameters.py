from typing import Any

from humps import camelize, decamelize


def parse_key(key: str):
    if "__" in key:
        key = ".".join(key.split("__"))

    return camelize(key)


def parse_value(value: Any):
    if isinstance(value, bool):
        return str(value).lower()

    return value


def parse_params(params: dict) -> dict:
    return {parse_key(key): parse_value(value) for key, value in params.items()}


def unparse_key(key: str):
    if "." in key:
        key = "__".join(key.split("."))

    return decamelize(key)


def unparse_value(value: Any):
    if value == "true":
        return True
    elif value == "false":
        return False

    return value


def unparse_params(params: dict) -> dict:
    return {unparse_key(key): unparse_value(value) for key, value in params.items()}
