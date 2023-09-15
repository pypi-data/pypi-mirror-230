import pyrebase
import requests

from trail.libconfig import libconfig


def retrieve_jwt_token(email, password):
    firebase = pyrebase.initialize_app(
        {
            "apiKey": libconfig.FIREBASE_API_KEY,
            "authDomain": libconfig.FIREBASE_AUTH_DOMAIN,
            "databaseURL": "THIS_IS_NOT_USED",
            "storageBucket": "THIS_IS_NOT_USED",
        }
    )
    auth = firebase.auth()

    try:
        user = auth.sign_in_with_email_and_password(email, password)
    except requests.exceptions.HTTPError as e:
        if e.errno.response.status_code == 400:  # type: ignore
            raise Exception("Invalid credentials") from None

        raise e

    return user["idToken"]
