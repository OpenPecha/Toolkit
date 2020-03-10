from .serialize import Serialize


class SerializeTsadra(Serialize):
    """
    Tsadra serializer class for OpenPecha.
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
            start_payload = '<span class="credits-page_front-title "'
            end_payload = '</span>'
        elif ann['type'] == 'author':
            start_payload = '<span class="credits-page_front-page---text-author">'
            end_payload = '</span>'
        elif ann['type'] == 'chapter_title':
            start_payload = '<span class="tibetan-chapter">'
            end_payload = '</span>'
        elif ann['type'] == 'tsawa':
            start_payload = '<span class="tibetan-root-text_tibetan-root-text-middle-lines">'
            end_payload = '</span>'
        elif ann['type'] == 'quotation':
            start_payload = '<span class="tibetan-citations-in-verse_tibetan-citations-middle-lines">'
            end_payload = '</span>'
        elif ann['type'] == 'sabche':
            start_payload = '<span class="tibetan-sabche">'
            end_payload = '</span>'
        elif ann['type'] == 'yigchung':
            start_payload = '<span class="tibetan-commentary-small">'
            end_payload = '</span>'
        
        start_cc, end_cc = self.__get_adapted_span(ann['span'], vol_id)
        self.add_chars(vol_id, start_cc, True, start_payload)
        if not only_start_ann:
            self.add_chars(vol_id, end_cc, False, end_payload)