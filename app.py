import os
import time as time_module
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from flask import Flask, request, jsonify
from datetime import datetime, time, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class BookingService:
    def __init__(self):
        self.driver = None
        self.wait = None

    def setup_driver(self, headless=False):
        """Setup Chrome driver with appropriate options"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

        try:
            # Use WebDriver Manager to automatically handle ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 20)
            logger.info("Chrome driver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {str(e)}")
            raise

    def loginAndBook(self, username, password, initial_url, logged_in_url, court_number):
        """Login And Book"""
        try:
            logger.info("Starting login process")
            self.driver.get(initial_url)
            # Wait for any cookie banner to appear

            self.accept_cookies()
            accept_cookies = self.driver.find_element(By.XPATH, "//*[@id='onetrust-accept-btn-handler']")
            accept_cookies.click()
            time_module.sleep(2)

            login_link = self.driver.find_element(By.XPATH, "//*[@id='root']/nav/div/div/ul/li[3]/button/span")
            login_link.click()
            time_module.sleep(2)
            # Wait for page to load
            login_popup = self.find_login_button()
            login_popup.find_element(By.XPATH, "//*[@id='username']").send_keys(username)
            login_popup.find_element(By.XPATH, "//*[@id='password']").send_keys(password)
            login_popup.find_element(By.XPATH, "/html/body/div[5]/div[3]/form/div[3]/button").click()

            #timeToWait = (milliseconds_until_10pm() - 10) / 1000
            #print("what is time to wait", timeToWait)
            #print("milliseconds _until 10PM", milliseconds_until_10pm())
            #time_module.sleep(timeToWait)
            time_module.sleep(10)
            self.driver.get(logged_in_url)

            booking_popup = self.find_booking_button()
            dropdown_input = booking_popup.find_element(By.XPATH, "/html/body/div[5]/div[3]/div[1]/div/div[2]/div[1]/div/div")
            dropdown_input.click()


            wait = WebDriverWait(self.driver, 10)
            options = wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "[id^='react-select-2-option']")
            ))

            # Select first option that doesn't start with "FULL-"
            for option in options:
                option_text = option.text.strip()
                if not option.text.startswith("FULL-"):
                    if option_text == court_number:
                        option.click()
                        break

            self.driver.find_element(By.XPATH, "/html/body/div[5]/div[3]/div[2]/button[1]/span").click()

            # Click Confirm button
            confirm_button = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='root']/main/div/div/div[1]/div/div[4]/div/div/div[3]/button"))
            )
            # confirm_button.click()

            return True

        except TimeoutException:
            logger.error("Login timeout - elements not found")
            return False
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False

    def accept_cookies(self):
        """Accept cookies with multiple fallback selectors"""
        cookie_selectors = [
            "//*[@id='onetrust-accept-btn-handler']",
            "//button[contains(text(), 'Accept')]",
            "//button[contains(text(), 'Accept All')]",
            "//button[contains(text(), 'Accept Cookies')]",
            "//button[contains(@class, 'accept')]",
            "//*[@id='accept-cookies']",
            "//*[@class='onetrust-accept-btn-handler']",
            "//button[@data-testid='accept-cookies']"
        ]

        try:
            # Wait for any cookie banner to appear
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'cookie') or contains(@id, 'cookie') or contains(@class, 'onetrust')]"))
            )

            for selector in cookie_selectors:
                try:
                    element = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    element.click()
                    logger.info(f"Successfully clicked cookie accept button with selector: {selector}")
                    return True
                except TimeoutException:
                    continue

            logger.warning("No cookie accept button found with any selector")
            return False

        except Exception as e:
            logger.error(f"Error handling cookies: {str(e)}")
            return False


    def find_login_button(self, timeout=10):
        """Find login/submit button with multiple selectors"""
        login_button_selectors = [
            "//*[@id='username']",
            "//button[@type='submit']",
            "//input[@type='submit']"
        ]

        for selector in login_button_selectors:
            try:
                element = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                if element.is_displayed():
                    logger.info(f"Found login button with selector: {selector}")
                    return element
            except TimeoutException:
                continue

        logger.error("Could not find login button")
        return None

    def find_booking_button(self, timeout=10):
        """Find login/submit button with multiple selectors"""
        booking_button_selectors = [
            "/html/body/div[5]/div[3]/div[1]/div/div[2]/div[1]/div/div",
            "//button[@type='submit']",
            "//input[@type='submit']",

        ]

        for selector in booking_button_selectors:
            try:
                element = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                if element.is_displayed():
                    logger.info(f"Found booking button with selector: {selector}")
                    return element
            except TimeoutException:
                continue

        logger.error("Could not find booking button")
        return None


    def make_booking(self, booking_data):
        """Complete booking process"""
        try:
            self.setup_driver(headless=False)

            # Login & Book
            if not self.loginAndBook(booking_data['username'], booking_data['password'],booking_data['initial_url'],booking_data['logged_in_url'],booking_data['court_number']):
                return {"success": False, "error": "Login failed"}

        except Exception as e:
            logger.error(f"Booking process failed: {str(e)}")
            return {"success": False, "error": str(e)}

        finally:
            if self.driver:
                self.driver.quit()


def milliseconds_until_10pm():
    now = datetime.now()
    ten_pm_today = datetime.combine(now.date(), time(22, 0))

    if now < ten_pm_today:
        delta = ten_pm_today - now
    else:
        ten_pm_tomorrow = ten_pm_today + timedelta(days=1)
        delta = ten_pm_tomorrow - now

    return int(delta.total_seconds() * 1000)  # Convert seconds to milliseconds


# Flask API for Make.com integration
@app.route('/book', methods=['POST'])
def book_court():
    """API endpoint for Make.com to trigger booking"""
    try:
        booking_data = request.json

        # Validate required fields
        required_fields = ['username', 'password', 'initial_url', "logged_in_url", 'court_number']
        for field in required_fields:
            if field not in booking_data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Create bot instance and make booking
        bot = BookingService()
        result = bot.make_booking(booking_data)

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API documentation"""
    return jsonify({
        "message": "Booking API",
        "endpoints": {
            "POST /book": "Make a booking",
            "GET /health": "Health check"
        },
        "example_payload": {
            "username": "BET1868995",
            "password": "W3ek3ndw@rri0rs4",
            "initial_url": "https://bookings.better.org.uk/location/canons-leisure-centre",
            "logged_in_url": "https://bookings.better.org.uk/location/canons-leisure-centre/badminton-40min/2025-06-22/by-time/slot/09:40-10:20",
            "court_number": "Court 3"
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)