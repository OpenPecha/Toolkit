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
        adapted_end = span['end'] - self.text_spans[vol_id]['end']
        return adapted_start, adapted_start


    def apply_annotation(self, vol_id, ann):
        """Applies annotation to specific volume base-text, where part of the text exists.

        Args:
            vol_id (str): id of vol, where part of the text exists.
            ann (dict): annotation of any type.

        Returns:
            None

        """
        if ann['type'] == 'pagination':
            start_cc, end_cc = self.__get_adapted_span(ann['span'], vol_id)
            start_payload = f'[{ann["page_index"]}] {ann["page_info"]}\n'
            self.add_chars(vol_id, start_cc, True, start_payload)
        elif ann['type'] == 'correction':
            start_cc, end_cc = self.__get_adapted_span(ann['span'], vol_id)
            start_payload = '('
            end_payload = f',{ann['correction']})'
            self.add_chars(vol_id, start_cc, True, start_payload)
            self.add_chars(vol_id, end_cc, False, end_payload)
        elif ann['type'] == 'peydurma':
            start_cc, end_cc = self.__get_adapted_span(ann['span'], vol_id)
            start_payload = '#'
            self.add_chars(vol_id, start_cc, True, start_payload)
        elif ann['type'] == 'error_candidate':
            start_cc, end_cc = self.__get_adapted_span(ann['span'], vol_id)
            start_payload = '['
            end_payload = ']'
            self.add_chars(vol_id, start_cc, True, start_payload)
            self.add_chars(vol_id, end_cc, False, end_payload)