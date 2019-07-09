# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
#
# Extracted data -> EbookItem -> Pipeline -> open-pecha

import datetime

import scrapy


class TsadraEbookItem(scrapy.Item):
    #Digital Publication Source
    org = {'bo': 'མཐའ་ཡས་དཔེ་མཛོད།', 'en': 'Timeless Treasuries'}
    website = 'http://dharmacloud.tsadra.org'
    aquisition_data = str(datetime.date.today())

    # Crawled Metadata
    title = {'bo': scrapy.Field(), 'en': scrapy.Field()}
    category = {'bo': scrapy.Field(), 'en': scrapy.Field()}
    collection = {'bo': scrapy.Field(), 'en': scrapy.Field()}
    publisher = {'bo': scrapy.Field(), 'en': scrapy.Field()}
    author = {'bo': scrapy.Field(), 'en': scrapy.Field()}
    sku = scrapy.Field()
    description: scrapy.Field()