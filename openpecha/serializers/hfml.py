from .serialize import Serialize


class SerializeHFML(Serialize):
    """
    HFML (Human Friendly Markup Language) serializer class for OpenPecha.
    """

    def apply_annotation(self, ann):
        if ann.type == 'page':
            self.add_chars(ann.start_cc-1, True, '[Page]')
        elif ann.type == 'line':
            self.add_chars(ann.start_cc, True, '[Line]')
        