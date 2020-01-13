from .serialize import Serialize


class SerializeHFML(Serialize):
    """
    HFML (Human Friendly Markup Language) serializer class for OpenPecha.
    """

    def apply_annotation(self, vol_id, ann):
        if ann['type'] == 'pagination':
            self.add_chars(vol_id, ann['span']['start'], True, f'[{ann["page_index"]}]\n')