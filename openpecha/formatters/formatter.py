from pathlib import Path
from uuid import uuid4
import yaml


class BaseFormatter:
    '''
    OpenPecha Base class Formatter to parse annotated text into openpecha format.

    Example of OpenPoti format
    ==========================

        W1OP000001.opf
            ├── base.txt          # plain text, without markups (annotations)
            ├── layers            # layers with annotation's char coordinate
            │   ├── title.yml     
            │   ├── yigchung.yml
            |   ├── citation.yml
    '''

    def __init__(self, output_path='./output'):
        self.output_path = Path(output_path)


    def get_unique_id(self):
        return uuid4().hex


    def _build_dirs(self, input_path, id=None):
        '''
        Build the necessary directories for OpenPecha format.
        '''
        if id:
            pecha_id = f'P{id:06}'
        else:
            pecha_id = input_path.stem

        self.pecha_id = pecha_id
        self.dirs = {'opf_path': self.output_path/f'{pecha_id}/{pecha_id}.opf'}
        self.dirs['layers_path'] = self.dirs['opf_path']/'layers'
        self.dirs['base_path'] = self.dirs['opf_path']/'base'
        
        self.dirs['layers_path'].mkdir(parents=True, exist_ok=True)
        self.dirs['base_path'].mkdir(parents=True, exist_ok=True)

    
    def normalizeUni(self, strNFC):
        strNFC = strNFC.replace("\u0F00", "\u0F68\u0F7C\u0F7E") # ༀ
        strNFC = strNFC.replace("\u0F43", "\u0F42\u0FB7") # གྷ
        strNFC = strNFC.replace("\u0F48", "\u0F47\u0FB7") # ཈
        strNFC = strNFC.replace("\u0F4D", "\u0F4C\u0FB7") # ཌྷ
        strNFC = strNFC.replace("\u0F52", "\u0F51\u0FB7") # དྷ
        strNFC = strNFC.replace("\u0F57", "\u0F56\u0FB7") # བྷ
        strNFC = strNFC.replace("\u0F5C", "\u0F5B\u0FB7") # ཛྷ
        strNFC = strNFC.replace("\u0F69", "\u0F40\u0FB5") # ཀྵ
        strNFC = strNFC.replace("\u0F73", "\u0F71\u0F72") # ཱི
        strNFC = strNFC.replace("\u0F75", "\u0F71\u0F74") #  ཱུ
        strNFC = strNFC.replace("\u0F76", "\u0FB2\u0F80") # ྲྀ
        strNFC = strNFC.replace("\u0F77", "\u0FB2\u0F71\u0F80") # ཷ
        strNFC = strNFC.replace("\u0F78", "\u0FB3\u0F80") # ླྀ
        strNFC = strNFC.replace("\u0F79", "\u0FB3\u0F71\u0F80") # ཹ
        strNFC = strNFC.replace("\u0F81", "\u0F71\u0F80") #  ཱྀ
        strNFC = strNFC.replace("\u0F93", "\u0F92\u0FB7") # ྒྷ
        strNFC = strNFC.replace("\u0F9D", "\u0F9C\u0FB7") # ྜྷ
        strNFC = strNFC.replace("\u0FA2", "\u0FA1\u0FB7") # ྡྷ
        strNFC = strNFC.replace("\u0FA7", "\u0FA6\u0FB7") # ྦྷ
        strNFC = strNFC.replace("\u0FAC", "\u0FAB\u0FB7") # ྫྷ
        strNFC = strNFC.replace("\u0FB9", "\u0F90\u0FB5") # ྐྵ
        return strNFC


    def text_preprocess(self, text):
        raise NotImplementedError('Text preprocessing depends on type of text format, \
                                   should be implemented in sub-class.')


    def get_input(self, input_path):
        '''
        Return a preprocess text from given input_file path
        '''
        m_text = self.text_preprocess(input_path.read_text())
        return self.normalizeUni(m_text)


    def format_layer(self, layers):
        '''
        Post-processing for various layer to easily dump into yaml file. For eg, title annotation has only one char coord, #<title_text>
        yigchung annotations has part of char coord, *<yigchun_text>*.
        '''
        raise NotImplementedError('Layers PostProcessing depends on the type of annotations, \
                                   should be implemented in sub-class.')


    def build_layers(self, text):
        '''
        Parse all the layers annotation from the given text.
        '''
        raise NotImplementedError('Parsing annotation depends type of annotation in the text, \
                                  should be implemented in sub-class.')


    def get_base_text(self, m_text):
        'Retuns text with all annotation removed'
        raise NotImplementedError('Every type of text have different format for annotation, \
                                  should be implemented in sub_class.')

    
    def dump(self, data, output_fn):
        with output_fn.open('w') as fn:
            yaml.dump(data, fn, default_flow_style=False,  sort_keys=False, allow_unicode=True)
        
    
    def load(self, fn):
        return yaml.safe_load(fn.open())


    def create_opf(self, input_path):
        input_path = Path(input_path)
        self._build_dirs(input_path)

        m_text = self.get_input(input_path)
        layers = self.build_layers(m_text)
        base_text = self.get_base_text(m_text)

        # save layers
        for layer, ann in layers.items():
            layer_fn = self.dirs['layers_path']/f'{layer}.yml'
            self.dump(ann, layer_fn)

        # save base_text
        (self.dirs['opf_path']/'base.txt').write_text(base_text)