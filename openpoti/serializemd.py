# TODO: use inheritance and abstract classes properly, see
# https://stackoverflow.com/questions/372042/difference-between-abstract-class-and-interface-in-python

from .serialize import Serialize

class SerializeMd(Serialize):
    """
    This class is serializes an opf file into MarkDown.
    """

    def apply_annotation(self, ann):
        """
        This applies an annotation. 

        This is currently a dummy example.
        """
        if ann.type == "title":
            self.add_chars(ann.start_cc, True, "# ")
        elif ann.type == 'yigchung':
            self.add_chars(ann.start_cc, True, "*")
            self.add_chars(ann.end_cc, False, '*')
        else:
            pass # to be implemented