import requests

from xprompt.constants import BACKEND_ENDPOINT


def login(user_email: str, password: str):
    try:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "accept": "application/json",
        }
        response = requests.post(
            f"{BACKEND_ENDPOINT}/token",
            headers=headers,
            data={"username": user_email, "password": password},
        )

        return response.json()

    except Exception:
        raise
