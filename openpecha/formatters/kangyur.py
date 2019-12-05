from uuid import uuid4
import re

from .formatter import BaseFormatter


class kangyurFormatter(BaseFormatter):
    '''
    OpenPecha Formatter for digitized wooden-printed Pecha based on annotation scheme from Esukhia.
    '''

    def __init__(self, output_path='./output'):
        super().__init__(output_path=output_path)
        self.base_text = ''
        self.vol_walker = 0
        self.topic_id = [] # made class variable as it needs to update cross poti
        self.current_topic_id = [] # made class variable as it needs to update cross poti
        self.sub_topic = [] # made class variable as it needs to update cross poti
        self.page = []
        self.error_id = []
        self.abs_er_id = []
        self.notes_id = []
        self.sub_topic_Id = [] # made class variable as it needs to update cross poti

    def text_preprocess(self, text):
        return text
    

    def format_layer(self, layers):
        pages = {'id': None, 'type': 'page', 'rev': "012123", 'log': None, 'content': []}
        lines = {'id': None, 'type': 'line', 'rev': "012123", 'log': None, 'content': []}

        for page, lines in zip(layers['page'], layers['line']):
            page_id = uuid4().hex
            pages['content'].append({
                'id': page_id,
                'span': {
                    'start_char': page[0], 
                    'end_char': page[1]
                }
            })
            for i, line in enumerate(lines):
                line_id = uuid().hex
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


    def total_pattern(self, plist, line):
        '''
        returns the total length of annotation detected in a line
        '''
        total_length = 0 # total length of annotation detected in a line
        for pp in ['line_pattern','topic_pattern','sub_topic_pattern']:
            if re.search(plist[pp], line):
                match_list = re.finditer(plist[pp], line) # list of match object of given pattern in line
                for i in match_list:
                    total_length = total_length + len(i[0])
        if re.search(plist['error_pattern'], line):
            errors = re.finditer(plist['error_pattern'], line) # list of match object of error pattern in line
            for error in errors:
                error_part = error[0].split(',')[0][1:]
                total_length = total_length + (len(error[0])-len(error_part))
            
        if re.search(plist['abs_er_pattern'], line):
            abs_ers = re.finditer(plist['abs_er_pattern'], line) # list of match object of abs_er pattern in line
            for abs_er in abs_ers:
                total_length = total_length + 2
        if re.search(plist['note_pattern'], line):
            abs_errors = re.finditer(plist['note_pattern'], line) # list of match object of note pattern in line
            for abs_error in abs_errors:
                total_length = total_length + 1
        return total_length


    def search_before(self, p, plist, line): 
        '''
        returns the length of annotation detected in a line before the p annotation
        '''
        length_before = 0
        for pp in ['line_pattern','topic_pattern','sub_topic_pattern']:
            if re.search(plist[pp], line):
                match_list = re.finditer(plist[pp], line) # list of match object of given pattern in line
                for i in match_list:
                    if p.start() > i.start():
                        length_before = length_before + len(i[0])
        if re.search(plist['error_pattern'], line):
            errors = re.finditer(plist['error_pattern'], line) # list of match object of error pattern in line
            for error in errors:
                if p.start() > error.start():
                    error_part = error[0].split(',')[0][1:]
                    length_before = length_before + (len(error[0])-len(error_part))
            
        if re.search(plist['abs_er_pattern'], line):
            abs_ers = re.finditer(plist['abs_er_pattern'], line) # list of match object of abs_er pattern in line
            for abs_er in abs_ers:
                if p.start() > abs_er.start():
                    length_before = length_before + 2
        if re.search(plist['note_pattern'], line):
            abs_errors = re.finditer(plist['note_pattern'], line) # list of match object of note pattern in line
            for abs_error in abs_errors:
                if p.start() > abs_error.start():
                    length_before = length_before+1
        return length_before


    def base_extract(self, plist, line): 
        '''
        Extract the base text from the given line
        '''
        base_line = line # stores the base_line which is line without annotation
        for p in ['line_pattern','topic_pattern','sub_topic_pattern']:
            base_line = re.sub(plist[p], '', base_line)
        if re.search(plist['error_pattern'], line):
            errors = re.finditer(plist['error_pattern'], line) # list of match object of error pattern in line
            for error in errors:
                error_part = error[0].split(',')[0][1:]
                base_line = re.sub(plist['error_pattern'], error_part, base_line, 1)
            
        if re.search(plist['abs_er_pattern'], line):
            abs_ers = re.finditer(plist['abs_er_pattern'], line)# list of match object of abs_er pattern in line
            for abs_er in abs_ers:
                base_line = re.sub(plist['abs_er_pattern'], abs_er[0][1:-1], base_line, 1)
        if re.search(plist['note_pattern'], line):
            base_line = re.sub(plist['note_pattern'], '', base_line)
        return base_line

    def get_result(self):

        result = {
            'page': self.page, # page variable format (start_index,end_index,pg_Info,pg_ann)
            'topic':self.topic_id[1:],
            'sub_topic':self.sub_topic[1:],
            'error':self.error_id,
            'abs_er':self.abs_er_id,
            'note':self.notes_id}
        return result

    

    def build_layers(self, m_text, num_vol):
        
        i = 0  # tracker variable through out the text 

        cur_vol_pages = [] # list variable to store page annotation according to base string index eg : [(startPage,endPage)]
        cur_vol_error_id = [] # list variable to store error annotation according to base string index eg : [(es,ee,'suggestion')]
        cur_vol_abs_er_id = [] # list variable to store abs_er annotation 
        note_id = [] # list variable to store note annotation '#"
        pg_info = []
        pg_ann = []
        vol_id = 'v' + str(self.vol_walker%1000)
        pat_list={ 'page_pattern':r'\[[0-9]+[a-z]{1}\]','line_pattern':r'\[\w+\.\d+\]','topic_pattern':r'\{\w+\}',
                    'sub_topic_pattern':r'\{\w+\-\w+\}','error_pattern':r'\(\S+\,\S+\)','abs_er_pattern':r'\[[^0-9].*?\]',
                    'note_pattern':r'#'}

        start_page = 0 # starting index of page
        end_page = 0 # ending index of page
        start_line = 0 #starting index of line
        end_line = 0 # ending index of line
        start_topic = 0 #starting index of topic_Id
        end_topic = 0 # ending index of topic_Id
        start_sub_topic = 0 #starting index of sub_topic_Id
        end_sub_topic = 0 #ending index of sub_topic_Id
        start_error = 0 #starting index of error
        end_error = 0 #ending index of error
        start_abs_er = 0 #starting index of abs_er
        end_abs_er = 0 #ending index of abs_er
        note = 0 #index of notes

        text_lines = m_text.splitlines() # list of all the lines in the text
        n_line = len(text_lines) # number of lines in the text 

        for idx, line in enumerate(text_lines):

                line = line.strip() 
                pat_len_before_ann = 0 # length of pattern recognised before  annotation
                if re.search(pat_list['page_pattern'], line):  # checking current line contains page annotation or not
                    start_page = end_page
                    end_page = end_line
                    page_info = line[re.search(pat_list['page_pattern'],line).end():]
                    pg_ann.append(re.search(pat_list['page_pattern'],line)[0][1:-1])
                    pg_info.append(page_info)
                    if start_page != end_page:
                        cur_vol_pages.append((start_page, end_page, pg_info[-2], pg_ann[-2]  ))
                        i = i+1  # To accumulate the \n character 
                        end_page = end_page+3
                        self.base_text = self.base_text + '\n'
                elif re.search(pat_list['line_pattern'], line): #checking current line contains line annotation or not
                    
                    start_line = i
                    length = len(line)

                    if re.search(pat_list['sub_topic_pattern'], line): #checking current line contain sub_topicID annotation or not
                        sub_topic_match = re.search(pat_list['sub_topic_pattern'], line)
                        pat_len_before_ann = self.search_before(sub_topic_match, pat_list, line)
                        if start_sub_topic  == 0:
                            start_sub_topic = end_sub_topic
                            end_sub_topic = sub_topic_match.start()+i-pat_len_before_ann-1

                            if start_sub_topic != end_sub_topic:
                                self.sub_topic_Id.append((start_sub_topic, end_sub_topic, vol_id))
                                end_sub_topic = end_sub_topic+1

                        else:
                            start_sub_topic = end_sub_topic
                            end_sub_topic = sub_topic_match.start()+i-pat_len_before_ann-2

                            if start_sub_topic != end_sub_topic:
                                self.sub_topic_Id.append((start_sub_topic, end_sub_topic,vol_id))
                                end_sub_topic = end_sub_topic+1

                    if re.search(pat_list['topic_pattern'], line): #checking current line contain topicID annotation or not
                        topic = re.search(pat_list['topic_pattern'], line)
                        pat_len_before_ann = self.search_before(topic, pat_list, line)
                        start_topic = end_topic
                        end_topic = topic.start()+i-pat_len_before_ann

                        if start_topic != end_topic:
                            self.current_topic_id.append((start_topic, end_topic, vol_id))
                            self.topic_id.append(self.current_topic_id)
                            self.current_topic_id = []
                            self.sub_topic.append(self.sub_topic_Id)
                            self.sub_topic_Id = []


                    
                    if re.search(pat_list['error_pattern'], line):   # checking current line contain error annotation or not
                        errors = re.finditer(pat_list['error_pattern'], line)
                        for error in errors:
                            suggestion = error[0].split(',')[1][:-1] # extracting the suggestion component
                            error_part = error[0].split(',')[0][1:]       # extracting the error component
                            pat_len_before_ann = self.search_before(error, pat_list, line)
                            start_error = error.start()+i-pat_len_before_ann

                            end_error = start_error+len(error_part)-1
                            cur_vol_error_id.append((start_error, end_error, suggestion))
                            
                    if re.search(pat_list['abs_er_pattern'], line):
                        abs_ers = re.finditer(pat_list['abs_er_pattern'],line)
                        for abs_er in abs_ers:
                            pat_len_before_ann=self.search_before(abs_er, pat_list, line)
                            start_abs_er = abs_er.start()+i-pat_len_before_ann
                            end_abs_er = start_abs_er + len(abs_er[0])-3
                            cur_vol_abs_er_id.append((start_abs_er,end_abs_er))
        
                    if re.search(pat_list['note_pattern'], line):
                        notes_in_line=re.finditer(pat_list['note_pattern'],line)
                        for notes in notes_in_line:
                            pat_len_before_ann=self.search_before(notes, pat_list, line)
                            note = notes.start()+i-pat_len_before_ann
                            note_id.append(note)
                    
                    pat_len_before_ann = self.total_pattern(pat_list, line)
                    end_line = start_line+length-pat_len_before_ann-1
                    i = end_line + 2
                    base_line = self.base_extract(pat_list, line) + '\n'
                    self.base_text = self.base_text + base_line
                    
                    if idx   ==  n_line-1:  # Last line case
                        start_page = end_page
                        start_topic = end_topic
                        start_sub_topic = end_sub_topic
                        self.sub_topic_Id.append((start_sub_topic, i-2, vol_id))
                        self.current_topic_id.append((start_topic, i -2, vol_id))
                        cur_vol_pages.append((start_page, i-2,pg_info[-1], pg_ann[-1]))
                        self.page.append(cur_vol_pages)
                        pages = []
                        if cur_vol_error_id:
                            self.error_id.append(cur_vol_error_id)
                            cur_vol_error_id = []
                        if cur_vol_abs_er_id:
                            self.abs_er_id.append(cur_vol_abs_er_id)
                            cur_vol_abs_er_id = []
                        if note_id:
                            self.notes_id.append(note_id)
                            note_id = []
                        self.vol_walker += 1
        if num_vol == self.vol_walker: # checks the last volume
            self.topic_id.append(self.current_topic_id)
            self.current_topic_id = []
            self.sub_topic.append(self.sub_topic_Id)

        pass


    def get_base_text(self):

        return self.base_text.strip()