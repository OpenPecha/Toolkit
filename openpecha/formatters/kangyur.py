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

        i = 0  # tracker variable through out the text 

        Line = [] # list of lines in a page eg : [[(sl1,el1),(sl2,el2)],[(sl1,el1),(sl2,el2),(sl3,el3)]]
        chapter = [] # list of chapters in a textID eg : [[(27, 1351), (1352, 1494), (1495, 2163)]]
        pages = [] # list variable to store page annotation according to base string index eg : [(startPage,endPage)]
        lines = [] # list variable to store line annotation according to base string index eg : [(startLine,endLine)]
        text_id = [] # list variable to store text id annotation according to base string index eg : [(st,et)]
        chapter_id = [] # list variable to store chapter id annotation according to base string index eg : [(sc,ec)]
        error_id = [] # list variable to store error annotation according to base string index eg : [(es,ee,'suggestion')]

        pat1 = "\[\w+\]" # regular expression to detect page annotation
        pat2 = "\[\w+\.\d+\]" # regular expression to detect line annotation
        pat3 = "\{\w+\}" # regular expression to detect textid annotation
        pat4 = "\{\w+\-\w+\}" #regular expression to detect chapterID annotation
        pat5 = "\(\S+\,\S+\)" # regular expression to detect error annotation

        start_page = 0 # starting index of page
        end_page = 0 # ending index of page
        start_line = 0 #starting index of line
        end_line = 0 # ending index of line
        start_text = 0 #starting index of text_Id
        end_text = 0 # ending index of text_Id
        start_chapter = 0 #starting index of chapter_Id
        end_chapter = 0 #ending index of chapter_Id
        start_error = 0 #starting index of error
        end_error = 0 #ending index of error

        text_lines = text.splitlines() # list of all the lines in the text
        n_line = len(text_lines) # number of lines in the text 

        for idx, line in enumerate(text_lines):

                line = line.strip() 

                l1 = 0 #length of line pattern
                l2 = 0 #length of textId pattern
                l3 = 0 #length of chapterID pattern
                l4 = 0 #length of error pattern

                if re.search(pat1, line):  # checking current line contains page annotation or not
                    start_page = end_page
                    end_page = end_line

                    if start_page != end_page:
                        Line.append(lines)
                        pages.append((start_page, end_page))
                        i = i+1  # To accumulate the \n character 
                        end_page = end_page+3
                        lines = []

                elif re.search(pat2, line): #checking current line contains line annotation or not
                    x = re.search(pat2, line)
                    l1 = len(x[0])
                    start_line = i
                    length = len(line)

                    if re.search(pat3, line): #checking current line contain textID annotation or not
                        y = re.search(pat3, line)
                        l2 = len(y[0])
                        h = y.start()
                        start_text = end_text
                        end_text = h-6+i

                        if start_text != end_text:
                            text_id.append((start_text, end_text))
                            chapter.append(chapter_id[1:])
                            chapter_id = []

                    if re.search(pat4, line): #checking current line contain chapterID annotation or not
                        z = re.search(pat4, line)
                        l3 = len(z[0])
                        k = z.start()

                        if start_chapter  == 0:
                            start_chapter = end_chapter
                            end_chapter = k-l1-l2+i-1

                            if start_chapter != end_chapter:
                                chapter_id.append((start_chapter, end_chapter))
                                end_chapter = end_chapter+1

                        else:
                            start_chapter = end_chapter
                            end_chapter = k-l1-l2+i-2

                            if start_chapter != end_chapter:
                                chapter_id.append((start_chapter, end_chapter))
                                end_chapter = end_chapter+1

                    if re.search(pat5, line):   # checking current line contain error annotation or not
                        s = re.search(pat5, line)
                        suggestion = s[0].split(',')[1][:-1] # extracting the suggestion component
                        error = s[0].split(',')[0][1:]       # extracting the error component
                        start_error = s.start()+i-l1-l2-l3
                        end_error = start_error+len(error)-1
                        error_id.append((start_error, end_error, suggestion))
                        l4 = len(s[0])-len(error)             # finding the length of recognised pattern excluding the error
                    
                    end_line = length-l1-l2-l3-l4+start_line-1
                    lines.append((start_line, end_line))
                    i = end_line+2
                    
                    if idx   ==  n_line-1:  # Last line case
                        start_page = end_page
                        start_text = end_text
                        start_chapter = end_chapter
                        text_id.append((start_text, i-2))
                        chapter_id.append((start_chapter, i-2))
                        pages.append((start_page, i-2))
                        Line.append(lines)
                        chapter.append(chapter_id[1:])

        return {'page': pages, 'line': Line ,'text':text_id[1:],'sub_text':chapter[1:],'error':error_id}


    def get_base_text(self, m_text):
        pass