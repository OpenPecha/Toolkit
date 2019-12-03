from openpecha.formatters import BaseFormatter


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
        pass


    def build_layers(self, htmls):

        return result
        


    def get_base_text(self, m_text):

        return self.base_text