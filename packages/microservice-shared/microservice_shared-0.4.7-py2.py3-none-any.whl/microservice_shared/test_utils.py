"""
Test cases utility functions.
"""
from typing import Any, Dict

import jwt
from decouple import Csv

from .test_config import (
    LOGIN_ENDPOINT,
    SIGNUP_ENDPOINT,
    USER_LOGIN_TEST_DATA,
    USER_SIGNUP_TEST_DATA,
    RECRUITER_LOGIN_TEST_DATA,
    RECRUITER_SIGNUP_TEST_DATA,
)


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
    data = (
        RECRUITER_SIGNUP_TEST_DATA
        if "recruiters" in config("DJANGO_SETTINGS_MODULE")
        else USER_SIGNUP_TEST_DATA
    )

    response = client.post(
        SIGNUP_ENDPOINT,
        data=data,
        headers=get_authorization_header(config),
    )

    return response


def make_login_request(client: Any, config) -> Any:
    """
    Make Login Request ans Return response
    """
    data = (
        RECRUITER_LOGIN_TEST_DATA
        if "recruiters" in config("DJANGO_SETTINGS_MODULE")
        else USER_LOGIN_TEST_DATA
    )

    response = client.post(
        LOGIN_ENDPOINT,
        data=data,
        headers=get_authorization_header(config),
    )

    return response
