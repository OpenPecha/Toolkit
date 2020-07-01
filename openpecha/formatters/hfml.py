"""
Formatter for HFML annotations in the text

This module implements all classes necessary to format HFML annotation to OpenPecha format.
HFML (Human Friendly Markup Language) contains tagset used for structuring and annotating the text.
"""
import re
from pathlib import Path

from openpecha.formatters.formatter import BaseFormatter
from openpecha.formatters.layers import *


class Global2LocalId:
    """Map global id of annotation in a layer to local id of a layer."""

    def __init__(self, local_id_dict):
        self.start_local_id = 200_000
        self.global2local_id = self._initialize(local_id_hash)
        self.local2global_id = {
            l_id: g_id for l_id, g_id in self.global2local_id.items()
        }
        self.last_local_id = self.find_last()

    def _initialize(self, local_id_dict):
        g2lid = {}
        for global_id, local_id in local_id_dict.items():
            g2lid[global_id] = {"local_id": local_id, "is_found": False}
        return g2lid

    def find_last(self):
        """Return last local id in a layer."""
        if self.gobal2local_id:
            return list(self.gobal2local_id.values()).pop()
        return chr(self.start_local_id - 1)

    def add(self, global_id):
        """Map given `global_id` to the last local id."""
        next_local_id = chr(ord(self.last_local_id) + 1)
        self.global2local_id[global_id] = next_local_id
        self.last_local_id = next_local_id

    def get_local_id(self, global_id):
        """Return `local_id` associated to given `global_id`."""
        return self.global2local_id.get(global_id, None)

    def get_global_id(self, local_id):
        """Return `global_id` associated to given `local_id`."""
        return self.local2global_id.get(local_id, None)

    def serialize(self):
        """Return just the global and local id paris."""
        return {
            global_id: self.global2local_id[global_id]["local_id"]
            for global_id in self.gobal2local_id
            if self.gobal2local_id[global_id]["is_found"]
        }


class LocalIdManager:
    """Maintains local_id to uuid map for echa layer."""

    def __init__(self, layers):
        self.map_name = "uuid2local-id"
        self.maps = self._get_local_id_maps(layers)

    def _get_local_id_maps(self, layers):
        maps = {}
        for layer in layers:
            maps[layer] = Global2LocalId(layers[layer].get(self.map_name, {}))
        return maps

    def add(self, layer_name, global_id):
        """Add `global_id` to layer's global2local id map."""
        self.maps[layer_name].add(global_id)


class HFMLFormatter(BaseFormatter):
    """
    OpenPecha Formatter for digitized wooden-printed Pecha based on annotation scheme from Esukhia.
    """

    def __init__(self, output_path="./output", is_book=False):
        super().__init__(output_path=output_path)
        self.is_book = is_book
        self.base_text = ""
        self.vol_walker = 0
        self.pecha_title = []
        self.poti_title = []
        self.chapter_title = []
        self.topic_id = []  # made class variable as it needs to update cross poti
        self.current_topic_id = (
            []
        )  # made class variable as it needs to update cross poti
        self.sub_topic = []  # made class variable as it needs to update cross poti
        self.page = []
        self.error_id = []
        self.abs_er_id = []
        self.notes_id = []
        self.sub_topic_Id = []  # made class variable as it needs to update cross poti
        self.topic_info = []
        self.sub_topic_info = []
        self.cur_sub = []
        self.author_pattern = []
        self.citation_pattern = []
        self.sabche_pattern = []
        self.tsawa_pattern = []
        self.yigchung_pattern = []

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
            elif re.search(p, line) == None:
                if para:
                    result_text += line
                else:
                    result_text += line + "\n"
        return result_text

    def get_input(self, input_path):
        fns = list(input_path.iterdir())
        fns_len = len(fns)
        for fn in sorted(fns):
            yield self.text_preprocess(fn.read_text()), fn.name, fns_len

    def get_old_layers(self, new_layers):
        layers = {}
        for layer in new_layers:
            layer_fn = self.dirs["layers_path"] / f"{layer}.yml"
            if layer_fn.is_file():
                layers[layer] = self.load(layer_fn)
        return layers

    def _inc_layer_revision(self, layer):
        inc_rev_int = int(layer["revision"]) + 1
        layer["revision"] = f"{inc_rev_int:05}"

    def add_new_ann(self, layer, ann):
        uuid = self.get_unique_id()
        layer["annotations"][uuid] = ann
        self.local_id_manager.add(layer["annotation_type"], uuid)

    def create_new_layer(self, layer_name, anns):
        new_layer = Layer(self.get_unique_id(), layer_name)
        for ann in anns:
            self.add_new_ann(new_layer, ann)
        return new_layer

    def update_layer(self, layer, anns):
        self._inc_layer_revision(layer)
        for local_id, ann in anns:
            if local_id:
                uuid = self.local_id_manager.maps[
                    layer["annotation_type"]
                ].get_global_id(local_id)
                if uuid:
                    for key, value in ann.items():
                        layer["annotations"][uuid][key] = value
            # Local_id missing, possible cases
            # 1. New Annotation created
            # 2. Local_id gets deleted
            else:
                self.add_new_ann(layer, ann)
                # TODO: implement case 2

    def format_layer(self, layers):
        old_layers = self.get_old_layers(layers)
        self.local_id_manager = LocalIdManager(old_layers)

        cross_vol_anns, non_cross_vol_anns = [], []
        for layer_name, layer_anns in layers.items():
            if layer_name in ["topic", "sub_topic"]:
                cross_vol_anns.append((layer_name, layer_anns))
            else:
                non_cross_vol_anns.append((layer_name, layer_anns))

        del layers

        # Create Annotaion layers
        for (i, vol_layers) in enumerate(zip(*non_cross_vol_anns)):
            base_id = f"v{i+1:03}"

            result = {}

            layer_name, layer_anns = vol_layers
            if layer_name not in old_layers:
                result[layer_name] = self.create_new_layer(layer_name, layer_anns)
            else:
                old_layer = old_layers[layer_name]
                self.update_layer(old_layer, layer_anns)
                result[layer_name] = old_layer

            yield result, base_id

        # Create Index layer
        Index_layer = Layer(self.get_unique_id(), "index")
        # loop over each topic
        for topic, sub_topic in zip(*cross_vol_anns):
            Topic = deepcopy(Text)
            Topic["id"] = self.get_unique_id()

            # loop over each sub_topic
            for corss_sub_topic in sub_topic:
                sub_text = deepcopy(SubText)
                sub_text["id"] = self.get_unique_id()
                for start, end, vol_id, work in corss_sub_topic:
                    sub_text["work"] = work
                    cross_vol_span = deepcopy(CrossVolSpan)
                    cross_vol_span["vol"] = f"base/v{vol_id:03}"
                    cross_vol_span["span"]["start"] = start
                    cross_vol_span["span"]["end"] = end
                    sub_text["span"].append(cross_vol_span)

                if corss_sub_topic:
                    Topic["parts"].append(sub_text)

            for start, end, vol_id, work in topic:
                Topic["work"] = work
                cross_vol_span = deepcopy(CrossVolSpan)
                cross_vol_span["vol"] = f"base/v{vol_id:03}"
                cross_vol_span["span"]["start"] = start
                cross_vol_span["span"]["end"] = end
                Topic["span"].append(cross_vol_span)

            Index_layer["annotations"].append(Topic)

        result = {"index": Index_layer}

        yield result, None

    def total_pattern(self, pat_list, annotated_line):
        """ It calculates the length of all the annotation detected in a line.

        Args:
            pat_list (dict): It contains all the annotation's regex pattern as value and name of annotation as key.
            annotated_line (str): It contains the annotated line to be process.

        Return:
            total_length (int): It accumulates as annotations are detected in the line.
        """
        total_length = 0  # total length of annotation detected in a line
        for pattern in ["line_pattern", "topic_pattern", "sub_topic_pattern"]:
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
                error_part = error[0].split(",")[0][1:]
                total_length = total_length + (len(error[0]) - len(error_part))

        if re.search(pat_list["abs_er_pattern"], annotated_line):
            abs_ers = re.findall(
                pat_list["abs_er_pattern"], annotated_line
            )  # list of match of abs_er pattern in line
            total_length = total_length + 2 * len(abs_ers)

        if re.search(pat_list["note_pattern"], annotated_line):
            note_patterns = re.findall(
                pat_list["note_pattern"], annotated_line
            )  # list of match of note pattern in line
            total_length = total_length + len(note_patterns)

        for pattern in [
            "author_pattern",
            "pecha_title_pattern",
            "poti_title_pattern",
            "chapter_title_pattern",
        ]:
            title_pattern = re.search(pat_list[pattern], annotated_line)
            if title_pattern:
                total_length += 4

        for pattern in ["start_cit_pattern", "end_cit_pattern"]:
            cit_patterns = re.findall(
                pat_list[pattern], annotated_line
            )  # list of match of citation pattern in line
            total_length = total_length + 2 * len(cit_patterns)

        for pattern in ["start_sabche_pattern", "end_sabche_pattern"]:
            sabche_patterns = re.findall(
                pat_list[pattern], annotated_line
            )  # list of match of sabche pattern in line
            total_length = total_length + 2 * len(sabche_patterns)

        for pattern in ["start_tsawa_pattern", "end_tsawa_pattern"]:
            tsawa_patterns = re.findall(
                pat_list[pattern], annotated_line
            )  # list of match of tsawa pattern in line
            total_length = total_length + 2 * len(tsawa_patterns)

        for pattern in ["start_yigchung_pattern", "end_yigchung_pattern"]:
            yigchung_patterns = re.findall(
                pat_list[pattern], annotated_line
            )  # list of match of yigchung pattern in line
            total_length = total_length + 2 * len(yigchung_patterns)

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
            result.append((start_list[walker], end_list[walker]))
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
        for pp in ["line_pattern", "topic_pattern", "sub_topic_pattern"]:
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
                if ann.start() > error.start():
                    error_part = error[0].split(",")[0][1:]
                    length_before = length_before + (len(error[0]) - len(error_part))

        if re.search(pat_list["abs_er_pattern"], line):
            abs_ers = re.finditer(
                pat_list["abs_er_pattern"], line
            )  # list of match object of abs_er pattern in line
            for abs_er in abs_ers:
                if ann.start() > abs_er.start():
                    length_before = length_before + 2

        if re.search(pat_list["note_pattern"], line):
            abs_errors = re.finditer(
                pat_list["note_pattern"], line
            )  # list of match object of note pattern in line
            for abs_error in abs_errors:
                if ann.start() > abs_error.start():
                    length_before = length_before + 1

        for pp in [
            "author_pattern",
            "pecha_title_pattern",
            "poti_title_pattern",
            "chapter_title_pattern",
        ]:
            title_pattern = re.search(pat_list[pp], line)
            if title_pattern:
                if ann.start() > title_pattern.start():
                    length_before += 4

        for pp in ["start_cit_pattern", "end_cit_pattern"]:
            cit_patterns = re.finditer(
                pat_list[pp], line
            )  # list of match object of citation pattern in line
            for cit_pattern in cit_patterns:
                if ann.start() > cit_pattern.start():
                    length_before = length_before + 2

        for pp in ["start_sabche_pattern", "end_sabche_pattern"]:
            sabche_patterns = re.finditer(
                pat_list[pp], line
            )  # list of match object of sabche pattern in line
            for sabche_pattern in sabche_patterns:
                if ann.start() > sabche_pattern.start():
                    length_before = length_before + 2

        for pp in ["start_tsawa_pattern", "end_tsawa_pattern"]:
            tsawa_patterns = re.finditer(
                pat_list[pp], line
            )  # list of match object of tsawa pattern in line
            for tsawa_pattern in tsawa_patterns:
                if ann.start() > tsawa_pattern.start():
                    length_before = length_before + 2

        for pp in ["start_yigchung_pattern", "end_yigchung_pattern"]:
            yigchung_patterns = re.finditer(
                pat_list[pp], line
            )  # list of match object of yigchung pattern in line
            for yigchung_pattern in yigchung_patterns:
                if ann.start() > yigchung_pattern.start():
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
        ]:
            base_line = re.sub(pat_list[pattern], "", base_line)

        for pattern in [
            "author_pattern",
            "pecha_title_pattern",
            "poti_title_pattern",
            "chapter_title_pattern",
        ]:
            title_pattern = re.search(pat_list[pattern], annotated_line)
            if title_pattern:
                title = title_pattern[0][3:-1]
                base_line = re.sub(pat_list[pattern], title, base_line, 1)

        for pattern in [
            "start_cit_pattern",
            "end_cit_pattern",
            "start_sabche_pattern",
            "end_sabche_pattern",
            "start_tsawa_pattern",
            "end_tsawa_pattern",
            "start_yigchung_pattern",
            "end_yigchung_pattern",
        ]:
            base_line = re.sub(pat_list[pattern], "", base_line)

        if re.search(pat_list["error_pattern"], annotated_line):
            errors = re.finditer(
                pat_list["error_pattern"], annotated_line
            )  # list of match object of error pattern in line
            for error in errors:
                error_part = error[0].split(",")[0][1:]
                base_line = re.sub(pat_list["error_pattern"], error_part, base_line, 1)

        if re.search(pat_list["abs_er_pattern"], annotated_line):
            abs_ers = re.finditer(
                pat_list["abs_er_pattern"], annotated_line
            )  # list of match object of abs_er pattern in line
            for abs_er in abs_ers:
                base_line = re.sub(
                    pat_list["abs_er_pattern"], abs_er[0][1:-1], base_line, 1
                )

        return base_line

    def build_layers(self, m_text, num_vol):

        i = 0  # tracker variable through out the text

        cur_vol_pages = (
            []
        )  # list variable to store page annotation according to base string index eg : [(startPage,endPage)]
        cur_vol_error_id = (
            []
        )  # list variable to store error annotation according to base string index eg : [(es,ee,'suggestion')]
        cur_vol_abs_er_id = []  # list variable to store abs_er annotation
        note_id = []  # list variable to store note annotation '#"
        pg_info = []  # lsit variable to store page info component
        pg_ann = []  # list variable to store page annotation content
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

        pat_list = {
            "author_pattern": r"\(au.+?\)",
            "pecha_title_pattern": r"\(k1.+?\)",
            "poti_title_pattern": r"\(k2.+?\)",
            "chapter_title_pattern": r"\(k3.+?\)",
            "page_pattern": r"\[[0-9]+[a-z]{1}\]",
            "line_pattern": r"\[\w+\.\d+\]",
            "topic_pattern": r"\{\w+\}",
            "start_cit_pattern": r"\(g",
            "end_cit_pattern": r"g\)",
            "start_sabche_pattern": r"\(q",
            "end_sabche_pattern": r"q\)",
            "start_tsawa_pattern": r"\(m",
            "end_tsawa_pattern": r"m\)",
            "start_yigchung_pattern": r"\(y",
            "end_yigchung_pattern": r"y\)",
            "sub_topic_pattern": r"\{\w+\-\w+\}",
            "error_pattern": r"\(\S+\,\S+\)",
            "abs_er_pattern": r"\[[^0-9].*?\]",
            "note_pattern": r"#",
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
            pat_len_before_ann = 0  # length of pattern recognised before  annotation
            if re.search(
                pat_list["page_pattern"], line
            ):  # checking current line contains page annotation or not
                start_page = end_page
                end_page = end_line
                page_info = line[re.search(pat_list["page_pattern"], line).end() :]
                pg_ann.append(re.search(pat_list["page_pattern"], line)[0][1:-1])
                pg_info.append(page_info)
                if len(pg_info) >= 2:
                    cur_vol_pages.append(
                        (start_page, end_page, pg_info[-2], pg_ann[-2])
                    )
                    if start_page < end_page:  # to ignore the empty pages
                        i = i + 1  # To accumulate the \n character
                        end_page = end_page + 3
                    self.base_text = self.base_text + "\n"
            elif re.search(
                pat_list["line_pattern"], line
            ):  # checking current line contains line annotation or not
                start_line = i
                length = len(line)

                for pp in [
                    "author_pattern",
                    "pecha_title_pattern",
                    "poti_title_pattern",
                    "chapter_title_pattern",
                ]:
                    title_pattern = re.search(pat_list[pp], line)
                    if title_pattern:
                        pat_len_before_ann = self.search_before(
                            title_pattern, pat_list, line
                        )
                        start_title = title_pattern.start() + i - pat_len_before_ann
                        end_title = start_title + len(title_pattern[0]) - 5
                        if pp == "author_pattern":
                            self.author_pattern.append((start_title, end_title))
                        if pp == "pecha_title_pattern":
                            self.pecha_title.append((start_title, end_title))
                        if pp == "poti_title_pattern":
                            poti_titles.append((start_title, end_title))
                            end_topic = len(title_pattern[0][2:])
                            end_sub_topic = len(title_pattern[0][2:])
                        if pp == "chapter_title_pattern":
                            chapter_titles.append((start_title, end_title))

                if re.search(
                    pat_list["sub_topic_pattern"], line
                ):  # checking current line contain sub_topicID annotation or not
                    sub_topic_match = re.search(pat_list["sub_topic_pattern"], line)
                    self.sub_topic_info.append(sub_topic_match[0][1:-1])
                    pat_len_before_ann = self.search_before(
                        sub_topic_match, pat_list, line
                    )
                    if start_sub_topic == 0:
                        start_sub_topic = end_sub_topic
                        end_sub_topic = sub_topic_match.start() + i - pat_len_before_ann

                        if start_sub_topic < end_sub_topic:
                            if len(self.sub_topic_info) >= 2:
                                self.sub_topic_Id.append(
                                    (
                                        start_sub_topic,
                                        end_sub_topic,
                                        self.vol_walker + 1,
                                        self.sub_topic_info[-2],
                                    )
                                )
                                end_sub_topic = end_sub_topic
                            else:
                                self.sub_topic_Id.append(
                                    (
                                        start_sub_topic,
                                        end_sub_topic,
                                        self.vol_walker + 1,
                                        self.sub_topic_info[-1],
                                    )
                                )
                                end_sub_topic = end_sub_topic
                    else:
                        start_sub_topic = end_sub_topic
                        end_sub_topic = sub_topic_match.start() + i - pat_len_before_ann

                        if start_sub_topic < end_sub_topic:
                            self.sub_topic_Id.append(
                                (
                                    start_sub_topic,
                                    end_sub_topic,
                                    self.vol_walker + 1,
                                    self.sub_topic_info[-2],
                                )
                            )
                            end_sub_topic = end_sub_topic

                if re.search(
                    pat_list["topic_pattern"], line
                ):  # checking current line contain topicID annotation or not
                    topic = re.search(pat_list["topic_pattern"], line)
                    pat_len_before_ann = self.search_before(topic, pat_list, line)
                    self.topic_info.append(topic[0][1:-1])
                    start_topic = end_topic
                    end_topic = topic.start() + i - pat_len_before_ann

                    if start_topic != end_topic or len(self.topic_info) >= 2:
                        if (
                            len(self.topic_info) >= 2
                        ):  # as we are ignoring the self.topic[0]
                            if start_topic < end_topic:
                                self.current_topic_id.append(
                                    (
                                        start_topic,
                                        end_topic,
                                        self.vol_walker + 1,
                                        self.topic_info[-2],
                                    )
                                )  # -2 as we need the secondlast item
                        else:
                            self.current_topic_id.append(
                                (
                                    start_topic,
                                    end_topic,
                                    self.vol_walker + 1,
                                    self.topic_info[-1],
                                )
                            )
                        self.topic_id.append(self.current_topic_id)
                        self.current_topic_id = []
                        if self.sub_topic_Id and end_sub_topic < end_topic:
                            self.sub_topic_Id.append(
                                (
                                    end_sub_topic,
                                    end_topic,
                                    self.vol_walker + 1,
                                    self.sub_topic_info[-1],
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
                        suggestion = error[0].split(",")[1][
                            :-1
                        ]  # extracting the suggestion component
                        error_part = error[0].split(",")[0][
                            1:
                        ]  # extracting the error component
                        pat_len_before_ann = self.search_before(error, pat_list, line)
                        start_error = error.start() + i - pat_len_before_ann

                        end_error = start_error + len(error_part) - 1
                        cur_vol_error_id.append((start_error, end_error, suggestion))

                if re.search(pat_list["abs_er_pattern"], line):
                    abs_ers = re.finditer(pat_list["abs_er_pattern"], line)
                    for abs_er in abs_ers:
                        pat_len_before_ann = self.search_before(abs_er, pat_list, line)
                        start_abs_er = abs_er.start() + i - pat_len_before_ann
                        end_abs_er = start_abs_er + len(abs_er[0]) - 3
                        cur_vol_abs_er_id.append((start_abs_er, end_abs_er))

                if re.search(pat_list["note_pattern"], line):
                    notes_in_line = re.finditer(pat_list["note_pattern"], line)
                    for notes in notes_in_line:
                        pat_len_before_ann = self.search_before(notes, pat_list, line)
                        note = notes.start() + i - pat_len_before_ann
                        note_id.append(note)

                if re.search(pat_list["start_cit_pattern"], line):
                    start_cits = re.finditer(pat_list["start_cit_pattern"], line)
                    for start_cit in start_cits:
                        pat_len_before_ann = self.search_before(
                            start_cit, pat_list, line
                        )
                        cit_start = start_cit.start() + i - pat_len_before_ann
                        start_cit_patterns.append(cit_start)

                if re.search(pat_list["end_cit_pattern"], line):
                    end_cits = re.finditer(pat_list["end_cit_pattern"], line)
                    for end_cit in end_cits:
                        pat_len_before_ann = self.search_before(end_cit, pat_list, line)
                        cit_end = end_cit.start() + i - pat_len_before_ann - 1
                        end_cit_patterns.append(cit_end)

                if re.search(pat_list["start_sabche_pattern"], line):
                    start_sabches = re.finditer(pat_list["start_sabche_pattern"], line)
                    for start_sabche in start_sabches:
                        pat_len_before_ann = self.search_before(
                            start_sabche, pat_list, line
                        )
                        sabche_start = start_sabche.start() + i - pat_len_before_ann
                        start_sabche_pattern.append(sabche_start)

                if re.search(pat_list["end_sabche_pattern"], line):
                    end_sabches = re.finditer(pat_list["end_sabche_pattern"], line)
                    for end_sabche in end_sabches:
                        pat_len_before_ann = self.search_before(
                            end_sabche, pat_list, line
                        )
                        sabche_end = end_sabche.start() + i - pat_len_before_ann - 1
                        end_sabche_pattern.append(sabche_end)

                if re.search(pat_list["start_tsawa_pattern"], line):
                    start_tsawas = re.finditer(pat_list["start_tsawa_pattern"], line)
                    for start_tsawa in start_tsawas:
                        pat_len_before_ann = self.search_before(
                            start_tsawa, pat_list, line
                        )
                        tsawa_start = start_tsawa.start() + i - pat_len_before_ann
                        start_tsawa_pattern.append(tsawa_start)

                if re.search(pat_list["end_tsawa_pattern"], line):
                    end_tsawas = re.finditer(pat_list["end_tsawa_pattern"], line)
                    for end_tsawa in end_tsawas:
                        pat_len_before_ann = self.search_before(
                            end_tsawa, pat_list, line
                        )
                        tsawa_end = end_tsawa.start() + i - pat_len_before_ann - 1
                        end_tsawa_pattern.append(tsawa_end)

                if re.search(pat_list["start_yigchung_pattern"], line):
                    start_yigchungs = re.finditer(
                        pat_list["start_yigchung_pattern"], line
                    )
                    for start_yigchung in start_yigchungs:
                        pat_len_before_ann = self.search_before(
                            start_yigchung, pat_list, line
                        )
                        yigchung_start = start_yigchung.start() + i - pat_len_before_ann
                        start_yigchung_pattern.append(yigchung_start)

                if re.search(pat_list["end_yigchung_pattern"], line):
                    end_yigchungs = re.finditer(pat_list["end_yigchung_pattern"], line)
                    for end_yigchung in end_yigchungs:
                        pat_len_before_ann = self.search_before(
                            end_yigchung, pat_list, line
                        )
                        yigchung_end = end_yigchung.start() + i - pat_len_before_ann - 1
                        end_yigchung_pattern.append(yigchung_end)

                pat_len_before_ann = self.total_pattern(pat_list, line)
                end_line = start_line + length - pat_len_before_ann - 1
                i = end_line + 2
                base_line = self.base_extract(pat_list, line) + "\n"
                self.base_text += base_line

                if idx == n_line - 1:  # Last line case
                    start_page = end_page
                    start_topic = end_topic
                    start_sub_topic = end_sub_topic
                    if self.sub_topic_Id:
                        self.sub_topic_Id.append(
                            (
                                start_sub_topic,
                                i - 2,
                                self.vol_walker + 1,
                                self.sub_topic_info[-1]
                                if self.sub_topic_info
                                else None,
                            )
                        )
                    if self.topic_info:
                        self.current_topic_id.append(
                            (
                                start_topic,
                                i - 2,
                                self.vol_walker + 1,
                                self.topic_info[-1],
                            )
                        )
                    cur_vol_pages.append((start_page, i - 2, pg_info[-1], pg_ann[-1]))
                    self.page.append(cur_vol_pages)
                    self.error_id.append(cur_vol_error_id)
                    cur_vol_error_id = []
                    self.abs_er_id.append(cur_vol_abs_er_id)
                    cur_vol_abs_er_id = []
                    self.notes_id.append(note_id)
                    note_id = []
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

    def get_result(self):

        if self.topic_id[0]:
            if self.topic_id[0][0][3] == self.topic_id[1][0][3]:
                self.topic_id = self.topic_id[1:]
                self.sub_topic = self.sub_topic[1:]
        self.sub_topic = self.__final_sub_topic(self.sub_topic)
        result = {
            "poti_title": self.poti_title,
            "chapter_title": self.chapter_title,
            "citation": self.citation_pattern,
            "pagination": self.page,  # page variable format (start_index,end_index,pg_Info,pg_ann)
            "topic": self.topic_id,
            "sub_topic": self.sub_topic,
            "sabche": self.sabche_pattern,
            "tsawa": self.tsawa_pattern,
            "yigchung": self.yigchung_pattern,
            "correction": self.error_id,
            "error_candidate": self.abs_er_id,
            "peydurma": self.notes_id,
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
                    if sub_topic[i][walker][3] == sub_topic[i][walker - 1][3]:
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

    def create_opf(self, input_path, **kwargs):
        input_path = Path(input_path)
        self._build_dirs(input_path)
        (self.dirs["opf_path"] / "base").mkdir(exist_ok=True)

        for i, (m_text, vol_name, n_vol) in enumerate(self.get_input(input_path)):
            print(f"[INFO] Processing Vol {i+1:03} of {n_vol}: {vol_name} ...")
            base_id = f"v{i+1:03}"
            self.build_layers(m_text, n_vol)
            # save base_text
            # if (self.dirs['opf_path']/'base'/f'{base_id}.txt').is_file(): continue
            if "is_text" in kwargs:
                if kwargs["is_text"]:
                    continue

            base_text = self.get_base_text()
            (self.dirs["opf_path"] / "base" / f"{base_id}.txt").write_text(base_text)

        # save pecha layers
        layers = self.get_result()
        for vol_layers, base_id in self.format_layer(layers):
            if base_id:
                print(f"[INFO] Creating layers for {base_id} ...")
                vol_layer_path = self.dirs["layers_path"] / base_id
                vol_layer_path.mkdir(exist_ok=True)
            else:
                print("[INFO] Creating index layer for Pecha ...")

            for layer, ann in vol_layers.items():
                if layer == "index":
                    layer_fn = self.dirs["opf_path"] / f"{layer}.yml"
                else:
                    layer_fn = vol_layer_path / f"{layer}.yml"
                self.dump(ann, layer_fn)


class HFMLTextFromatter(HFMLFormatter):
    def __init_(self, output_path="./output", is_book=False):
        super().__init__(output_path=output_path, is_book=is_book)
        self.text_id = None

    def get_input(self, input_path):
        mtext = input_path.read_text()
        if self.is_book:
            return (self.text_preprocess(mtext), "Book", 1)

        vol_pattern = r"\[v\d{3}\]"
        cur_vol_text = ""
        vol_text = []
        vol_info = []
        vol_walker = 0
        lines = mtext.splitlines()
        n_line = len(lines)
        self.text_id = re.search(r"\{\w+\}", mtext)[0]
        for idx, line in enumerate(lines):
            vol_pat = re.search(vol_pattern, line)
            if vol_pat:
                vol_info.append(vol_pat[0][1:-1])
                if vol_walker > 0:
                    vol_text.append(cur_vol_text)
                    cur_vol_text = ""
                vol_walker += 1
            else:
                cur_vol_text += line + "\n"
            if idx == n_line - 1:
                vol_text.append(cur_vol_text)
                cur_vol_text = ""

        result = []
        for i, vol_id in enumerate(vol_info):
            result.append((self.text_preprocess(vol_text[i]), vol_id, vol_walker))
        return result

    def __adapt_span_to_vol(self, extra, vol_walker):
        """ It adapts the index of parse output of serilized hfml file of a particular text id.

        Agrs:
            extra (int): start of text Id span which needs to be added to all the index of annotation present in that text id.
            vol_walker (int): Adapts all the annotation which contains volume information.
        """

        first_vol = []
        if self.poti_title[0]:
            start = self.poti_title[0][0] + extra
            end = self.poti_title[0][1] + extra
            first_vol.append((start, end))
            first_vol.append(self.poti_title[1:])
            self.poti_title = first_vol
            first_vol = []
        if self.chapter_title[0]:
            start = self.chapter_title[0][0] + extra
            end = self.chapter_title[0][1] + extra
            first_vol.append((start, end))
            first_vol.append(self.chapter_title[1:])
            self.poti_title = first_vol
            first_vol = []
        if self.citation_pattern[0]:
            for cit in self.citation_pattern[0]:
                start = cit[0] + extra
                end = cit[1] + extra
                first_vol.append((start, end))
            self.citation_pattern[0] = first_vol
            first_vol = []
        if self.sabche_pattern[0]:
            for sabche in self.sabche_pattern[0]:
                start = sabche[0] + extra
                end = sabche[1] + extra
                first_vol.append((start, end))
            self.sabche_pattern[0] = first_vol
            first_vol = []
        if self.yigchung_pattern[0]:
            for yig in self.yigchung_pattern[0]:
                start = yig[0] + extra
                end = yig[1] + extra
                first_vol.append((start, end))
            self.yigchung_pattern[0] = first_vol
            first_vol = []
        if self.tsawa_pattern[0]:
            for tsawa in self.tsawa_pattern[0]:
                start = tsawa[0] + extra
                end = tsawa[1] + extra
                first_vol.append((start, end))
            self.tsawa_pattern[0] = first_vol
            first_vol = []
        if self.error_id[0]:
            for cor in self.error_id[0]:
                start = cor[0] + extra
                end = cor[1] + extra
                first_vol.append((start, end, cor[2]))
            self.error_id[0] = first_vol
            first_vol = []
        if self.notes_id[0]:
            for cor in self.notes_id[0]:
                start = cor[0] + extra
                first_vol.append(start)
            self.notes_id[0] = first_vol
            first_vol = []
        if self.abs_er_id[0]:
            for er in self.abs_er_id[0]:
                start = er[0] + extra
                end = er[1] + extra
                first_vol.append((start, end))
            self.abs_er_id[0] = first_vol
            first_vol = []
        if self.page[0]:
            for pg in self.page[0]:
                start = pg[0] + extra
                end = pg[1] + extra
                first_vol.append((start, end, pg[2], pg[3]))
            self.page[0] = first_vol
            first_vol = []

        if self.topic_id:
            cur_top = []
            for cur_vol_top in self.topic_id[0]:
                start = cur_vol_top[0]
                end = cur_vol_top[1]
                if cur_vol_top[2] == 1:
                    start += extra
                    end += extra
                cur_top.append(
                    (start, end, cur_vol_top[2] + vol_walker, cur_vol_top[3])
                )
            self.topic_id[0] = cur_top

        if self.sub_topic[0][0]:
            cur_topic = []
            for st in self.sub_topic[0][0]:
                cur_sub_top = []
                for cst in st:
                    start = cst[0]
                    end = cst[1]
                    if cst[2] == 1:
                        start += extra
                        end += extra
                    cur_sub_top.append((start, end, t[2] + vol_walker, t[3]))
                cur_topic.append(cur_sub_top)
            self.sub_topic[0] = cur_topic

    def get_result(self):
        index = self.load(self.dirs["opf_path"] / "index.yml")
        extra = 0
        for i, ann in enumerate(index["annotations"]):
            if ann["work"] == self.text_id:
                extra = ann["work"]["span"][0]["vol"]["span"]["start"]
                break
        if not self.is_book:
            self.__adapt_span_to_vol(extra, i)

        result = {
            "pecha_title": self.poti_title,
            "chapter_title": self.chapter_title,
            "citation": self.citation_pattern,
            "pagination": self.page,  # page variable format (start_index,end_index,pg_Info,pg_ann)
            "topic": self.topic_id,
            "sub_topic": self.sub_topic,
            "sabche": self.sabche_pattern,
            "tsawa": self.tsawa_pattern,
            "yigchung": self.yigchung_pattern,
            "correction": self.error_id,
            "error_candidate": self.abs_er_id,
            "peydurma": self.notes_id,
        }

        return result


if __name__ == "__main__":
    formatter = HFMLFormatter()
    formatter.create_opf("./tests/data/formatter/hfml/P000002/")

    formatter = HFMLTextFromatter()
    formatter.new_poti("./tests/data/formatter/hfml/vol_sep_test")
