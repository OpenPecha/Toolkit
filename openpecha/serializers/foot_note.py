import re

from .serialize import Serialize


class SerializeFootNote(Serialize):
    """
    Serializes the foot-note for given text_id
    """

    def apply_annotation(self, vol_id, ann):
        payload = ""
        if ann["type"] == "pagination":
            payload = f'[{ann["page_index"]}] {ann["page_info"]}\n'
            start_cc, end_cc = self._get_adapted_span(ann["span"], vol_id)
            self.add_chars(vol_id, start_cc, True, payload)
        elif "peydurma" in ann["type"]:
            payload = f'<{ann["note"]}>'
            start_cc, end_cc = self._get_adapted_span(ann["span"], vol_id)
            self.add_chars(vol_id, end_cc, True, payload)
        elif ann["type"] == "correction":
            start_cc, end_cc = self._get_adapted_span(ann["span"], vol_id)
            error = self.base_layers[vol_id][start_cc : end_cc + 1]
            self.base_layers[vol_id] = (
                self.base_layers[vol_id][:start_cc]
                + ann["correction"]
                + self.base_layers[vol_id][end_cc + 1 :]
            )

            payload = f"<{error} སྡེ་དགེ།>"
            n_diff = len(ann["correction"]) - len(error)
            if not n_diff == 0:
                self.n_char_shifted.append((ann["span"]["start"], n_diff))
                start_cc, end_cc = self._get_adapted_span(ann["span"], vol_id)
            self.add_chars(vol_id, end_cc, False, payload)

    def generate_foot_notes(self, text):

        annotated_text = ""
        foot_notes = []
        notes = re.finditer(r"\<.*?\>", text)
        last_note_end_idx = 0
        for i, note in enumerate(notes):
            start, end = note.span(0)
            note_text = text[start:end]
            annotated_text += text[last_note_end_idx:start]
            foot_note_id = f"[^{i+1}K]"
            annotated_text += foot_note_id
            foot_notes.append(f"{foot_note_id}: {note_text[1:-1]}")
            last_note_end_idx = note.span(0)[1]
        else:
            annotated_text += text[last_note_end_idx:]

        return annotated_text + "\n\n" + "\n".join(foot_notes)

    def get_result(self):
        self.layers.pop()
        annotated_text, text_id = Serialize.get_result(self)
        return self.generate_foot_notes(annotated_text), text_id


if __name__ == "__main__":
    OPF_PECHA_PATH = "../openpecha-user/.openpecha/data/P000002/P000002.opf"

    serializer = SerializeFootNote(
        OPF_PECHA_PATH,
        text_id="D1794",
        layers=["correction", "peydurma-note", "pagination"],
    )
    serializer.apply_layers()
    annotated_text, text_id = serializer.get_result()
    print(annotated_text)
