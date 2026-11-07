
from pathlib import Path
import math

import firebase_admin
import pandas as pd
from firebase_admin import credentials, firestore

ROOT = Path(__file__).resolve().parents[1]

KEY_FILE = ROOT / "secrets" / "firebase-service-account.json"
DATA_FILE = ROOT / "data" / "raw" / "lee_woosung_2025_daily.csv"

PLAYER_ID = "63260"
SEASON = 2025


def clean_value(value):
    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        value = value.item()

    if isinstance(value, float) and not math.isfinite(value):
        return None

    return value


def main():
    print("[1] 입력 파일 확인")

    if not KEY_FILE.is_file():
        raise FileNotFoundError("Firebase 인증키 파일이 없습니다.")

    if not DATA_FILE.is_file():
        raise FileNotFoundError("KBO 원본 CSV 파일이 없습니다.")

    df = pd.read_csv(DATA_FILE, dtype={"opponent": str})

    required = ["date", "PA", "AB", "H"]

    if not all(col in df.columns for col in required):
        raise ValueError("필수 컬럼이 누락되었습니다.")

    if df["date"].isna().any():
        raise ValueError("날짜 결측값이 있습니다.")

    if df["date"].duplicated().any():
        raise ValueError("중복 날짜가 있습니다.")

    df["date"] = pd.to_datetime(
        df["date"], errors="raise"
    ).dt.strftime("%Y-%m-%d")

    if not df["date"].str.startswith("2025-").all():
        raise ValueError("2025년 이외의 기록이 포함되었습니다.")

    if len(df) != 105:
        raise ValueError("기록 수가 105건이 아닙니다.")

    if (
        int(df["PA"].sum()),
        int(df["AB"].sum()),
        int(df["H"].sum())
    ) != (337, 300, 75):
        raise ValueError("시즌 합계 검증 실패")

    print("CSV_VALIDATION_OK")

    print("[2] Firebase 연결")

    if not firebase_admin._apps:
        cred = credentials.Certificate(str(KEY_FILE))
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    collection = db.collection("data")

    print("FIREBASE_CONNECTION_OK")

    print("[3] Firestore 업로드")

    # 날짜별 고정 ID로 재실행 시 중복 문서 생성 방지
    batch = db.batch()

    for row in df.to_dict(orient="records"):
        date = row["date"]
        document_id = f"{PLAYER_ID}_{SEASON}_{date}"

        record = {
            key: clean_value(value)
            for key, value in row.items()
        }

        record["player_id"] = PLAYER_ID
        record["player_name"] = "이우성"
        record["season"] = SEASON

        doc_ref = collection.document(document_id)
        batch.set(doc_ref, record)

    batch.commit()

    print("UPLOAD_COMPLETE:", len(df))

    print("[4] 업로드 검증")

    saved_records = []

    for row in df.to_dict(orient="records"):
        document_id = f"{PLAYER_ID}_{SEASON}_{row['date']}"
        snapshot = collection.document(document_id).get()

        if not snapshot.exists:
            raise ValueError(
                f"Firestore 문서 누락: {document_id}"
            )

        saved_records.append(snapshot.to_dict())

    saved_df = pd.DataFrame(saved_records)

    saved_pa = int(saved_df["PA"].sum())
    saved_ab = int(saved_df["AB"].sum())
    saved_h = int(saved_df["H"].sum())

    print("SAVED_ROWS:", len(saved_df))
    print("SAVED_PA:", saved_pa)
    print("SAVED_AB:", saved_ab)
    print("SAVED_H:", saved_h)

    if (
        len(saved_df),
        saved_pa,
        saved_ab,
        saved_h
    ) != (105, 337, 300, 75):
        raise ValueError("Firestore 저장 검증 실패")

    print("FIRESTORE_UPLOAD_OK")


if __name__ == "__main__":
    main()
