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

        #metadata
        product_details = response.css('div.woocommerce-product-details__short-description *::text').extract()
        product_meta = response.css('div.product_meta *::text').extract()
        des = response.css('div#tab-description *::text').extract()
        tib_page_url = response.css('a[title=Tibetan]::attr(href)').get() 

        if not ebook_path.is_file():
            ebook_path.write_bytes(requests.get(dl_link).content)
            print('******* Download Complete !!! ********')
        self.items['title'] = title
        self.items['path'] = ebook_path
        yield self.items


    def get_metadata(raw_data, lang):
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
        
        metadata = {}
        md_type = ''
        
        for line in raw_data[:-2]:
            line = line.strip()
            line = line.replace('\xa0', ' ')
            #pdb.set_trace()
            if line: 
                if line == metadata_key['collection'][lang]: 
                    metadata['collection'] = '' 
                    md_type = 'collection' 
                elif lang == 'en' and metadata_key['title'][lang] in line: 
                    metadata['title'] = '' 
                    md_type = 'title'  
                elif line == metadata_key['author'][lang]: 
                    metadata['author'] = ''
                    md_type = 'author'
                elif line == metadata_key['publisher'][lang]: 
                    metadata['publisher'] = '' 
                    md_type = 'publisher'
                elif line == metadata_key['sku'][lang]: 
                    metadata['sku'] = '' 
                    md_type = 'sku'
                elif line == metadata_key['category'][lang]: 
                    metadata['category'] = '' 
                    md_type = 'category'
                elif line == metadata_key['description'][lang]: 
                    metadata['description'] = '' 
                    md_type = 'description'


                if md_type == 'collection' and line != metadata_key['collection'][lang]: 
                    metadata['collection'] += line
                elif md_type == 'title': 
                    metadata['title'] += line.split(':')[-1].strip()
                elif md_type == 'author' and line != metadata_key['author'][lang]: 
                    metadata['author'] += line
                elif md_type == 'publisher' and line != metadata_key['publisher'][lang]: 
                    metadata['publisher'] += line
                elif md_type == 'sku' and line != metadata_key['sku'][lang]: 
                    metadata['sku'] += line
                elif md_type == 'category' and line != metadata_key['category'][lang]: 
                    metadata['category'] += line
                elif md_type == 'description' and line != metadata_key['description'][lang]: 
                    metadata['description'] += line
                            
        return metadata

