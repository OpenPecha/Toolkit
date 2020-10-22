# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
#
# Extracted data -> EbookItem -> Pipeline -> open-poti

import scrapy


class TsadraEbookItem(scrapy.Item):
    # Digital Publication Source
    org_bo = scrapy.Field()
    org_en = scrapy.Field()
    website = scrapy.Field()
    aquisition_data = scrapy.Field()

    # Crawled Metadata
    title_bo = scrapy.Field()
    title_en = scrapy.Field()
    collection_bo = scrapy.Field()
    collection_en = scrapy.Field()
    publisher_bo = scrapy.Field()
    publisher_en = scrapy.Field()
    author_bo = scrapy.Field()
    author_en = scrapy.Field()

    sku = scrapy.Field()
    category_bo = scrapy.Field()
    category_en = scrapy.Field()

    description_bo = scrapy.Field()
    description_en = scrapy.Field()

    filename = scrapy.Field()
