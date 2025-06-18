from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from selenium_stealth import stealth
import time
import smtplib
from email.mime.text import MIMEText

# ---------- CONFIG ----------
PRODUCT_URL = "https://www.popmart.com/us/pop-now/set/125"  # Set to LABUBU when needed
REFRESH_INTERVAL = 3  # seconds

# Email/SMS config
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = 'mozoa149@gmail.com'
EMAIL_PASSWORD = 'yvfxpjfvnwqcrszb'
TO_SMS = '9542255945@tmomail.net'
TO_EMAIL = 'mozoa149@gmail.com'

# ---------- ALERT FUNCTIONS ----------
def send_sms():
    msg = MIMEText("🚨 LABUBU Set is in stock and added to your cart!")
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = TO_SMS
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print("📲 SMS alert sent!")
    except Exception as e:
        print("❌ SMS failed:", e)

def send_email():
    msg = MIMEText("LABUBU Set of 6 is in stock and was added to your cart!")
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = TO_EMAIL
    msg['Subject'] = "LABUBU In Stock!"
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print("📧 Email alert sent!")
    except Exception as e:
        print("❌ Email failed:", e)

# ---------- BROWSER SETUP ----------
def build_driver():
    print("🚀 Launching Chrome...")
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = uc.Chrome(options=options, headless=False, use_subprocess=True)

    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="MacIntel",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True)
    return driver

# ---------- PRODUCT FLOW ----------
def try_add_to_cart(driver):
    try:
        print("🔍 Checking availability...")
        driver.get(PRODUCT_URL)
        time.sleep(2)

        # Try multi-box flow
        try:
            print("🕵️ Looking for 'Buy Multiple Boxes' button...")
            multi_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Buy Multiple Boxes')]"))
            )
            print("📦 Scrolling to 'Buy Multiple Boxes' button...")
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", multi_button)
            time.sleep(1)

            if multi_button.is_enabled():
                print("✅ Clicking 'Buy Multiple Boxes'...")
                driver.execute_script("arguments[0].click();", multi_button)
            else:
                print("⚠️ Button found but not clickable.")
                return False

            # Wait for popup and click 'Select all' label (which toggles the checkbox)
            print("⏳ Waiting for 'Select all' checkbox label...")
            select_all_label = WebDriverWait(driver, 6).until(
                EC.element_to_be_clickable((By.XPATH, "//label[contains(., 'Select all ')]"))
            )
            print("✅ Clicking 'Select all' label...")
            driver.execute_script("arguments[0].click();", select_all_label)
            time.sleep(1)


            # Click "Add to bag"
            add_button = WebDriverWait(driver, 6).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Add to bag')]"))
            )
            print("🛒 Clicking 'Add to bag'...")
            add_button.click()
            return True

        except Exception as e:
            print("⚠️ Multi-box flow error:")
            import traceback
            traceback.print_exc()

        # Fallback: Try standard Add to Cart
        print("🔁 Trying standard Add to Cart...")
        add_buttons = driver.find_elements(By.XPATH, '//button[contains(text(), "Add to Cart")]')
        for btn in add_buttons:
            if btn.is_enabled():
                print("✅ Clicking standard 'Add to Cart'...")
                btn.click()
                return True

    except Exception as e:
        print("❌ General error during attempt:")
        import traceback
        traceback.print_exc()
    return False


# ---------- MAIN ----------
def main():
    driver = build_driver()
    driver.get(PRODUCT_URL)
    input("⏸️ Log in manually, then press ENTER to continue...")

    print("🕐 Monitoring product page...")
    while True:
        if try_add_to_cart(driver):
            send_sms()
            send_email()
            break
        time.sleep(REFRESH_INTERVAL)

    driver.quit()

if __name__ == "__main__":
    main()
