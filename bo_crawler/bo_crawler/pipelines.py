# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


# Spiders
from bo_crawler.spiders.tsadra_spider import TsadraSpider


class BoCrawlerPipeline(object):
    def process_item(self, item, spider):
        metadata = {}
        if spider.name == TsadraSpider.name:
            metadata = {
                "title": {"en": item["title_en"], "bo": item["title_bo"]},
                "collection": {
                    "en": item["collection_en"],
                    "bo": item["collection_bo"],
                },
                "author": {"en": item["author_en"], "bo": item["author_bo"]},
                "pusblisher": {"en": item["publisher_en"], "bo": item["publisher_bo"]},
                "sku": item["sku"],
                "category": {"en": item["category_en"], "bo": item["category_bo"]},
                "org": {"bo": item["org_en"], "en": item["org_bo"]},
                "website": item["website"],
                "aquisition_data": item["aquisition_data"],
                "filename": item["filename"],
                "description": {
                    "en": item["description_en"],
                    "bo": item["description_bo"],
                },
            }

        return metadata
