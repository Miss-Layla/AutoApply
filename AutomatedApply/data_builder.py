from datetime import datetime
from bs4 import BeautifulSoup
from zillow import ZillowClone
import logging

logger = logging.getLogger(__name__)

def transform_cards_to_data(cards):
    """
    Transforms a list of raw HTML card elements into structured rental data.
    - Parses each card with BeautifulSoup
    - Extracts address, rent, and link using ZillowClone methods
    - Adds a timestamp to each entry
    - Logs detailed info for each transformation step
    Args:
        cards (list): List of HTML elements representing rental listings
    Returns:
        list[dict]: Structured data with keys: timestamp, address, rent, link
    """
    zc = ZillowClone()
    data = []

    logger.info("Starte Transformation von %d Karten", len(cards))

    for i, card in enumerate(cards):
        soup = BeautifulSoup(str(card), "lxml")

        address = zc.get_add(soup)
        rent = zc.get_rent(soup)
        link = zc.get_links(soup)

        logger.debug("Card #%d: %s | %s | %s", i + 1, address, rent, link)

        data.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "address": address,
            "rent": rent,
            "link": link
        })

    logger.info("%d Karten erfolgreich transformiert", len(data))
    return data

