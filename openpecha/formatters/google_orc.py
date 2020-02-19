from copy import deepcopy
import gzip
import json
import math
from pathlib import Path
import re
import yaml

from openpecha.formatters import BaseFormatter
from openpecha.formatters.format import Layer
from openpecha.formatters.format import Page
from openpecha.utils import gzip_str


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
                yield json.load(gzip.open(str(fn), 'rb')), fn.name.split('.')[0]
            except:
                yield None


    def _get_page_index(self, n):
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
        for pg, page_ref in zip(layers['pages'], layers['pages_ref']):
            page = deepcopy(Page)
            page['id'] = self.get_unique_id()
            page['span']['start'] = pg[0]
            page['span']['end'] = pg[1]
            page['page_index'] = self._get_page_index(pg[2])
            page['reference'] = page_ref
            Pagination['annotations'].append(page)

        result = {
            'pagination': Pagination
        }

        return result


    def _get_coord(self, vertices):
        coord = []
        for vertice in vertices:
            coord.append((vertice['x'], vertice['y']))
        
        return coord


    def _get_page(self, response):
        try:
            page = response['textAnnotations'][0]
        except KeyError:
            return None, None
        
        text = page['description']
        # vertices = page['boundingPoly']['vertices']  # get text box
        
        return text, None #self._get_coord(vertices)


    def _get_lines(self, text, last_pg_end_idx, first_pg):
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


    def save_boundingPoly(self, response, path):

        def tlbr(vertices):
            return {'tl': vertices[0], 'br': vertices[2]}

        boundingPolies = {}
        for ann in response['textAnnotations']:
            boundingPolies[ann['description']] = tlbr(ann['boundingPoly']['vertices'])

        zipped_boundingPolies = gzip_str(json.dumps(boundingPolies))
        path.write_bytes(zipped_boundingPolies)


    def build_layers(self, responses, base_id=None):
        if base_id:
            resource_vol_path = self.dirs['release_path']/base_id
            resource_vol_path.mkdir(exist_ok=True)

        pages = []
        pages_ref = []
        last_pg_end_idx = 0
        for n_pg, (response, page_ref) in enumerate(responses):
            # extract annotation
            if not response:
                print(f'[ERROR] Failed : {n_pg+1}')
                continue
            text, _ = self._get_page(response)
            if not text: continue # skip empty page
            lines, last_pg_end_idx = self._get_lines(text, last_pg_end_idx, n_pg == 0)
            pages.append((lines[0][0], lines[-1][1], n_pg+1))
            pages_ref.append(response.get('image_link', page_ref))

            # create base_text
            self.base_text.append(text)

            if base_id:
                # save the boundingPoly to resources
                self.save_boundingPoly(response, resource_vol_path/f'{n_pg+1:04}.json.gz')

        result = {
            'pages': pages,
            'pages_ref': pages_ref,
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
                'volume': '',
                'author': converter.toUnicode(author_tag.text) if author_tag else '',
            }
        }

        return metadata


    def create_opf(self, input_path, pecha_id):
        input_path = Path(input_path)
        self._build_dirs(input_path, id=pecha_id)

        self.dirs['release_path'] = self.dirs['opf_path'].parent/'releases/bouding_poly'
        self.dirs['release_path'].mkdir(exist_ok=True, parents=True)

        for i, vol_path in enumerate(sorted(input_path.iterdir())):
            print(f'[INFO] Processing Vol {i+1:03} : {vol_path.name} ...')
            base_id = f'v{i+1:03}'
            if (self.dirs['opf_path']/'base'/f'{base_id}.txt').is_file(): continue
            responses = self.get_input(vol_path)
            layers = self.build_layers(responses, base_id)
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

        return self.dirs['opf_path'].parent


if __name__ == "__main__":
    formatter = GoogleOCRFormatter()
    formatter.create_opf('./tests/data/formatter/google_ocr/W3CN472', 300)