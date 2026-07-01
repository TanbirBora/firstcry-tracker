import os
import sys
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

URL = os.environ.get("TRACKING_URL")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}")

def check_firstcry_stock():
    # Set up invisible Chrome Browser
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Runs invisible
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        print(f"Loading FirstCry: {URL}")
        driver.get(URL)
        
        # Give FirstCry's Javascript time to load the actual data
        time.sleep(5) 
        
        # Check the page text AFTER Javascript has rendered
        page_source = driver.page_source.lower()
        
        # FirstCry uses specific phrasing for out of stock items
        if "out of stock" in page_source or "currently unavailable" in page_source:
            print("Status: Confirmed Out Of Stock by FirstCry.")
        else:
            # Secondary check: Does the 'Add to Cart' button exist?
            # FirstCry typically uses divs with text like "ADD TO CART"
            if "add to cart" in page_source:
                print("Status: ADD TO CART BUTTON FOUND!")
                send_telegram_alert(f"🚨 HOT WHEELS RESTOCK ALERT! 🚨\n\n'Add to Cart' is active on FirstCry! Check immediately:\n{URL}")
            else:
                print("Status: Unclear. Could not verify stock status or block detected.")

    except Exception as e:
        print(f"Error checking FirstCry: {e}")
    finally:
        driver.quit() # Always close the browser to free memory

if __name__ == "__main__":
    check_firstcry_stock()
    
