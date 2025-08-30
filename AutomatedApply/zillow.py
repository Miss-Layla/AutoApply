import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

URL = "https://appbrewery.github.io/Zillow-Clone/"

class ZillowClone:
    """
       A scraper class for extracting rental listing data from the Zillow demo page.
       This class wraps network handling and HTML parsing using BeautifulSoup,
       and provides helper methods to extract:
       - Property cards (`get_cards`)
       - Addresses (`get_add`)
       - Rent prices (`get_rent`)
       - Listing links (`get_links`)
       Usage:
           zc = ZillowClone()
           soup = zc.get_page()
           cards = zc.get_cards(soup)
           addresses = zc.get_add(soup)
       """
    def __init__(self):
        self.session = requests.Session()

    def get_page(self):
        try:
            page = self.session.get(URL, timeout=10)
            page.raise_for_status()
            return BeautifulSoup(page.content, 'lxml')
        except requests.exceptions.RequestException:
            logger.exception("Fehler beim Abrufen der Zillow-Seite")
            return None

    def get_cards(self, soup):
        cards = soup.select(".StyledPropertyCardDataWrapper")
        logger.debug("Found %d property cards", len(cards))
        return cards

    def get_add(self, soup):
        tags = soup.select("address")
        addresses = [tag.get_text(strip=True).replace(" | ", " ") for tag in tags]
        logger.debug("Parsed %d addresses", len(addresses))
        return addresses

    def get_rent(self, soup):
        price_tags = soup.select("span")
        rents = [tag.get_text(strip=True).replace("/mo", "").split("+")[0] for tag in price_tags if "$" in tag.text]
        logger.debug("Parsed %d rents", len(rents))
        return rents

    def get_links(self, soup):
        links = [a["href"].strip() for a in soup.select(".StyledPropertyCardDataWrapper a[href]")]
        logger.debug("Parsed %d links", len(links))
        return links



