import argparse
from pathlib import Path
import shutil

from bs4 import BeautifulSoup
from tqdm import tqdm

#Global vars
rt_base = 'tibetan-root-text_tibetan-root-text'
root_text_classes = {
    'first': f'{rt_base}-first-line',
    'middle': f'{rt_base}-middle-lines',
    'last': f'{rt_base}-last-line'
}
p_with_citations = []


def find_titles(soup, output):
    # find all titles
    book_title = ''
    chapter_title = ''


    front_title = soup.find('p', class_='credits-page_front-title')
    if front_title:
        meta = {'Book Title': '', 'Vol Number': '', 'Book Author': ''}
        meta['Book Title'] = front_title.text
        book_number = soup.find('p', class_='credits-page_front-page---book-number')
        text_author = soup.find('p', class_='credits-page_front-page---text-author')
        if book_number: meta['Vol Number'] = book_number.text
        if text_author: meta['Book Author'] = ' '.join((text_author.text).split(' ')[1:])
        return meta, True
    else:
        book_sub_title = soup.find('p', class_='tibetan-book-sub-title')
        if not book_sub_title:
            book_sub_title = soup.find('p', class_='tibetan-book-title')
            if book_sub_title: book_sub_title = book_sub_title.text
        else:
            book_sub_title = book_sub_title.text
            book_title = soup.find('p', class_='tibetan-book-title')
            if book_title: book_title = book_title.text

        
        chapter = soup.find_all('p', class_=f'tibetan-chapter')
        if chapter: 
            chapter_title = ''.join([c.text for c in chapter])
        else:
            for i in range(1, 4):
                chapter = soup.find_all('p', class_=f'tibetan-chapter{i}')
                if chapter: 
                    chapter_title = ''.join([c.text for c in chapter])
                    break

        #write markdown
        if book_title: output += f'{{++#++}}{book_title}\n\n'
        if book_sub_title: output += f'{{++##++}}{book_sub_title}\n\n'
        if chapter_title: output += f'{{++###++}}{chapter_title}\n\n'

        return output, False


def preprocess_text(text):
    text = text.replace('{', '')
    text = text.replace('}', '')
    return text

def find_the_rest(soup, output):
    root_text_tmp = ''
    sabche_tmp = ''

    ps = soup.find_all('p')
    for p in ps[output.count('\n')//2:]:
        if rt_base in p['class'][0]:
            #TODO: one line root text.
            if p['class'][0] == root_text_classes['first'] or \
               p['class'][0] == root_text_classes['middle']:
                root_text_tmp += preprocess_text(p.text) + '\n'
            elif p['class'][0] == root_text_classes['last']:
                root_text_tmp += preprocess_text(p.text) + '\n'
                output += f'{{++**++}}\n{root_text_tmp}{{++**++}}\n\n'
                root_text_tmp = ''
        elif 'commentary' in p['class'][0] or 'regular' in p['class'][0]:
            citation_tmp = ''
            p_tmp = ''
            for s in p.contents:
                #check for page with no content and skip the page
                if isinstance(s, str): return '' 
                #some child are not <span> rather like <a> and some <span> has no 'class' attr
                try:
                    s['class'][0]
                except:
                   p_tmp += preprocess_text(s.text)
                   continue

                if 'small' in s['class'][0]:
                    p_tmp += f'{{++*++}}{preprocess_text(s.text)}{{++*++}}'
                elif 'external-citations' in s['class'][0]:
                    citation_tmp += preprocess_text(s.text)
                elif citation_tmp:
                    p_tmp += f'{{++~~++}}{citation_tmp}{{++~~++}}'
                    citation_tmp = ''
                    p_tmp += preprocess_text(s.text)
                else:
                    p_tmp += preprocess_text(s.text)

            #when citation ends the para
            if citation_tmp: p_tmp += f'{{++~~++}}{citation_tmp}{{++~~++}}'
            if p_tmp:
                output += f'{p_tmp}\n\n'
                if '~~' in p_tmp:
                    p_with_citations.append(p_tmp)
            else:
                output += '\n\n'
        elif 'sabche' in p['class'][0]:
            sabche_tmp = ''
            p_with_sabche_tmp = ''
            for s in p.contents:
                try:
                    s['class'][0]
                except:
                   p_with_sabche_tmp += preprocess_text(s.text)
                   continue

                if 'sabche' in s['class'][0]:
                    sabche_tmp += preprocess_text(s.text)
                elif sabche_tmp:
                    p_with_sabche_tmp += f'{{++[++}}{sabche_tmp}{{++]++}}'
                    sabche_tmp = ''
                    p_with_sabche_tmp += preprocess_text(s.text)
                else:
                    p_with_sabche_tmp += preprocess_text(s.text)

            #when sabche ends the para
            if sabche_tmp: p_with_sabche_tmp += f'{{++[++}}{sabche_tmp}{{++]++}}'
            output += f'{p_with_sabche_tmp}\n\n'
        else:
            output  += f'{preprocess_text(p.text)}\n\n'

    return output


def detect_fn_prefix(parts): 
    for i, e in enumerate(parts): 
        try:  
           int(e)  
           return i
        except:  
           continue

def semantic_order(html_path):
    html_fn = html_path.name
    if '_-' in html_fn or '_.' in html_fn:
        html_fn = html_fn.replace('_', '')
    
    parts = (Path(html_fn).stem).split('-')
    if '_' in html_fn:
        subtle_parts = []
        for part in parts:
            if '_' in part:
                subtle_parts.extend(part.split('_'))
            else:
                subtle_parts.extend(part)
        parts = subtle_parts

    prefix_idx = detect_fn_prefix(parts)
    if not prefix_idx: return '00'
    order = parts[prefix_idx-1:]
    if order:
        return f'{int(order[-1]):02}'
    else:
        return '00'


def parse(path, ebook_id):
    path = path/'OEBPS'
    html_paths = [o for o in path.iterdir() if o.suffix == '.xhtml' and o.stem != 'cover']
    html_paths = sorted(html_paths, key=semantic_order)

    meta_path = ((path.parent).parent).parent/'ebook_metadata.csv'
    text = ''
    htmls = [html.read_text() for html in html_paths]
    
    for html in htmls:
        soup = BeautifulSoup(html, 'html.parser')
        output = ''

        output, is_front_page = find_titles(soup, output)
        if not is_front_page:
            output = find_the_rest(soup, output)
            if output.strip('\n'): text += output + '\n\n\n\n'
        else:
            # write metadata in csv
            output['ID'] = ebook_id
            output['Slug'] = (path.parent).name
            with open(meta_path, 'a+') as meta_file:
                row = f'{output["ID"]},{output["Book Title"]},{output["Vol Number"]},{output["Book Author"]},{output["Slug"]}\n'
                meta_file.write(row)
    return text
                

if __name__ == "__main__":

    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--path", type=str, help="directory path containing all the data")
    ap.add_argument("--citation", action='store_true')
    args = ap.parse_args()
    
    out_path = Path(args.path).parent/'export'
    out_path.mkdir(parents=True, exist_ok=True)
    paths = sorted([o for o in Path(args.path).iterdir() if o.is_dir()])
    for i, path in enumerate(tqdm(paths)):
        ebook_id = f'W1OP{i+1:06}'
        fn = out_path/f'{ebook_id}.txt'
        text = parse(path, ebook_id)
        fn.write_text(text)

        # copy ebook to export and rename
        source_fn = f'{path}.epub'
        dest_fn = out_path/f'{ebook_id}.epub'
        shutil.copy(source_fn, str(dest_fn))

    if args.citation:
        #write citations to json
        import jsonpickle as jp
        jp.set_encoder_options('simplejson', sort_keys=True, indent=4, ensure_ascii=False)

        citation_fn = Path('citations.json')
        all_examples = []
        print(f'[INFO] No. of Citation examples: {len(p_with_citations)}')
        for i, citation in enumerate(p_with_citations):
            example = {'order': i, 'ex': citation, 'type': 'citation'}
            all_examples.append(example)
        citation_fn.write_text(jp.dumps(all_examples))
