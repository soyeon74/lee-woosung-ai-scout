"""Firestore-backed time-series CRUD for the Lee Woo-sung assignment."""
import hmac
import math
import os
from datetime import date
from statistics import mean
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field

from backend.services.firebase_service import get_firestore_client

router = APIRouter(prefix="/api/data", tags=["KBO 데이터 CRUD"])


class DataInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    date: date
    value: float = Field(ge=0, le=1000000, allow_inf_nan=False)
    memo: str = Field(default="", max_length=300)


def db():
    try:
        return get_firestore_client()
    except Exception as exc:
        # Credentials, filesystem paths and tokens must never appear in API errors.
        raise HTTPException(status_code=503, detail="Firestore 연결 불가: 서버 환경을 점검하세요.") from exc


def verify_admin(x_admin_key: str | None):
    key = os.getenv("DATA_ADMIN_KEY", "")
    if not key:
        raise HTTPException(status_code=503, detail="관리자 키(DATA_ADMIN_KEY)가 설정되지 않았습니다.")
    if not x_admin_key or not hmac.compare_digest(key, x_admin_key):
        raise HTTPException(status_code=401, detail="관리자 인증에 실패했습니다.")


def get_all_rows():
    rows = []
    for snapshot in db().collection("data").stream():
        raw = snapshot.to_dict() or {}
        raw_date = raw.get("date")
        raw_value = raw.get("value", raw.get("H"))
        if raw_date is None or raw_value is None:
            continue
        try:
            d = raw_date.isoformat()[:10] if hasattr(raw_date, "isoformat") else str(raw_date)[:10]
            date.fromisoformat(d)
            v = float(raw_value)
            if not math.isfinite(v):
                continue
        except (ValueError, TypeError, OverflowError):
            continue
        rows.append({"id": snapshot.id, "date": d, "value": v,
                     "memo": str(raw.get("memo") or raw.get("opponent") or "")[:300]})
    return sorted(rows, key=lambda r: (r["date"], r["id"]))


@router.get("/summary")
def read_summary():
    rows = get_all_rows()
    if not rows:
        return {"period": None, "count": 0, "metrics": None,
                "trend": "데이터 없음", "recent_count": 0, "recent_average": None}
    values = [r["value"] for r in rows]
    window = min(10, len(rows))
    recent = mean(values[-window:])
    previous = mean(values[-2*window:-window]) if len(rows) >= 2*window else None
    trend = "비교 불가" if previous is None else (
        "증가" if recent > previous else "감소" if recent < previous else "유지"
    )
    return {"period": {"start": rows[0]["date"], "end": rows[-1]["date"]},
            "count": len(rows),
            "metrics": {"total": sum(values), "average": mean(values),
                        "max": max(values), "min": min(values)},
            "trend": trend, "recent_count": window,
            "recent_average": recent, "previous_average": previous,
            "note": "기존 KBO 데이터에서 value는 경기별 안타(H) 수입니다. 이 평균은 타율이 아닙니다."}


@router.get("")
def read_data(limit: int = Query(default=105, ge=1, le=1000)):
    rows = get_all_rows()
    return {"count": min(len(rows), limit), "total": len(rows),
            "records": list(reversed(rows))[:limit]}


@router.post("", status_code=201)
def create_data(payload: DataInput, x_admin_key: Annotated[str | None, Header()] = None):
    verify_admin(x_admin_key)
    row = payload.model_dump(mode="json")
    ref = db().collection("data").document(str(uuid4()))
    ref.set(row)
    return {"id": ref.id, **row}


@router.put("/{id}")
def update_data(id: str, payload: DataInput, x_admin_key: Annotated[str | None, Header()] = None):
    verify_admin(x_admin_key)
    ref = db().collection("data").document(id)
    original = ref.get()
    if not original.exists:
        raise HTTPException(status_code=404, detail="데이터를 찾을 수 없습니다.")
    row = payload.model_dump(mode="json")
    original_data = original.to_dict() or {}
    # Keep old KBO fields consistent if the user edits an imported match.
    if "H" in original_data:
        if not row["value"].is_integer():
            raise HTTPException(status_code=422, detail="기존 경기의 안타(H)는 정수여야 합니다.")
        row["H"] = int(row["value"])
    ref.update(row)
    return {"id": id, **row}


@router.delete("/{id}")
def delete_data(id: str, x_admin_key: Annotated[str | None, Header()] = None):
    verify_admin(x_admin_key)
    ref = db().collection("data").document(id)
    if not ref.get().exists:
        raise HTTPException(status_code=404, detail="데이터를 찾을 수 없습니다.")
    ref.delete()
    return {"id": id, "deleted": True}
