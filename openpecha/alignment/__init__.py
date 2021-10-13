from .segmenters import Segmenter


class Alignment:
    def __init__(self, id=None, segmenter: Segmenter = None):
        self.id = id
        self.segmenter = segmenter

    def create(self):
        pass

    def export(self, format=None):
        pass
