from openpecha.serializers import Serialize


class SerializeHFML(Serialize):
    """
    HFML (Human Friendly Markup Language) serializer class for OpenPecha.
    """

    def apply_annotation(self, vol_id, ann):
        only_start_ann = False
        start_payload = '('
        end_payload = ')'
        side = 'ab'
        if ann['type'] == 'pagination':
            if ann['page_index'] == '0b':
                pg_n = ann['reference'][5:-1]
                pg_side = ann['reference'][-1]
                if '-' in pg_n:
                    pg_n = int(pg_n.split('-')[0])
                    pg_side = side[int(pg_side)]
                    start_payload = f'[{pg_n}{pg_side}]'
                else:
                    pg_n = int(pg_n)
                    if pg_side.isdigit():
                        pg_n = str(pg_n) + pg_side
                        pg_side = ''
                    start_payload = f'[{pg_n}{pg_side}]'
            else:
                start_payload = f'[{ann["page_index"]}]'
            
            if ann["page_info"]:
                start_payload += f' {ann["page_info"]}\n'
            else:
                start_payload += f' {ann["reference"]}\n'
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
        #start_cc -= 4
        self.add_chars(vol_id, start_cc, True, start_payload)
        if not only_start_ann:
            self.add_chars(vol_id, end_cc, False, end_payload)