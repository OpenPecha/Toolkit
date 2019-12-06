from openpecha.formatters import BaseFormatter


class TsadraFormatter(BaseFormatter):
    '''
    OpenPecha Formatter for Tsadra DarmaCloud ebooks
    '''

    def __init__(self, output_path='./output'):
        super().__init__(output_path=output_path)
        self.base_text = ''
        self.walker = 0


    def text_preprocess(self, text):
        
        return text
    
    def __find_titles(self, soup, output):
        i = self.walker # The walker
        # find all titles
        book_title = ''
        chapter_title = ''
        book_title_idx = []
        book_sub_title_idx = []
        chapter_title_idx = []

        front_title = soup.find('p', class_='credits-page_front-title')
        if front_title:
            meta = {'Book Title': '', 'Vol Number': '', 'Book Author': ''}
            meta['Book Title'] = front_title.text
            book_number = soup.find('p', class_='credits-page_front-page---book-number')
            text_author = soup.find('p', class_='credits-page_front-page---text-author')
            if book_number: meta['Vol Number'] = book_number.text
            if text_author: meta['Book Author'] = ' '.join((text_author.text).split(' ')[1:])
            return meta, True
        else:
            book_sub_title = soup.find('p', class_='tibetan-book-sub-title')
            if not book_sub_title:
                book_sub_title = soup.find('p', class_='tibetan-book-title')
                if book_sub_title: book_sub_title = book_sub_title.text
            else:
                book_sub_title = book_sub_title.text
                book_title = soup.find('p', class_='tibetan-book-title')
                if book_title: book_title = book_title.text

            
            chapter = soup.find_all('p', class_=f'tibetan-chapter')
            if chapter: 
                chapter_title = ''.join([c.text for c in chapter])
            else:
                for i in range(1, 4):
                    chapter = soup.find_all('p', class_=f'tibetan-chapter{i}')
                    if chapter: 
                        chapter_title = ''.join([c.text for c in chapter])
                        break

            #write markdown
            if book_title:
                book_title_idx.append((i,len(preprocess_text(book_title)-1)))
                i += len(preprocess_text(book_title)) + 1
                self.base_text += f'{book_title}\n\n'
            if book_sub_title:
                book_sub_title_idx.append((i,len(preprocess_text(book_sub_title)-1)))
                i += len(preprocess_text(book_sub_title)) + 1
                self.base_text += f'{book_sub_title}\n\n'
            if chapter_title:
                chapter_title_idx.append((i,len(preprocess_text(chapter_title_idx))-1))
                i += len(preprocess_text(chapter_title_idx)) + 1
                self.base_text += f'{chapter_title}\n\n'
        output = {
            'book_title': book_title_idx,
            'book_sub_title': book_sub_title_idx,
            'chapter_title': chapter_title_idx
        }

        return output, False

    def __find_the_rest(self, soup, output):

        root_text_tmp = ''
        sabche_tmp = ''
        commentary_tmp = ''
        citation_tmp = ''

        i = self.walker  # The walker
        root_text = [] # list variable to store root text index
        citation = [] # list variable to store citation index
        sabche = [] # list variable to store sabche index
        yigchung = [] # list variable to store yigchung index

        ps = soup.find_all('p')
        for p in ps[output.count('\n')//2:]:
            if rt_base in p['class'][0]:
                #TODO: one line root text.
                if p['class'][0] == root_text_classes['first'] or \
                p['class'][0] == root_text_classes['middle']:
                    root_text_tmp += preprocess_text(p.text) + '\n'
                    self.base_text += preprocess_text(p.text) + '\n'
                elif p['class'][0] == root_text_classes['last']:
                    for s in p.contents:
                        if 'root' in s['class'][0]:
                            root_text_tmp += preprocess_text(s.text)
                            root_text.append((i,len(root_text_tmp)+i))
                            i += len(root_text_tmp) + 1
                            root_text_tmp = ''
                        else:
                            i += len(preprocess_text(s.text))
                    self.base_text += preprocess_text(p.text) + '\n'

            elif 'tibetan-chapter' in p['class'][0]:
                chapter.append((i, len(preprocess_text(p.text))-1+i))
                i += len(preprocess_text(p.text))
                self.base_text += preprocess_text(p.text) + '\n'

            elif 'commentary' in p['class'][0] or 'tibetan-regular-indented' in p['class'][0]:

                if p['class'][0] == com_classes['first'] or \
                p['class'][0] == com_classes['middle']:
                    commentary_tmp += preprocess_text(p.text) + '\n'
                    self.base_text += preprocess_text(p.text) + '\n'
                elif p['class'][0] == com_classes['last']:
                    commentary_tmp += preprocess_text(p.text) + '\n'
                    self.base_text += preprocess_text(p.text) + '\n'
                    i += len(commentary_tmp)
                    commentary_tmp = ''
                
                else:            
                    p_tmp = ''
                    p_walker=i 
                    for s in p.contents:
                        #check for page with no content and skip the page
                        if isinstance(s, str): return '' 
                        #some child are not <span> rather like <a> and some <span> has no 'class' attr
                        try:
                            s['class'][0]
                        except:
                            p_tmp += preprocess_text(s.text)
                            continue

                        if 'small' in s['class'][0]:
                        # p_tmp += f'{{++*++}}{preprocess_text(s.text)}{{++*++}}'
                            if citation_tmp:
                            #citation_tmp += citation_tmp
                                citation.append((p_walker,len(citation_tmp)-1+p_walker))
                                p_walker += len(citation_tmp)
                                citation_tmp = ''
                            yigchung.append((p_walker,len(preprocess_text(s.text))+p_walker))
                            p_walker += len(preprocess_text(s.text))

                        elif 'external-citations' in s['class'][0]:
                            citation_tmp += preprocess_text(s.text)
                            #p_tmp += preprocess_text(s.text)
                        
                        elif 'front-title' in s['class'][0]:
                            if citation_tmp:
                            #citation_tmp += citation_tmp
                                citation.append((p_walker,len(citation_tmp)-1+p_walker))
                                p_walker += len(citation_tmp)
                                citation_tmp = ''
                            p_walker += len(preprocess_text(s.text))
                        else:
                            if citation_tmp:
                            #citation_tmp += citation_tmp
                                citation.append((p_walker,len(citation_tmp)-1+p_walker))
                                p_walker += len(citation_tmp)
                                citation_tmp = ''
                            p_walker += len(preprocess_text(s.text))

                    #when citation ends the para
                    if citation_tmp: 
                        citation.append((p_walker,len(citation_tmp)-1+p_walker))
                        p_walker += len(citation_tmp)
                        citation_tmp = ''
                

                    commentary_tmp = preprocess_text(p.text) + '\n'
                    self.base_text += preprocess_text(commentary_tmp)
                    i += len(commentary_tmp)
                    commentary_tmp = ''
                    p_walker = 0

            elif 'sabche' in p['class'][0]:
                sabche_tmp = ''
                p_with_sabche_tmp = ''
                k = i
                for s in p.contents:
                    try:
                        s['class'][0]
                    except:
                    p_with_sabche_tmp += preprocess_text(s.text)
                    continue

                    if 'sabche' in s['class'][0]:
                        sabche_tmp += preprocess_text(s.text)
                    
                    elif 'front-tile' in s['class'][0]:
                        k += len(preprocess_text(s.text))
                

                #when sabche ends the para
                if sabche_tmp:
                        sabche.append((k,len(sabche_tmp)+k))
                        sabche_tmp=''             
                i += len(preprocess_text(p.text))+1
                self.base_text += preprocess_text(p.text) + '\n'
                k = 0
            elif cit_base in p['class'][0]:
                if p['class'][0] == cit_classes['first'] or \
                    p['class'][0] == cit_classes['middle']:
                    citation_tmp += preprocess_text(p.text) + '\n'
                    self.base_text += preprocess_text(p.text) + '\n'
                elif p['class'][0] == cit_classes['last']:
                    citation_tmp += preprocess_text(p.text) + '\n'
                    citation.append((i,len(citation_tmp)-1+i))
                    self.base_text += preprocess_text(p.text) + '\n'
                    i += len(citation_tmp)
                    citation_tmp = ''
                elif p['class'][0] == cit_classes['indent']:
                    citation_tmp += preprocess_text(p.text) + '\n'
                    self.base_text += preprocess_text(p.text) + '\n'
                    citation.append(i, len(citation_tmp)-1+i)
                    i += len(citation_tmp)
                    citation_tmp = ''

            else:
                i += len(preprocess_text(p.text))
        
        output = {
        'tsawa': root_text,
        'quotes': citation,
        'sabche': sabche,
        'yigchung': yigchung
        }

        return output


    def format_layer(self, layers):
        pass


    def build_layers(self, htmls):

        tsawa_idx = []
        quotes_idx = []
        sabche_idx = []
        yigchung_idx = []

        for html in htmls:
            soup = BeautifulSoup(html, 'html.parser')
            title_output, is_front_page = find_titles(soup, output)
            if not is_front_page:
                rest_output = self.find_the_rest(self, soup, output)
                tsawa_idx.append(rest_output['tsawa'])
                quotes_idx.append(rest_output['quotes'])
                sabche_idx.append(rest_output['sabche'])
                yigchung_idx.append(rest_output['yigchung'])
        
        rest_result={
            'tsawa': tsawa_idx,
            'quotes': quotes_idx,
            'sabche': sabche_idx,
            'yigchung': yigchung_idx
        }

        result = dict(title_output)
        result.update(rest_result)

        return result
        


    def get_base_text(self, m_text):

        return self.base_text