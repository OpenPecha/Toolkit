from .segmenters import Segmenter


class Alignment:
  def __init__(self, id=None, segmenter: Segmenter = None):
    self.id = id
    self.segmentor = segmentor

  def create(self):
    pass



  def export(self, format=None):
    pass
