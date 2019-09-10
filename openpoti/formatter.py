from collections import defaultdict
from pathlib import Path
import yaml


class OPFormatter:
    '''
    OpenPoti Formatter class to parse annotated text into openpoti format.

    Example of OpenPoti format
    ==========================

        W1OP000001.opf
            ├── base.txt
            ├── layers
            │   ├── title.yml
            │   ├── yigchung.yml
            |   ├── citation.yml
    '''

    def __init__(self, output_path='./output'):
        self.output_path = Path(output_path)S
        

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
        text = text.replace('{++', '')
        text = text.replace('++}', '')
        text = text.replace('###', '#')
        text = text.replace('##', '#')
        return text


    def get_input_text(self):
        '''
        Return a preprocess text from given input_file path
        '''
        m_text = self.text_preprocess(self.input_file.read_text())
        return m_text


    def layers_postprocess(self, layers):
        '''
        Post-processing for various layer to easily dump into yaml file. For eg, title annotation has only one char coord, #<title_text>
        yigchung annotations has part of char coord, *<yigchun_text>*.
        '''
        for layer, anns in layers.items():
            out = {}
            if layer == 'title':
                for i, ann in enumerate(anns):
                    out[i] = ann
            else:
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
        for c in text:
            if c == '#':
                layers['title'].append(i)
            elif c == '*':
                layers['yigchung'].append(i)
            elif c == '**':
                layers['tsawa'].append(i)
            elif c == '~~':
                layers['quotes'].append(i)
            elif c == '[' or c == ']':
                layers['sapche'].append(i)
            else:
                i += 1

        return self.layers_postprocess(layers)


    def dump(self, data, output_fn):
        with output_fn.open('w') as fn:
            yaml.dump(data, fn, default_flow_style=False)


    def formatter(work):
        m_text = get_text(work)
        layers = build_layers(m_text)
        
        output_dir = Path('new_layer_output')
        work_dir = output_dir/work
        layer_dir = work_dir/f'{work}.opf'/'layers'

        for layer, ann in layers.items():
            layer_fn = layer_dir/f'{layer}.yml'
            dump(ann, layer_fn)
        
    def new_poti(self, input_file):
        self.input_file = Path(input_file)
        self._build_dirs()

        m_text = self.get_input_text()
        layers = self.build_layers(m_text)

        for layer, ann in layers.items():
            layer_fn = self.dirs['layers_path']/f'{layer}.yml'
            self.dump(ann, layer_fn)        



if __name__ == "__main__":
    formatter = OPFormatter('usage/new_layer_output')
    formatter.new_poti('usage/input/W1OP000001.txt')