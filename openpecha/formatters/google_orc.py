from copy import deepcopy
import json
import math
from pathlib import Path
import re
import yaml

from openpecha.formatters import BaseFormatter
from openpecha.formatters.format import Layer
from openpecha.formatters.format import Page


class GoogleOCRFormatter(BaseFormatter):
    '''
    OpenPecha Formatter for Google OCR JSON output of scanned pecha.
    '''

    def __init__(self, output_path='./output'):
        super().__init__(output_path=output_path)
        self.n_page_breaker_char = 3
        self.page_break = '\n' * self.n_page_breaker_char
        self.base_text = []


    def text_preprocess(self, text):
        
        return text

    
    def get_input(self, input_path):
        '''
        load and return all jsons in the input_path.
        '''
        for fn in sorted(list(input_path.iterdir())):
            try: 
                yield json.load(fn.open())
            except:
                yield None


    def __get_page_index(self, n):
        page_sides = 'ab'
        div = n/2
        page_num = math.ceil(div)
        if div.is_integer():
            return f'{page_num}{page_sides[1]}'
        else:
            return f'{page_num}{page_sides[0]}'


    def format_layer(self, layers, base_id):
        # Format page annotation
        Pagination = deepcopy(Layer)
        Pagination['id'] = self.get_unique_id()
        Pagination['annotation_type'] = 'pagination'
        Pagination['revision'] = f'{1:05}'
        for i, (pg, pg_img_url) in enumerate(zip(layers['page'], layers['img_url'])):
            page = deepcopy(Page)
            page['id'] = self.get_unique_id()
            page['span']['start'] = pg[0]
            page['span']['end'] = pg[1]
            page['page_index'] = self.__get_page_index(i+1)
            page['reference'] = pg_img_url
            Pagination['annotations'].append(page)

        result = {
            'pagination': Pagination
        }

        return result


    def __get_coord(self, vertices):
        coord = []
        for vertice in vertices:
            coord.append((vertice['x'], vertice['y']))
        
        return coord


    def __get_page(self, response):
        try:
            page = response['textAnnotations'][0]
        except KeyError:
            return None, None
        
        text = page['description']
        # vertices = page['boundingPoly']['vertices']  # get text box
        
        return text, None #self.__get_coord(vertices)


    def __get_lines(self, text, last_pg_end_idx, first_pg):
        lines = []
        line_breaks = [m.start() for m in re.finditer('\n', text)]
        
        start = last_pg_end_idx
        
        # increase the start idx with page_breaker_char for page greater than frist page.
        if not first_pg:
            start += self.n_page_breaker_char+1
            line_breaks = list(map(lambda x: x+start, line_breaks))

        for line in line_breaks:
            lines.append((start, line-1)) # skip new_line, which has 1 char length
            start += (line-start) + 1
        
        return lines, line


    def build_layers(self, responses):
        pages = []
        img_urls = []
        img_char_coord = []
        last_pg_end_idx = 0
        for n_pg, response in enumerate(responses):
            # extract annotation
            if not response:
                print(f'[ERROR] Failed : {n_pg+1}')
                continue
            text, page_coord = self.__get_page(response)
            if not text: continue # skip empty page
            lines, last_pg_end_idx = self.__get_lines(text, last_pg_end_idx, n_pg == 0)
            pages.append((lines[0][0], lines[-1][1], page_coord))
            img_urls.append(response.get('image_link', ''))

            # create base_text
            self.base_text.append(text)

        result = {
            'page': pages,
            'img_url': img_urls,
        }
            
        return result

    
    def get_base_text(self):
        base_text = f'{self.page_break}'.join(self.base_text)
        self.base_text = []

        return base_text


    def get_metadata(self, work_id):
        import requests
        import xml.etree.ElementTree as ET
        from pyewts import pyewts
        
        converter = pyewts()
        query_url = 'https://www.tbrc.org/xmldoc?rid={}'
        bdrc_metadata_url = query_url.format(work_id)
        r = requests.get(bdrc_metadata_url)
        root = ET.fromstring(r.content.decode('utf-8'))        
        title_tag = root[0]
        author_tag = root.find('{http://www.tbrc.org/models/work#}creator')
        metadata = {
            'id': f'opecha:{self.pecha_id}',
            'initial_creation_type': 'ocr',
            'source_metadata': {
                'id': f'bdr:{work_id}',
                'title': converter.toUnicode(title_tag.text),
                'author': converter.toUnicode(author_tag.text) if author_tag else '',
            }
        }

        return metadata


    def create_opf(self, input_path, id):
        input_path = Path(input_path)
        self._build_dirs(input_path, id)
        (self.dirs['opf_path']/'base').mkdir(exist_ok=True)

        for i, vol_path in enumerate(sorted(input_path.iterdir())):
            print(f'[INFO] Processing Vol {i+1:03} : {vol_path.name} ...')
            base_id = f'v{i+1:03}'
            if (self.dirs['opf_path']/'base'/f'{base_id}.txt').is_file(): continue
            responses = self.get_input(vol_path)
            layers = self.build_layers(responses)
            formatted_layers = self.format_layer(layers, base_id)
            base_text = self.get_base_text()

            # save base_text
            (self.dirs['opf_path']/'base'/f'{base_id}.txt').write_text(base_text)

            # save layers
            vol_layer_path = self.dirs['layers_path']/base_id
            vol_layer_path.mkdir(exist_ok=True)
            for layer, ann in formatted_layers.items():
                layer_fn = vol_layer_path/f'{layer}.yml'
                self.dump(ann, layer_fn)

        # create meta.yml
        meta_fn = self.dirs['opf_path']/'meta.yml'
        self.dump(self.get_metadata(input_path.name), meta_fn)


if __name__ == "__main__":
    formatter = GoogleOCRFormatter()
    formatter.create_opf('./tests/data/formatter/google_ocr/W3CN472', 300)