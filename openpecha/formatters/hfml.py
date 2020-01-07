from copy import deepcopy
from pathlib import Path
import re

from openpecha.formatters.formatter import BaseFormatter
from openpecha.formatters.format import *

class HFMLFormatter(BaseFormatter):
    '''
    OpenPecha Formatter for digitized wooden-printed Pecha based on annotation scheme from Esukhia.
    '''

    def __init__(self, output_path='./output'):
        super().__init__(output_path=output_path)
        self.base_text = ''
        self.vol_walker = 0
        self.pecha_title = []
        self.poti_title = []
        self.chapter_title = []
        self.topic_id = [] # made class variable as it needs to update cross poti
        self.current_topic_id = [] # made class variable as it needs to update cross poti
        self.sub_topic = [] # made class variable as it needs to update cross poti
        self.page = []
        self.error_id = []
        self.abs_er_id = []
        self.notes_id = []
        self.sub_topic_Id = [] # made class variable as it needs to update cross poti
        self.topic_info = []
        self.sub_topic_info = []
        self.cur_sub = []
        self.author_pattern = []
        self.citation_pattern = []
        self.sabche_pattern = []


    def text_preprocess(self, text):
        if text[0] == '\ufeff':
            return text[1:]
        return text


    def get_input(self, input_path):
        fns = list(input_path.iterdir())
        fns_len = len(fns)
        for fn in sorted(fns):
            yield self.text_preprocess(fn.read_text()), fn, fns_len


    def format_layer(self, layers):
        cross_vol_anns = [layers['topic'], layers['sub_topic']]
        non_cross_vol_anns = [layers['page'], layers['correction'], layers['peydurma'], layers['error_candidate']]
        anns = {'cross_vol': cross_vol_anns, 'non_cross_vol': non_cross_vol_anns}
        for ann in anns:
            if ann == 'non_cross_vol':
                for i, (pecha_pg, pecha_correction, pecha_peydurma, pecha_error) in enumerate(zip(*anns[ann])):
                    base_id = f'v{i+1:03}'
                    # Page annotation
                    Pagination = deepcopy(Layer)
                    Pagination['id'] = self.get_unique_id()
                    Pagination['annotation_type'] = 'pagination'
                    Pagination['revision'] = f'{1:05}'
                    for start, end, pg_info, index in pecha_pg:
                        page = deepcopy(Page)
                        page['id'] = self.get_unique_id()
                        page['span']['start'] = start
                        page['span']['end'] = end
                        page['page_index'] = index
                        page['page_info'] = pg_info
                        Pagination['annotations'].append(page)

                    # Correction annotation
                    Correction_layer = deepcopy(Layer)
                    Correction_layer['id'] = self.get_unique_id()
                    Correction_layer['annotation_type'] = 'correction'
                    Correction_layer['revision'] = f'{1:05}'
                    for start, end, sug in pecha_correction:
                        correction = deepcopy(Correction)
                        correction['id'] = self.get_unique_id()
                        correction['span']['start'] = start
                        correction['span']['end'] = end
                        correction['type'] = 'correction'
                        correction['correction'] = sug
                        Correction_layer['annotations'].append(correction)

                    # Error_candidate annotation
                    Error_layer = deepcopy(Layer)
                    Error_layer['id'] = self.get_unique_id()
                    Error_layer['annotation_type'] = 'error_candidate'
                    Error_layer['revision'] = f'{1:05}'
                    for start, end in pecha_error:
                        error = deepcopy(ErrorCandidate)
                        error['id'] = self.get_unique_id()
                        error['span']['start'] = start
                        error['span']['end'] = end
                        Error_layer['annotations'].append(error)

                    # Yigchung annotation
                    Peydurma_layer = deepcopy(Layer)
                    Peydurma_layer['id'] = self.get_unique_id()
                    Peydurma_layer['annotation_type'] = 'note_marker'
                    Peydurma_layer['revision'] = f'{1:05}'
                    for pey in pecha_peydurma:
                        peydurma = deepcopy(Peydurma)
                        peydurma['id'] = self.get_unique_id()
                        peydurma['span']['start'] = pey
                        peydurma['span']['end'] = pey
                        Peydurma_layer['annotations'].append(peydurma)


                    result = {
                        'pagination': Pagination,
                        'correction': Correction,
                        'peydurma': Peydurma_layer,
                        'error_candidate': Error_layer
                    }

                    yield result, base_id
            else:
                Index_layer = deepcopy(Layer)
                Index_layer['id'] = self.get_unique_id()
                Index_layer['annotation_type'] = 'index'
                Index_layer['revision'] = f'{1:05}'
                # loop over each topic
                for topic, sub_topic in zip(*anns[ann]):
                    Topic = deepcopy(Text)
                    Topic['id'] = self.get_unique_id()

                    # loop over each sub_topic
                    for corss_sub_topic in sub_topic:
                        sub_text = deepcopy(SubText)
                        sub_text['id'] = self.get_unique_id()
                        for start, end, vol_id, work in corss_sub_topic:
                            sub_text['work'] = work
                            cross_vol_span = deepcopy(CrossVolSpan)
                            cross_vol_span['vol'] = f'base/v{vol_id:03}'
                            cross_vol_span['span']['start'] = start
                            cross_vol_span['span']['end'] = end

                        Topic['parts'].append(sub_text)

                    for start, end, vol_id, work in topic:
                        Topic['work'] = work
                        cross_vol_span = deepcopy(CrossVolSpan)
                        cross_vol_span['vol'] = f'base/v{vol_id:03}'
                        cross_vol_span['span']['start'] = start
                        cross_vol_span['span']['end'] = end
                        Topic['span'].append(cross_vol_span)

                    Index_layer['annotations'].append(Topic)

                result = {
                    'index': Index_layer
                }

                yield result, None


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

        for pp in ['author_pattern','pecha_title_pattern','poti_title_pattern','chapter_title_pattern']:
            title_pattern = re.search(plist[pp],line)
            if title_pattern:
                total_length += 4
        
        for pp in ['start_cit_pattern','end_cit_pattern']:
            cit_patterns = re.finditer(plist[pp],line)
            for cit_pattern in cit_patterns:
                total_length = total_length+2

        for pp in ['start_sabche_pattern','end_sabche_pattern']:
            sabche_patterns = re.finditer(plist[pp],line)
            for sabche_pattern in sabche_patterns:
                total_length = total_length+2

        return total_length

    def merge(self, start_list, end_list, pattern):
        walker = 0
        while walker<len(end_list):
            if pattern == 'cit':
                self.citation_pattern.append((start_list[walker],end_list[walker]))
            elif pattern == 'sab':
                self.sabche_pattern.append((start_list[walker],end_list[walker]))
            walker +=1
        pass

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

        for pp in ['author_pattern','pecha_title_pattern','poti_title_pattern','chapter_title_pattern']:
            title_pattern = re.search(plist[pp],line)
            if title_pattern:
                if p.start() > title_pattern.start():
                    length_before += 4
        
        for pp in ['start_cit_pattern','end_cit_pattern']:
            cit_patterns = re.finditer(plist[pp],line)
            for cit_pattern in cit_patterns:
                if p.start() > cit_pattern.start():
                    length_before = length_before+2

        for pp in ['start_sabche_pattern','end_sabche_pattern']:
            sabche_patterns = re.finditer(plist[pp],line)
            for sabche_pattern in sabche_patterns:
                if p.start() > sabche_pattern.start():
                    length_before = length_before+2
        

        return length_before


    def base_extract(self, plist, line): 
        '''
        Extract the base text from the given line
        '''
        base_line = line # stores the base_line which is line without annotation
        for p in ['line_pattern','topic_pattern','sub_topic_pattern']:
            base_line = re.sub(plist[p], '', base_line)
        
        for p in ['author_pattern','pecha_title_pattern','poti_title_pattern','chapter_title_pattern']:
            title_pattern = re.search(plist[p],line)
            if title_pattern:
                title = title_pattern[0][3:-1]
                base_line = re.sub(plist[p], title, base_line, 1)
        
        for p in ['start_cit_pattern','end_cit_pattern','start_sabche_pattern','end_sabche_pattern']:
            base_line = re.sub(plist[p],'', base_line, 1)

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

    
    def build_layers(self, m_text, num_vol):
        
        i = 0  # tracker variable through out the text 

        cur_vol_pages = [] # list variable to store page annotation according to base string index eg : [(startPage,endPage)]
        cur_vol_error_id = [] # list variable to store error annotation according to base string index eg : [(es,ee,'suggestion')]
        cur_vol_abs_er_id = [] # list variable to store abs_er annotation 
        note_id = [] # list variable to store note annotation '#"
        pg_info = []
        pg_ann = []
        start_cit_patterns = []
        end_cit_patterns = []
        start_sabche_pattern = []
        end_sabche_pattern = []
        
        pat_list={ 
            'author_pattern': r'\(AU.+?\)',
            'pecha_title_pattern': r'\(K1.+?\)',
            'poti_title_pattern': r'\(K2.+?\)',
            'chapter_title_pattern': r'\(K3.+?\)',
            'page_pattern': r'\[[0-9]+[a-z]{1}\]',
            'line_pattern': r'\[\w+\.\d+\]','topic_pattern':r'\{\w+\}',
            'start_cit_pattern': r'\(G','end_cit_pattern': r'G\)',
            'start_sabche_pattern': r'\(Q','end_sabche_pattern': r'Q\)',
            'root_text_pattern': r'\(M',
            'yigchung_pattern': r'\(Y.+?\)',
            'sub_topic_pattern': r'\{\w+\-\w+\}',
            'error_pattern': r'\(\S+\,\S+\)',
            'abs_er_pattern': r'\[[^0-9].*?\]',
            'note_pattern':r'#'
        }

        start_page = 0 # starting index of page
        end_page = 0 # ending index of page
        start_line = 0 #starting index of line
        end_line = 0 # ending index of line
        start_title = 0 # starting of the title component
        end_title = 0 # ending of the title component
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
                    page_info = line[re.search(pat_list['page_pattern'], line).end():]
                    pg_ann.append(re.search(pat_list['page_pattern'], line)[0][1:-1])
                    pg_info.append(page_info)
                    if len(pg_info)>=2:
                        cur_vol_pages.append((start_page, end_page, pg_info[-2], pg_ann[-2]))
                        if start_page < end_page: # to ignore the empty pages
                            i = i+1  # To accumulate the \n character 
                            end_page = end_page+3
                        self.base_text = self.base_text + '\n'
                elif re.search(pat_list['line_pattern'], line): #checking current line contains line annotation or not
                    start_line = i
                    length = len(line)

                    for pp in ['author_pattern','pecha_title_pattern','poti_title_pattern','chapter_title_pattern']:
                        title_pattern = re.search(pat_list[pp],line)
                        if title_pattern:
                            pat_len_before_ann = self.search_before(title_pattern, pat_list, line)
                            start_title = title_pattern.start()+i-pat_len_before_ann
                            end_title = start_title + len(title_pattern[0]) - 5
                            if pp == 'author_pattern':
                                self.author_pattern.append((start_title,end_title))
                            if pp == 'pecha_title_pattern':
                                self.pecha_title.append((start_title,end_title))
                            if pp == 'poti_title_pattern':
                                self.poti_title.append((start_title,end_title))
                            if pp == 'chapter_title_pattern':
                                self.chapter_title.append((start_title,end_title))

                    if re.search(pat_list['sub_topic_pattern'], line): #checking current line contain sub_topicID annotation or not
                        sub_topic_match = re.search(pat_list['sub_topic_pattern'], line)
                        self.sub_topic_info.append(sub_topic_match[0][1:-1])
                        pat_len_before_ann = self.search_before(sub_topic_match, pat_list, line)
                        if start_sub_topic  == 0:
                            start_sub_topic = end_sub_topic
                            end_sub_topic = sub_topic_match.start()+i-pat_len_before_ann

                            if start_sub_topic < end_sub_topic:
                                if len(self.sub_topic_info) >= 2:
                                    self.sub_topic_Id.append((start_sub_topic, end_sub_topic, self.vol_walker+1, self.sub_topic_info[-2]))
                                    end_sub_topic = end_sub_topic+1
                                else:
                                    self.sub_topic_Id.append((start_sub_topic, end_sub_topic, self.vol_walker+1, self.sub_topic_info[-1]))
                                    end_sub_topic = end_sub_topic+1
                        else:
                            start_sub_topic = end_sub_topic
                            end_sub_topic = sub_topic_match.start()+i-pat_len_before_ann-2

                            if start_sub_topic != end_sub_topic:
                                self.sub_topic_Id.append((start_sub_topic, end_sub_topic, self.vol_walker+1, self.sub_topic_info[-2]))
                                end_sub_topic = end_sub_topic+1

                    if re.search(pat_list['topic_pattern'], line): #checking current line contain topicID annotation or not
                        topic = re.search(pat_list['topic_pattern'], line)
                        pat_len_before_ann = self.search_before(topic, pat_list, line)
                        self.topic_info.append(topic[0][1:-1])
                        start_topic = end_topic
                        end_topic = topic.start()+i-pat_len_before_ann

                        if (start_topic != end_topic or len(self.topic_info)>=2):
                            if len(self.topic_info) >= 2: # as we are ignoring the self.topic[0]
                                if start_topic < end_topic:
                                    self.current_topic_id.append((start_topic, end_topic, self.vol_walker+1, self.topic_info[-2])) # -2 as we need the secondlast item
                            else:
                                self.current_topic_id.append((start_topic, end_topic, self.vol_walker+1, self.topic_info[-1]))
                            self.topic_id.append(self.current_topic_id)
                            self.current_topic_id = []
                            if self.sub_topic_Id and end_sub_topic != end_topic:
                                self.sub_topic_Id.append((end_sub_topic,end_topic,self.vol_walker+1,self.sub_topic_info[-1]))
                            self.sub_topic.append(self.sub_topic_Id)
                            self.sub_topic_Id = []
                            if self.sub_topic_Id:
                                last=self.sub_topic_info[-1]
                                self.sub_topic_info =[]
                                self.sub_topic_info.append(last)
                        
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
                    
                    if re.search(pat_list['start_cit_pattern'],line):
                        start_cits = re.finditer(pat_list['start_cit_pattern'],line)
                        for start_cit in start_cits:
                            pat_len_before_ann=self.search_before(start_cit,pat_list,line)
                            cit_start= start_cit.start()+i-pat_len_before_ann
                            start_cit_patterns.append(cit_start)

                    if re.search(pat_list['end_cit_pattern'],line):
                        end_cits = re.finditer(pat_list['end_cit_pattern'],line)
                        for end_cit in end_cits:
                            pat_len_before_ann=self.search_before(end_cit,pat_list,line)
                            cit_end= end_cit.start()+i-pat_len_before_ann-1
                            end_cit_patterns.append(cit_end)
                        
                    if re.search(pat_list['start_sabche_pattern'],line):
                        start_sabches = re.finditer(pat_list['start_sabche_pattern'],line)
                        for start_sabche in start_sabches:
                            pat_len_before_ann = self.search_before(start_sabche,pat_list,line)
                            sabche_start = start_sabche.start()+i-pat_len_before_ann
                            start_sabche_pattern.append(sabche_start)
                    
                    if re.search(pat_list['end_sabche_pattern'],line):
                        end_sabches = re.finditer(pat_list['end_sabche_pattern'],line)
                        for end_sabche in end_sabches:
                            pat_len_before_ann = self.search_before(end_sabche,pat_list,line)
                            sabche_end = end_sabche.start()+i-pat_len_before_ann-1
                            end_sabche_pattern.append(sabche_end)

                    pat_len_before_ann = self.total_pattern(pat_list, line)
                    end_line = start_line+length-pat_len_before_ann-1
                    i = end_line + 2
                    base_line = self.base_extract(pat_list, line) + '\n'
                    self.base_text += base_line
                    
                    if idx   ==  n_line-1:  # Last line case
                        start_page = end_page
                        start_topic = end_topic
                        start_sub_topic = end_sub_topic
                        if self.sub_topic_Id:
                            self.sub_topic_Id.append((start_sub_topic, i-2, self.vol_walker+1, self.sub_topic_info[-1] if self.sub_topic_info else None))
                        self.current_topic_id.append((start_topic, i-2, self.vol_walker+1, self.topic_info[-1]))
                        cur_vol_pages.append((start_page, i-2, pg_info[-1], pg_ann[-1]))
                        self.page.append(cur_vol_pages)
                        pages = []
                        self.error_id.append(cur_vol_error_id)
                        cur_vol_error_id = []
                        self.abs_er_id.append(cur_vol_abs_er_id)
                        cur_vol_abs_er_id = []
                        self.notes_id.append(note_id)
                        note_id = []
                        self.vol_walker += 1
        
        if num_vol == self.vol_walker: # checks the last volume
            self.topic_id.append(self.current_topic_id)
            self.current_topic_id = []
            self.sub_topic.append(self.sub_topic_Id)

        self.merge(start_cit_patterns, end_cit_patterns, pattern='cit') # The starting and ending of citation is merged
        self.merge(start_sabche_pattern, end_sabche_pattern, pattern = 'sab')
    
    def get_result(self):
        if self.topic_id[0][0][3] == self.topic_id[1][0][3]:
            self.topic_id = self.topic_id[1:]
            self.sub_topic = self.sub_topic[1:]
        self.sub_topic = self.__final_sub_topic(self.sub_topic)
        result = {
            'poti_title': self.poti_title,
            'chapter_title': self.chapter_title,
            'citation': self.citation_pattern,
            'page': self.page, # page variable format (start_index,end_index,pg_Info,pg_ann)
            'topic': self.topic_id,
            'sub_topic': self.sub_topic,
            'sabche': self.sabche_pattern,
            'correction': self.error_id,
            'error_candidate': self.abs_er_id,
            'peydurma': self.notes_id}
       
        return result

    def __final_sub_topic(self, sub_topics):
        '''
        To include all the same subtopic in one list
        '''
        result = []
        cur_topic = []
        cur_sub = []
        sub_topic = sub_topics
        walker = 0;
        for i in range(0, len(sub_topic)):
            if len(sub_topic[i]) != 0:
                cur_sub.append(sub_topic[i][0])
                for walker in range(1, len(sub_topic[i])):
                    if sub_topic[i][walker][3] == sub_topic[i][walker-1][3]:
                        cur_sub.append(sub_topic[i][walker])
                    else:
                        cur_topic.append(cur_sub)
                        cur_sub = []
                        cur_sub.append(sub_topic[i][walker])
                if cur_sub:
                    cur_topic.append(cur_sub)
                    cur_sub = []       
            else:
                cur_topic.append(cur_sub)
                cur_sub = []
            result.append(cur_topic)
            cur_topic = []
        return result

    def get_base_text(self):
        base_text = self.base_text.strip()
        self.base_text = ''

        return base_text


    def new_poti(self,  input_path):
        input_path = Path(input_path)
        self._build_dirs(input_path)
        (self.dirs['opf_path']/'base').mkdir(exist_ok=True)

        for i, (m_text, vol_fn, n_vol) in enumerate(self.get_input(input_path)):
            print(f'[INFO] Processing Vol {i+1:03} of {n_vol}: {vol_fn.name} ...')
            base_id = f'v{i+1:03}'
            self.build_layers(m_text, n_vol)
            # save base_text
            # if (self.dirs['opf_path']/'base'/f'{base_id}.txt').is_file(): continue
            base_text = self.get_base_text()
            (self.dirs['opf_path']/'base'/f'{base_id}.txt').write_text(base_text)

        # save pecha layers
        layers = self.get_result()
        for vol_layers, base_id in self.format_layer(layers):
            if base_id:
                print(f'[INFO] Creating layers for {base_id} ...')
                vol_layer_path = self.dirs['layers_path']/base_id
                vol_layer_path.mkdir(exist_ok=True)
            else:
                print('[INFO] Creating index layer for Pecha ...')

            for layer, ann in vol_layers.items():
                if layer == 'index':
                    layer_fn = self.dirs['opf_path']/f'{layer}.yml'
                else:
                    layer_fn = vol_layer_path/f'{layer}.yml'
                self.dump(ann, layer_fn)


if __name__ == "__main__":
    formatter = HFMLFormatter()
    formatter.new_poti('./tests/data/formatter/hfml/P000002/')