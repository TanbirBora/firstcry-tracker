import os
import sys
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Fetch secrets from GitHub environment
URL = os.environ.get("TRACKING_URL")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_alert(message):
    """Sends a message to your Telegram app."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        # Short timeout so it doesn't hang
        requests.post(url, json=payload, timeout=10) 
        print("Telegram alert sent successfully!")
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

def get_robust_session():
    """Creates a bulletproof connection that retries on temporary web errors."""
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

def check_stock():
    session = get_robust_session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        print(f"Checking stock for: {URL}")
        response = session.get(URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        page_text = soup.get_text().lower()
        
        # Checking for common FirstCry out-of-stock phrases
        if "out of stock" in page_text or "sold out" in page_text:
            print("Status: Still out of stock.")
        else:
            print("Status: POTENTIAL RESTOCK!")
            send_telegram_alert(f"🚨 HOT WHEELS RESTOCK ALERT! 🚨\n\nIt looks like the item might be back in stock. Check immediately:\n{URL}")

    except Exception as e:
        print(f"An error occurred while checking the page: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if not all([URL, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        print("Error: Missing environment variables. Check GitHub Secrets.")
        sys.exit(1)
    
    check_stock()
  
