from collections import defaultdict
from pathlib import Path
import yaml


class OPFormatter:
    '''
    OpenPoti Formatter class to parse annotated text into openpecha format.

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
        

    def _build_dirs(self):
        '''
        Build the necessary directories for OpenPoti format.
        '''
        _work_no = self.input_file.stem

        self.dirs = {'opf_path': self.output_path/f'{_work_no}/{_work_no}.opf'}
        self.dirs['layers_path'] = self.dirs['opf_path']/'layers'
        
        self.dirs['opf_path'].mkdir(parents=True, exist_ok=True)
        self.dirs['layers_path'].mkdir(parents=True, exist_ok=True)

    
    def text_preprocess(self, text):
        '''
        This is temporary method to remove all the critic markups and make existing
        markup consistent.
        '''
        # remove critic markup
        text = text.replace('{++', '')
        text = text.replace('++}', '')

        # edit the existing markup
        text = text.replace('###', '#') # book_title to title
        text = text.replace('##', '#')  # chapter_title to title
        text = text.replace("**", "`")  # change tsawa markup
        text = text.replace("~~", '~')  # change quote markup

        return text

    
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


    def get_input_text(self):
        '''
        Return a preprocess text from given input_file path
        '''
        m_text = self.text_preprocess(self.input_file.read_text())
        return self.normalizeUni(m_text)


    def layers_postprocess(self, layers):
        '''
        Post-processing for various layer to easily dump into yaml file. For eg, title annotation has only one char coord, #<title_text>
        yigchung annotations has part of char coord, *<yigchun_text>*.
        '''
        for layer, anns in layers.items():
            out = {}
            anns = [e-1 if i%2 == 0 else e for i, e in enumerate(anns, start=1)]
            for i, e in enumerate(range(0, len(anns), 2)):
                out[i] = anns[e:e+2]
            layers[layer] = out            
        return layers


    def build_layers(self, text):
        '''
        Parse all the layers annotation from the given text.
        '''
        layers = defaultdict(list)
        i =  0
        is_title = False
        for c in text:
            if c == '#':
                layers['title'].append(i)
                is_title = True
            elif is_title and c == '\n':
                layers['title'].append(i)
                is_title = False
                i += 1
            elif c == '*':
                layers['yigchung'].append(i)
            elif c == '`':
                layers['tsawa'].append(i)
            elif c == '~':
                layers['quotes'].append(i)
            elif c == '[' or c == ']':
                layers['sapche'].append(i)
            else:
                i += 1

        return self.layers_postprocess(layers)

    def get_base_text(self, m_text):
        m_text = m_text.replace('#', '')
        m_text = m_text.replace('*', '')
        m_text = m_text.replace('`', '')
        m_text = m_text.replace('~', '')
        m_text = m_text.replace('[', '')
        text = m_text.replace(']', '')
        return text

    def dump(self, data, output_fn):
        with output_fn.open('w') as fn:
            yaml.dump(data, fn, default_flow_style=False)
            
        
    def new_poti(self, input_file):
        self.input_file = Path(input_file)
        self._build_dirs()

        m_text = self.get_input_text()
        layers = self.build_layers(m_text)
        base_text = self.get_base_text(m_text)

        # save layers
        for layer, ann in layers.items():
            layer_fn = self.dirs['layers_path']/f'{layer}.yml'
            self.dump(ann, layer_fn)

        # save base_text
        (self.dirs['opf_path']/'base.txt').write_text(base_text)


if __name__ == "__main__":
    formatter = OPFormatter('usage/new_layer_output')
    formatter.new_poti('usage/input/W1OP000002.txt')