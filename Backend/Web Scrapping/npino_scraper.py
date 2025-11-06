# npino_scraper.py
import re, time, os, requests, pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ------------------------------------------------------------
# Selenium setup
# ------------------------------------------------------------
def setup_driver():
    options = Options()
    # comment this next line if you want to SEE the browser window
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def clean(t):
    return re.sub(r"\s+", " ", t or "").strip()

# ------------------------------------------------------------
# Scrape npino.com (dynamic)
# ------------------------------------------------------------
def scrape_npino(npi):
    url = f"https://npino.com/npi/{npi}/"
    print(f"\n🔍 Loading provider data for NPI: {npi} ...")

    driver = setup_driver()
    driver.get(url)

    # Wait for Practice Address or at least Name section
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Practice')]"))
        )
    except:
        time.sleep(5)

    # Scroll down to trigger lazy-loads
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)

    data = {
        "NPI": npi, "Name": None, "Credential": None, "Gender": None,
        "Specialty": None, "Organization": None, "Practice_Address": None,
        "Mailing_Address": None, "Phone": None, "Enumeration_Date": None,
        "Last_Update": None, "Medicare_Status": None, "Source": "npino.com"
    }

    # --- Name ---
    h1 = soup.find("h1")
    if h1:
        raw = re.sub(r"^NPI\s*\d+\s*", "", h1.get_text(strip=True))
        data["Name"] = re.split(r"\s+in\s+|\s+-\s+", raw)[0]

    # --- Table rows ---
    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) != 2:
            continue
        key = clean(cells[0].text)
        val = clean(cells[1].text)
        if not key or not val:
            continue

        if "Credential" in key:
            data["Credential"] = val
        elif "Gender" in key:
            data["Gender"] = val
        elif "Primary Taxonomy" in key or "Specialty" in key:
            data["Specialty"] = val
        elif "Organization" in key:
            data["Organization"] = val
        elif "Practice Address" in key:
            data["Practice_Address"] = val
        elif "Mailing Address" in key:
            data["Mailing_Address"] = val
        elif "Phone" in key:
            data["Phone"] = val
        elif "Enumeration Date" in key:
            data["Enumeration_Date"] = val
        elif "Last Update" in key:
            data["Last_Update"] = val
        elif "Medicare" in key:
            data["Medicare_Status"] = val

    # --- Fallbacks from visible text ---
    if not data["Gender"]:
        if "Male" in text: data["Gender"] = "Male"
        elif "Female" in text: data["Gender"] = "Female"

    if not data["Phone"]:
        m = re.search(r"\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}", text)
        if m: data["Phone"] = m.group(0)

    # --- Practice / Mailing sections (h3/h4 blocks) ---
    for head in soup.find_all(["h3", "h4"]):
        title = head.get_text(strip=True)
        if "Practice" in title and "Address" in title:
            addr_block = []
            sib = head.find_next_sibling()
            while sib and sib.name not in ["h3", "h4"]:
                addr_block.append(clean(sib.get_text(" ", strip=True)))
                sib = sib.find_next_sibling()
            if addr_block:
                data["Practice_Address"] = " ".join(addr_block)
        elif "Mailing" in title and "Address" in title:
            addr_block = []
            sib = head.find_next_sibling()
            while sib and sib.name not in ["h3", "h4"]:
                addr_block.append(clean(sib.get_text(" ", strip=True)))
                sib = sib.find_next_sibling()
            if addr_block:
                data["Mailing_Address"] = " ".join(addr_block)

    return data

# ------------------------------------------------------------
# Fetch missing fields from official NPPES API
# ------------------------------------------------------------
def fill_from_nppes(data):
    npi = data["NPI"]
    url = f"https://npiregistry.cms.hhs.gov/api/?number={npi}&version=2.1"
    try:
        res = requests.get(url, timeout=10)
        js = res.json()
        if js.get("results"):
            info = js["results"][0]
            basic = info.get("basic", {})
            addr = info.get("addresses", [{}])[0]
            taxonomy = info.get("taxonomies", [{}])[0]

            # Fill blanks only
            data["Name"] = data["Name"] or f"{basic.get('first_name','')} {basic.get('last_name','')}".strip()
            data["Credential"] = data["Credential"] or basic.get("credential")
            data["Gender"] = data["Gender"] or basic.get("gender")
            data["Specialty"] = data["Specialty"] or taxonomy.get("desc")
            if not data["Practice_Address"]:
                data["Practice_Address"] = f"{addr.get('address_1','')}, {addr.get('city','')}, {addr.get('state','')} {addr.get('postal_code','')}"
            data["Phone"] = data["Phone"] or addr.get("telephone_number")
            if not data["Organization"]:
                data["Organization"] = basic.get("organization_name") or "N/A"
            data["Source"] += " + NPPES API"
    except Exception as e:
        print(f"⚠️  NPPES fallback failed: {e}")
    return data

# ------------------------------------------------------------
# Utility
# ------------------------------------------------------------
def display_summary(d):
    print("\n================= 🩺 Provider Summary =================")
    print(f"👤 Name: {d['Name'] or 'Not found'}")
    print(f"📛 NPI: {d['NPI']}")
    print(f"🎓 Credential: {d['Credential'] or 'Not found'}")
    print(f"⚧ Gender: {d['Gender'] or 'Not found'}")
    print(f"💼 Specialty: {d['Specialty'] or 'Not found'}")
    print(f"🏢 Organization: {d['Organization'] or 'Not found'}")
    print(f"📍 Practice Address: {d['Practice_Address'] or 'Not found'}")
    print(f"📬 Mailing Address: {d['Mailing_Address'] or 'Not found'}")
    print(f"📞 Phone: {d['Phone'] or 'Not found'}")
    print(f"🗓️ Enumeration Date: {d['Enumeration_Date'] or 'Not found'}")
    print(f"🔄 Last Update: {d['Last_Update'] or 'Not found'}")
    print(f"💊 Medicare Status: {d['Medicare_Status'] or 'Not found'}")
    print(f"🌐 Source: {d['Source']}")
    print("========================================================\n")

def save_csv(d):
    os.makedirs("outputs", exist_ok=True)
    file = "outputs/npi_results.csv"
    df = pd.DataFrame([d])
    if os.path.exists(file):
        old = pd.read_csv(file)
        df = pd.concat([old, df], ignore_index=True)
    df.to_csv(file, index=False)
    print(f"✅ Data saved to {file}\n")

# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():
    print("=== 🩺 Hybrid NPI Scraper (npino + NPPES API) ===")
    npi = input("Enter the provider's NPI number: ").strip()
    data = scrape_npino(npi)
    # Fill blanks from API if needed
    if any(v in [None, "Not found", ""] for k, v in data.items() if k not in ["Source","NPI"]):
        data = fill_from_nppes(data)
    display_summary(data)
    save_csv(data)
    print("🎉 Done! Full data scraped & validated.\n")

if __name__ == "__main__":
    main()
