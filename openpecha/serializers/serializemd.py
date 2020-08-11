# TODO: use inheritance and abstract classes properly, see
# https://stackoverflow.com/questions/372042/difference-between-abstract-class-and-interface-in-python

from .serialize import Serialize


class SerializeMd(Serialize):
    """
    This class is serializes an opf file into MarkDown.

    Markdown markup for layers:
        title    --> # (Heading)
        yigchung --> *(italic)*
        tsawa    --> **(blod)**
        quotes   --> `(span)`
        sapche   --> [<sapche>](#) link
    """

    def apply_annotation(self, ann):
        """
        This applies an annotation.

        This is currently a dummy example.
        """
        if ann.type == "title":
            self.add_chars(ann.start_cc, True, "# ")
        elif ann.type == "yigchung":
            self.add_chars(ann.start_cc, True, "*")
            self.add_chars(ann.end_cc, False, "*")
        elif ann.type == "tsawa":
            self.add_chars(
                ann.start_cc, True, "**"
            )  # TODO: remove new line after ** from parser
            self.add_chars(ann.end_cc, False, "**")
        elif ann.type == "quotes":
            self.add_chars(ann.start_cc, True, "`")
            self.add_chars(ann.end_cc, False, "`")
        elif ann.type == "sapche":
            self.add_chars(ann.start_cc, True, "[")
            self.add_chars(ann.end_cc, False, "](#)")
