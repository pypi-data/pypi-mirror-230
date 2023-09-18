"""
JWT Utilities

This module provides utility functions for verifying JWT tokens.
"""

import jwt

from decouple import Csv


def verify_token(config, access_token):  # type: ignore
    """
    Verify the JWT token's authenticity and decode its payload.

    Args:
        config (dict): Configurations.
        access_token (str): The JWT access token to be verified.

    Returns:
        dict or Exception:
            The decoded token payload if the token is valid,
            Exception if invalid.
    """
    try:
        decoded_token = jwt.decode(
            access_token,
            config("JWT_SIGNING_KEY"),
            algorithms=config("JWT_ALGORITHM", cast=Csv()),
            audience=config("JWT_AUDIENCE", cast=Csv()),
        )
        return decoded_token
    except (
        jwt.InvalidAudienceError,
        jwt.ExpiredSignatureError,
        jwt.InvalidTokenError,
    ) as error:
        return error
    except jwt.PyJWTError as error:
        return error
