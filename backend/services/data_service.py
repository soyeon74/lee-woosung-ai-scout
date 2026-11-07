
from pathlib import Path
import json
import math

import pandas as pd
from fastapi import HTTPException

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data/processed/daily_analysis.csv"
SUMMARY_FILE = ROOT / "data/processed/analysis_summary.json"


def clean_value(value):
    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        return value.item()

    if isinstance(value, float) and not math.isfinite(value):
        return None

    return value


def get_records(limit: int = 105):
    if not DATA_FILE.is_file():
        raise HTTPException(
            status_code=503,
            detail="분석 데이터 파일이 없습니다."
        )

    df = pd.read_csv(DATA_FILE)

    if "date" not in df.columns:
        raise HTTPException(
            status_code=500,
            detail="날짜 컬럼이 없습니다."
        )

    df = df.sort_values("date", ascending=False)
    df = df.head(limit)

    return [
        {key: clean_value(value) for key, value in row.items()}
        for row in df.to_dict(orient="records")
    ]


def get_summary():
    if not SUMMARY_FILE.is_file():
        raise HTTPException(
            status_code=503,
            detail="통계 요약 파일이 없습니다."
        )

    with SUMMARY_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)
