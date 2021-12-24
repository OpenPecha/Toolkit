import os
import re
from uuid import uuid4
from zipfile import ZipFile
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup

from openpecha.core.ids import get_pecha_id
from openpecha.utils import dump_yaml


def create_metadata(ebook_path, opfs_path, id_):
    """
    It parse through the content.opf's metadata to create the metadata of the pecha
    """
    def get_meta(obj):
        if obj:
            meta = obj.next
            text = meta.text
        else:
            return None
        return text

    def parse_ebook_source_metadata(soup):
        ebook_metadata = soup.metadata
        title = get_meta(ebook_metadata.find("dc:title"))
        subtitle = get_meta(ebook_metadata.find("dc:subtitle"))
        author = get_meta(ebook_metadata.find("dc:creator"))
        publisher = get_meta(ebook_metadata.find("dc:publisher"))
        published_at = ebook_metadata.find("dc:date").next[:10]
        source_metadata = {
            "title": title,
            "author": author,
            "subtitle": subtitle,
            "publisher": publisher,
            "published_at": published_at

        }
        return source_metadata

    source_metadata = {}

    def get_layer_names(opfs_path):
        layer_names = []
        dirs = os.listdir(f"{opfs_path}/layers")
        for dir in dirs:
            tags = os.listdir(f"{opfs_path}/layers/{dir}")
            for tag in tags:
                layers = os.listdir(f"{opfs_path}/layers/{dir}/{tag}")
                for layer in layers:
                    if layer not in layer_names:
                        layer_names.append(layer)
        return layer_names

    def get_todays_date():
        today = date.today()
        year = today.year
        month = today.month
        day = today.day
        todays_date = f"{day}/{month}/{year}"
        return todays_date

    content = Path(f"{ebook_path}/content.opf").read_text(encoding='utf-8')
    soup = BeautifulSoup(content, "html.parser")
    source_metadata = parse_ebook_source_metadata(soup)
    layer_names = get_layer_names(opfs_path)
    source_metadata["layers"] = layer_names

    metadata = {
        "id": id_,
        "initial_creation_type": "ebook",
        "created_at": get_todays_date(),
        "last_modified_at": get_todays_date(),
        "source_metadata": source_metadata

    }
    meta_path = Path(f"{opfs_path}/meta.yml")
    dump_yaml(metadata, meta_path)
     

def write_base_text(ps, dirs, filename,):
    base_text = ""
    for p in ps:
        if p.text:
            base_text += p.text + "\n"
    Path(f"{dirs['base_path']}/{filename}.txt").write_text(base_text, encoding='utf-8')


def write_layer(current_annotation, current_class, filename, dirs, type):
    annotations = {}
    
    for span in current_annotation:
        uuid = uuid4().hex
        ann = { 
            uuid :{
                "span": span["span"]
                }
            }
        annotations.update(ann)
    layer = {
        "id": uuid4().hex,
        "annotation_name": current_class,
        "revision": "00001",
        "annotations": annotations
    }

    Path(f"{dirs['layers_path']}/{filename}").mkdir(exist_ok=True)
    Path(f"{dirs['layers_path']}/{filename}/{type}").mkdir(exist_ok=True)
    layer_path = Path(f"{dirs['layers_path']}/{filename}/{type}/{current_class}.yml")
    dump_yaml(layer, layer_path)


def parse_ann(tmp_text, walker):
    span_dict = {"span":{
        "start": walker, 
        "end": len(tmp_text) - 1 + walker
        }
    }
    return span_dict

def get_annotation_of_paragraph(paragraph_html, current_class):
    """

    It goes through the new paragraph_htmls and calculate the text's 
    span start and end of the paragraph with class equal to current_class.
    Args:
        paragraph_html(list): It contains the paragraph list of the html with class all None except the class equal to current_class
        current_class(str): It is the current span, which's layer's annotations are created
    returns:
        current_annortation(list): It is a list of the annotations of the current_class
    """
    temp_text = ""
    base_text = ""
    current_annotation = []
    walker = 0
    soup = BeautifulSoup(paragraph_html, "html.parser")
    ps = soup.find_all("p")
    for p in ps:
        if p["class"][0] == current_class:
            temp_text = p.text
            if temp_text:
                current_annotation.append(
                    parse_ann(temp_text, walker)
                )
                base_text += temp_text + "\n"
                walker += len(temp_text) + 1
        elif p["class"][0] == "None":
            temp_text = p.text
            if temp_text:
                base_text += temp_text + "\n"
                walker += len(temp_text) + 1
 
    return current_annotation

def get_annotation_of_span(paragraph_html, current_class):
    """

    It goes through the new paragraph_htmls and calculate the text's 
    span start and end of the paragraph with class equal to current_class or span with equal to current_class.
    Args:
        paragraph_html(list): It contains the paragraph list of the html with class all None except the class equal to current_class
        current_class(str): It is a span tag, which's layer annotations are created
    returns:
        current_annortation(list): It is a list of the annotations of the current_class
    """
    temp_text = ""
    base_text = ""
    current_annotation = []
    walker = 0
    soup = BeautifulSoup(paragraph_html, "html.parser")
    ps = soup.find_all("p")
    for p in ps:
        if p["class"][0] == current_class:
            temp_text = p.text
            if temp_text:
                current_annotation.append(
                    parse_ann(temp_text, walker)
                )
                base_text += temp_text + "\n"
                walker += len(temp_text) + 1
        elif p["class"][0] == "None":
            temp_text = p.text
            if temp_text:
                base_text += temp_text + "\n"
                walker += len(temp_text) + 1
        elif p["class"][0] == "span":
            spans = p.find_all("span")
            for span in spans:
                if current_class == span["class"][0]:
                    temp_text = span.text
                    if temp_text:
                        current_annotation.append(
                            parse_ann(temp_text, walker)
                        )
                elif span["class"][0] == "None":
                    temp_text = span.text
        
                base_text += temp_text
                walker += len(temp_text)
            base_text += "\n"
            walker += 1
        temp_text = ""  
    return current_annotation


def get_para_class(p):
    """ Returns the class name of the paragraph
    """
    try:
        p["class"][0]
        return p["class"][0]
    except:
        return None


def get_span_html(ps, current_class):
    """
    It goes through all the paragraph's span class and change all the span class to None, except the span class equal to current_class
    """
    span_html = ""
    for p in ps:
        para_text = p.text
        if para_text:
            para_soup = BeautifulSoup(repr(p), "html.parser")
            if para_soup.find("span"):
                span_tags = para_soup.find_all("span")
                if len(span_tags) > 1:
                    span_html += "<p class=span>"
                    for span_tag in span_tags:
                        try:
                            span_tag["class"][0]
                            if current_class == span_tag["class"][0]:
                                text = f"<span class={current_class}>{span_tag.text}</span>"
                            else:
                                text = f"<span class=None>{span_tag.text}</span>"
                        except:
                            text = f"<span class=None>{span_tag.text}</span>"
                        span_html += text
                    span_html += "</p>\n"
                else:
                    for span_tag in span_tags:
                        try:
                            span_tag["class"][0]
                            if current_class == span_tag["class"][0]:
                                span_text = span_tag.text
                                text = f"<p class={current_class}>{span_text}</p>\n"
                                if span_text != para_text:
                                    texts = re.split(fr"{span_text}", para_text )
                                    span_html += "<p class=span>"
                                    span_html += f"<span class=None>{texts[0]}</span>"
                                    span_html += f"<span class={current_class}>{span_text}</span>\n"
                                    span_html += f"<span class=None>{texts[1]}</span>"
                                    span_html += "</p>\n"
                                else:
                                    span_html += text
                            else:
                                span_text = span_tag.text
                                text = f"<p class=None>{span_text}</p>\n"
                                span_html += text
                        except:
                            text = f"<p class=None>{span_tag.text}</p>\n"
                            span_html += text
            else:
                text = f"<p class=None>{para_text}</p>"
                span_html += text + "\n"
    return span_html


def create_layer_for_span(html_soup, filename, dirs):
    """
    It parse through the html_soup for all the span within the paragraph tag of the html and create the layer files 
    """
    all_classes = []
    ps = html_soup.find_all("p")
    for p in ps:
        span_html = ""
        para_text = p.text
        if para_text:
            para_soup = BeautifulSoup(repr(p), "html.parser")
            if para_soup.find("span"):
                span_tags = para_soup.find_all("span")
                for span_tag in span_tags:
                    try:
                        span_tag["class"][0]
                        current_class = span_tag["class"][0]
                        if current_class not in all_classes:
                            span_html = get_span_html(ps, current_class)
                            break
                    except:
                        print("no class")
                if span_html:
                    type = "Span_Tag"
                    current_annotation = get_annotation_of_span(span_html, current_class)
                    write_layer(current_annotation, current_class, filename, dirs, type)
                    all_classes.append(current_class)


def get_all_paragraph_with_current_class(ps, current_class):
    """
    It goes through all the paragraph's class and change all the class to None, except the class equal to current_class
    """
    paragraph_html = ""
    for p in ps:
        try:
            p["class"][0]
            if p["class"][0] == current_class:
                text = f"<p class={current_class}>{p.text}</p>"
                paragraph_html += text + "\n"
            else:
                text = f"<p class=None>{p.text}</p>"
                paragraph_html += text + "\n"
        except:
            if p.text:
                text = f"<p class=None>{p.text}</p>"
                paragraph_html += text + "\n"
    return paragraph_html


def build_base_and_layers(html, filename, dirs):
    """
    To Build the base and layers
    """
    soup = BeautifulSoup(html, "html.parser")
    all_classes = []
    ps = soup.find_all("p")
    if ps:
        for p in ps:
            try:
                p["class"][0]
                current_class = p["class"][0]
                if current_class not in all_classes:
                    type = "Paragraph_Tag"
                    paragraph_html = get_all_paragraph_with_current_class(ps, current_class)
                    current_annotation = get_annotation_of_paragraph(paragraph_html, current_class)
                    write_layer(current_annotation, current_class, filename, dirs, type)
                    all_classes.append(current_class)
            except Exception as e:
                print(e)
        create_layer_for_span(soup, filename, dirs)
        write_base_text(ps, dirs, filename)


def get_html_path(ebook_path):
    """
    It yeilds all the html_paths which are in spine tag of the content.opf
    """
    def get_hrefs(soup, idrefs):
        all_paths = []
        manifest = soup.manifest
        for item in manifest:
            if item != "\n":
                id = item.get("id")
                if id in idrefs:
                    path = item.get("href")
                    all_paths.append(path)
        return all_paths

    def get_all_paths_of_content(soup):
        idrefs = []
        all_toc = soup.spine
        for toc in all_toc:
            if toc != "\n":
                id = toc.get("idref")
                idrefs.append(id)
        all_paths = get_hrefs(soup, idrefs)
        return all_paths

    content = Path(f"{ebook_path}/content.opf").read_text(encoding='utf-8')
    soup = BeautifulSoup(content, "html.parser")

    for html_fn in get_all_paths_of_content(soup):
        html_path = ebook_path/html_fn
        yield html_path


def build_dirs(output_path, id_):
    """
    Build the necessary directories for OpenPecha format.
    """
    if id_:
        pecha_id = id_
    else:
        pecha_id = get_pecha_id()

    dirs = {
        "opf_path": f"{output_path}/{pecha_id}/{pecha_id}.opf"
    }
    dirs["layers_path"] = Path(f"{dirs['opf_path']}/layers")
    dirs["base_path"] = Path(f"{dirs['opf_path']}/base")
    dirs["layers_path"].mkdir(parents=True, exist_ok=True)
    dirs["base_path"].mkdir(parents=True, exist_ok=True)
    return dirs


def create_opf(ebook_path, output_path, id_=None):
    """ It creates the opf of the unzipped ebook with html tags as a layer yaml file.
    
    Args:
        ebook_path(str): It is the path of the unzipped ebook directory.
        ouput_path(str): It is the path to where the opf is to be created.
        id_(str): It is name of the pecha(Optional)
    """

    ebook_path = Path(f"{ebook_path}/OEBPS")
    dirs = build_dirs(output_path, id_)

    # cover image path
    image_path = ebook_path / "Images"
    asset_path = Path(f"{dirs['opf_path']}/assets")
    asset_path.mkdir(exist_ok=True)
    os.system(f"cp -R {image_path} {asset_path}")
    
    # parse base and layers from html files of ebook
    for html_path in get_html_path(ebook_path):
        html = Path(html_path).read_text()
        filename = Path(html_path).stem
        build_base_and_layers(html, filename, dirs )
    create_metadata(ebook_path, dirs['opf_path'], id_)

    return Path(dirs['opf_path'])

def unzip_epub(epub_path, epub_name, ebook_output_path):
    """
    It changes the .epub to .zip and then unzip the zipped ebook.
    returns:
        output_path(str): It is the path of the unzipped ebook.
    """
    if not os.path.exists(f"{ebook_output_path}/{epub_name}"):
        os.mkdir(f"{ebook_output_path}/{epub_name}")
    ebook_path = Path(f"{ebook_output_path}/{epub_name}")
    epub_path = Path(f"{epub_path}.epub")
    os.system(f"cp -R {epub_path} {ebook_path}")
    epub = Path(f"{ebook_path}/{epub_name}.epub")
    epub.rename(epub.with_suffix('.zip'))
    zf = ZipFile(f"{ebook_path}/{epub_name}.zip")
    zf.extractall(f"{ebook_path}")
    os.remove(Path(f"{ebook_path}/{epub_name}.zip"))

    return ebook_path



def ebook_to_opf(epub_path, output_path, pecha_id=None):
    """
    This function takes the epub and unzip it then .
    returns:
        output_path(str): It is the path of the unzipped ebook.
    """
    output_path = Path(f"{output_path}/pecha")
    output_path.mkdir(exist_ok=True)
    epub_name = epub_path.stem
    ebook_output_path = Path(f"{output_path}/ebook_output")
    ebook_output_path.mkdir(exist_ok=True)
    ebook_path = unzip_epub(epub_path, epub_name, ebook_output_path)
    pecha_opf_path = create_opf(ebook_path, output_path, pecha_id)
   
    return pecha_opf_path

