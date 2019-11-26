import json
import re

from .formatter import BaseFormatter


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
            yield json.load(fn.open())
         
        
    def format_layer(self, layers):
        pass

    
    def __get_coord(self, vertices):
        coord = []
        for vertice in vertices:
            coord.append((vertice['x'], vertice['y']))
        
        return coord


    def __get_page(self, response):
        page = response['textAnnotations'][0]
        text = page['description']
        vertices = page['boundingPoly']['vertices']  # get text box
        
        return text, self.__get_coord(vertices)


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


    def __get_symbols(self, response):
        symbols = []
        for page in response['fullTextAnnotation']['pages']:
            for block in page['blocks']:
                for paragraph in block['paragraphs']:
                    for word in paragraph['words']:
                        for symbol in word['symbols']:
                            conf = symbol['confidence'] if 'confidence' in symbol else None
                            symbols.append((
                                symbol['text'],
                                conf,
                                self.__get_coord(symbol['boundingBox']['vertices'])
                            ))
        return symbols


    def build_layers(self, responses):
        pages = []
        page_lines = []
        img_urls = []
        img_char_coord = []
        last_pg_end_idx = 0
        for n_pg, response in enumerate(responses):
            # extract annotation
            text, page_coord = self.__get_page(response)
            lines, last_pg_end_idx = self.__get_lines(text, last_pg_end_idx, n_pg == 0)
            page_lines.append(lines)
            pages.append((lines[0][0], lines[-1][1], page_coord))
            img_urls.append(response['image_url'])
            img_char_coord.append(self.__get_symbols(response))

            # create base_text
            self.base_text.append(text)

        result = {
            'page': pages,
            'line': page_lines,
            'img_url': img_urls,
            'img_char_coord': img_char_coord
        }
            
        return result

    
    def get_base_text(self, responses):
        
        return f'{self.page_break}'.join(self.base_text)