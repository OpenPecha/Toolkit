"""
Formatter for HFML annotations in the text

This module implements all classes necessary to format HFML annotation to OpenPecha format.
HFML (Human Friendly Markup Language) contains tagset used for structuring and annotating the text.
"""
import re
from json import encoder
from pathlib import Path

import yaml

from ..utils import Vol2FnManager, dump_yaml, load_yaml
from .formatter import BaseFormatter
from .layers import *
from .layers import AnnType, _attr_names


class HFMLFormatter(BaseFormatter):
    """
    OpenPecha Formatter for digitized wooden-printed Pecha based on annotation scheme from Esukhia.
    """

    def __init__(self, output_path=None, metadata=None, is_book=False):
        super().__init__(output_path, metadata)
        self.is_book = is_book
        self.base_text = ""
        self.vol_walker = 0
        self.book_title = []
        self.book_number = []
        self.poti_title = []
        self.author = []
        self.chapter_title = []
        self.topic_id = []  # made class variable as it needs to update cross poti
        self.current_topic_id = (
            []
        )  # made class variable as it needs to update cross poti
        self.sub_topic = []  # made class variable as it needs to update cross poti
        self.page = []
        self.error_id = []
        self.archaic_word_id = []
        self.abs_er_id = []
        self.notes_id = []
        self.sub_topic_Id = []  # made class variable as it needs to update cross poti
        self.topic_info = []
        self.topic_local_id = []
        self.sub_topic_info = []
        self.sub_topic_local_id = []
        self.cur_sub = []
        self.author_pattern = []
        self.citation_pattern = []
        self.sabche_pattern = []
        self.tsawa_pattern = []
        self.yigchung_pattern = []
        self.durchen_pattern = []

    def text_preprocess(self, text):
        if text[0] == "\ufeff":
            text = text[1:]

        if not self.is_book:
            return text

        p = r"\[p\]"
        lines = text.splitlines()
        result_text = ""
        para = False
        for line in lines:
            if re.search(p, line):
                if para:
                    para = False
                    result_text += "\n"
                else:
                    para = True
            elif re.search(p, line) is None:
                if para:
                    result_text += line
                else:
                    result_text += line + "\n"
        return result_text

    def _load_metadata(self):
        if self.metadata:
            return self.metadata
        meta_fn = self.dirs["opf_path"] / "meta.yml"
        if meta_fn.is_file():
            return load_yaml(meta_fn)
        else:
            return {}

    def _save_metadata(self, **kwargs):
        meta_fn = self.dirs["opf_path"] / "meta.yml"
        if kwargs:
            self.metadata.update(kwargs)
        if "id" not in self.metadata:
            self.metadata["id"] = f"opecha:{self.pecha_path.name}"
        dump_yaml(self.metadata, meta_fn)

    def get_input(self, input_path):
        fns = list(input_path.iterdir())
        fns_len = len(fns)
        for fn in sorted(fns):
            yield self.text_preprocess(fn.read_text()), fn.name, fns_len

    def total_pattern(self, pat_list, annotated_line):
        """ It calculates the length of all the annotation detected in a line.

        Args:
            pat_list (dict): It contains all the annotation's regex pattern as value and name of annotation as key.
            annotated_line (str): It contains the annotated line to be process.

        Return:
            total_length (int): It accumulates as annotations are detected in the line.
        """
        total_length = 0  # total length of annotation detected in a line
        for pattern in [
            "line_pattern",
            "topic_pattern",
            "sub_topic_pattern",
            "note_pattern",
            "start_cit_pattern",
            "start_sabche_pattern",
            "start_tsawa_pattern",
            "start_yigchung_pattern",
            "start_durchen_pattern",
        ]:
            if re.search(pat_list[pattern], annotated_line):
                match_list = re.finditer(
                    pat_list[pattern], annotated_line
                )  # list of match object of given pattern in line
                for match in match_list:
                    total_length = total_length + len(match[0])

        if re.search(pat_list["error_pattern"], annotated_line):
            errors = re.finditer(
                pat_list["error_pattern"], annotated_line
            )  # list of match object of error pattern in line
            for error in errors:
                if error.group(1):
                    starting_point = 2
                else:
                    starting_point = 1
                error_part = error[0].split(",")[0][starting_point:]
                total_length = total_length + (len(error[0]) - len(error_part))

        if re.search(pat_list["archaic_word_pattern"], annotated_line):
            archaic_words = re.finditer(
                pat_list["archaic_word_pattern"], annotated_line
            )  # list of match object of error pattern in line
            for archaic_word in archaic_words:
                if archaic_word.group(1):
                    starting_point = 2
                else:
                    starting_point = 1
                archaic_part = archaic_word[0].split(",")[0][starting_point:]
                total_length = total_length + (len(archaic_word[0]) - len(archaic_part))

        if re.search(pat_list["abs_er_pattern"], annotated_line):
            abs_ers = re.finditer(
                pat_list["abs_er_pattern"], annotated_line
            )  # list of match of abs_er pattern in line
            for abs_er in abs_ers:
                if abs_er.group(1):
                    total_length += 3
                else:
                    total_length += 2
        for pattern in [
            "author_pattern",
            "book_title_pattern",
            "poti_title_pattern",
            "chapter_title_pattern",
            "book_number_pattern",
        ]:
            title_pattern = re.search(pat_list[pattern], annotated_line)
            if title_pattern:
                if title_pattern.group(1):
                    total_length += 5
                else:
                    total_length += 4

        for pattern in [
            "end_cit_pattern",
            "end_sabche_pattern",
            "end_tsawa_pattern",
            "end_yigchung_pattern",
            "end_durchen_pattern",
        ]:
            end_patterns = re.findall(
                pat_list[pattern], annotated_line
            )  # list of match of citation pattern in line
            total_length = total_length + 2 * len(end_patterns)

        return total_length

    def merge(self, start_list, end_list):
        """ It merges two list.
        The starting  and ending of annotation(citaion,yigchung,sabche and tsawa) are stored in two list.
        Merging these two list will generate a list in which both starting and ending of an annotation together in a tuple.
        It is applicable only if the annotaions are not cross volume.
        Args:
            start_list (list): It contains index of where starting annotations(citaion,yigchung,sabche and tsawa) are detected.
            end_list (list): It contains index of where ending annotations(citaion,yigchung,sabche and tsawa) are detected.

        Return:
            result (list): It contains tuples where starting and ending of an annotation(citaion,yigchung,sabche and tsawa) is combined.
        """
        walker = 0
        result = []
        while walker < len(end_list) and walker < len(start_list):
            result.append(
                (
                    start_list[walker][0],
                    {"span": Span(start_list[walker][1], end_list[walker])},
                )
            )
            walker += 1
        return result

    def search_before(self, ann, pat_list, line):
        """ It calculates the length of annotation detected in a given line before a given annotation.
        Args:
            ann (match object): It is a match object of the annotation of which we want to calculate
                                the length of any annotation detected before it.
            pat_list (dict): It contains all the annotation's regex pattern as value and name of annotation as key.
            line (str): It contains the line in which we wants to calculate the legth of annotation found before the given annotation.
        Return:
            length_before (int): It accumalates as we detect annotation which is before the given annotation and
                                finally gives the total length of annotation caught before the given annotation in the given line.
        """
        length_before = 0
        for pp in [
            "line_pattern",
            "topic_pattern",
            "sub_topic_pattern",
            "note_pattern",
            "start_cit_pattern",
            "start_sabche_pattern",
            "start_tsawa_pattern",
            "start_yigchung_pattern",
            "start_durchen_pattern",
        ]:
            if re.search(pat_list[pp], line):
                match_list = re.finditer(
                    pat_list[pp], line
                )  # list of match object of given pattern in line
                for match in match_list:
                    if ann.start() > match.start():
                        length_before = length_before + len(match[0])

        if re.search(pat_list["error_pattern"], line):
            errors = re.finditer(
                pat_list["error_pattern"], line
            )  # list of match object of error pattern in line
            for error in errors:
                if error.group(1):
                    starting_point = 2
                else:
                    starting_point = 1
                if ann.start() > error.start():
                    error_part = error[0].split(",")[0][starting_point:]
                    length_before = length_before + (len(error[0]) - len(error_part))

        if re.search(pat_list["archaic_word_pattern"], line):
            archaic_words = re.finditer(
                pat_list["archaic_word_pattern"], line
            )  # list of match object of error pattern in line
            for archaic_word in archaic_words:
                if archaic_word.group(1):
                    starting_point = 2
                else:
                    starting_point = 1
                if ann.start() > archaic_word.start():
                    archaic_part = archaic_word[0].split(",")[0][starting_point:]
                    length_before = length_before + (
                        len(archaic_word[0]) - len(archaic_part)
                    )

        if re.search(pat_list["abs_er_pattern"], line):
            abs_ers = re.finditer(
                pat_list["abs_er_pattern"], line
            )  # list of match object of abs_er pattern in line
            for abs_er in abs_ers:
                if ann.start() > abs_er.start():
                    if abs_er.group(1):
                        pat_len = 3
                    else:
                        pat_len = 2
                    length_before = length_before + pat_len

        for pp in [
            "author_pattern",
            "book_title_pattern",
            "poti_title_pattern",
            "chapter_title_pattern",
            "book_number_pattern",
        ]:
            title_pattern = re.search(pat_list[pp], line)
            if title_pattern:
                if ann.start() > title_pattern.start():
                    if title_pattern.group(1):
                        length_before += 4
                    else:
                        length_before += 3

        for pp in [
            "end_cit_pattern",
            "end_sabche_pattern",
            "end_tsawa_pattern",
            "end_yigchung_pattern",
            "end_durchen_pattern",
        ]:
            end_patterns = re.finditer(
                pat_list[pp], line
            )  # list of match object of citation pattern in line
            for end_pattern in end_patterns:
                if ann.start() > end_pattern.start():
                    length_before = length_before + 2

        return length_before

    def base_extract(self, pat_list, annotated_line):
        """ It extract the base text from annotated text.
        Args:
            pat_list (dict): It contains all the annotation's regex pattern as value and name of annotation as key.
            annotated_line (str): It contains the annotated line from which we want to extract the base text.

        Return:
            base_line (str): It contains the base text which is being extracted from the given annotated line.
        """
        base_line = (
            annotated_line  # stores the base_line which is line without annotation
        )
        for pattern in [
            "line_pattern",
            "topic_pattern",
            "sub_topic_pattern",
            "note_pattern",
            "start_cit_pattern",
            "end_cit_pattern",
            "start_sabche_pattern",
            "end_sabche_pattern",
            "start_tsawa_pattern",
            "end_tsawa_pattern",
            "start_yigchung_pattern",
            "end_yigchung_pattern",
            "start_durchen_pattern",
            "end_durchen_pattern",
        ]:
            base_line = re.sub(pat_list[pattern], "", base_line)

        for pattern in [
            "author_pattern",
            "book_title_pattern",
            "poti_title_pattern",
            "chapter_title_pattern",
            "book_number_pattern",
        ]:
            title_pattern = re.search(pat_list[pattern], annotated_line)
            if title_pattern:
                if title_pattern.group(1):
                    starting_point = 4
                else:
                    starting_point = 3
                title = title_pattern[0][starting_point:-1]
                base_line = re.sub(pat_list[pattern], title, base_line, 1)

        if re.search(pat_list["error_pattern"], annotated_line):
            errors = re.finditer(
                pat_list["error_pattern"], annotated_line
            )  # list of match object of error pattern in line
            for error in errors:
                if error.group(1):
                    starting_point = 2
                else:
                    starting_point = 1
                error_part = error[0].split(",")[0][starting_point:]
                base_line = re.sub(pat_list["error_pattern"], error_part, base_line, 1)

        if re.search(pat_list["archaic_word_pattern"], annotated_line):
            archaic_words = re.finditer(
                pat_list["archaic_word_pattern"], annotated_line
            )  # list of match object of error pattern in line
            for archaic_word in archaic_words:
                if archaic_word.group(1):
                    starting_point = 2
                else:
                    starting_point = 1
                archaic_part = archaic_word[0].split(",")[0][starting_point:]
                base_line = re.sub(
                    pat_list["archaic_word_pattern"], archaic_part, base_line, 1
                )

        if re.search(pat_list["abs_er_pattern"], annotated_line):
            abs_ers = re.finditer(
                pat_list["abs_er_pattern"], annotated_line
            )  # list of match object of abs_er pattern in line
            for abs_er in abs_ers:
                if abs_er.group(1):
                    starting_point = 2
                else:
                    starting_point = 1
                base_line = re.sub(
                    pat_list["abs_er_pattern"],
                    abs_er[0][starting_point:-1],
                    base_line,
                    1,
                )

        return base_line

    def get_local_id(self, match_obj):
        if match_obj.group(1):
            return ord(match_obj.group(1))
        else:
            return None

    def parse_start_ann(self, ann, pat_list, walker, line):
        pat_len_before_ann = self.search_before(ann, pat_list, line)
        local_id = self.get_local_id(ann)
        ann_start = ann.start() + walker - pat_len_before_ann
        return (local_id, ann_start)

    def parse_end_ann(self, ann, pat_list, walker, line):
        pat_len_before_ann = self.search_before(ann, pat_list, line)
        ann_end = ann.start() + walker - pat_len_before_ann - 1
        return ann_end

    def parse_payload_ann(self, ann, pat_list, walker, line):
        local_id = self.get_local_id(ann)
        payload = ann[0].split(",")[1][:-1]  # extracting the modern word
        if local_id:
            annotation = ann[0].split(",")[0][2:]  # extracting the error component
        else:
            annotation = ann[0].split(",")[0][1:]
        pat_len_before_ann = self.search_before(ann, pat_list, line)
        start_ann = ann.start() + walker - pat_len_before_ann
        end_ann = start_ann + len(annotation) - 1
        span = Span(start_ann, end_ann)
        return (local_id, span, payload)

    def build_layers(self, m_text, num_vol):

        char_walker = 0  # tracker variable through out the text

        cur_vol_pages = (
            []
        )  # list variable to store page annotation according to base string index eg : [(startPage,endPage)]
        cur_vol_error_id = (
            []
        )  # list variable to store error annotation according to base string index eg : [(es,ee,'suggestion')]
        cur_vol_abs_er_id = []  # list variable to store abs_er annotation
        cur_vol_archaic_id = []
        note_id = []  # list variable to store note annotation '#"
        pg_refs = []  # lsit variable to store page info component
        pg_ann = []  # list variable to store page annotation content
        pg_tid = []

        author_titles = []
        book_titles = []
        book_numbers = []
        poti_titles = []
        chapter_titles = []
        start_cit_patterns = (
            []
        )  # list variable to store index of start citation pattern => (g
        end_cit_patterns = (
            []
        )  # list variable to store index of start citation pattern => g)
        start_sabche_pattern = (
            []
        )  # list variable to store index of start sabche pattern => (q
        end_sabche_pattern = (
            []
        )  # list variable to store index of end sabche pattern => q)
        start_tsawa_pattern = (
            []
        )  # list variable to store index of start tsawa pattern => (m
        end_tsawa_pattern = (
            []
        )  # list variable to store index of end sabche pattern => m)
        start_yigchung_pattern = (
            []
        )  # list variable to store index of start yigchung pattern => (y
        end_yigchung_pattern = (
            []
        )  # list variable to store index of end yigchung pattern => y)
        start_durchen_pattern = (
            []
        )  # list variable to store index of start durchen pattern => <d
        end_durchen_pattern = (
            []
        )  # list variable to store index of end durchen pattern => d>

        pat_list = {
            "author_pattern": r"\<([𰵀-󴉱])?au.+?\>",
            "book_title_pattern": r"\<([𰵀-󴉱])?k1.+?\>",
            "book_number_pattern": r"\<([𰵀-󴉱])?k4.+?\>",
            "poti_title_pattern": r"\<([𰵀-󴉱])?k2.+?\>",
            "chapter_title_pattern": r"\<([𰵀-󴉱])?k3.+?\>",
            "page_pattern": r"〔([𰵀-󴉱])?\d+〕",
            "line_pattern": r"\[\w+\.\d+\]",
            "topic_pattern": r"\{([𰵀-󴉱])?\w+\}",
            "start_cit_pattern": r"\<([𰵀-󴉱])?g",
            "end_cit_pattern": r"g\>",
            "start_sabche_pattern": r"\<([𰵀-󴉱])?q",
            "end_sabche_pattern": r"q\>",
            "start_tsawa_pattern": r"\<([𰵀-󴉱])?m",
            "end_tsawa_pattern": r"m\>",
            "start_yigchung_pattern": r"\<([𰵀-󴉱])?y",
            "end_yigchung_pattern": r"y\>",
            "start_durchen_pattern": r"\<([𰵀-󴉱])?d",
            "end_durchen_pattern": r"d\>",
            "sub_topic_pattern": r"\{([𰵀-󴉱])?\w+\-\w+\}",
            "error_pattern": r"\<([𰵀-󴉱])?\S+?\,\S+?\>",
            "archaic_word_pattern": r"\{([𰵀-󴉱])?\S+?\,\S+?\}",
            "abs_er_pattern": r"\[([𰵀-󴉱])?[^0-9].*?\]",
            "note_pattern": r"#([𰵀-󴉱])?",
        }

        start_page = 0  # starting index of page
        end_page = 0  # ending index of page
        start_line = 0  # starting index of line
        end_line = 0  # ending index of line
        start_title = 0  # starting of the title component
        end_title = 0  # ending of the title component
        start_topic = 0  # starting index of topic_Id
        end_topic = 0  # ending index of topic_Id
        start_sub_topic = 0  # starting index of sub_topic_Id
        end_sub_topic = 0  # ending index of sub_topic_Id
        start_error = 0  # starting index of error
        end_error = 0  # ending index of error
        start_abs_er = 0  # starting index of abs_er
        end_abs_er = 0  # ending index of abs_er
        note = 0  # index of notes

        text_lines = m_text.splitlines()  # list of all the lines in the text
        n_line = len(text_lines)  # number of lines in the text

        for idx, line in enumerate(text_lines):
            line = line.strip()
            start_line = char_walker
            length = len(line)
            pat_len_before_ann = 0  # length of pattern recognised before  annotation
            if re.search(
                pat_list["page_pattern"], line
            ):  # checking current line contains page annotation or not
                start_page = end_page
                end_page = end_line
                local_id = self.get_local_id(re.search(pat_list["page_pattern"], line))
                pg_tid.append(local_id)
                page_reference = line[re.search(pat_list["page_pattern"], line).end() :]
                if local_id:
                    pg_ann.append(re.search(pat_list["page_pattern"], line)[0][2:-1])
                else:
                    pg_ann.append(re.search(pat_list["page_pattern"], line)[0][1:-1])
                pg_refs.append(page_reference)
                if len(pg_refs) >= 2:
                    cur_vol_pages.append(
                        (
                            pg_tid[-2],
                            Page(
                                Span(start_page, end_page),
                                imgnum=pg_ann[-2],
                                page_ref=pg_refs[-2],
                            ),
                        )
                    )
                    if start_page < end_page:  # to ignore the empty pages
                        char_walker = char_walker + 1  # To accumulate the \n character
                        end_page = end_page + 3
                    self.base_text = self.base_text + "\n"
                continue

            for pp in [
                "author_pattern",
                "book_title_pattern",
                "poti_title_pattern",
                "chapter_title_pattern",
                "book_number_pattern",
            ]:
                title_pattern = re.search(pat_list[pp], line)
                if title_pattern:
                    local_id = self.get_local_id(title_pattern)
                    pat_len_before_ann = self.search_before(
                        title_pattern, pat_list, line
                    )
                    start_title = (
                        title_pattern.start() + char_walker - pat_len_before_ann
                    )
                    if local_id:
                        end_title = start_title + len(title_pattern[0]) - 6
                    else:
                        end_title = start_title + len(title_pattern[0]) - 5
                    span = Span(start_title, end_title)
                    if pp == "author_pattern":
                        author_titles.append((local_id, Author(span)))
                    if pp == "book_title_pattern":
                        book_titles.append((local_id, BookTitle(span)))
                    if pp == "book_number_pattern":
                        book_numbers.append((local_id, BookNumber(span)))
                    if pp == "poti_title_pattern":
                        poti_titles.append((local_id, PotiTitle(span)))
                        if local_id:
                            end_topic = len(title_pattern[0][2:])
                            end_sub_topic = len(title_pattern[0][2:])
                        else:
                            end_topic = len(title_pattern[0][1:])
                            end_sub_topic = len(title_pattern[0][1:])
                    if pp == "chapter_title_pattern":
                        chapter_titles.append((local_id, Chapter(span)))

            if re.search(
                pat_list["sub_topic_pattern"], line
            ):  # checking current line contain sub_topicID annotation or not
                sub_topic_match = re.search(pat_list["sub_topic_pattern"], line)
                local_id = self.get_local_id(sub_topic_match)
                if local_id:
                    self.sub_topic_info.append(sub_topic_match[0][2:-1])
                else:
                    self.sub_topic_info.append(sub_topic_match[0][1:-1])
                self.sub_topic_local_id.append(local_id)
                pat_len_before_ann = self.search_before(sub_topic_match, pat_list, line)
                if start_sub_topic == 0:
                    start_sub_topic = end_sub_topic
                    end_sub_topic = (
                        sub_topic_match.start() + char_walker - pat_len_before_ann
                    )

                    if start_sub_topic < end_sub_topic:
                        if len(self.sub_topic_info) >= 2:
                            span = CrossVolSpan(
                                self.vol_walker + 1, start_sub_topic, end_sub_topic
                            )
                            self.sub_topic_Id.append(
                                (
                                    self.sub_topic_local_id[-2],
                                    {"work_id": self.sub_topic_info[-2], "span": span},
                                )
                            )
                            end_sub_topic = end_sub_topic
                        else:
                            span = CrossVolSpan(
                                self.vol_walker + 1, start_sub_topic, end_sub_topic
                            )
                            self.sub_topic_Id.append(
                                (
                                    self.sub_topic_local_id[-1],
                                    {"work_id": self.sub_topic_info[-1], "span": span},
                                )
                            )
                            end_sub_topic = end_sub_topic
                else:
                    start_sub_topic = end_sub_topic
                    end_sub_topic = (
                        sub_topic_match.start() + char_walker - pat_len_before_ann
                    )

                    if start_sub_topic < end_sub_topic:
                        span = CrossVolSpan(
                            self.vol_walker + 1, start_sub_topic, end_sub_topic
                        )
                        self.sub_topic_Id.append(
                            (
                                self.sub_topic_local_id[-2],
                                {"work_id": self.sub_topic_info[-2], "span": span},
                            )
                        )
                        end_sub_topic = end_sub_topic

            if re.search(
                pat_list["topic_pattern"], line
            ):  # checking current line contain topicID annotation or not
                topic = re.search(pat_list["topic_pattern"], line)
                pat_len_before_ann = self.search_before(topic, pat_list, line)
                local_id = self.get_local_id(topic)
                if local_id:
                    self.topic_info.append(topic[0][2:-1])
                else:
                    self.topic_info.append(topic[0][1:-1])
                self.topic_local_id.append(local_id)
                start_topic = end_topic
                end_topic = topic.start() + char_walker - pat_len_before_ann

                if start_topic != end_topic or len(self.topic_info) >= 2:
                    if (
                        len(self.topic_info) >= 2
                    ):  # as we are ignoring the self.topic[0]
                        if start_topic < end_topic:
                            span = CrossVolSpan(
                                self.vol_walker + 1, start_topic, end_topic
                            )
                            self.current_topic_id.append(
                                (
                                    self.topic_local_id[-2],
                                    {"work_id": self.topic_info[-2], "span": span},
                                )
                            )  # -2 as we need the secondlast item
                    else:
                        self.current_topic_id.append(
                            (
                                self.topic_local_id[-1],
                                {
                                    "work_id": self.topic_info[-1],
                                    "span": CrossVolSpan(
                                        self.vol_walker + 1, start_topic, end_topic
                                    ),
                                },
                            )
                        )
                    self.topic_id.append(self.current_topic_id)
                    self.current_topic_id = []
                    if self.sub_topic_Id and end_sub_topic < end_topic:
                        self.sub_topic_Id.append(
                            (
                                self.sub_topic_local_id[-1],
                                {
                                    "work_id": self.sub_topic_info[-1],
                                    "span": CrossVolSpan(
                                        self.vol_walker + 1, end_sub_topic, end_topic
                                    ),
                                },
                            )
                        )
                    self.sub_topic.append(self.sub_topic_Id)
                    self.sub_topic_Id = []
                    if self.sub_topic_Id:
                        last = self.sub_topic_info[-1]
                        self.sub_topic_info = []
                        self.sub_topic_info.append(last)

            if re.search(
                pat_list["error_pattern"], line
            ):  # checking current line contain error annotation or not
                errors = re.finditer(pat_list["error_pattern"], line)
                for error in errors:
                    local_id, span, suggestion = self.parse_payload_ann(
                        error, pat_list, char_walker, line
                    )
                    cur_vol_error_id.append(
                        (local_id, Correction(span, correction=suggestion))
                    )

            if re.search(
                pat_list["archaic_word_pattern"], line
            ):  # checking current line contain error annotation or not
                archaics = re.finditer(pat_list["archaic_word_pattern"], line)
                for archaic in archaics:
                    local_id, span, modern_word = self.parse_payload_ann(
                        archaic, pat_list, char_walker, line
                    )
                    cur_vol_archaic_id.append(
                        (local_id, Archaic(span, modern=modern_word))
                    )

            if re.search(pat_list["abs_er_pattern"], line):
                abs_ers = re.finditer(pat_list["abs_er_pattern"], line)
                for abs_er in abs_ers:
                    pat_len_before_ann = self.search_before(abs_er, pat_list, line)
                    local_id = self.get_local_id(abs_er)
                    start_abs_er = abs_er.start() + char_walker - pat_len_before_ann
                    if local_id:
                        end_abs_er = (
                            start_abs_er + len(abs_er[0][2:-1]) - 1
                        )  # 3 is minus as two border bracket and local id
                    else:
                        end_abs_er = start_abs_er + len(abs_er[0][1:-1]) - 1
                    cur_vol_abs_er_id.append(
                        (local_id, ErrorCandidate(Span(start_abs_er, end_abs_er)))
                    )

            if re.search(pat_list["note_pattern"], line):
                notes_in_line = re.finditer(pat_list["note_pattern"], line)
                for notes in notes_in_line:
                    pat_len_before_ann = self.search_before(notes, pat_list, line)
                    local_id = self.get_local_id(notes)
                    note = notes.start() + char_walker - pat_len_before_ann
                    note_id.append((local_id, {_attr_names.SPAN: Span(note, note)}))

            if re.search(pat_list["start_cit_pattern"], line):
                start_cits = re.finditer(pat_list["start_cit_pattern"], line)
                for start_cit in start_cits:
                    start_cit_patterns.append(
                        self.parse_start_ann(start_cit, pat_list, char_walker, line)
                    )

            if re.search(pat_list["end_cit_pattern"], line):
                end_cits = re.finditer(pat_list["end_cit_pattern"], line)
                for end_cit in end_cits:
                    end_cit_patterns.append(
                        self.parse_end_ann(end_cit, pat_list, char_walker, line)
                    )

            if re.search(pat_list["start_sabche_pattern"], line):
                start_sabches = re.finditer(pat_list["start_sabche_pattern"], line)
                for start_sabche in start_sabches:
                    start_sabche_pattern.append(
                        self.parse_start_ann(start_sabche, pat_list, char_walker, line)
                    )

            if re.search(pat_list["end_sabche_pattern"], line):
                end_sabches = re.finditer(pat_list["end_sabche_pattern"], line)
                for end_sabche in end_sabches:
                    end_sabche_pattern.append(
                        self.parse_end_ann(end_sabche, pat_list, char_walker, line)
                    )

            if re.search(pat_list["start_tsawa_pattern"], line):
                start_tsawas = re.finditer(pat_list["start_tsawa_pattern"], line)
                for start_tsawa in start_tsawas:
                    start_tsawa_pattern.append(
                        self.parse_start_ann(start_tsawa, pat_list, char_walker, line)
                    )

            if re.search(pat_list["end_tsawa_pattern"], line):
                end_tsawas = re.finditer(pat_list["end_tsawa_pattern"], line)
                for end_tsawa in end_tsawas:
                    end_tsawa_pattern.append(
                        self.parse_end_ann(end_tsawa, pat_list, char_walker, line)
                    )

            if re.search(pat_list["start_yigchung_pattern"], line):
                start_yigchungs = re.finditer(pat_list["start_yigchung_pattern"], line)
                for start_yigchung in start_yigchungs:
                    start_yigchung_pattern.append(
                        self.parse_start_ann(
                            start_yigchung, pat_list, char_walker, line
                        )
                    )

            if re.search(pat_list["end_yigchung_pattern"], line):
                end_yigchungs = re.finditer(pat_list["end_yigchung_pattern"], line)
                for end_yigchung in end_yigchungs:
                    end_yigchung_pattern.append(
                        self.parse_end_ann(end_yigchung, pat_list, char_walker, line)
                    )

            if re.search(pat_list["start_durchen_pattern"], line):
                start_durchens = re.finditer(pat_list["start_durchen_pattern"], line)
                for start_durchen in start_durchens:
                    start_durchen_pattern.append(
                        self.parse_start_ann(start_durchen, pat_list, char_walker, line)
                    )

            if re.search(pat_list["end_durchen_pattern"], line):
                end_durchens = re.finditer(pat_list["end_durchen_pattern"], line)
                for end_durchen in end_durchens:
                    end_durchen_pattern.append(
                        self.parse_end_ann(end_durchen, pat_list, char_walker, line)
                    )

            pat_len_before_ann = self.total_pattern(pat_list, line)
            if line:
                end_line = start_line + length - pat_len_before_ann - 1
            else:
                end_line = start_line + length - 1
            char_walker = end_line + 2
            base_line = self.base_extract(pat_list, line) + "\n"
            self.base_text += base_line

            if idx == n_line - 1:  # Last line case
                start_page = end_page
                start_topic = end_topic
                start_sub_topic = end_sub_topic
                if self.sub_topic_Id:
                    self.sub_topic_Id.append(
                        (
                            self.sub_topic_local_id[-1]
                            if self.sub_topic_local_id
                            else None,
                            {
                                "work_id": self.sub_topic_info[-1]
                                if self.sub_topic_info
                                else None,
                                "span": CrossVolSpan(
                                    self.vol_walker + 1,
                                    start_sub_topic,
                                    char_walker - 2,
                                ),
                            },
                        )
                    )
                if self.topic_info:
                    self.current_topic_id.append(
                        (
                            self.topic_local_id[-1],
                            {
                                "work_id": self.topic_info[-1],
                                "span": CrossVolSpan(
                                    self.vol_walker + 1, start_topic, char_walker - 2
                                ),
                            },
                        )
                    )
                if pg_tid:
                    cur_vol_pages.append(
                        (
                            pg_tid[-1],
                            Page(
                                Span(start_page, char_walker - 2),
                                imgnum=pg_ann[-1],
                                page_ref=pg_refs[-1],
                            ),
                        )
                    )
                self.page.append(cur_vol_pages)
                self.error_id.append(cur_vol_error_id)
                cur_vol_error_id = []
                self.abs_er_id.append(cur_vol_abs_er_id)
                self.archaic_word_id.append(cur_vol_archaic_id)
                cur_vol_archaic_id = []
                cur_vol_abs_er_id = []
                self.notes_id.append(note_id)
                note_id = []
                self.author.append(author_titles)
                self.book_title.append(book_titles)
                self.book_number.append(book_numbers)
                self.poti_title.append(poti_titles)
                self.chapter_title.append(chapter_titles)
                self.vol_walker += 1

        if num_vol == self.vol_walker:  # checks the last volume
            self.topic_id.append(self.current_topic_id)
            self.current_topic_id = []
            self.sub_topic.append(self.sub_topic_Id)

        self.citation_pattern.append(
            self.merge(start_cit_patterns, end_cit_patterns)
        )  # The starting and ending of  citation pattern is merged
        self.sabche_pattern.append(
            self.merge(start_sabche_pattern, end_sabche_pattern)
        )  # The starting and ending of  sabche pattern is merged
        self.tsawa_pattern.append(
            self.merge(start_tsawa_pattern, end_tsawa_pattern)
        )  # The starting and ending of  tsawa pattern is merged
        self.yigchung_pattern.append(
            self.merge(start_yigchung_pattern, end_yigchung_pattern)
        )  # The starting and ending of  yigchung pattern is merged
        self.durchen_pattern.append(
            self.merge(start_durchen_pattern, end_durchen_pattern)
        )  # The starting and ending of  yigchung pattern is merged

    def get_result(self):

        if len(self.topic_id) > 1:
            if self.topic_id[0][0][1]["work_id"] == self.topic_id[1][0][1]["work_id"]:
                self.topic_id = self.topic_id[1:]
                self.sub_topic = self.sub_topic[1:]
        self.sub_topic = self.__final_sub_topic(self.sub_topic)
        result = {
            AnnType.book_title: self.book_title,
            AnnType.book_number: self.book_number,
            AnnType.author: self.author,
            AnnType.poti_title: self.poti_title,
            AnnType.chapter: self.chapter_title,
            AnnType.citation: self.citation_pattern,
            AnnType.pagination: self.page,  # page variable format (start_index,end_index,pg_Info,pg_ann)
            AnnType.topic: self.topic_id,
            AnnType.sub_topic: self.sub_topic,
            AnnType.sabche: self.sabche_pattern,
            AnnType.tsawa: self.tsawa_pattern,
            AnnType.yigchung: self.yigchung_pattern,
            AnnType.correction: self.error_id,
            AnnType.error_candidate: self.abs_er_id,
            AnnType.peydurma: self.notes_id,
            AnnType.archaic: self.archaic_word_id,
            AnnType.durchen: self.durchen_pattern,
        }

        return result

    def __final_sub_topic(self, sub_topics):
        """ It include all the sub topic belonging in one topic in a list.

        Args:
            sub_topic (list): It contains all the sub topic annotation's starting and ending index along with sub-topic info.

        Return:
            result (list): It contains list in which sub topic belonging to same topics are grouped together.
        """
        result = []
        cur_topic = []
        cur_sub = []
        sub_topic = sub_topics
        walker = 0
        for i in range(0, len(sub_topic)):
            if len(sub_topic[i]) != 0:
                cur_sub.append(sub_topic[i][0])
                for walker in range(1, len(sub_topic[i])):
                    if (
                        sub_topic[i][walker][1]["work_id"]
                        == sub_topic[i][walker - 1][1]["work_id"]
                    ):
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
        self.base_text = ""

        return base_text

    def create_opf(self, input_path, id_=None, **kwargs):
        input_path = Path(input_path)
        self._build_dirs(input_path, id_=id_)
        self.metadata = self._load_metadata()
        vol2fn_manager = Vol2FnManager(self.metadata)

        for m_text, vol_name, n_vol in self.get_input(input_path):
            vol_id = vol2fn_manager.get_vol_id(vol_name)
            print(f"[INFO] parsing Vol {vol_name} ...")
            self.build_layers(m_text, n_vol)
            if "is_text" in kwargs:
                if kwargs["is_text"]:
                    continue

            base_text = self.get_base_text()
            (self.dirs["opf_path"] / "base" / f"{vol_id}.txt").write_text(base_text)

        # save pecha layers
        layers = self.get_result()
        for vol_layers, vol_id in self.format_layer(layers):
            if vol_id:
                print(f"[INFO] Creating layers for {vol_id} ...")
                vol_layer_path = self.dirs["layers_path"] / vol_id
                vol_layer_path.mkdir(exist_ok=True)
            else:
                print("[INFO] Creating index layer for Pecha ...")

            for layer, ann in vol_layers.items():
                if layer == "index":
                    layer_fn = self.dirs["opf_path"] / f"{layer}.yml"
                else:
                    layer_fn = vol_layer_path / f"{layer}.yml"
                dump_yaml(ann, layer_fn)

        self._save_metadata(vol2fn=dict(vol2fn_manager.vol2fn))


class HFMLTextFromatter(HFMLFormatter):
    def __init_(self, output_path="./output", is_book=False, text_id=None):
        super().__init__(output_path=output_path, is_book=is_book)
        self.text_id = text_id

    def from_yaml(self, yml_path):
        return yaml.safe_load(yml_path.read_text(encoding="utf-8"))

    def get_offset(self, index_layer, text_id):
        offset = {}
        for text_uuid, text in index_layer["annotations"].items():
            if text["work_id"] == text_id:
                for span in text["span"]:
                    offset[span["vol"]] = span["start"]
                return offset
        return offset

    def get_text_vol_ids(self, text_opf_path):
        base_layers = list((text_opf_path / "base").iterdir())
        base_layers.sort()
        text_vol_ids = [text_id.stem for text_id in base_layers]
        return text_vol_ids

    def get_old_text_base(pecha_idx, pecha_base_text, text_id, text_vol_id):
        vol_num = int(text_vol_id[1:])
        for text_uuid, text in pecha_idx["annotations"].items():
            if text["word_id"] == text_id:
                for vol_span in text["span"]:
                    if vol_span["vol"] == vol_num:
                        return pecha_base_text[vol_span["start"] : vol_span["end"]]
        return pecha_base_text

    def update_base_text(self, pecha_opf_path, text_opf_path, pecha_idx, text_id):
        text_vol_ids = self.get_text_vol_ids(text_opf_path)
        for text_vol_id in text_vol_ids:
            pecha_base_text = (pecha_opf_path / f"base/{text_vol_id}.txt").read_text(
                encoding="utf-8"
            )
            old_text_base = self.get_old_base_text(
                pecha_idx, pecha_base_text, text_id, text_vol_id
            )
            new_text_base = (text_opf_path / f"base/{text_vol_id}.txt").read_text(
                encoding="utf-8"
            )
            new_base_text = pecha_base_text.replace(old_text_base, new_base_text)
            yield text_vol_id, new_base_text
            (pecha_opf_path / f"base/{text_vol_id}.txt").write_text(
                new_base_text, encoding="utf-8"
            )
        print("INFO: base text updated")

    def get_new_ann(self, cur_pecha_ann, cur_text_ann, cur_vol_offset):
        cur_pecha_ann["span"]["start"] = cur_text_ann["span"]["start"] + cur_vol_offset
        cur_pecha_ann["span"]["end"] = cur_text_ann["span"]["end"] + cur_vol_offset
        return cur_pecha_ann

    def get_new_layer(self, cur_vol_pecha_layer, cur_vol_text_layer, cur_vol_offset):
        for ann_id, local_id in cur_vol_text_layer["local_ids"]:
            pecha_ann_id = cur_vol_pecha_layer["local_ids"].key(local_id)
            cur_text_ann = cur_vol_text_layer["annotations"][ann_id]
            cur_pecha_ann = cur_vol_pecha_layer["annotations"][pecha_ann_id]
            cur_vol_pecha_layer["annotations"][pecha_ann_id] = self.get_new_ann(
                cur_pecha_ann, cur_text_ann, cur_vol_offset
            )
        return cur_vol_pecha_layer

    def update_layers(self, pecha_opf_path, text_opf_path, vol_wise_offset):
        text_vol_ids = self.get_text_vol_ids(text_opf_path)
        for text_vol_id in text_vol_ids:
            layers_to_update = list((text_opf_path / f"layers/{text_vol_id}").iterdir())
            for layer_to_update in layers_to_update:
                cur_vol_pecha_layer = self.from_yaml(
                    (
                        pecha_opf_path
                        / f"layers/{text_vol_id}/{layer_to_update.stem}.yml"
                    )
                )
                cur_vol_text_layer = self.from_yaml(layer_to_update)
                cur_vol_offset = vol_wise_offset[text_vol_id]
                new_layer = self.get_new_layer(
                    cur_vol_pecha_layer, cur_vol_text_layer, cur_vol_offset
                )
                new_layer = yaml.safe_load(new_layer)
                (
                    pecha_opf_path / f"layers/{text_vol_id}/{layer_to_update.stem}.yml"
                ).write_text(new_layer, encoding="utf-8")
        print("INFO: layers updated")

    def save_text_to_pecha(self, pecha_opf_path, text_opf_path, text_id):
        pecha_idx = self.from_yaml((pecha_opf_path / "index.yml"))
        for vol_id, new_base_text in self.update_base_text(
            pecha_opf_path, text_opf_path, pecha_idx, text_id
        ):
            (pecha_opf_path / f"base/{vol_id}.txt").write_text(
                new_base_text, encoding="utf-8"
            )
            print(f"INFO: {vol_id} base text updated")
        vol_wise_offset = self.get_offset(pecha_idx, text_id)
        self.update_layers(pecha_opf_path, text_opf_path, vol_wise_offset)
        print(f"{text_id} of {pecha_opf_path.stem} saved...")
