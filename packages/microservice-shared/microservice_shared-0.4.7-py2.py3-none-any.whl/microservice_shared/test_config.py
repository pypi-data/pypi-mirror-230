"""
Test configuration module.
"""
SIGNUP_ENDPOINT = "/api/v1/signup/"
LOGIN_ENDPOINT = "/api/v1/login/"
RECRUITER_SIGNUP_TEST_DATA = {
    "data": {
        "type": "RecruiterSignup",
        "attributes": {
            "company_name": "Findmyjobz",
            "contact_name": "Testuser",
            "mobile": "+919999999999",
            "email": "xyz@gmail.com",
            "password": "ABCD@123!",
            "confirm_password": "ABCD@123!",
        },
    }
}
USER_SIGNUP_TEST_DATA = {
    "data": {
        "type": "UserSignup",
        "attributes": {
            "full_name": "Findmyjobz",
            "mobile": "+919999999999",
            "email": "xyz@gmail.com",
            "password": "ABCD@123!",
            "confirm_password": "ABCD@123!",
        },
    }
}
RECRUITER_LOGIN_TEST_DATA = {
    "data": {
        "type": "RecruiterLogin",
        "attributes": {
            "email": "xyz@gmail.com",
            "password": "ABCD@123!",
        },
    }
}
USER_LOGIN_TEST_DATA = {
    "data": {
        "type": "UserLogin",
        "attributes": {
            "email": "xyz@gmail.com",
            "password": "ABCD@123!",
        },
    }
}
