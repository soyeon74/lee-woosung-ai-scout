"""Firebase Admin app initialization using environment-managed credentials.

Guard initialization against parallel FastAPI requests during cold starts.
"""
import json
import os
from pathlib import Path
from threading import Lock

EXPECTED_PROJECT_ID = "lee-woosung-ai-scout"
_initialization_lock = Lock()


def get_firestore_client():
    # Import lazily so Windows enterprise policy blocking grpc does not stop /docs.
    import firebase_admin
    from firebase_admin import credentials, firestore

    # Parallel requests to /api/data and /api/data/summary may hit a cold
    # Render instance simultaneously. Firebase's get_app/initialize_app pair
    # must be serialized to prevent a duplicate-initialization race.
    with _initialization_lock:
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
