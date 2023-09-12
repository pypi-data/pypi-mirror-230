# pylint: disable=too-few-public-methods
"""
This module contains regular expression patterns for validation purposes in the project.
"""


class CompanyNameConstants:
    """
    Constants related to company names.

    These constants define the validation pattern, error message, error code,
    and help text for company names in the application.

    Attributes:
        PATTERN (str): The regular expression pattern to allow letters, numbers,
            and spaces in company names.
        MESSAGE (str): The error message to display when the company name does
            not match the validation pattern.
        CODE (str): The error code associated with invalid company names.
        HELP_TEXT (str): The help text to display for the company name field.
    """

    PATTERN = r"^[a-zA-Z0-9\s]+$"
    MESSAGE = "Company name can only contain letters, numbers, and spaces."
    CODE = "invalid_company_name"
    HELP_TEXT = "The name of the company."


class ContactNameConstants:
    """
    Constants related to contact names.

    These constants define the validation pattern, error message, error code,
    and help text for contact names in the application.

    Attributes:
        PATTERN (str): The regular expression pattern to allow letters, spaces,
            hyphens, and apostrophes in contact names.
        MESSAGE (str): The error message to display when the contact name does
            not match the validation pattern.
        CODE (str): The error code associated with invalid contact names.
        HELP_TEXT (str): The help text to display for the contact name field.
    """

    PATTERN = r"^[a-zA-Z\s\-\'\.]+$"
    MESSAGE = "Contact name can only contain letters, spaces, hyphens, and apostrophes."
    CODE = "invalid_contact_name"
    HELP_TEXT = "The name of the contact person."


class MobileNumberConstants:
    """
    Constants related to mobile numbers.

    These constants define the validation pattern, error message, error code,
    and help text for mobile numbers in the application.

    Attributes:
        PATTERN (str): The regular expression pattern to match mobile numbers
            starting with a plus sign (+) followed by one or more digits.
        MESSAGE (str): The error message to display when the mobile number does
            not match the validation pattern.
        CODE (str): The error code associated with invalid mobile numbers.
        HELP_TEXT (str): The help text to display for the mobile number field.
    """

    PATTERN = r"^\+\d+$"
    MESSAGE = (
        "Invalid mobile number format. Enter a valid mobile number starting "
        "with + and containing only numbers."
    )
    CODE = "invalid_mobile_number"
    HELP_TEXT = "The unique mobile number for authentication."


class EmailFieldConstants:
    """
    Constants related to the email field.

    These constants define the help text for the email field in the application.

    Attributes:
        HELP_TEXT (str): The help text for the email field.
    """

    HELP_TEXT = "The unique email address for authentication."


class PasswordFieldConstants:
    """
    Constants related to the password field.

    These constants define the help text for the password field in the application.

    Attributes:
        HELP_TEXT (str): The help text for the password field.
    """

    HELP_TEXT = "The account password."


class MobileVerifiedFieldConstants:
    """
    Constants related to the mobile verified field.

    These constants define the help text for the mobile verified field in the application.

    Attributes:
        HELP_TEXT (str): The help text for the mobile verified field.
    """

    HELP_TEXT = "Indicates if the mobile number is verified."


class EmailVerifiedFieldConstants:
    """
    Constants related to the email verified field.

    These constants define the help text for the email verified field in the application.

    Attributes:
        HELP_TEXT (str): The help text for the email verified field.
    """

    HELP_TEXT = "Indicates if the email address is verified."


class IsActiveFieldConstants:
    """
    Constants related to the is active field.

    These constants define the help text for the is active field in the application.

    Attributes:
        HELP_TEXT (str): The help text for the is active field.
    """

    HELP_TEXT = "Indicates if the account is active."


class FullNameFieldConstants:
    """
    Constants related to the full name field.

    These constants define the help text for the full name field in the application.

    Attributes:
        HELP_TEXT (str): The help text for the full name field.
    """

    PATTERN = r"^[a-zA-Z\s\-\'\.]+$"
    MESSAGE = "Full name can only contain letters, spaces, hyphens, and apostrophes."
    CODE = "invalid_full_name"
    HELP_TEXT = "Your full name."
