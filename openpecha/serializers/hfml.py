from .serialize import Serialize


class SerializeHFML(Serialize):
    """
    HFML (Human Friendly Markup Language) serializer class for OpenPecha.
    """

    def __get_adapted_span(self, span, vol_id):
        """Adapts the annotation span to base-text of the text

        Adapts the annotation span, which is based on volume base-text
        to text base-text.

        Args:
            span (dict): span of a annotation, eg: {start:, end:}
            vol_id (str): id of vol, where part of the text exists.

        Returns:
            adapted_start (int): adapted start based on text base-text
            adapted_end (int): adapted end based on text base-text

        """
        adapted_start = span['start'] - self.text_spans[vol_id]['start']
        adapted_end = span['end'] - self.text_spans[vol_id]['start']
        return adapted_start, adapted_end


    def apply_annotation(self, vol_id, ann):
        """Applies annotation to specific volume base-text, where part of the text exists.

        Args:
            vol_id (str): id of vol, where part of the text exists.
            ann (dict): annotation of any type.

        Returns:
            None

        """
        only_start_ann = False
        start_payload = '('
        end_payload = ')'
        if ann['type'] == 'pagination':
            start_payload = f'[{ann["page_index"]}] {ann["page_info"]}\n'
            only_start_ann = True
        elif ann['type'] == 'correction':
            start_payload = '('
            end_payload = f',{ann["correction"]})'
        elif ann['type'] == 'peydurma':
            start_payload = '#'
            only_start_ann = True
        elif ann['type'] == 'error_candidate':
            start_payload = '['
            end_payload = ']'
        elif ann['type'] == 'book_title':
            start_payload = '(k1'
            end_payload = ')'
        elif ann['type'] == 'author':
            start_payload = '(au'
            end_payload = ')'
        elif ann['type'] == 'chapter_title':
            start_payload = '(k3'
            end_payload = ')'
        elif ann['type'] == 'tsawa':
            start_payload = '(m'
            end_payload = 'm)'
        elif ann['type'] == 'quotation':
            start_payload = '(g'
            end_payload = 'g)'
        elif ann['type'] == 'sabche':
            start_payload = '(q'
            end_payload = 'q)'
        elif ann['type'] == 'yigchung':
            start_payload = '(y'
            end_payload = 'y)'
        
        start_cc, end_cc = self.__get_adapted_span(ann['span'], vol_id)
        self.add_chars(vol_id, start_cc, True, start_payload)
        if not only_start_ann:
            self.add_chars(vol_id, end_cc, False, end_payload)