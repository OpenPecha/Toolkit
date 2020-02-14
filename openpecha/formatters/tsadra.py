from copy import deepcopy
from pathlib import Path
from functools import partial

from bs4 import BeautifulSoup

from openpecha.formatters import BaseFormatter
from openpecha.formatters.format import *


class TsadraFormatter(BaseFormatter):
    '''
    OpenPecha Formatter for Tsadra DarmaCloud ebooks
    '''

    def __init__(self, output_path='./opfs'):
        super().__init__(output_path=output_path)
        self.base_text = ''
        self.walker = 0 # The walker to traverse every character in the pecha
        self.book_title = [] # list variable to store book title index
        self.author = [] # list variable to store author annotion index
        self.chapter = [] # list variable to store chapter annotation index
        self.root_text = [] # list variable to store root text index
        self.citation = [] # list variable to store citation index
        self.sabche = [] # list variable to store sabche index
        self.yigchung = [] # list variable to store yigchung index


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
            'quotation': Quotation_layer,
            'sabche': Sabche_layer,
            'yigchung': Yigchung_layer
        }

        return result


    def build_layers(self, html):
        '''
        To Build the layer
        '''
        soup = BeautifulSoup(html, 'html.parser')
        book_title_tmp = ''
        author_tmp = ''
        chapter_title_tmp = ''
        root_text_tmp = ''
        sabche_tmp = ''
        commentary_tmp = ''
        citation_tmp = ''
        rt_base = 'tibetan-root-text_tibetan-root-text'
        cit_base = 'tibetan-citations-in-verse_'
        com_base = 'tibetan-commentary'
        com_classes = {
            'first': f'{com_base}-first-line',
            'middle': f'{com_base}-middle-lines',
            'last': f'{com_base}-last-line',
            'non': f'{com_base}-non-indent1'
        }
        cit_classes = {
            'first': f'{cit_base}tibetan-citations-first-line',
            'middle': f'{cit_base}tibetan-citations-middle-lines',
            'last': f'{cit_base}tibetan-citations-last-line',
            'indent': f'{cit_base}tibetan-regular-indented'
        }
        root_text_classes = {
            'first': f'{rt_base}-first-line',
            'middle': f'{rt_base}-middle-lines',
            'last': f'{rt_base}-last-line'
        }
        #p_with_citations = []
        ps = soup.find_all('p')
        for p in ps:
            if 'credits-page_front-title' in  p['class'][0]: # to get the book title index
                book_title_tmp = self.text_preprocess(p.text) + '\n'
                self.book_title.append((self.walker, len(book_title_tmp)-2+self.walker))
                self.base_text += book_title_tmp
                self.walker += len(book_title_tmp)

            if 'text-author' in p['class'][0]: # to get the author annotation index
                author_tmp = self.text_preprocess(p.text) + '\n'
                self.author.append((self.walker, len(author_tmp)-2+self.walker))
                self.base_text += author_tmp
                self.walker += len(author_tmp)

            if rt_base in p['class'][0]: # to get the root text or 'tsawa' annotation index (verse form)
                #TODO: one line root text.   
                if p['class'][0] == root_text_classes['first'] or \
                p['class'][0] == root_text_classes['middle']:
                    root_text_tmp += self.text_preprocess(p.text) + '\n'
                    self.base_text += self.text_preprocess(p.text) + '\n'
                elif p['class'][0] == root_text_classes['last']:
                    for s in p.contents:
                        if 'root' in s['class'][0]:
                            root_text_tmp += self.text_preprocess(s.text)
                            self.root_text.append((self.walker,len(root_text_tmp)-1+self.walker))
                            self.walker+= len(root_text_tmp) + 1
                            root_text_tmp = ''
                        else:
                            self.walker+= len(self.text_preprocess(s.text))
                    self.base_text += self.text_preprocess(p.text) + '\n'

            elif 'tibetan-chapter' in p['class'][0]: # to get chapter title index
                chapter_title_tmp = self.text_preprocess(p.text) +'\n'
                self.chapter.append((self.walker, len(chapter_title_tmp)-2+self.walker))
                self.walker+= len(chapter_title_tmp)
                self.base_text += chapter_title_tmp

            elif 'commentary' in p['class'][0] or 'tibetan-regular-indented' in p['class'][0]:

                # travesing through commetary which are in verse form
                if p['class'][0] == com_classes['first'] or \
                p['class'][0] == com_classes['middle']:
                    commentary_tmp += self.text_preprocess(p.text) + '\n'
                    self.base_text += self.text_preprocess(p.text) + '\n'
                elif p['class'][0] == com_classes['last']:
                    commentary_tmp += self.text_preprocess(p.text) + '\n'
                    self.base_text += self.text_preprocess(p.text) + '\n'
                    self.walker+= len(commentary_tmp)
                    commentary_tmp = ''
                #travesing through each span of commentary and regular ptag to search annotations
                else:            
                    p_tmp = ''
                    p_walker=self.walker
                    for s in p.contents:
                        #check for page with no content and skip the page
                        if isinstance(s, str): return '' 
                        #some child are not <span> rather like <a> and some <span> has no 'class' attr
                        try:
                            s['class'][0]
                        except:
                            p_tmp += self.text_preprocess(s.text)
                            continue

                        if 'small' in s['class'][0]: # checking for yigchung annotation
                        # p_tmp += f'{{++*++}}{self.text_preprocess(s.text)}{{++*++}}'
                            if citation_tmp:
                            #citation_tmp += citation_tmp
                                self.citation.append((p_walker,len(citation_tmp)-2+p_walker))
                                p_walker += len(citation_tmp)
                                citation_tmp = ''
                            self.yigchung.append((p_walker,len(self.text_preprocess(s.text))-1+p_walker))
                            p_walker += len(self.text_preprocess(s.text))

                        elif 'external-citations' in s['class'][0]: # checking for citation annotation
                            citation_tmp += self.text_preprocess(s.text)
                        
                        elif 'front-title' in s['class'][0]:
                            if citation_tmp:
                                self.citation.append((p_walker,len(citation_tmp)-2+p_walker))
                                p_walker += len(citation_tmp)
                                citation_tmp = ''
                            p_walker += len(self.text_preprocess(s.text))
                        else:
                            if citation_tmp:
                                self.citation.append((p_walker,len(citation_tmp)-2+p_walker))
                                p_walker += len(citation_tmp)
                                citation_tmp = ''
                            p_walker += len(self.text_preprocess(s.text))

                    #when citation ends the para
                    if citation_tmp: 
                        self.citation.append((p_walker,len(citation_tmp)-2+p_walker))
                        p_walker += len(citation_tmp)
                        citation_tmp = ''
                

                    commentary_tmp = self.text_preprocess(p.text) + '\n'
                    self.base_text += self.text_preprocess(commentary_tmp)
                    self.walker+= len(commentary_tmp)
                    commentary_tmp = ''
                    p_walker = 0

            elif 'sabche' in p['class'][0]: # checking for sabche annotation
                sabche_tmp = ''
                p_with_sabche_tmp = ''
                k = self.walker
                for s in p.contents:
                    try:
                        s['class'][0]
                    except:
                        p_with_sabche_tmp += self.text_preprocess(s.text)
                        continue

                    if 'sabche' in s['class'][0]:
                        sabche_tmp += self.text_preprocess(s.text)
                    
                    elif 'front-tile' in s['class'][0]:
                        k += len(self.text_preprocess(s.text))
                

                #when sabche ends the para
                if sabche_tmp:
                        self.sabche.append((k,len(sabche_tmp)-1+k))
                        sabche_tmp=''             
                self.walker+= len(self.text_preprocess(p.text))+1
                self.base_text += self.text_preprocess(p.text) + '\n'
                k = 0
            elif cit_base in p['class'][0]: # checking for citation annotation first two if for verse form and last for non verse
                if p['class'][0] == cit_classes['first'] or \
                    p['class'][0] == cit_classes['middle']:
                    citation_tmp += self.text_preprocess(p.text) + '\n'
                    self.base_text += self.text_preprocess(p.text)  + '\n'
                elif p['class'][0] == cit_classes['last']:
                    citation_tmp += self.text_preprocess(p.text) + '\n'
                    self.citation.append((self.walker,len(citation_tmp)-2+self.walker))
                    self.base_text += self.text_preprocess(p.text) + '\n'
                    self.walker+= len(citation_tmp)
                    citation_tmp = ''
                elif p['class'][0] == cit_classes['indent']:
                    citation_tmp += self.text_preprocess(p.text) + '\n'
                    self.base_text += self.text_preprocess(p.text) + '\n'
                    self.citation.append(self.walker, len(citation_tmp)-2+self.walker)
                    self.walker+= len(citation_tmp)
                    citation_tmp = ''


    def get_result(self):
        '''
        To return all the result
        '''
        result = {
            'book_title': self.book_title,
            'author': self.author,
            'chapter_title': self.chapter,
            'tsawa': self.root_text,
            'quotation': self.citation,
            'sabche': self.sabche,
            'yigchung': self.yigchung
        }
        return result


    def _get_meta_data(ann):
            return ','.join([self.base_text[a[0]: a[1]+1] for a in ann])


    def get_base_text(self):
        '''
        To return base text of each processed page
        '''
        return self.base_text


    def get_input(self, input_path):
        
        def get_prefix(html_paths):
            self.sku = list(html_paths[0].parents)[1].name
            return sorted(html_paths, key=lambda p: len(p.stem))[0].stem

        def semantic_order(sku, html_path):
            html_fn = html_path.stem
            order = html_fn[len(sku)+1:]
            if order:
                return int(order)
            else:
                return 0

        html_paths = [o for o in input_path.iterdir() if o.suffix == '.xhtml' and o.stem != 'cover']
        sku_sementic_order = partial(semantic_order, get_prefix(html_paths))
        html_paths = sorted(html_paths, key=sku_sementic_order)
        html_paths.insert(0, input_path/'cover.xhtml')

        for html_fn in html_paths:
            yield Path(html_fn).read_text()


    def create_metadata(self, layers):

        def get_text(span):
            return self.base_text[span[0]: span[1]+1].replace('\n', '')

        meta_data = {}
        meta_data['title'] = get_text(layers['book_title'][0])
        meta_data['authors'] = [get_text(span) for span in layers['author']]
        meta_data['sku'] = self.sku
        meta_data['layers'] = [l for l in layers if layers[l]]
        return {'ebook_metadata': meta_data}


    def create_opf(self, input_path, id):
        input_path = Path(input_path)
        self._build_dirs(input_path, id=id)
        (self.dirs['opf_path']/'base').mkdir(exist_ok=True)

        # parse layers
        for html in self.get_input(input_path):
            self.build_layers(html)
        
        # save base-text
        (self.dirs['opf_path']/'base'/f'v001.txt').write_text(self.get_base_text())

        # format and save layer
        vol_layer_path = self.dirs['layers_path']/'v001'
        vol_layer_path.mkdir(exist_ok=True)
        layers = self.get_result()
        for layer, ann in self.format_layer(layers).items():
            if ann['annotations']: 
                layer_fn = vol_layer_path/f'{layer}.yml'
                self.dump(ann, layer_fn)

        # save metatdata
        meta_data = self.create_metadata(layers)
        meta_fn = self.dirs['opf_path']/'meta.yml'
        self.dump(meta_data, meta_fn)

if __name__ == "__main__":
    path = 'bo_crawler/bo_crawler/data/tsadra/data/ebooks/IBA-LG-04-1/OEBPS/'
    formatter = TsadraFormatter(output_path='./test_opf')
    formatter.create_opf(path, 1)
