# Web Scraper Script

A unified Python script that scrapes URLs from a CSV file and adds the extracted data back to the CSV.

## Features

- ✅ Reads URLs from CSV file
- ✅ Scrapes web pages using Selenium (handles JavaScript-rendered content)
- ✅ Extracts structured data using BeautifulSoup
- ✅ Supports authentication cookies (pre-configured for elitegln.com)
- ✅ Updates CSV with scraped data
- ✅ Command-line interface with multiple options
- ✅ Debug mode to save HTML for troubleshooting

## Installation

### 1. Activate Virtual Environment (if using one)

```bash
source venv/bin/activate
```

### 2. Install Dependencies

Using pip:
```bash
pip3 install -r requirements.txt
```

Or install individually:
```bash
pip3 install selenium webdriver-manager beautifulsoup4 lxml
```

### 3. Verify Installation

```bash
python3 scraper.py --help
```

## Usage

### Basic Usage

```bash
python3 scraper.py --csv urls_to_scrape.csv
```

This will:
1. Read URLs from the `url` column in `urls_to_scrape.csv`
2. Scrape each URL
3. Extract company data
4. Update the same CSV file with the extracted data

### Advanced Options

```bash
# Specify a different URL column name
python3 scraper.py --csv data.csv --url-column website_url

# Run in headless mode (no browser window)
python3 scraper.py --csv data.csv --headless

# Save debug HTML files for each page
python3 scraper.py --csv data.csv --debug

# Save output to a different file
python3 scraper.py --csv input.csv --output output.csv

# Combine multiple options
python3 scraper.py --csv data.csv --url-column link --headless --debug --output results.csv
```

### Command-Line Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--csv` | Yes | - | Path to CSV file containing URLs |
| `--url-column` | No | `url` | Name of the column containing URLs |
| `--headless` | No | `False` | Run browser in headless mode |
| `--debug` | No | `False` | Save debug HTML files |
| `--output` | No | (input file) | Output CSV file path |

## CSV Format

### Input CSV

Your CSV file should have at least one column containing URLs:

```csv
url,company_id
https://www.elitegln.com/directory/members/136964,1
https://www.elitegln.com/directory/members/123456,2
```

### Output CSV

The script will add all extracted fields to the CSV:

```csv
url,company_id,company_name,location,member_id,phone,website,address,...
https://www.elitegln.com/directory/members/136964,1,CARGO SOLUTIONS LOGISTICS PVT LTD,"Coimbatore, India",136964,+91 422 232 4289,http://www.cargosolutionslogistics.com/,"No. 284, Sri Vigneswara Complex...",...
```

## Extracted Fields

The script extracts the following fields (when available):

- `company_name` - Company name
- `location` - City and country
- `member_id` - Member ID
- `proudly_enrolled_since` - Enrollment date
- `membership_expires` - Expiration date
- `company_profile` - Company description
- `address` - Full address
- `phone` - Phone number
- `website` - Website URL
- `title` - Contact person title
- Additional fields based on page structure

## Authentication

The script includes pre-configured authentication cookies for `elitegln.com`. To update cookies or add authentication for other sites:

1. Open `scraper.py`
2. Modify the `COOKIES` list at the top of the file
3. Add your authentication cookies

Example:
```python
COOKIES = [
    {
        "name": "session_id",
        "value": "your_session_value",
        "domain": "example.com",
        "path": "/"
    }
]
```

## Troubleshooting

### No data extracted

1. Run with `--debug` flag to save HTML files
2. Check the debug HTML file to see what was loaded
3. Verify the page structure matches the extraction logic
4. Update the `extract_company_data()` function if needed

### Browser issues

1. Make sure Chrome is installed
2. Try running without `--headless` to see what's happening
3. Check if cookies are still valid

### Column not found error

Make sure your CSV has the correct column name, or specify it with `--url-column`:

```bash
python3 scraper.py --csv data.csv --url-column your_column_name
```

## Example Workflow

1. Create a CSV with URLs:
```csv
url
https://www.elitegln.com/directory/members/136964
https://www.elitegln.com/directory/members/123456
```

2. Run the scraper:
```bash
python3 scraper.py --csv urls.csv --output results.csv
```

3. Check the results in `results.csv`

## Notes

- The script includes a 2-second delay between requests to be respectful to servers
- Pages wait up to 25 seconds for content to load
- Failed scrapes are logged but don't stop the entire process
- The output CSV will have all columns from both input and scraped data
