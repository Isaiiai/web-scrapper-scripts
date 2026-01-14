from bs4 import BeautifulSoup
import csv

INPUT_HTML = "debug.html"
OUTPUT_CSV = "company_data.csv"


def extract_company_data(html_file):
    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml")

    data = {}

    # --- Company name, city, country ---
    company_div = soup.select_one(".company_name .company")
    if company_div:
        data["company_name"] = company_div.get_text(strip=True)

        parent_text = company_div.parent.get_text(" ", strip=True)
        location = parent_text.replace(data["company_name"], "").strip(" ,")
        data["location"] = location

    # --- Member ID ---
    member_id = soup.select_one(".compid span")
    if member_id:
        data["member_id"] = member_id.get_text(strip=True).replace("ID:", "").strip()

    # --- Enrollment dates ---
    labels = soup.select(".member_expire_lalel")
    values = soup.select(".member_expire_value")

    for label, value in zip(labels, values):
        key = label.get_text(strip=True).lower().replace(" ", "_").replace(":", "")
        data[key] = value.get_text(strip=True)

    # --- Profile description ---
    profile_td = soup.select_one(".profile_table td")
    if profile_td:
        data["company_profile"] = profile_td.get_text("\n", strip=True)

    # --- Address ---
    address = soup.select_one(".profile_headline:contains('Address') + div span")
    if address:
        data["address"] = address.get_text(" ", strip=True)

    # --- Contact details ---
    rows = soup.select(".profile_row")
    for row in rows:
        label = row.select_one(".profile_label")
        value = row.select_one(".profile_val")

        if label and value:
            key = label.get_text(strip=True).lower().replace(" ", "_").replace(":", "")
            val = value.get_text(" ", strip=True)

            if "members only" not in val.lower():
                data[key] = val

    return data


def write_csv(data, output_file):
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        writer.writeheader()
        writer.writerow(data)


if __name__ == "__main__":
    company_data = extract_company_data(INPUT_HTML)
    write_csv(company_data, OUTPUT_CSV)

    print("✅ Data extracted successfully")
    print(f"📄 Saved to {OUTPUT_CSV}")
