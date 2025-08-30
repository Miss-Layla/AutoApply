from data_builder import transform_cards_to_data
from zillow import ZillowClone
from pprint import pprint

"""
Test file to fetch the Zillow demo page, extract all property listings,
and transform them into structured data for further processing.
"""


zc = ZillowClone()

soup = zc.get_page()

cards = zc.get_cards(soup)

result = transform_cards_to_data(cards)

pprint(result)