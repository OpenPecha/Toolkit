import datetime
from pathlib import Path
import requests
import scrapy
from inline_requests import inline_requests

from bo_crawler.items import TsadraEbookItem


class TsadraSpider(scrapy.Spider):
    name = "tsadra"
    start_urls = ['http://dharmacloud.tsadra.org/library/']
    
    def __init__(self):
        self.path = Path('../data') /self.name
        self.path.mkdir(parents=True, exist_ok=True)
        self.items = TsadraEbookItem()

    def parse(self, response):
        ebook_page_urls = response.css('.product-images::attr(href)').extract()
        for ebook_page_url in ebook_page_urls[0:1]:
            yield scrapy.Request(url=ebook_page_url, callback=self.download_ebook)

        # follow paginataion links
        # next_page = response.css('a.next::attr(href)').extract_first()
        # if next_page is not None:
        #     yield scrapy.Request(url=next_page, callback=self.parse)

    @inline_requests
    def download_ebook(self, response):
        title = response.css('h1.product_title::text').extract_first()
        sub_title = '་'.join(title.split('་')[:8])
        dl_link = response.css('a.download_button::attr(href)').extract_first()
        print(title)
        print(dl_link)
        ebook_path = (self.path/'{}.epub'.format(sub_title)).resolve()

        #metadata
        raw_metadata_en, tib_page_url = self.parse_metadata(response, lang='en')
        if raw_metadata_en: # and not ebook_path.is_file():
            self.get_metadata(raw_metadata_en, lang='en')
            tib_page_response = yield scrapy.Request(tib_page_url)
            raw_metadata_bo = self.parse_metadata(tib_page_response, lang='bo')
            print(raw_metadata_bo)
            self.get_metadata(raw_metadata_bo, lang='bo')
            self.items['org_bo'] = 'མཐའ་ཡས་དཔེ་མཛོད།'
            self.items['org_en'] = 'Timeless Treasuries'
            self.items['website'] = 'http://dharmacloud.tsadra.org'
            self.items['aquisition_data'] = str(datetime.date.today())
            self.items['title_bo'] = title

            # ebook_path.write_bytes(requests.get(dl_link).content)
            # print('******* Download Completed !!! ********')
        yield self.items

    def parse_metadata(self, response, lang):
        product_details = response.css('div.woocommerce-product-details__short-description *::text').extract()
        product_meta = response.css('div.product_meta *::text').extract()
        des = response.css('div#tab-description *::text').extract()
        if lang == 'en' and 'DOWNLOAD EBOOK' in product_details:
            tib_page_url = response.css('a[title=Tibetan]::attr(href)').get()
            return product_details[:-2] + product_meta + des, tib_page_url
        elif lang == 'bo':
            return product_details[:-2 ] + product_meta + des
        else:
            return '', ''

    def get_metadata(self, raw_data, lang):
        metadata_key = {
            'collection': {
                'en': 'Collection:',
                'bo': 'ཕྱོགས་བསྡུས།'
            },
            'title': {
                'en': 'Title:',
            },
            'author': {
                'en': 'Author:',
                'bo': 'མཛད་པ་པོ།'
            },
            'publisher': {
                'en': 'Publisher:',
                'bo': 'པར་འགྲེམས་བྱེད་པོ།'
            },
            'sku': {
                'en': 'SKU:',
                'bo': 'SKU:'
            },
            'category': {
                'en': 'Category:',
                'bo': 'Category:'
            },
            'description': {
                'en': 'Description',
                'bo': 'Description'
            }
        }
  
        md_type = ''
        
        for line in raw_data:
            line = line.strip()
            line = line.replace('\xa0', ' ')
            #pdb.set_trace()
            if line: 
                if line == metadata_key['collection'][lang]: 
                    self.items[f'collection_{lang}'] = '' 
                    md_type = 'collection' 
                elif lang == 'en' and metadata_key['title'][lang] in line: 
                    self.items[f'title_{lang}'] = '' 
                    md_type = 'title'  
                elif line == metadata_key['author'][lang]: 
                    self.items[f'author_{lang}'] = ''
                    md_type = 'author'
                elif line == metadata_key['publisher'][lang]: 
                    self.items[f'publisher_{lang}'] = '' 
                    md_type = 'publisher'
                elif line == metadata_key['sku'][lang]: 
                    self.items['sku'] = '' 
                    md_type = 'sku'
                elif line == metadata_key['category'][lang]: 
                    self.items[f'category_{lang}'] = '' 
                    md_type = 'category'
                elif line == metadata_key['description'][lang]: 
                    self.items[f'description_{lang}'] = '' 
                    md_type = 'description'


                if md_type == 'collection' and line != metadata_key['collection'][lang]: 
                    self.items[f'collection_{lang}'] += line
                elif md_type == 'title': 
                   self.items[f'title_{lang}'] += line.split(':')[-1].strip()
                elif md_type == 'author' and line != metadata_key['author'][lang]: 
                    self.items[f'author_{lang}'] += line
                elif md_type == 'publisher' and line != metadata_key['publisher'][lang]: 
                    self.items[f'publisher_{lang}'] += line
                elif md_type == 'sku' and line != metadata_key['sku'][lang]: 
                    self.items['sku'] += line
                elif md_type == 'category' and line != metadata_key['category'][lang]: 
                   self.items[f'category_{lang}'] += line
                elif md_type == 'description' and line != metadata_key['description'][lang]: 
                    self.items[f'description_{lang}'] += line