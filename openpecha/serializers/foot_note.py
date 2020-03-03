import re

from openpecha.serializers import Serialize

class SerializeFootNote(Serialize):
    """
    Serializes the foot-note for given text_id
    """

    def apply_annotation(self, vol_id, ann):
        payload = ''
        if ann['type'] == 'pagination':
            payload = f'[{ann["page_index"]}] {ann["page_info"]}\n'
        elif 'peydurma' in ann['type']:
            payload = f'<{ann["note"]}>'
        elif ann['type'] == 'correction':
            payload = f'<{ann["correction"]}>'
        
        start_cc, end_cc = self._get_adapted_span(ann['span'], vol_id)
        if ann['type'] == 'pagination':
            self.add_chars(vol_id, start_cc, True, payload)
        else:
            self.add_chars(vol_id, end_cc, False, payload)


    def generate_foot_notes(self, text):
        annotated_text = ''
        foot_notes = []
        notes = re.finditer(r'\<.*?\>', text)
        last_note_end_idx = 0
        for i, note in enumerate(notes):
            annotated_text += text[last_note_end_idx:note.span(0)[0]]
            foot_note_id = f'[^{i+1}K]'
            annotated_text += foot_note_id
            
            foot_note = f'{foot_note_id}: {text[note.span(0)[0]+1: note.span(0)[1]-1]}'
            foot_notes.append(foot_note)

            last_note_end_idx = note.span(0)[1]
        else:
            annotated_text += text[last_note_end_idx:]

        return annotated_text + '\n\n' + '\n'.join(foot_notes)


    def get_result(self):
        self.layers.pop()
        annotated_text, text_id = Serialize.get_result(self)
        return self.generate_foot_notes(annotated_text), text_id

if __name__ == "__main__":
    OPF_PECHA_PATH = '../openpecha-user/.openpecha/data/P000002/P000002.opf'

    serializer = SerializeFootNote(OPF_PECHA_PATH, text_id='D1115', layers=['peydurma-note', 'correction', 'pagination'])
    serializer.apply_layers()
    annotated_text, text_id = serializer.get_result()
    print(result)