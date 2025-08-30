import logging
import random
import time
from selenium import webdriver
from selenium.common import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from zillow import ZillowClone

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/112.0.0.0 Safari/537.36",
]

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeLLwlICI396brIvazfMJslEztlxuDRXGDson_dCzjOMhrHSQ/viewform"


def create_browser():
    """
       Launches a Chrome browser instance in incognito mode with a random user agent.
       Returns:
           WebDriver: A configured Selenium Chrome WebDriver instance.
       Raises:
           SystemExit: If the browser cannot be started.
       """
    options = Options()
    options.add_argument("--incognito")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_experimental_option("detach", True)
    user_agent = random.choice(USER_AGENTS)
    options.add_argument(f"user-agent={user_agent}")

    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        return driver
    except WebDriverException as e:
        logger.exception("Fehler beim Starten des Browsers: %s", e)
        raise SystemExit("Browser konnte nicht gestartet werden.")


def submit_all(data: list[dict]):
    """
       Submits all rental listings by filling out a Google Form using Selenium.
       Steps:
       - Scrapes fresh listing data from the ZillowClone
       - Checks for equal-length address/price/link lists
       - Loops through all entries and fills out the form
       - Handles exceptions and logs each attempt
       Args:
           data (list[dict]): Not directly used in this mode, but kept for interface compatibility.
       Raises:
           SystemExit: If the Zillow page cannot be loaded.
       """
    zc = ZillowClone()
    soup = zc.get_page()

    if not soup:
        logger.error("❌ Konnte die Zillow-Seite nicht laden. Abbruch.")
        raise SystemExit("Konnte die Seite nicht laden.")

    all_addresses = zc.get_add(soup)
    all_prices = zc.get_rent(soup)
    all_links = zc.get_links(soup)

    # Prüfen, ob alle Listen gleich lang sind
    if not (len(all_addresses) == len(all_prices) == len(all_links)):
        min_len = min(len(all_addresses), len(all_prices), len(all_links))
        logger.warning("⚠️ Nur %d vollständige Einträge werden verarbeitet (Datenlisten ungleich lang)", min_len)
        all_addresses = all_addresses[:min_len]
        all_prices = all_prices[:min_len]
        all_links = all_links[:min_len]

    logger.info("Starte Google-Formular-Ausfüllung für %d Einträge...", len(all_addresses))

    driver = create_browser()
    submitted = 0

    try:
        for i in range(len(all_addresses)):
            try:
                fill_out_form(driver, all_addresses[i], all_prices[i], all_links[i])
                submitted += 1
                logger.info("✔️ Formular #%d gesendet: %s", i + 1, all_addresses[i])
                time.sleep(random.uniform(0.7, 1.4))
            except TimeoutException:
                logger.exception("⏱️ Timeout bei Formular #%d: %s", i + 1, all_addresses[i])
            except Exception as e:
                logger.exception("❌ Fehler bei Formular #%d: %s – %s", i + 1, all_addresses[i], e)
    finally:
        try:
            driver.quit()
        except Exception:
            logger.warning("⚠️ Fehler beim Beenden des Browsers – vermutlich war er bereits geschlossen.")

        logger.info("✔️ %d Formulare erfolgreich gesendet", submitted)


def fill_out_form(driver, address, price, link):
    """
     Fills out the Google Form for one rental listing and submits it.
     Args:
         driver (WebDriver): The active Selenium browser instance.
         address (str): Rental property address.
         price (str): Rental price (e.g. '$1,200').
         link (str): URL to the listing.
     """
    logger.debug("Öffne Formular für: %s", address)

    driver.get(FORM_URL)
    wait = WebDriverWait(driver, 10)

    address_field = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div[1]/div/div[1]/input')))
    price_field = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/input')))
    link_field = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[3]/div/div/div[2]/div/div[1]/div/div[1]/input')))
    submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[3]/div[1]/div[1]/div')))

    address_field.click()
    address_field.send_keys(address)
    time.sleep(0.3)

    price_field.click()
    price_field.send_keys(price)
    time.sleep(0.3)

    link_field.click()
    link_field.send_keys(link)
    time.sleep(0.3)

    submit_button.click()
    logger.debug("Formular abgeschickt für: %s", address)


















