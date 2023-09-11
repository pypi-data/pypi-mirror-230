"""
Test cases utility functions.
"""
from typing import Any, Dict

import jwt
from decouple import Csv

from .test_config import SIGNUP_ENDPOINT, USER_SIGNUP_TEST_DATA


def generate_test_token(config) -> str:
    """
    Get the access token by making a request to the token endpoint.

    Returns:
        str: The access token.
    """
    return jwt.encode(
        {"aud": config("JWT_AUDIENCE", cast=Csv())},
        config("JWT_SIGNING_KEY"),
        algorithm=config("JWT_ALGORITHM"),
    )


def get_authorization_header(config) -> Dict[str, str]:
    """
    Get Authorization Header
    """
    access_token = generate_test_token(config)
    return {config("JWT_HEADER"): f"{config('JWT_PREFIX')} {access_token}"}


def make_signup_request(client: Any, config) -> Any:
    """
    Make Signup Request ans Return response
    """
    response = client.post(
        SIGNUP_ENDPOINT,
        data=USER_SIGNUP_TEST_DATA,
        headers=get_authorization_header(config),
    )

    return response
