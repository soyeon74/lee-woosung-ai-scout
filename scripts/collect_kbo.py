
from pathlib import Path
from datetime import datetime
import csv
import re

from playwright.sync_api import sync_playwright

URL = (
    "https://www.koreabaseball.com/Record/Player/"
    "HitterDetail/Daily.aspx?playerId=63260"
)

YEAR = 2025
PLAYER_ID = "63260"

YEAR_SELECT = "#cphContents_cphContents_cphContents_ddlYear"
SERIES_SELECT = "#cphContents_cphContents_cphContents_ddlSeries"

COLUMNS = [
    "date", "opponent", "AVG1", "PA", "AB", "R", "H",
    "2B", "3B", "HR", "RBI", "SB", "CS", "BB",
    "HBP", "SO", "GDP", "AVG2"
]

NUMERIC_COLUMNS = [
    "PA", "AB", "R", "H", "2B", "3B", "HR",
    "RBI", "SB", "CS", "BB", "HBP", "SO", "GDP"
]

OUT = Path("data/raw")
OUT.mkdir(parents=True, exist_ok=True)


def parse_table(table):
    rows = table.locator("tr")

    header = [
        re.sub(r"\s+", " ", x).strip()
        for x in rows.nth(0).locator("th, td").all_inner_texts()
    ]

    if len(header) != len(COLUMNS):
        raise ValueError(f"열 개수 오류: {header}")

    month_text = header[0]
    match = re.match(r"^(\d{1,2})월$", month_text)

    if not match:
        raise ValueError(f"월 제목 오류: {month_text}")

    month = int(match.group(1))
    records = []
    monthly_total = None

    for i in range(1, rows.count()):
        cells = [
            x.strip()
            for x in rows.nth(i).locator("th, td").all_inner_texts()
        ]

        # KBO 월별 합계 행에는 상대팀 열이 없음
        if cells and cells[0] == "합계":
            if len(cells) == len(COLUMNS) - 1:
                cells.insert(1, "")

            if len(cells) != len(COLUMNS):
                raise ValueError(
                    f"{month}월 합계 행 열 개수 오류: {cells}"
                )

            monthly_total = dict(zip(COLUMNS, cells))
            continue

        if len(cells) != len(COLUMNS):
            raise ValueError(
                f"{month}월 {i}행 열 개수 오류: {cells}"
            )

        if not re.fullmatch(r"\d{2}\.\d{2}", cells[0]):
            raise ValueError(f"날짜 형식 오류: {cells[0]}")

        date = datetime.strptime(
            f"{YEAR}.{cells[0]}", "%Y.%m.%d"
        ).strftime("%Y-%m-%d")

        if int(cells[0][:2]) != month:
            raise ValueError(f"월 불일치: {date}")

        record = dict(zip(COLUMNS, cells))
        record["date"] = date

        for col in NUMERIC_COLUMNS:
            record[col] = int(record[col])

        for col in ["AVG1", "AVG2"]:
            record[col] = (
                None if record[col] == "-"
                else float(record[col])
            )

        records.append(record)

    if monthly_total is None:
        raise ValueError(f"{month}월 합계 행 없음")

    return month, records, monthly_total


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(locale="ko-KR")

        try:
            print("KBO 공식 기록실 접속 중...")

            page.goto(
                URL,
                wait_until="domcontentloaded",
                timeout=60000
            )

            page.locator(YEAR_SELECT).wait_for()

            print(f"{YEAR}년 선택 중...")

            page.locator(YEAR_SELECT).select_option(str(YEAR))

            page.wait_for_function(
                """(selector) =>
                    document.querySelector(selector)?.value === '2025'
                """,
                arg=YEAR_SELECT,
                timeout=30000
            )

            page.locator(SERIES_SELECT).select_option("0")

            # 연도 선택 후 실제 표 데이터가 갱신될 시간을 확보
            page.wait_for_timeout(2000)

            page.wait_for_function(
                """() => {
                    const tables = document.querySelectorAll(
                        'table.tbl.tt.mb5'
                    );
                    return tables.length > 0 &&
                        document.querySelector(
                            '#cphContents_cphContents_cphContents_ddlYear'
                        )?.value === '2025';
                }""",
                timeout=30000
            )

            tables = page.locator("table.tbl.tt.mb5")

            print("월별 기록표 개수:", tables.count())

            all_records = []
            monthly_summaries = []

            for i in range(tables.count()):
                month, records, total = parse_table(tables.nth(i))

                all_records.extend(records)
                monthly_summaries.append(
                    (month, records, total)
                )

            if not all_records:
                raise ValueError("수집된 날짜별 기록이 없습니다.")

            if len({r["date"] for r in all_records}) != len(all_records):
                raise ValueError("중복 날짜가 발견되었습니다.")

            all_records.sort(key=lambda x: x["date"])

            print("\n[월별 합계 검증]")

            for month, records, total in monthly_summaries:
                for col in NUMERIC_COLUMNS:
                    calculated = sum(r[col] for r in records)
                    expected = int(total[col])

                    if calculated != expected:
                        raise ValueError(
                            f"{month}월 {col} 불일치: "
                            f"수집={calculated}, KBO={expected}"
                        )

                monthly_ab = sum(r["AB"] for r in records)
                monthly_h = sum(r["H"] for r in records)

                print(
                    f"{month:02d}월: {len(records)}행 "
                    f"AB={monthly_ab} "
                    f"H={monthly_h} 검증 OK"
                )

            total_pa = sum(r["PA"] for r in all_records)
            total_ab = sum(r["AB"] for r in all_records)
            total_h = sum(r["H"] for r in all_records)

            average = total_h / total_ab if total_ab else None

            print("\n[2025시즌 수집 결과]")
            print("기록 행 수:", len(all_records))
            print("타석 PA:", total_pa)
            print("타수 AB:", total_ab)
            print("안타 H:", total_h)
            print(
                "타율 AVG:",
                f"{average:.3f}" if average is not None else "-"
            )

            # 사용자가 제공한 KBO 2025시즌 기록과 대조
            if (total_pa, total_ab, total_h) != (337, 300, 75):
                raise ValueError(
                    "기존 KBO 기록과 시즌 합계 불일치: "
                    f"PA={total_pa}, AB={total_ab}, H={total_h}"
                )

            if len(all_records) < 100:
                raise ValueError(
                    f"최소 100개 기록 조건 미충족: "
                    f"{len(all_records)}개"
                )

            output_file = OUT / "lee_woosung_2025_daily.csv"

            with output_file.open(
                "w",
                newline="",
                encoding="utf-8-sig"
            ) as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=COLUMNS
                )
                writer.writeheader()
                writer.writerows(all_records)

            print("\nCSV 저장:", output_file)
            print("COLLECTION_OK")

        finally:
            browser.close()


if __name__ == "__main__":
    main()
