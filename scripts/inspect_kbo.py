from pathlib import Path
from playwright.sync_api import sync_playwright

URL = (
    "https://www.koreabaseball.com/Record/Player/"
    "HitterDetail/Daily.aspx?playerId=63260"
)

OUTPUT = Path("data/raw")
OUTPUT.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    page = browser.new_page(
        viewport={"width": 1440, "height": 900},
        locale="ko-KR"
    )

    print("KBO 페이지 접속 중...")

    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(3000)

    print("페이지 제목:", page.title())
    print("현재 URL:", page.url)

    selects = page.locator("select")

    print("\n[연도 및 선택 메뉴 검사]")

    for i in range(selects.count()):
        select = selects.nth(i)

        print(f"\nSELECT {i}")
        print("ID:", select.get_attribute("id"))
        print("NAME:", select.get_attribute("name"))

        options = select.locator("option")

        for j in range(min(options.count(), 30)):
            option = options.nth(j)
            print(
                option.get_attribute("value"),
                option.inner_text()
            )

    tables = page.locator("table")

    print("\n[HTML 표 검사]")
    print("표 개수:", tables.count())

    for i in range(min(tables.count(), 10)):
        table = tables.nth(i)

        print(f"\nTABLE {i}")
        print("ID:", table.get_attribute("id"))
        print("CLASS:", table.get_attribute("class"))

        rows = table.locator("tr")

        print("행 개수:", rows.count())

        for j in range(min(rows.count(), 3)):
            print(rows.nth(j).inner_text()[:300])

    page.screenshot(
        path=str(OUTPUT / "kbo_page_inspection.png"),
        full_page=True
    )

    print("\n진단 스크린샷 저장 완료")
    print("INSPECTION_OK")

    browser.close()