import os
import sys
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

URL = os.environ.get("TRACKING_URL")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_alert(message, image_path=None):
    """Sends a text message and an optional screenshot to your Telegram app."""
    try:
        # Send the text alert first
        text_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(text_url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=10)
        
        # Send the screenshot photo if it exists
        if image_path and os.path.exists(image_path):
            photo_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
            with open(image_path, 'rb') as photo:
                requests.post(photo_url, data={"chat_id": TELEGRAM_CHAT_ID}, files={"photo": photo}, timeout=20)
    except Exception as e:
        print(f"Telegram error: {e}")

def check_firstcry_stock():
    # Set up invisible Chrome Browser with modern anti-bot evasion
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        print(f"Loading FirstCry: {URL}")
        driver.get(URL)
        
        # INCREASED WAIT TIME: GitHub Actions runners are slow. 
        # Waiting 10 seconds ensures all React/JavaScript pricing and stock data finishes loading.
        time.sleep(10) 
        
        # Take a screenshot so we know exactly what the bot is looking at
        screenshot_path = "debug_screenshot.png"
        driver.save_screenshot(screenshot_path)
        
        page_source = driver.page_source.lower()
        
        # 1. Check if we got blocked by a security screen
        if "access denied" in page_source or "captcha" in page_source or "cloudflare" in page_source:
            print("Status: Blocked by FirstCry security. No alert sent.")
            return

        # 2. VERY STRICT text check to avoid false positives
        if "out of stock" in page_source or "currently unavailable" in page_source or "sold out" in page_source:
            print("Status: Confirmed Out Of Stock.")
        else:
            # 3. Only alert if 'out of stock' is missing AND 'add to cart' is explicitly visible
            if "add to cart" in page_source:
                print("Status: POTENTIAL RESTOCK!")
                send_telegram_alert(
                    f"🚨 HOT WHEELS RESTOCK ALERT! 🚨\n\n'Add to Cart' found on the page! Look at the screenshot to verify, then check the link immediately:\n{URL}",
                    image_path=screenshot_path
                )
            else:
                print("Status: Page loaded, but couldn't find 'Add to Cart' or 'Out of Stock'.")

    except Exception as e:
        print(f"Error checking FirstCry: {e}")
    finally:
        driver.quit() # Always close the browser to free memory

if __name__ == "__main__":
    check_firstcry_stock()
    
