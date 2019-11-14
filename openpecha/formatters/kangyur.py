from .formatter import BaseFormatter

class kangyurFormatter(BaseFormatter):
    '''
    OpenPecha Formatter for digitized wooden-printed Pecha based on annotation scheme from Esukhia.
    '''

    def text_preprocess(self, text):
        pass
    

    def format_layer(self, layers):
        pages = {'id':, 'type': 'page', 'rev': "012123", 'log':, 'content': []}
        lines = {'id':, 'type': 'line', 'rev': "012123", 'log':, 'content': []}

        for page, lines in zip(layers['page'], layers['line']):1
            page_id = get_unique_id()
            pages['content'].append({
                'id': page_id,
                'span': {
                    'start_char': page[0], 
                    'end_char': page[1]
                }
            })
            for i, line in enumerate(lines):
                line_id = get_unique_id()
                lines['content'].append({
                    'id': line_id,
                    'span': {
                        'start_char': line[0], 
                        'end_char': line[1]
                    },
                    'part_of': f'page/{page_id}'
                    'part_index': i+1
                })

        return {'page': pages, 'line': lines}


    
    def build_layers(self, text):
        pass


    def get_base_text(self, m_text):
        pass