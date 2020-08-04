from collections import defaultdict

from openpecha.formatters import BaseFormatter


class TsadraFormatter(BaseFormatter):
    """
    OpenPecha Formatter for Tsadra DarmaCloud ebooks
    """

    def text_preprocess(self, text):
        """
        This is temporary method to remove all the critic markups and make existing
        markup consistent.
        """
        # remove critic markup
        text = text.replace("{++", "")
        text = text.replace("++}", "")

        # edit the existing markup
        text = text.replace("###", "#")  # book_title to title
        text = text.replace("##", "#")  # chapter_title to title
        text = text.replace("**", "`")  # change tsawa markup
        text = text.replace("~~", "~")  # change quote markup

        return text

    def format_layer(self, layers):
        """
        Post-processing for various layer to easily dump into yaml file. For eg, title annotation has only one char coord, #<title_text>
        yigchung annotations has part of char coord, *<yigchun_text>*.
        """
        for layer, anns in layers.items():
            out = {}
            anns = [e - 1 if i % 2 == 0 else e for i, e in enumerate(anns, start=1)]
            for i, e in enumerate(range(0, len(anns), 2)):
                out[i] = anns[e : e + 2]
            layers[layer] = out
        return layers

    def build_layers(self, text):
        """
        Parse all the layers annotation from the given text.
        """
        layers = defaultdict(list)
        i = 0
        is_title = False
        for c in text:
            if c == "#":
                layers["title"].append(i)
                is_title = True
            elif is_title and c == "\n":
                layers["title"].append(i)
                is_title = False
                i += 1
            elif c == "*":
                layers["yigchung"].append(i)
            elif c == "`":
                layers["tsawa"].append(i)
            elif c == "~":
                layers["quotes"].append(i)
            elif c == "[" or c == "]":
                layers["sapche"].append(i)
            else:
                i += 1

        return self.format_layer(layers)

    def get_base_text(self, m_text):
        m_text = m_text.replace("#", "")
        m_text = m_text.replace("*", "")
        m_text = m_text.replace("`", "")
        m_text = m_text.replace("~", "")
        m_text = m_text.replace("[", "")
        text = m_text.replace("]", "")
        return text


if __name__ == "__main__":
    formatter = TsadraFormatter("usage/new_layer_output")
    formatter.new_poti("usage/input/W1OP000002.txt")
