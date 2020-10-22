import datetime
from pathlib import Path

import requests
import scrapy
from inline_requests import inline_requests

from bo_crawler.items import TsadraEbookItem


class TsadraSpider(scrapy.Spider):
    name = "tsadra"
    start_urls = ["http://dharmacloud.tsadra.org/library/"]

    def __init__(self):
        self.path = Path("../data/tsadra/data/ebooks")
        self.path.mkdir(parents=True, exist_ok=True)

    def create_item(self):
        item = TsadraEbookItem()
        item = self._init_item(item)
        return item

    def _init_item(self, item):
        item["org_bo"] = ""
        item["org_en"] = ""
        item["website"] = ""
        item["aquisition_data"] = ""
        item["title_bo"] = ""
        item["title_en"] = ""
        item["collection_bo"] = ""
        item["collection_en"] = ""
        item["publisher_bo"] = ""
        item["publisher_en"] = ""
        item["author_bo"] = ""
        item["author_en"] = ""
        item["sku"] = ""
        item["category_bo"] = ""
        item["category_en"] = ""
        item["description_bo"] = ""
        item["description_en"] = ""
        item["filename"] = ""
        return item

    def parse(self, response):
        ebook_page_urls = response.css(".product-images::attr(href)").extract()
        for ebook_page_url in ebook_page_urls:
            yield scrapy.Request(url=ebook_page_url, callback=self.download_ebook)

        # follow paginataion links
        next_page = response.css("a.next::attr(href)").extract_first()
        if next_page is not None:
            yield scrapy.Request(url=next_page, callback=self.parse)

    @inline_requests
    def download_ebook(self, response):
        title_bo = response.css("h1.product_title::text").extract_first()
        print(title_bo)

        # metadata
        raw_metadata_en, tib_page_url = self.parse_metadata(response, lang="en")
        if raw_metadata_en:
            item = self.create_item()
            item = self.get_metadata(raw_metadata_en, item, lang="en")

            # some page doesn't have Tibetan version
            if tib_page_url:
                tib_page_response = yield scrapy.Request(tib_page_url)
                raw_metadata_bo = self.parse_metadata(tib_page_response, lang="bo")
                item = self.get_metadata(raw_metadata_bo, item, lang="bo")

            item["org_bo"] = "མཐའ་ཡས་དཔེ་མཛོད།"
            item["org_en"] = "Timeless Treasuries"
            item["website"] = "http://dharmacloud.tsadra.org"
            item["aquisition_data"] = str(datetime.date.today())
            item["title_bo"] = title_bo

            # download the ebook
            dl_link = response.css("a.download_button::attr(href)").extract_first()
            ebook_filename = dl_link.split("/")[-1]
            item["filename"] = ebook_filename
            target = (self.path / f"{ebook_filename}").resolve()
            if not target.is_file():
                target.write_bytes(requests.get(dl_link).content)
                print("******* Download Completed !!! ********")

            yield item

    def parse_metadata(self, response, lang):
        product_details = response.css(
            "div.woocommerce-product-details__short-description *::text"
        ).extract()
        product_meta = response.css("div.product_meta *::text").extract()
        des = response.css("div#tab-description *::text").extract()
        if lang == "en" and "DOWNLOAD EBOOK" in product_details:
            tib_page_url = response.css("a[title=Tibetan]::attr(href)").get()
            return product_details[:-2] + product_meta + des, tib_page_url
        elif lang == "bo":
            return product_details[:-2] + product_meta + des
        else:
            return "", ""

    def get_metadata(self, raw_data, item, lang):
        metadata_key = {
            "collection": {"en": "Collection:", "bo": "ཕྱོགས་བསྡུས།"},
            "title": {"en": "Title:"},
            "author": {"en": "Author:", "bo": "མཛད་པ་པོ།"},
            "publisher": {"en": "Publisher:", "bo": "པར་འགྲེམས་བྱེད་པོ།"},
            "sku": {"en": "SKU:", "bo": "SKU:"},
            "category": {"en": "Category:", "bo": "Category:"},
            "description": {"en": "Description", "bo": "Description"},
        }

        md_type = ""

        for line in raw_data:
            line = line.strip()
            line = line.replace("\xa0", " ")
            # pdb.set_trace()
            if line:
                if line == metadata_key["collection"][lang]:
                    md_type = "collection"
                elif lang == "en" and metadata_key["title"][lang] in line:
                    md_type = "title"
                elif line == metadata_key["author"][lang] or (
                    lang == "en" and line == "Authors:"
                ):
                    md_type = "author"
                elif line == metadata_key["publisher"][lang]:
                    md_type = "publisher"
                elif line == metadata_key["sku"][lang]:
                    md_type = "sku"
                elif line == metadata_key["category"][lang]:
                    md_type = "category"
                elif line == metadata_key["description"][lang]:
                    md_type = "description"

                if md_type == "collection" and line != metadata_key["collection"][lang]:
                    item[f"collection_{lang}"] += line
                elif md_type == "title":
                    title_values = line.split(":")[1:]
                    print("+++++++++++++++++++++++", line, title_values)
                    if len(title_values) > 1:
                        item[f"title_{lang}"] += ":".join(
                            [value.strip() for value in title_values]
                        )
                    else:
                        item[f"title_{lang}"] += title_values.pop().strip()
                elif md_type == "author" and line != metadata_key["author"][lang]:
                    item[f"author_{lang}"] += line
                elif md_type == "publisher" and line != metadata_key["publisher"][lang]:
                    item[f"publisher_{lang}"] += line
                elif md_type == "sku" and line != metadata_key["sku"][lang]:
                    item["sku"] += line
                elif md_type == "category" and line != metadata_key["category"][lang]:
                    item[f"category_{lang}"] += line
                elif (
                    md_type == "description"
                    and line != metadata_key["description"][lang]
                ):
                    item[f"description_{lang}"] += line

        return item
