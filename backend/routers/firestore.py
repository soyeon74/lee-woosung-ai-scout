
from fastapi import APIRouter, HTTPException, Query
from google.api_core.exceptions import GoogleAPICallError

from backend.services.firebase_service import get_firestore_client

router = APIRouter(
    prefix="/api/firestore",
    tags=["Firestore 데이터"],
)

PLAYER_ID = "63260"
SEASON = 2025


@router.get("/records")
def read_firestore_records(
    limit: int = Query(default=105, ge=1, le=105)
):
    """Firestore에서 이우성 선수의 2025시즌 기록을 조회합니다."""

    try:
        db = get_firestore_client()

        documents = (
            db.collection("data")
            .where("player_id", "==", PLAYER_ID)
            .where("season", "==", SEASON)
            .stream()
        )

        records = []

        for doc in documents:
            record = doc.to_dict()
            record["document_id"] = doc.id
            records.append(record)

        records.sort(
            key=lambda item: str(item.get("date", "")),
            reverse=True,
        )

        return {
            "source": "firestore",
            "total": len(records),
            "count": min(limit, len(records)),
            "records": records[:limit],
        }

    except GoogleAPICallError as exc:
        raise HTTPException(
            status_code=503,
            detail="Firestore 데이터 조회에 실패했습니다.",
        ) from exc
