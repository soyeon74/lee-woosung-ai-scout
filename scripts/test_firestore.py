
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore

ROOT = Path(__file__).resolve().parents[1]
KEY_FILE = ROOT / "secrets" / "firebase-service-account.json"

print("[1] Firebase 인증키 확인")

if not KEY_FILE.is_file():
    raise FileNotFoundError(
        "Firebase 인증키 파일이 없습니다: "
        "secrets/firebase-service-account.json"
    )

print("KEY_FILE_OK")

print("[2] Firebase Admin SDK 초기화")

if not firebase_admin._apps:
    cred = credentials.Certificate(str(KEY_FILE))
    firebase_admin.initialize_app(cred)

print("FIREBASE_INIT_OK")

print("[3] Firestore 연결 테스트")

db = firestore.client()

# 실제 데이터 변경 없이 Firestore에 읽기 요청
test_ref = db.collection("_connection_test").document("check")
snapshot = test_ref.get()

print("FIRESTORE_CONNECTION_OK")
print("TEST_DOCUMENT_EXISTS:", snapshot.exists)
print("TEST_COMPLETE")
