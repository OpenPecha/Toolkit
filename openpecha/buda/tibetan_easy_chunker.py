from openpecha.buda.chunker import StringChunker


class TibetanEasyChunker(StringChunker):
    def __init__(self, full_string, n):
        StringChunker.__init__(
            self,
            full_string,
            "([སའངགདནབམརལཏ]\u0f7c།[^ཀ-ཬ]*|།།[^ཀ-ཬ༠-༩]*།[^ཀ-ཬ༠-༩]*)",
            n,
        )
