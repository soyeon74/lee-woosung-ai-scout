"""Firebase Admin app initialization using environment-managed credentials."""
import json
import os
from pathlib import Path

EXPECTED_PROJECT_ID = "lee-woosung-ai-scout"


def get_firestore_client():
    # Import lazily so Windows enterprise policy blocking grpc does not stop /docs.
    import firebase_admin
    from firebase_admin import credentials, firestore

    try:
        app = firebase_admin.get_app()
    except ValueError:
        json_value = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "").strip()
        credential_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
        if json_value:
            credential = credentials.Certificate(json.loads(json_value))
        elif credential_path and Path(credential_path).is_file():
            credential = credentials.Certificate(credential_path)
        else:
            raise RuntimeError("Firebase credentials are missing")
        app = firebase_admin.initialize_app(credential, {"projectId": EXPECTED_PROJECT_ID})
    if app.project_id != EXPECTED_PROJECT_ID:
        raise RuntimeError("Firebase project mismatch")
    return firestore.client(app=app)
