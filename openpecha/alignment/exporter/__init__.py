from pathlib import Path


class Exporter:
    def __init__(self, alignment_path) -> None:
        self.alignment_path = Path(alignment_path)

    def export(self):
        raise NotImplementedError
