from .serialize import Serialize


class SerializeHFML(Serialize):
    """
    HFML (Human Friendly Markup Language) serializer class for OpenPecha.
    """

    def apply_annotation(self, vol_id, ann):
        if ann['type'] == 'pagination':
            start_cc = ann['span']['start'] - self.text_spans[vol_id]['start']
            self.add_chars(vol_id, start_cc, True, f'[{ann["page_index"]}]\n')