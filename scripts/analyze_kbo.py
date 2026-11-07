
from pathlib import Path
import pandas as pd

SOURCE = Path("data/raw/lee_woosung_2025_daily.csv")
OUTPUT = Path("data/processed")
OUTPUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(SOURCE, dtype={"opponent": str})
df["date"] = pd.to_datetime(df["date"], errors="raise")
df = df.sort_values("date").reset_index(drop=True)

required = [
    "date", "opponent", "PA", "AB", "H",
    "2B", "3B", "HR", "BB", "HBP", "SO"
]

assert all(c in df.columns for c in required), "필수 컬럼 누락"
assert len(df) == 105, "기록 수 불일치"
assert df["date"].is_unique, "날짜 중복"
assert df["date"].dt.year.eq(2025).all(), "연도 불일치"

numeric = ["PA", "AB", "H", "2B", "3B", "HR", "BB", "HBP", "SO"]

assert df[numeric].notna().all().all(), "수치 결측"
assert df[numeric].ge(0).all().all(), "음수 기록"
assert df["H"].le(df["AB"]).all(), "안타 > 타수"
assert df["AB"].le(df["PA"]).all(), "타수 > 타석"
assert (df["2B"] + df["3B"] + df["HR"]).le(df["H"]).all(), "장타 수 오류"

assert (
    int(df["PA"].sum()),
    int(df["AB"].sum()),
    int(df["H"].sum())
) == (337, 300, 75), "시즌 합계 불일치"

# 원본의 0타수 기록은 보존
df["month"] = df["date"].dt.strftime("%Y-%m")
df["single_hits"] = df["H"] - df["2B"] - df["3B"] - df["HR"]
df["total_bases"] = (
    df["single_hits"]
    + 2 * df["2B"]
    + 3 * df["3B"]
    + 4 * df["HR"]
)

# 타수 0이면 타율은 계산 불가
df["game_avg"] = (
    df["H"] / df["AB"].replace(0, float("nan"))
)

# 최근 5개/10개 날짜별 기록의 합계로 타율 계산
for window in [5, 10]:
    hits = df["H"].rolling(window, min_periods=window).sum()
    at_bats = df["AB"].rolling(window, min_periods=window).sum()
    df[f"avg_last_{window}"] = (
        hits / at_bats.replace(0, float("nan"))
    )

# 월별 합계에서 타율 재계산
monthly = (
    df.groupby("month", as_index=False)
    .agg(
        records=("date", "size"),
        PA=("PA", "sum"),
        AB=("AB", "sum"),
        H=("H", "sum"),
        HR=("HR", "sum"),
        SO=("SO", "sum"),
        BB=("BB", "sum")
    )
)
monthly["AVG"] = monthly["H"] / monthly["AB"].replace(
    0, float("nan")
)

# 상대팀별 합계
opponents = (
    df.groupby("opponent", as_index=False)
    .agg(
        records=("date", "size"),
        PA=("PA", "sum"),
        AB=("AB", "sum"),
        H=("H", "sum"),
        HR=("HR", "sum")
    )
)
opponents["AVG"] = opponents["H"] / opponents["AB"].replace(
    0, float("nan")
)

df["date"] = df["date"].dt.strftime("%Y-%m-%d")

df.to_csv(
    OUTPUT / "daily_analysis.csv",
    index=False,
    encoding="utf-8-sig"
)
monthly.to_csv(
    OUTPUT / "monthly_summary.csv",
    index=False,
    encoding="utf-8-sig"
)
opponents.to_csv(
    OUTPUT / "opponent_summary.csv",
    index=False,
    encoding="utf-8-sig"
)

print("[DATA VALIDATION]")
print("ROWS:", len(df))
print("DATE_RANGE:", df["date"].iloc[0], "~", df["date"].iloc[-1])
print("PA:", int(df["PA"].sum()))
print("AB:", int(df["AB"].sum()))
print("H:", int(df["H"].sum()))
print("AVG:", f"{df['H'].sum() / df['AB'].sum():.3f}")
print("ZERO_AB_ROWS:", int(df["AB"].eq(0).sum()))

print("\n[MONTHLY SUMMARY]")
print(monthly.to_string(index=False))

print("\n[OUTPUT FILES]")
for path in sorted(OUTPUT.glob("*.csv")):
    print(path)

print("\nANALYSIS_OK")
