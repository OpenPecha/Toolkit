from collections import defaultdict
from pathlib import Path

import yaml

from openpecha.serializers import SerializeFootNote


def to_bo_pagination(text):

    def index_to_bo(index):
        chars = list(index)
        result = ''
        for c in chars:
            if c.isdigit():
                result += bo_num[int(c)]
            elif c == 'a':
                result += sides[0]
            else:
                result += sides[1]
        return result + '་'

    bo_num = '༠༡༢༣༤༥༦༧༨༩'
    sides = 'ནབ'

    result = ''
    is_first_fn_passed = False
    for line in text.split('\n'):
        if not line: continue
        if line.startswith('[v'): continue
        if line.startswith('[^'):
            if is_first_fn_passed:
                result += f'{line}\n'
            else:
                result += f'\n{line}\n'
                is_first_fn_passed = True
        elif line.startswith('['):
            en_pg_index = line.strip()[1:-1]
            bo_pg_index = index_to_bo(en_pg_index)
            result += f'({bo_pg_index})\n'
        else:
            result += f'{line}\n'

    return result


def create_foot_notes(text_id, opf_path, metadata, index_layer):
    serializer = SerializeFootNote(
        opf_path, text_id=text_id, index_layer=index_layer,
        layers=['peydurma-note', 'correction', 'pagination']
    )
    serializer.apply_layers()
    annotated_text, text_id = serializer.get_result()
    
    bo_text = to_bo_pagination(annotated_text)
    return f'{bo_text[0]}{metadata[text_id]["loc"]} {bo_text[1:]}'


def get_text_metadata(path):
    import xml.dom.minidom as md
    from pyewts import pyewts
    converter = pyewts()

    def _text(tag_name, to_bo=False, is_loc=False):
        tag = item.getElementsByTagName(tag_name)
        if not tag: return 'no-author'
        if not tag[0].firstChild:
            if tag_name == 'author':
                return 'no-author'
            else:
                return ''
        value = tag[0].firstChild.nodeValue
        if to_bo:
            return converter.toUnicode(value)
        if is_loc:
            name = converter.toUnicode(value.split(',')[0])
            vol = converter.toUnicode(value.split(',')[1].split(' ')[1])
            return f'{name}། {vol}'
        else:
            return value

    metadata = defaultdict(dict)
    dom = md.parseString(path.read_text())
    for item in dom.getElementsByTagName('item'):
        metadata[_text('ref')] = {
            'title': _text('tib', to_bo=True),
            'author': _text('author', to_bo=True),
            'loc': _text('loc', is_loc=True)
        }

    return metadata


if __name__ == "__main__":
    data_path = Path('../openpecha-user')
    opf_path = data_path/'.openpecha/data/P000002/P000002.opf'
    notes_path = data_path/'data'/'2-1-a_reinserted'
    text_metadata_path = data_path/'data'/'tanjurd.xml'

    text_metadata = get_text_metadata(text_metadata_path)
    index_layer = yaml.safe_load((opf_path/'index.yml').open())

    for path in sorted(notes_path.iterdir())[1:]:
        text_id = path.name.split('_')[0]
        foot_noted_text = create_foot_notes(text_id, opf_path, text_metadata, index_layer)
        print(foot_noted_text)