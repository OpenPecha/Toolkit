from uuid import uuid4

from .formatter import BaseFormatter

class kangyurFormatter(BaseFormatter):
    '''
    OpenPecha Formatter for digitized wooden-printed Pecha based on annotation scheme from Esukhia.
    '''

    def text_preprocess(self, text):
        pass
    

    def format_layer(self, layers):
        pages = {'id': None, 'type': 'page', 'rev': "012123", 'log': None, 'content': []}
        lines = {'id': None, 'type': 'line', 'rev': "012123", 'log': None, 'content': []}

        for page, lines in zip(layers['page'], layers['line']):
            page_id = uuid4().hex
            pages['content'].append({
                'id': page_id,
                'span': {
                    'start_char': page[0], 
                    'end_char': page[1]
                }
            })
            for i, line in enumerate(lines):
                line_id = uuid().hex
                lines['content'].append({
                    'id': line_id,
                    'span': {
                        'start_char': line[0], 
                        'end_char': line[1]
                    },
                    'part_of': f'page/{page_id}',
                    'part_index': i+1
                })

        return {'page': pages, 'line': lines}


    def build_layers(self, text):
        pass


    def get_base_text(self, m_text):
        pass