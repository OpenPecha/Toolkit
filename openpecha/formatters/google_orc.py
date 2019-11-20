from .formatter import BaseFormatter


class GoogleOCRFormatter(BaseFormatter):
    '''
    OpenPecha Formatter for Google OCR JSON output of scanned pecha.
    '''

    def __init__(self, output_path='./output')


    def text_preprocess(self, text):
        return text

    
    def get_input_text(self):
        # need to load json and return json
        pass
    
    def format_layer(self, layers):
        pass


    def build_layers(self, text):
        pass

    
    def get_base_text(self, responses):
        base_text = ''
        for response in responses:
            text = response['textAnnotations'][0]['description']
            base_text = ''


    def new_poti(self, input_file):
        # need to adapt to json input file
        pass