import re
import itertools

from .formatter import BaseFormatter

class kangyurFormatter(BaseFormatter):
    '''
    OpenPecha Formatter for digitized wooden-printed Pecha based on annotation scheme from Esukhia.
    '''

    def __init__(self, output_path='./output'):
        super().__init__(output_path=output_path)
        self.base_text = ''


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


    def total_pattern(self, plist, line): # returns the total length of annotation detected in a line
        tl=0
        for pp in dict(itertools.islice(plist.items(),1, 4)):
            if re.search(plist[pp],line):
                t=re.finditer(plist[pp],line)
                for i in t:
                    tl=tl+len(i[0])
        if re.search(plist['error_pattern'],line):
            t1=re.finditer(plist['error_pattern'],line)
            for s in t1:
                error=s[0].split(',')[0][1:]
                tl=tl+(len(s[0])-len(error))
            
        if re.search(plist['yigchung_pattern'],line):
            t2=re.finditer(plist['yigchung_pattern'],line)
            for k in t2:
                tl=tl+2
        if re.search(plist['unreadable_pattern'],line):
            t3=re.finditer(plist['unreadable_pattern'],line)
            for l in t3:
                tl=tl+1
        return tl


    def search_before(self, p, plist, line): # returns the length of annotation detected in a line before the p annotation
        ll=0
        for pp in dict(itertools.islice(plist.items(),1, 4)):
            if re.search(plist[pp],line):
                t=re.finditer(plist[pp],line)
                for i in t:
                    if p.start()>i.start():
                        ll=ll+len(i[0])
        if re.search(plist['error_pattern'],line):
            t1=re.finditer(plist['error_pattern'],line)
            for s in t1:
                if p.start()>s.start():
                    error=s[0].split(',')[0][1:]
                    ll=ll+(len(s[0])-len(error))
            
        if re.search(plist['yigchung_pattern'],line):
            t2=re.finditer(plist['yigchung_pattern'],line)
            for j in t2:
                if p.start()>j.start():
                    ll=ll+2
        if re.search(plist['unreadable_pattern'],line):
            t3=re.finditer(plist['unreadable_pattern'],line)
            for k in t3:
                if p.start()>k.start():
                    ll=ll+1
        return ll

    def base_extract(self, plist, line): # Extract the base text from the given line
        t = line
        for p in dict(itertools.islice(plist.items(),1, 4)):
            t = re.sub(plist[p], '', t)
        if re.search(plist['error_pattern'], line):
            t1 = re.finditer(plist['error_pattern'], line)
            for s in t1:
                error = s[0].split(',')[0][1:]
                t = re.sub(plist['error_pattern'], error, t, 1)
            
        if re.search(plist['yigchung_pattern'], line):
            t2 = re.finditer(plist['yigchung_pattern'], line)
            for k in t2:
                t = re.sub(plist['yigchung_pattern'], k[0][1:-1], t, 1)
        if re.search(plist['unreadable_pattern'], line):
            t = re.sub(plist['unreadable_pattern'], '', t)
        return t
    
    def build_layers(self, m_text):
        
        i = 0  # tracker variable through out the text 

        Line = [] # list of lines in a page eg : [[(sl1,el1),(sl2,el2)],[(sl1,el1),(sl2,el2),(sl3,el3)]]
        chapter = [] # list of chapters in a textID eg : [[(27, 1351), (1352, 1494), (1495, 2163)]]
        pages = [] # list variable to store page annotation according to base string index eg : [(startPage,endPage)]
        lines = [] # list variable to store line annotation according to base string index eg : [(startLine,endLine)]
        text_id = [] # list variable to store text id annotation according to base string index eg : [(st,et)]
        chapter_id = [] # list variable to store chapter id annotation according to base string index eg : [(sc,ec)]
        error_id = [] # list variable to store error annotation according to base string index eg : [(es,ee,'suggestion')]
        yigchung_id = [] # list variable to store yigchung annotation 
        unreadable_id = [] # list variable to store unreadable annotation '#"

        pat_list={ 'page_pattern':'\[[0-9]+[a-z]{1}\]','line_pattern':'\[\w+\.\d+\]','text_pattern':'\{\w+\}',
                    'chapter_pattern':'\{\w+\-\w+\}','error_pattern':'\(\S+\,\S+\)','yigchung_pattern':'\[[^0-9].*?\]',
                    'unreadable_pattern':'#'}

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
        start_yigchung = 0 #starting index of yigchung
        end_yigchung = 0 #ending index of yigchung
        unreadable=0 #index of unreadable 

        text_lines = m_text.splitlines() # list of all the lines in the text
        n_line = len(text_lines) # number of lines in the text 

        for idx, line in enumerate(text_lines):

                line = line.strip() 

                l1 = 0 #length of pattern recognised before text annotation
                l2 = 0 #length of pattern recognised before chapter annotation
                l3 = 0 #length of pattern recognised before error annotation
                l4 = 0 #length of pattern recognised before yigchung annotation
                l5 = 0 #length of pattern recognised before unreadable annotation
                l6 = 0 #length of pattern recognised in a line

                if re.search(pat_list['page_pattern'], line):  # checking current line contains page annotation or not
                    start_page = end_page
                    end_page = end_line

                    if start_page != end_page:
                        Line.append(lines)
                        pages.append((start_page, end_page))
                        i = i+1  # To accumulate the \n character 
                        end_page = end_page+3
                        lines = []
                        self.base_text = self.base_text + '\n'
                elif re.search(pat_list['line_pattern'], line): #checking current line contains line annotation or not
                    #x = re.search(pat2, line)
                    start_line = i
                    length = len(line)

                    if re.search(pat_list['text_pattern'], line): #checking current line contain textID annotation or not
                        y = re.search(pat_list['text_pattern'], line)
                        l1=self.search_before(y,pat_list,line)
                        h = y.start()
                        start_text = end_text
                        end_text = h+i-l1

                        if start_text != end_text:
                            text_id.append((start_text, end_text))
                            chapter.append(chapter_id[1:])
                            chapter_id = []

                    if re.search(pat_list['chapter_pattern'], line): #checking current line contain chapterID annotation or not
                        z = re.search(pat_list['chapter_pattern'], line)
                        #l3 = len(z[0])
                        k = z.start()
                        l2=self.search_before(z,pat_list,line)
                        if start_chapter  == 0:
                            start_chapter = end_chapter
                            end_chapter = k+i-l2-1

                            if start_chapter != end_chapter:
                                chapter_id.append((start_chapter, end_chapter))
                                end_chapter = end_chapter+1

                        else:
                            start_chapter = end_chapter
                            end_chapter = k+i-l2-2

                            if start_chapter != end_chapter:
                                chapter_id.append((start_chapter, end_chapter))
                                end_chapter = end_chapter+1
                    
                    if re.search(pat_list['error_pattern'], line):   # checking current line contain error annotation or not
                        t=re.finditer(pat_list['error_pattern'],line)
                        for s in t:
                            suggestion = s[0].split(',')[1][:-1] # extracting the suggestion component
                            error = s[0].split(',')[0][1:]       # extracting the error component
                            l3=self.search_before(s,pat_list,line)
                            start_error = s.start()+i-l3

                            end_error = start_error+len(error)-1
                            error_id.append((start_error, end_error, suggestion))
                            #l4 = len(s[0])-len(error)             # finding the length of recognised pattern excluding the error

                    if re.search(pat_list['yigchung_pattern'], line):
                        t1=re.finditer(pat_list['yigchung_pattern'],line)
                        for j in t1:
                            l4=self.search_before(j,pat_list,line)
                            start_yigchung = j.start()+i-l4
                        
                            end_yigchung = start_yigchung + len(j[0])-3
                            yigchung_id.append((start_yigchung,end_yigchung))
                            #l5 = 2

                    if re.search(pat_list['unreadable_pattern'], line):
                        t2=re.finditer(pat_list['unreadable_pattern'],line)
                        for k in t2:
                            l5=self.search_before(k,pat_list,line)
                            unreadable=k.start()+i-l5
                            unreadable_id.append(unreadable)
                        

                    l6=self.total_pattern(pat_list,line)
                    end_line = start_line+length-l6-1
                    lines.append((start_line, end_line))
                    i = end_line + 2
                    temp = self.base_extract(pat_list, line) + '\n'
                    self.base_text = self.base_text + temp
                    temp = ''

                    if idx   ==  n_line-1:  # Last line case
                        start_page = end_page
                        start_text = end_text
                        start_chapter = end_chapter
                        text_id.append((start_text, i-2))
                        chapter_id.append((start_chapter, i-2))
                        pages.append((start_page, i-2))
                        Line.append(lines)
                        chapter.append(chapter_id[1:])

        result = {
            'page': pages,
            'line': Line ,
            'text':text_id[1:],
            'sub_text':chapter[1:],
            'error':error_id,
            'yigchung':yigchung_id,
            'unreadable':unreadable_id
        }

        return result


    def get_base_text(self):
        
        return self.base_text.strip()


