# Quick Start Guide

## Setup (One-time)

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

## Usage

### Option 1: Use the sample CSV

Run the scraper with the provided sample CSV:

```bash
python3 scraper.py --csv urls_to_scrape.csv --output results.csv
```

### Option 2: Create your own CSV

1. Create a CSV file with a `url` column:
   ```csv
   url
   https://www.elitegln.com/directory/members/136964
   https://www.elitegln.com/directory/members/123456
   ```

2. Run the scraper:
   ```bash
   python3 scraper.py --csv your_file.csv
   ```

### Option 3: Update existing CSV

If you already have a CSV with URLs in a different column:

```bash
python3 scraper.py --csv company_data.csv --url-column website_url
```

## Common Commands

```bash
# Basic scraping
python3 scraper.py --csv urls.csv

# Headless mode (no browser window)
python3 scraper.py --csv urls.csv --headless

# Debug mode (saves HTML files)
python3 scraper.py --csv urls.csv --debug

# Save to different file
python3 scraper.py --csv input.csv --output output.csv
```

## What Gets Extracted?

The scraper extracts:
- Company name
- Location (city, country)
- Member ID
- Enrollment dates
- Company profile/description
- Address
- Phone number
- Website
- Contact title
- And more...

## Troubleshooting

**Problem:** `ModuleNotFoundError: No module named 'selenium'`
- **Solution:** Run `pip3 install -r requirements.txt`

**Problem:** No data extracted
- **Solution:** Run with `--debug` flag and check the HTML file

**Problem:** Column 'url' not found
- **Solution:** Use `--url-column your_column_name` to specify the correct column

For more details, see [README.md](README.md)
