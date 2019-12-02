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
            
        if re.search(plist['yigchung_pattern'], line):
            yigchungs = re.finditer(plist['yigchung_pattern'], line) # list of match object of yigchung pattern in line
            for yigchung in yigchungs:
                total_length = total_length + 2
        if re.search(plist['absolute_error_pattern'], line):
            abs_errors = re.finditer(plist['absolute_error_pattern'], line) # list of match object of absolute error pattern in line
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
                    length_before = length_before + (len(s[0])-len(error_part))
            
        if re.search(plist['yigchung_pattern'], line):
            yigchungs = re.finditer(plist['yigchung_pattern'], line) # list of match object of yigchung pattern in line
            for yigchung in yigchungs:
                if p.start() > yigchung.start():
                    length_before = length_before + 2
        if re.search(plist['absolute_error_pattern'], line):
            abs_errors = re.finditer(plist['absolute_error_pattern'], line) # list of match object of absolute error pattern in line
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
            
        if re.search(plist['yigchung_pattern'], line):
            yigchungs = re.finditer(plist['yigchung_pattern'], line)# list of match object of yigchung pattern in line
            for yigchung in yigchungs:
                base_line = re.sub(plist['yigchung_pattern'], yigchung[0][1:-1], base_line, 1)
        if re.search(plist['absolute_error_pattern'], line):
            base_line = re.sub(plist['absolute_error_pattern'], '', base_line)
        return base_line
    
    def build_layers(self, m_text):
        
        i = 0  # tracker variable through out the text 

        sub_topic = [] # list of sub_topics in a topicID eg : [[(27, 1351), (1352, 1494), (1495, 2163)]]
        pages = [] # list variable to store page annotation according to base string index eg : [(startPage,endPage)]
        topic_id = [] # list variable to store topic id annotation according to base string index eg : [(st,et)]
        sub_topic_id = [] # list variable to store sub_topic id annotation according to base string index eg : [(sc,ec)]
        error_id = [] # list variable to store error annotation according to base string index eg : [(es,ee,'suggestion')]
        yigchung_id = [] # list variable to store yigchung annotation 
        absolute_error_id = [] # list variable to store absolute_error annotation '#"

        pat_list={ 'page_pattern':r'\[[0-9]+[a-z]{1}\]','line_pattern':r'\[\w+\.\d+\]','topic_pattern':r'\{\w+\}',
                    'sub_topic_pattern':r'\{\w+\-\w+\}','error_pattern':r'\(\S+\,\S+\)','yigchung_pattern':r'\[[^0-9].*?\]',
                    'absolute_error_pattern':r'#'}

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
        start_yigchung = 0 #starting index of yigchung
        end_yigchung = 0 #ending index of yigchung
        absolute_error=0 #index of absolute_error 

        text_lines = m_text.splitlines() # list of all the lines in the text
        n_line = len(text_lines) # number of lines in the text 

        for idx, line in enumerate(text_lines):

                line = line.strip() 
                pat_len_before_ann = 0 # length of pattern recognised before  annotation
                if re.search(pat_list['page_pattern'], line):  # checking current line contains page annotation or not
                    start_page = end_page
                    end_page = end_line

                    if start_page != end_page:
                        pages.append((start_page, end_page))
                        i = i+1  # To accumulate the \n character 
                        end_page = end_page+3
                        self.base_text = self.base_text + '\n'
                elif re.search(pat_list['line_pattern'], line): #checking current line contains line annotation or not
                    
                    start_line = i
                    length = len(line)

                    if re.search(pat_list['topic_pattern'], line): #checking current line contain topicID annotation or not
                        topic = re.search(pat_list['topic_pattern'], line)
                        pat_len_before_ann = self.search_before(topic, pat_list, line)
                        start_topic = end_topic
                        end_topic = topic.start()+i-pat_len_before_ann

                        if start_topic != end_topic:
                            topic_id.append((start_topic, end_topic))
                            sub_topic.append(sub_topic_id[1:])
                            sub_topic_id = []

                    if re.search(pat_list['sub_topic_pattern'], line): #checking current line contain sub_topicID annotation or not
                        sub_topic_match = re.search(pat_list['sub_topic_pattern'], line)
                        pat_len_before_ann = self.search_before(sub_topic_match, pat_list, line)
                        if start_sub_topic  == 0:
                            start_sub_topic = end_sub_topic
                            end_sub_topic = sub_topic_match.start()+i-pat_len_before_ann-1

                            if start_sub_topic != end_sub_topic:
                                sub_topic_id.append((start_sub_topic, end_sub_topic))
                                end_sub_topic = end_sub_topic+1

                        else:
                            start_sub_topic = end_sub_topic
                            end_sub_topic = sub_topic_match.start()+i-pat_len_before_ann-2

                            if start_sub_topic != end_sub_topic:
                                sub_topic_id.append((start_sub_topic, end_sub_topic))
                                end_sub_topic = end_sub_topic+1
                    
                    if re.search(pat_list['error_pattern'], line):   # checking current line contain error annotation or not
                        errors = re.finditer(pat_list['error_pattern'], line)
                        for error in errors:
                            suggestion = error[0].split(',')[1][:-1] # extracting the suggestion component
                            error_part = error[0].split(',')[0][1:]       # extracting the error component
                            pat_len_before_ann = self.search_before(error, pat_list, line)
                            start_error = error.start()+i-pat_len_before_ann

                            end_error = start_error+len(error_part)-1
                            error_id.append((start_error, end_error, suggestion))
                            
                    if re.search(pat_list['yigchung_pattern'], line):
                        yigchungs = re.finditer(pat_list['yigchung_pattern'],line)
                        for yigchung in yigchungs:
                            pat_len_before_ann=self.search_before(yigchung, pat_list, line)
                            start_yigchung = yigchung.start()+i-pat_len_before_ann
                            end_yigchung = start_yigchung + len(yigchung[0])-3
                            yigchung_id.append((start_yigchung,end_yigchung))
        
                    if re.search(pat_list['absolute_error_pattern'], line):
                        abs_errors=re.finditer(pat_list['absolute_error_pattern'],line)
                        for abs_error in abs_errors:
                            pat_len_before_ann=self.search_before(abs_error, pat_list, line)
                            absolute_error = abs_error.start()+i-pat_len_before_ann
                            absolute_error_id.append(absolute_error)
                    
                    pat_len_before_ann = self.total_pattern(pat_list, line)
                    end_line = start_line+length-pat_len_before_ann-1
                    i = end_line + 2
                    base_line = self.base_extract(pat_list, line) + '\n'
                    self.base_text = self.base_text + base_line
                    
                    if idx   ==  n_line-1:  # Last line case
                        start_page = end_page
                        start_topic = end_topic
                        start_sub_topic = end_sub_topic
                        topic_id.append((start_topic, i-2))
                        sub_topic_id.append((start_sub_topic, i-2))
                        pages.append((start_page, i-2))
                        sub_topic.append(sub_topic_id[1:])

        result = {
            'page': pages,
            'topic':topic_id[1:],
            'sub_topic':sub_topic[1:],
            'error':error_id,
            'yigchung':yigchung_id,
            'absolute_error':absolute_error_id
        }

        return result


    def get_base_text(self):
        
        return self.base_text.strip()


