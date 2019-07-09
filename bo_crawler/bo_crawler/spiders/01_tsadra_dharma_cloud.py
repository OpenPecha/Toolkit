from pathlib import Path
import requests
import scrapy

from bo_crawler.items import TsadraEbookItem


class TsadraSpider(scrapy.Spider):
    name = "tsadra_dharma_cloud"
    start_urls = ['http://dharmacloud.tsadra.org/library/']
    
    def __init__(self):
        self.path = Path('../data') /self.name
        self.path.mkdir(parents=True, exist_ok=True)
        self.items = TsadraEbookItem()

    def parse(self, response):
        ebook_page_urls = response.css('.product-images::attr(href)').extract()
        for ebook_page_url in ebook_page_urls:
            yield scrapy.Request(url=ebook_page_url, callback=self.download_ebook)

        # follow paginataion links
        next_page = response.css('a.next::attr(href)').extract_first()
        if next_page is not None:
            yield scrapy.Request(url=next_page, callback=self.parse)

    def download_ebook(self, response):
        title = response.css('h1.product_title::text').extract_first()
        sub_title = '་'.join(title.split('་')[:8])
        dl_link = response.css('a.download_button::attr(href)').extract_first()
        print(title)
        print(dl_link)
        ebook_path = (self.path/'{}.epub'.format(sub_title)).resolve()
        if not ebook_path.is_file():
            ebook_path.write_bytes(requests.get(dl_link).content)
            print('******* Download Complete !!! ********')
        self.items['title'] = title
        self.items['path'] = ebook_path
        yield self.items

