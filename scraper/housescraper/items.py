# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HousescraperItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    pass


class HouseItem(scrapy.Item):
    link = scrapy.Field()
    header = scrapy.Field()
    address = scrapy.Field()
    price = scrapy.Field()
    upped = scrapy.Field()
    image_url = scrapy.Field()
    details = scrapy.Field()
