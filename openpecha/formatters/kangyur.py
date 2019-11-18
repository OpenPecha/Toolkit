import re

from .formatter import BaseFormatter

class kangyurFormatter(BaseFormatter):
    '''
    OpenPecha Formatter for digitized wooden-printed Pecha based on annotation scheme from Esukhia.
    '''

    def text_preprocess(self, text):
        return text
    

    def format_layer(self, layers):
        pages = {'id': None, 'type': 'page', 'rev': "012123", 'log': None, 'content': []}
        lines = {'id': None, 'type': 'line', 'rev': "012123", 'log': None, 'content': []}

        for page, lines in zip(layers['page'], layers['line']):
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
                    'part_of': f'page/{page_id}',
                    'part_index': i+1
                })

        return {'page': pages, 'line': lines}


    
    def build_layers(self, text):
        i=0
        Line=[]
        pages=[] # list variable to store page annotation according to base string index
        lines=[] # list variable to store line annotation according to base string index
        text_id=[] # list variable to store text id annotation according to base string index
        chapter_id=[] # list variable to store chapter id annotation according to base string index
        pat1="\[\w+\]" # regular expression to detect page annotation
        pat2="\[\w+\.\d+\]" # regular expression to detect line annotation
        pat3="\{\w+\}" # regular expression to detect textid annotation
        pat4="{\w+\-\w+\}" #regular expression to detect chapterID annotation
        start_page=0 # starting index of page
        end_page=0 # ending index of page
        start_line=0 #starting index of line
        end_line=0 # ending index of line
        start_text=0 #starting index of text_Id
        end_text=0 # ending index of text_Id
        start_chapter=0 #starting index of chapter_Id
        end_chapter=0 #ending index of chapter_Id
        text_lines=text.splitlines()
        n_line=len(text_lines)
        for idx,line in enumerate(text_lines):
                line=line.strip()
                l1=0 #length of line pattern
                l2=0 #length of textId pattern
                l3=0 #length of chapterID pattern
                if(re.search(pat1,line)):  # checking current line contains page annotation or not
                    start_page=end_page
                    end_page=end_line
                    if(start_page!=end_page):
                        Line.append(lines)
                        pages.append((start_page,end_page))
                        i=i+1
                        end_page=end_page+3
                        lines=[]
                elif(re.search(pat2,line)): #checking current line contains line annotation or not
                    x=re.search(pat2,line)
                    l1=len(x[0])
                    start_line=i
                    length=len(line)
                    if(re.search(pat3,line)): #checking current line contain textID annotation or not

                        y=re.search(pat3,line)
                        l2=len(y[0])
                        h=y.start()
                        start_text=end_text
                        end_text=h-6+i
                        if(start_text!=end_text):
                            text_id.append((start_text,end_text))
                
                    if(re.search(pat4,line)): #checking current line contain chapterID annotation or not
                        z=re.search(pat4,line)
                        l3=len(z[0])
                        k=z.start()
                        start_chapter=end_chapter
                        end_chapter=k-l1-l2+i
                        if(start_chapter!=end_chapter):
                            chapter_id.append((start_chapter,end_chapter))
                    end_line=length-l1-l2-l3+start_line-1
                    lines.append((start_line,end_line))
                    i=end_line+2
                    if(idx == n_line-1):
                        start_page=end_page
                        start_text=end_text
                        start_chapter=end_chapter
                        text_id.append((start_text,i))
                        chapter_id.append((start_chapter,i))
                        pages.append((start_page,i-2))
                        Line.append(lines)

                    

        return {'page': pages, 'line': Line}


    def get_base_text(self, m_text):
        pass