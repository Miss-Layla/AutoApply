import os
import logging
from dotenv import load_dotenv
from zillow import ZillowClone
from data_builder import transform_cards_to_data
from backends import gform_backend, sheety_backend
from send_mail import send_mail


load_dotenv()

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
    )

def build_data(logger):
    zc = ZillowClone()
    soup = zc.get_page()
    if not soup:
        logger.error("❌ Konnte die Seite nicht laden.")
        raise SystemExit("Konnte die Seite nicht laden.")

    cards = zc.get_cards(soup)
    if not cards:
        logger.error("❌ Keine Listings gefunden.")
        raise SystemExit("Keine Daten gefunden.")

    logger.info(f"✔️ {len(cards)} Listings gefunden.")
    return transform_cards_to_data(cards)

def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Programmstart")

    mode = os.getenv("MODE", "gform").lower()

    if mode not in ["gform", "sheety"]:
        logger.error(f"❌ Ungültiger MODE in .env: '{mode}'")
        raise ValueError("MODE muss 'gform' oder 'sheety' sein.")

    logger.info(f"Modus gewählt: {mode}")

    data = build_data(logger)

    if not data:
        logger.warning("Keine Daten zum Übermitteln – Abbruch.")
        return

    if mode == "gform":
        logger.info("Daten werden per Google Form übermittelt...")
        gform_backend.submit_all(data)
        send_mail()

    elif mode == "sheety":
        logger.info("Daten werden an Sheety übermittelt...")
        sheety_backend.submit_all(data)
        send_mail()

    logger.info("✔️ Prozess abgeschlossen.")

if __name__ == "__main__":
    main()
