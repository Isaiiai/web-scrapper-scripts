#!/usr/bin/env python3
"""
Web Scraper Script
Reads URLs from a CSV file, scrapes member data, and updates the CSV with extracted information.

Usage:
    python scraper.py --csv <path_to_csv> [--url-column <column_name>]
    
Example:
    python scraper.py --csv company_data.csv --url-column url
"""

import argparse
import csv
import time
import sys
from pathlib import Path
from typing import Dict, List, Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


# Authentication cookies for elitegln.com
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


def setup_driver(headless: bool = False) -> webdriver.Chrome:
    """Initialize and configure Chrome WebDriver."""
    options = Options()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver


def scrape_url(url: str, driver: webdriver.Chrome, debug: bool = False) -> Optional[str]:
    """
    Scrape a URL and return the page source HTML.
    
    Args:
        url: The URL to scrape
        driver: Selenium WebDriver instance
        debug: If True, save HTML to debug file
        
    Returns:
        HTML page source or None if scraping failed
    """
    wait = WebDriverWait(driver, 25)
    
    try:
        # Load base domain first
        base_domain = f"{url.split('/')[0]}//{url.split('/')[2]}"
        driver.get(base_domain)
        time.sleep(2)
        
        # Inject cookies if URL is from elitegln.com
        if "elitegln.com" in url:
            for cookie in COOKIES:
                driver.add_cookie(cookie)
        
        # Load the target URL
        driver.get(url)
        
        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(5)
        
        # Get page source
        html = driver.page_source
        
        # Save debug HTML if requested
        if debug:
            debug_file = f"debug_{int(time.time())}.html"
            with open(debug_file, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"  💾 Debug HTML saved to {debug_file}")
        
        return html
        
    except Exception as e:
        print(f"  ❌ Error scraping {url}: {str(e)}")
        return None


def extract_company_data(html: str) -> Dict[str, str]:
    """
    Extract structured company data from HTML using BeautifulSoup.
    
    Args:
        html: HTML page source
        
    Returns:
        Dictionary containing extracted company data
    """
    soup = BeautifulSoup(html, "lxml")
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


def read_csv(csv_path: str, url_column: str) -> List[Dict[str, str]]:
    """
    Read CSV file and return list of rows.
    
    Args:
        csv_path: Path to CSV file
        url_column: Name of column containing URLs
        
    Returns:
        List of dictionaries representing CSV rows
    """
    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def write_csv(csv_path: str, rows: List[Dict[str, str]], fieldnames: List[str]):
    """
    Write data to CSV file.
    
    Args:
        csv_path: Path to output CSV file
        rows: List of dictionaries to write
        fieldnames: List of column names
    """
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Scrape URLs from CSV and add extracted data back to the CSV"
    )
    parser.add_argument(
        "--csv",
        required=True,
        help="Path to CSV file containing URLs to scrape"
    )
    parser.add_argument(
        "--url-column",
        default="url",
        help="Name of the column containing URLs (default: 'url')"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Save debug HTML files for each scraped page"
    )
    parser.add_argument(
        "--output",
        help="Output CSV file path (default: overwrites input file)"
    )
    
    args = parser.parse_args()
    
    # Validate CSV file exists
    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"❌ Error: CSV file not found: {args.csv}")
        sys.exit(1)
    
    # Read CSV
    print(f"📖 Reading CSV file: {args.csv}")
    try:
        rows = read_csv(args.csv, args.url_column)
    except Exception as e:
        print(f"❌ Error reading CSV: {str(e)}")
        sys.exit(1)
    
    if not rows:
        print("⚠️  CSV file is empty")
        sys.exit(0)
    
    # Check if URL column exists
    if args.url_column not in rows[0]:
        print(f"❌ Error: Column '{args.url_column}' not found in CSV")
        print(f"Available columns: {', '.join(rows[0].keys())}")
        sys.exit(1)
    
    print(f"✅ Found {len(rows)} rows to process")
    
    # Initialize WebDriver
    print("🌐 Initializing Chrome WebDriver...")
    driver = setup_driver(headless=args.headless)
    
    # Track all fieldnames for final CSV
    all_fieldnames = set(rows[0].keys())
    
    try:
        # Process each row
        for idx, row in enumerate(rows, 1):
            url = row.get(args.url_column, "").strip()
            
            if not url:
                print(f"⏭️  Row {idx}: Skipping (no URL)")
                continue
            
            print(f"\n🔍 [{idx}/{len(rows)}] Scraping: {url}")
            
            # Scrape the URL
            html = scrape_url(url, driver, debug=args.debug)
            
            if html:
                # Extract data
                scraped_data = extract_company_data(html)
                
                if scraped_data:
                    print(f"  ✅ Extracted {len(scraped_data)} fields")
                    
                    # Merge scraped data into row
                    row.update(scraped_data)
                    all_fieldnames.update(scraped_data.keys())
                else:
                    print(f"  ⚠️  No data extracted from {url}")
            
            # Small delay between requests
            time.sleep(2)
        
    finally:
        # Clean up
        print("\n🧹 Closing browser...")
        driver.quit()
    
    # Write output CSV
    output_path = args.output if args.output else args.csv
    print(f"\n💾 Writing results to: {output_path}")
    
    # Ensure consistent column order
    fieldnames = sorted(all_fieldnames)
    write_csv(output_path, rows, fieldnames)
    
    print(f"✅ Done! Processed {len(rows)} rows")
    print(f"📄 Output saved to: {output_path}")


if __name__ == "__main__":
    main()
