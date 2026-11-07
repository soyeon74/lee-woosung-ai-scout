
from pathlib import Path
import json

import matplotlib.pyplot as plt
import pandas as pd

BASE = Path("data/processed")
FIGURES = Path("reports/figures")
FIGURES.mkdir(parents=True, exist_ok=True)

daily = pd.read_csv(BASE / "daily_analysis.csv")
monthly = pd.read_csv(BASE / "monthly_summary.csv")
opponents = pd.read_csv(BASE / "opponent_summary.csv")

daily["date"] = pd.to_datetime(daily["date"])
daily = daily.sort_values("date").reset_index(drop=True)

# 원본 데이터와 분석 결과 재검증
assert len(daily) == 105, "기록 수 불일치"
assert daily["date"].is_unique, "중복 날짜 발견"
assert int(daily["PA"].sum()) == 337, "타석 합계 오류"
assert int(daily["AB"].sum()) == 300, "타수 합계 오류"
assert int(daily["H"].sum()) == 75, "안타 합계 오류"

assert int(monthly["AB"].sum()) == 300, "월별 타수 오류"
assert int(monthly["H"].sum()) == 75, "월별 안타 오류"

season_avg = daily["H"].sum() / daily["AB"].sum()

# 1. 최근 5개/10개 기록 이동 타율 그래프
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(
    daily["date"],
    daily["avg_last_5"],
    label="Last 5 records",
    alpha=0.65
)
ax.plot(
    daily["date"],
    daily["avg_last_10"],
    label="Last 10 records",
    linewidth=2
)
ax.axhline(
    season_avg,
    linestyle="--",
    label=f"Season AVG ({season_avg:.3f})"
)

ax.set_title("Lee Woo-sung | 2025 Batting Average Trend")
ax.set_xlabel("Date")
ax.set_ylabel("Batting Average")
ax.legend()
ax.grid(alpha=0.25)
fig.autofmt_xdate()
fig.tight_layout()
fig.savefig(
    FIGURES / "batting_average_trend.png",
    dpi=160
)
plt.close(fig)

# 2. 월별 타율과 타수 그래프
fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(monthly["month"], monthly["AVG"])
ax.set_title("Monthly Batting Average | 2025")
ax.set_xlabel("Month")
ax.set_ylabel("Batting Average")
ax.set_ylim(0, 1.05)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.2)
fig.tight_layout()
fig.savefig(
    FIGURES / "monthly_batting_average.png",
    dpi=160
)
plt.close(fig)

# 3. 상대팀별 타율 그래프
sorted_opponents = opponents.sort_values("AVG")
fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(
    sorted_opponents["opponent"],
    sorted_opponents["AVG"]
)
ax.set_title("Batting Average by Opponent | 2025")
ax.set_xlabel("Batting Average")
ax.grid(axis="x", alpha=0.2)
fig.tight_layout()
fig.savefig(
    FIGURES / "opponent_batting_average.png",
    dpi=160
)
plt.close(fig)

# AI가 사용할 수 있는 통계 요약
last10 = daily.tail(10)
last10_ab = int(last10["AB"].sum())
last10_h = int(last10["H"].sum())

summary = {
    "player": "이우성",
    "player_id": "63260",
    "season": 2025,
    "source": (
        "https://www.koreabaseball.com/Record/Player/"
        "HitterDetail/Daily.aspx?playerId=63260"
    ),
    "data_points": int(len(daily)),
    "period": {
        "start": daily["date"].min().strftime("%Y-%m-%d"),
        "end": daily["date"].max().strftime("%Y-%m-%d")
    },
    "season": {
        "PA": int(daily["PA"].sum()),
        "AB": int(daily["AB"].sum()),
        "H": int(daily["H"].sum()),
        "HR": int(daily["HR"].sum()),
        "BB": int(daily["BB"].sum()),
        "SO": int(daily["SO"].sum()),
        "AVG": round(float(season_avg), 4)
    },
    "recent_10_records": {
        "records": 10,
        "AB": last10_ab,
        "H": last10_h,
        "AVG": (
            round(last10_h / last10_ab, 4)
            if last10_ab > 0 else None
        )
    },
    "monthly": monthly.to_dict(orient="records"),
    "by_opponent": opponents.to_dict(orient="records"),
    "limitations": [
        "일자별 기록은 날짜 단위이며 반드시 경기 단위와 같지는 않음",
        "최근 10개 기록은 최근 10일이 아니라 기록이 있는 최근 10개 날짜",
        "타수 0인 날짜의 타율은 계산하지 않음",
        "희생플라이 자료가 없어 정확한 출루율과 OPS는 계산하지 않음",
        "표본이 작은 월이나 상대팀의 타율은 해석에 주의"
    ]
}

# JSON 구조에서 season 키가 중복되지 않도록
# 연도는 season_year로 구분
summary["season_year"] = summary.pop("season") if False else 2025

output = BASE / "analysis_summary.json"
with output.open("w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print("[ANALYSIS SUMMARY]")
print("DATA_POINTS:", len(daily))
print("SEASON_AVG:", f"{season_avg:.3f}")
print("LAST_10_AB:", last10_ab)
print("LAST_10_H:", last10_h)
print(
    "LAST_10_AVG:",
    f"{last10_h / last10_ab:.3f}" if last10_ab else "-"
)
print("MONTHS:", len(monthly))
print("OPPONENTS:", len(opponents))
print("SUMMARY_FILE:", output)
print("FIGURES:", len(list(FIGURES.glob("*.png"))))
print("REPORT_BUILD_OK")
