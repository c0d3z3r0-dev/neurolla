import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth

cred = credentials.Certificate(
    "firebase-admin.json"
)

firebase_admin.initialize_app(
    cred
)


def verify_google_token(id_token):
    decoded_token = auth.verify_id_token(
        id_token
    )

    return decoded_token