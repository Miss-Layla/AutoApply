import logging
import os
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

SHEETY_URL = os.getenv("SHEETY_API_POST")
SHEETY_TOKEN = os.getenv("SHEETY_TOKEN", "")

HEADERS = {
    "Content-Type": "application/json",
    **({"Authorization": f"Bearer {SHEETY_TOKEN}"} if SHEETY_TOKEN else {})
}

def submit_row(row: dict):
    """
    Sends a single row of rental data to the Sheety API.
    - Builds a JSON payload based on the expected Sheety schema
    - Sends the data via POST request with optional auth header
    - Logs success or error messages accordingly
    Args:
        row (dict): Dictionary containing address, rent, link, and timestamp.
    Returns:
        dict: JSON response from the Sheety API if successful.
    Raises:
        requests.RequestException: If the request fails.
    """
    payload = {
        "tabellenblatt1": {
            "address": str(row.get("address", "")),
            "rent": str(row.get("rent", "")),
            "link": str(row.get("link", "")),
            "timestamp": str(row.get("timestamp", ""))
        }
    }

    try:
        logger.debug("Sende Payload an Sheety: %s", payload)
        r = requests.post(SHEETY_URL, json=payload, headers=HEADERS, timeout=30)
        r.raise_for_status()
        logger.info("✔️ Zeile erfolgreich hochgeladen: %s", payload["tabellenblatt1"]["address"])
        return r.json()
    except requests.RequestException:
        logger.error("❌ Fehler beim Hochladen für Adresse: %s", payload["tabellenblatt1"]["address"])
        logger.error("❌ Antwort von Sheety: %s", r.text)
        raise

def submit_all(data: list[dict]):
    """
      Sends multiple rows of rental data to the Sheety API, one by one.
      - Iterates through the given data list
      - Calls `submit_row()` for each row
      - Logs the total number of successful uploads
      Args:
          data (list[dict]): List of rental data dictionaries.
      Raises:
          RuntimeError: If the Sheety URL is missing in the environment variables.
      """
    if not SHEETY_URL:
        raise RuntimeError("SHEETY_API_POST fehlt in .env")
    count = 0
    for row in data:
        submit_row(row)
        count += 1
    logger.info(f"[Sheety] {count} Zeilen erfolgreich hochgeladen ✔️")











