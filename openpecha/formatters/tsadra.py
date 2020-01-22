from openpecha.formatters import BaseFormatter
from bs4 import BeautifulSoup
import re


class TsadraFormatter(BaseFormatter):
    '''
    OpenPecha Formatter for Tsadra DarmaCloud ebooks
    '''

    def __init__(self, output_path='./output'):
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
    
    def preprocess_text(self,text):
        #text = text.replace('{', '')
        return text

    def format_layer(self, layers):
        pass

    def build_layers(self, htmls):
        '''
        To Build the layer
        '''
        soup = BeautifulSoup(htmls, 'html.parser')
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
                book_title_tmp = self.preprocess_text(p.text) + '\n'
                self.book_title.append((self.walker, len(book_title_tmp)-2+self.walker))
                self.base_text += book_title_tmp
                self.walker += len(book_title_tmp)

            if 'text-author' in p['class'][0]: # to get the author annotation index
                author_tmp = self.preprocess_text(p.text) + '\n'
                self.author.append((self.walker, len(author_tmp)-2+self.walker))
                self.base_text += author_tmp
                self.walker += len(author_tmp)

            if rt_base in p['class'][0]: # to get the root text or 'tsawa' annotation index (verse form)
                #TODO: one line root text.   
                if p['class'][0] == root_text_classes['first'] or \
                p['class'][0] == root_text_classes['middle']:
                    root_text_tmp += self.preprocess_text(p.text) + '\n'
                    self.base_text += self.preprocess_text(p.text) + '\n'
                elif p['class'][0] == root_text_classes['last']:
                    for s in p.contents:
                        if 'root' in s['class'][0]:
                            root_text_tmp += self.preprocess_text(s.text)
                            self.root_text.append((self.walker,len(root_text_tmp)-1+self.walker))
                            self.walker+= len(root_text_tmp) + 1
                            root_text_tmp = ''
                        else:
                            self.walker+= len(self.preprocess_text(s.text))
                    self.base_text += self.preprocess_text(p.text) + '\n'

            elif 'tibetan-chapter' in p['class'][0]: # to get chapter title index
                chapter_title_tmp = self.preprocess_text(p.text) +'\n'
                self.chapter.append((self.walker, len(chapter_title_tmp)-2+self.walker))
                self.walker+= len(chapter_title_tmp)
                self.base_text += chapter_title_tmp

            elif 'commentary' in p['class'][0] or 'tibetan-regular-indented' in p['class'][0]:

                # travesing through commetary which are in verse form
                if p['class'][0] == com_classes['first'] or \
                p['class'][0] == com_classes['middle']:
                    commentary_tmp += self.preprocess_text(p.text) + '\n'
                    self.base_text += self.preprocess_text(p.text) + '\n'
                elif p['class'][0] == com_classes['last']:
                    commentary_tmp += self.preprocess_text(p.text) + '\n'
                    self.base_text += self.preprocess_text(p.text) + '\n'
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
                            p_tmp += self.preprocess_text(s.text)
                            continue

                        if 'small' in s['class'][0]: # checking for yigchung annotation
                        # p_tmp += f'{{++*++}}{self.preprocess_text(s.text)}{{++*++}}'
                            if citation_tmp:
                            #citation_tmp += citation_tmp
                                self.citation.append((p_walker,len(citation_tmp)-2+p_walker))
                                p_walker += len(citation_tmp)
                                citation_tmp = ''
                            self.yigchung.append((p_walker,len(self.preprocess_text(s.text))-1+p_walker))
                            p_walker += len(self.preprocess_text(s.text))

                        elif 'external-citations' in s['class'][0]: # checking for citation annotation
                            citation_tmp += self.preprocess_text(s.text)
                        
                        elif 'front-title' in s['class'][0]:
                            if citation_tmp:
                                self.citation.append((p_walker,len(citation_tmp)-2+p_walker))
                                p_walker += len(citation_tmp)
                                citation_tmp = ''
                            p_walker += len(self.preprocess_text(s.text))
                        else:
                            if citation_tmp:
                                self.citation.append((p_walker,len(citation_tmp)-2+p_walker))
                                p_walker += len(citation_tmp)
                                citation_tmp = ''
                            p_walker += len(self.preprocess_text(s.text))

                    #when citation ends the para
                    if citation_tmp: 
                        self.citation.append((p_walker,len(citation_tmp)-2+p_walker))
                        p_walker += len(citation_tmp)
                        citation_tmp = ''
                

                    commentary_tmp = self.preprocess_text(p.text) + '\n'
                    self.base_text += self.preprocess_text(commentary_tmp)
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
                        p_with_sabche_tmp += self.preprocess_text(s.text)
                        continue

                    if 'sabche' in s['class'][0]:
                        sabche_tmp += self.preprocess_text(s.text)
                    
                    elif 'front-tile' in s['class'][0]:
                        k += len(self.preprocess_text(s.text))
                

                #when sabche ends the para
                if sabche_tmp:
                        self.sabche.append((k,len(sabche_tmp)-1+k))
                        sabche_tmp=''             
                self.walker+= len(self.preprocess_text(p.text))+1
                self.base_text += self.preprocess_text(p.text) + '\n'
                k = 0
            elif cit_base in p['class'][0]: # checking for citation annotation first two if for verse form and last for non verse
                if p['class'][0] == cit_classes['first'] or \
                    p['class'][0] == cit_classes['middle']:
                    citation_tmp += self.preprocess_text(p.text) + '\n'
                    self.base_text += self.preprocess_text(p.text)  + '\n'
                elif p['class'][0] == cit_classes['last']:
                    citation_tmp += self.preprocess_text(p.text) + '\n'
                    self.citation.append((self.walker,len(citation_tmp)-2+self.walker))
                    self.base_text += self.preprocess_text(p.text) + '\n'
                    self.walker+= len(citation_tmp)
                    citation_tmp = ''
                elif p['class'][0] == cit_classes['indent']:
                    citation_tmp += self.preprocess_text(p.text) + '\n'
                    self.base_text += self.preprocess_text(p.text) + '\n'
                    self.citation.append(self.walker, len(citation_tmp)-2+self.walker)
                    self.walker+= len(citation_tmp)
                    citation_tmp = ''

        
        pass
       
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

    def get_base_text(self):
        '''
        To return base text of each processed page
        '''
        base_text = self.base_text # to avoid accumulation of base text
        #self.base_text = ''
        return base_text