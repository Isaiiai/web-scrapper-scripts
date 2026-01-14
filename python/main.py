from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

URL = "https://www.elitegln.com/directory/members/136964"

COOKIES = [
    {
        "name": ".ASPXAUTH",
        "value": "D2C2A06FD4FDFB9C7D8C961FD86A6CA2621C85FE4DD43EE4F40E7B22B89EC7B2DC0A29D0307ACDEB2CDEE6CCDBDECE40C0B98A5A0F38701487201DB3FFEA374C4E98D4808B6C94714517A5C26D9A815F2D57B1CC6770D7C34DB2E77504A9CA6A",
        "domain": "www.elitegln.com",
        "path": "/"
    },
    {
        "name": "wca",
        "value": "False",
        "domain": "www.elitegln.com",
        "path": "/"
    },
    {
        "name": "__RequestVerificationToken",
        "value": "edbm041wcxqex4mmftuzqjo2",
        "domain": "www.elitegln.com",
        "path": "/"
    }
]


def scrape_member():
    options = Options()
    # ❌ disable headless while debugging
    # options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    wait = WebDriverWait(driver, 25)

    # 1️⃣ Load base domain
    driver.get("https://www.elitegln.com")
    time.sleep(2)

    # 2️⃣ Inject cookies
    for cookie in COOKIES:
        driver.add_cookie(cookie)

    # 3️⃣ Load protected member page
    driver.get(URL)

    # 4️⃣ Wait for JS rendering
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(5)

    # 5️⃣ Dump HTML for debugging
    with open("debug.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)

    data = {}

    # 6️⃣ Check for iframes
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    if iframes:
        driver.switch_to.frame(iframes[0])

    # 7️⃣ Extract visible label/value pairs
    elements = driver.find_elements(By.XPATH, "//*[self::div or self::li][.//text()]")

    for el in elements:
        try:
            texts = [t.strip() for t in el.text.split("\n") if t.strip()]
            if len(texts) == 2:
                key = texts[0].lower().replace(" ", "_")
                value = texts[1]
                if len(key) < 40 and len(value) < 200:
                    data[key] = value
        except:
            continue

    # 8️⃣ Fallback: dump all visible text
    if not data:
        print("\n⚠️ No structured data found — dumping visible text:\n")
        print(driver.find_element(By.TAG_NAME, "body").text)

    driver.quit()
    return data


if __name__ == "__main__":
    result = scrape_member()

    if result:
        print("\n--- MEMBER DATA ---")
        for k, v in result.items():
            print(f"{k}: {v}")
    else:
        print("\n❌ No data extracted — check debug.html")