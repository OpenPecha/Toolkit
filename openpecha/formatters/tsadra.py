from copy import deepcopy

from openpecha.formatters import BaseFormatter
from openpecha.formatters.format import *


class TsadraFormatter(BaseFormatter):
    '''
    OpenPecha Formatter for Tsadra DarmaCloud ebooks
    '''

    def __init__(self, output_path='./output'):
        super().__init__(output_path=output_path)
        self.base_text = ''


    def text_preprocess(self, text):
        
        return text


    def format_layer(self, layers):
        for layer in layers:
            if layer == 'book_title':
                Book_title_layer = deepcopy(Layer)
                Book_title_layer['id'] = self.get_unique_id()
                Book_title_layer['annotation_type'] = 'book_title'
                Book_title_layer['revision'] = f'{1:05}'
                Book_title['span']['start'] = layers[layer][0][0]
                Book_title['span']['end'] = layers[layer][0][1]
                Book_title_layer['annotations'].append(Book_title)
            elif layer == 'author':
                Author_layer = deepcopy(Layer)
                Author_layer['id'] = self.get_unique_id()
                Author_layer['annotation_type'] = 'author'
                Author_layer['revision'] = f'{1:05}'
                for a in layers[layer]:
                    author = deepcopy(Author)
                    author['span']['start'] = a[0]
                    author['span']['end'] = a[1]
                    Author_layer['annotations'].append(author)
            elif layer == 'chapter_title':
                Chapter_layer = deepcopy(Layer)
                Chapter_layer['id'] = self.get_unique_id()
                Chapter_layer['annotation_type'] = 'chapter_title'
                Chapter_layer['revision'] = f'{1:05}'
                for a in layers[layer]:
                    chapter = deepcopy(Chapter)
                    chapter['id'] = self.get_unique_id()
                    chapter['span']['start'] = a[0]
                    chapter['span']['end'] = a[1]
                    Chapter_layer['annotations'].append(chapter)
            elif layer == 'tsawa':
                Tsawa_layer = deepcopy(Layer)
                Tsawa_layer['id'] = self.get_unique_id()
                Tsawa_layer['annotation_type'] = 'tsawa'
                Tsawa_layer['revision'] = f'{1:05}'
                for a in layers[layer]:
                    tsawa = deepcopy(Tsawa)
                    tsawa['id'] = self.get_unique_id()
                    tsawa['span']['start'] = a[0]
                    tsawa['span']['end'] = a[1]
                    Tsawa_layer['annotations'].append(tsawa)
            elif layer == 'quotation':
                Quotation_layer = deepcopy(Layer)
                Quotation_layer['id'] = self.get_unique_id()
                Quotation_layer['annotation_type'] = 'tsawa'
                Quotation_layer['revision'] = f'{1:05}'
                for a in layers[layer]:
                    quote = deepcopy(Quotation)
                    quote['id'] = self.get_unique_id()
                    quote['span']['start'] = a[0]
                    quote['span']['end'] = a[1]
                    Quotation_layer['annotations'].append(quote)
            elif layer == 'sabche':
                Sabche_layer = deepcopy(Layer)
                Sabche_layer['id'] = self.get_unique_id()
                Sabche_layer['annotation_type'] = 'tsawa'
                Sabche_layer['revision'] = f'{1:05}'
                for a in layers[layer]:
                    sabche = deepcopy(Sabche)
                    sabche['id'] = self.get_unique_id()
                    sabche['span']['start'] = a[0]
                    sabche['span']['end'] = a[1]
                    Sabche_layer['annotations'].append(sabche)
            elif layer == 'yigchung':
                Yigchung_layer = deepcopy(Layer)
                Yigchung_layer['id'] = self.get_unique_id()
                Yigchung_layer['annotation_type'] = 'tsawa'
                Yigchung_layer['revision'] = f'{1:05}'
                for a in layers[layer]:
                    yigchung = deepcopy(Yigchung)
                    yigchung['id'] = self.get_unique_id()
                    yigchung['span']['start'] = a[0]
                    yigchung['span']['end'] = a[1]
                    Yigchung_layer['annotations'].append(yigchung)
        
        result = {
            'book_title': Book_title_layer,
            'author': Author_layer,
            'chapter_title': Chapter_layer,
            'tsawa': Tsawa_layer,
            'quotes': Quotation_layer,
            'sabche': Sabche_layer,
            'yigchung': Yigchung_layer
        }

        return result


    def build_layers(self, htmls):

        return result


    def get_base_text(self, m_text):

        return self.base_text

    def _get_meta_data(ann):
            return ','.join([self.base_text[a[0]: a[1]+1] for a in ann])