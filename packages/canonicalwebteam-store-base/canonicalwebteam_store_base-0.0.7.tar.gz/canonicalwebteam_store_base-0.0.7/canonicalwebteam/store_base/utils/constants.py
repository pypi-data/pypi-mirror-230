import os

LOGIN_URL = os.getenv("LOGIN_URL", "https://login.ubuntu.com")
LOGIN_LAUNCHPAD_TEAM = os.getenv(
    "LOGIN_LAUNCHPAD_TEAM",
    "canonical-webmonkeys",
)
