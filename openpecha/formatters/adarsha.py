from logging import raiseExceptions
import os
from pathlib import Path
from uuid import uuid4
import shutil
import requests
import re
import json
from bs4 import BeautifulSoup

from openpecha.core.annotation import Page, Span
from openpecha.core.layer import InitialCreationEnum, Layer, LayerEnum, PechaMetaData
from openpecha.core.pecha import OpenPechaFS
from openpecha.utils import load_yaml
from openpecha.core.ids import get_pecha_id
from datetime import datetime


base = "https://adarsha.dharma-treasure.org/"
workBase = "https://adarsha.dharma-treasure.org/kdbs/{name}"
apiBase = "https://adarsha.dharma-treasure.org/api/kdbs/{name}/pbs?size=10&lastId={pbs}"
sutraBase = "https://adarsha.dharma-treasure.org/api/kdbs/{name}/biographies/{sutra_id}"

prev_volume = None
prev_Line = []
vol_sutra_map = {}


def writePage(page, opf_path, is_last, is_test):

    global prev_Line, prev_volume
    volume = extractLines(page)
    if volume == prev_volume and is_last == False:
        prev_Line.append(page)
    elif prev_volume != None and is_last == False:
        prev_volume = "{:0>3d}".format(int(prev_volume))
        create_opf(str(prev_volume), prev_Line, opf_path)
        prev_Line.clear()
        prev_Line.append(page)
        prev_volume = volume
    elif is_last == True:
        prev_Line.append(page)
        volume = "{:0>3d}".format(int(volume))
        create_opf(str(volume), prev_Line, opf_path)
    else:
        prev_Line.clear()
        prev_Line.append(page)
        prev_volume = volume


def extractLines(page):

    lines = []
    vol = page["pbId"]
    volume = int(re.search(r'(\d+?)-', vol).group(1))

    return volume


def testUrl(work, pbs):
    # check if url has text
    url = apiBase.format(name=work[0], pbs=pbs)
    response = get_response(url)
    if response.text == '{"total":0,"data":[]}':
        status = False
    else:
        status = True
    return status


def normalizeUni(strNFC):
    strNFC = strNFC.replace("\u0F00", "\u0F68\u0F7C\u0F7E")  # ༀ
    strNFC = strNFC.replace("\u0F43", "\u0F42\u0FB7")  # གྷ
    strNFC = strNFC.replace("\u0F48", "\u0F47\u0FB7")  # ཈
    strNFC = strNFC.replace("\u0F4D", "\u0F4C\u0FB7")  # ཌྷ
    strNFC = strNFC.replace("\u0F52", "\u0F51\u0FB7")  # དྷ
    strNFC = strNFC.replace("\u0F57", "\u0F56\u0FB7")  # བྷ
    strNFC = strNFC.replace("\u0F5C", "\u0F5B\u0FB7")  # ཛྷ
    strNFC = strNFC.replace("\u0F69", "\u0F40\u0FB5")  # ཀྵ
    strNFC = strNFC.replace("\u0F73", "\u0F71\u0F72")  # ཱི
    strNFC = strNFC.replace("\u0F75", "\u0F71\u0F74")  # ཱུ
    strNFC = strNFC.replace("\u0F76", "\u0FB2\u0F80")  # ྲྀ
    strNFC = strNFC.replace("\u0F77", "\u0FB2\u0F71\u0F80")  # ཷ
    strNFC = strNFC.replace("\u0F78", "\u0FB3\u0F80")  # ླྀ
    strNFC = strNFC.replace("\u0F79", "\u0FB3\u0F71\u0F80")  # ཹ
    strNFC = strNFC.replace("\u0F81", "\u0F71\u0F80")  # ཱྀ
    strNFC = strNFC.replace("\u0F93", "\u0F92\u0FB7")  # ྒྷ
    strNFC = strNFC.replace("\u0F9D", "\u0F9C\u0FB7")  # ྜྷ
    strNFC = strNFC.replace("\u0FA2", "\u0FA1\u0FB7")  # ྡྷ
    strNFC = strNFC.replace("\u0FA7", "\u0FA6\u0FB7")  # ྦྷ
    strNFC = strNFC.replace("\u0FAC", "\u0FAB\u0FB7")  # ྫྷ
    strNFC = strNFC.replace("\u0FB9", "\u0F90\u0FB5")  # ྐྵ
    return strNFC


def getwork(work, opf_path, is_test):
    i = work[1]
    j = 0
    while testUrl(work, i):
        url = apiBase.format(name=work[0], pbs=i)
        response = get_response(url)
        text = response.text.replace("},{", "},\n{")
        text = normalizeUni(text)
        text = json.loads(text)
        pages = text["data"]
        is_last = False if testUrl(work, i + 10) else True
        for page in pages:
            page["text"] = page["text"].replace('\r', '')
            writePage(page, opf_path, is_last, is_test)

        if is_test:
            create_opf(str("{:0>3d}".format(int(prev_volume))), prev_Line, opf_path)
            return
        i += 10

    create_index_meta(opf_path, work)


def create_opf(file_name, formatted_line, opf_path):

    global vol_sutra_map
    vol_sutra_map[file_name] = formatted_line[0]["BiographyId"]

    with open("sutra_map.txt", "w") as f:
        f.write(str(vol_sutra_map))

    opf = OpenPechaFS(opf_path=opf_path)
    layers = {f"v{file_name}": {LayerEnum.pagination: get_pagination_layer(formatted_line)}}

    base_text = get_base_text(formatted_line)
    bases = {f"v{file_name}": base_text}

    opf.layers = layers
    opf.base = bases
    opf.save_base()
    opf.save_layers()


def create_index_meta(opf_path, work):
    opf = OpenPechaFS(opf_path=opf_path)
    index = Layer(annotation_type=LayerEnum.index, annotations=get_sutra_span_map(opf_path, work))

    meta = get_metadata(opf_path, work)
    opf._index = index
    opf._meta = meta
    opf.save_index()
    opf.save_meta()


def get_sutra_span_map(opf_path, work):
    global vol_sutra_map

    with open("notes.txt", "w") as f:
        f.write(str(vol_sutra_map))

    page_annotations = {}
    sutra_id = sorted(set(vol_sutra_map.values()))
    for id in sutra_id:
        url = sutraBase.format(name=work[0], sutra_id=id)

        response = get_response(url)
        page_annotation = get_index_annotation(response.json()["data"], opf_path)
        page_annotations.update(page_annotation)

    return page_annotations


def get_index_annotation(data, opf_path):

    work_id = data["sutraid"]
    meta_data, spans = get_page_metadata(data["page"], work_id, opf_path)
    annotation = {"work_id": work_id, "parts": meta_data , "span": spans}

    page_annotation = {
        uuid4().hex: annotation
    }

    return page_annotation


def get_page_metadata(page, work_id, opf_path):
    meta_datas = {}
    page_group = page.split(",")
    spans = []

    for page in page_group:
        page_start = re.search(r"༼.+༽ (.+)~(.+)( \(.+\))?", page).group(1)
        page_end = re.search(r"༼.+༽ (.+)~(.+)( \(.+\))?", page).group(2)
        volume = int(re.search(r'(\d+?)-', page_start).group(1))

        start_span, end_span = get_span(page_start, page_end, opf_path)
        meta_data = {uuid4().hex: {"work_id": f"{work_id}-{volume}", "span": [{"vol": volume , "start": start_span, "end": end_span}]}}
        meta_datas.update(meta_data)
        spans.append({"vol": volume , "start": start_span, "end": end_span})

    return (meta_datas, spans)


def get_span(page_start, page_end, opf_path):
    start = ""
    end = ""

    vol_start = int(re.search(r'(\d+?)-', page_start).group(1))
    vol_end = int(re.search(r'(\d+?)-', page_end).group(1))

    vol = "{:0>3d}".format(vol_start)

    page_start = get_standard_sutra_format(page_start)
    page_end = get_standard_sutra_format(page_end)

    start_img = re.search(r"(\d+?-\d+?-\d+?[a-z]+)\d?", page_start).group(1).replace("line", "")
    end_img = re.search(r"(\d+?-\d+?-\d+?[a-z]+)\d?", page_end).group(1).replace("line", "")

    start_line = re.search(r"\d+?-\d+?-(\d+?)[a-z]+(\d?)", page_start).group(2)
    end_line = re.search(r"\d+?-\d+?-(\d+?)[a-z]+(\d?)", page_end).group(2)

    start_line = start_line if start_line else "firstline"
    end_line = end_line if end_line else "endline"

    pagination_layer_path = Path(f"{opf_path}/layers/v{vol}/Pagination.yml")
    pagination_yml = load_yaml(pagination_layer_path)
    paginations = pagination_yml["annotations"]

    base_layer_path = f"{opf_path}/base/v{vol}.txt"

    for pagination in paginations:
        if paginations[pagination]["metadata"]["Img_name"] == start_img:
            if start_line == "firstline":
                start = paginations[pagination]["span"]["start"]
            else:
                start_index = paginations[pagination]["span"]["start"]
                start = start_index + offset(base_layer_path, int(start_line), int(start_index), "start")
        elif paginations[pagination]["metadata"]["Img_name"] == end_img:
            if end_line == "endline":
                end = paginations[pagination]["span"]["end"]
            else:
                end_index = paginations[pagination]["span"]["start"]
                end = end_index - 1 + offset(base_layer_path, int(end_line), int(end_index), "end")

    return (start, end)


def get_standard_sutra_format(value):
    try:
        res = re.search(r"\d+?-\d+?-(\(.*\))?\d+?[a-z]+?\d?", value).group(1)
    except Exception as e:
        print(e)

    if res:
        return value.replace(res, "")
    else:
        return value


def offset(base_layer_path, start_line, start_index, type_of_parse):

    with open(base_layer_path) as f:
        base_text = f.read()
    count = 0
    char_count = 0

    if start_line == 1 or start_index == len(base_text):
        return 0

    for i in range(start_index, len(base_text)):
        char_count += 1
        if base_text[i] == "\n":
            count += 1
        if type_of_parse == "start" and count + 1 == start_line:
            return char_count
        elif type_of_parse == "end" and count == start_line:
            return char_count - 1
        elif i == len(base_text) - 1:
            return 0


def get_pagination_layer(formatted_line):

    page_annotations = {}
    char_walker = 0

    for line in formatted_line:
        page_annotation, end = get_page_annotation(line, char_walker)
        page_annotations.update(page_annotation)
        char_walker = end

    pagination_layer = Layer(
        annotation_type=LayerEnum.pagination, annotations=page_annotations
    )

    return pagination_layer


def get_page_annotation(line, char_walker):

    metadata = {}

    text = line["text"].lstrip("\n").lstrip("\n")
    imgnum = line["pbId"]
    pbid = line["id"]

    img_num_first = re.search(r'(\d+?-\d+?)-\d+?[a-z]?', imgnum).group(1)
    img_num_last = get_img_num(re.search(r'\d+?-\d+?-(\d+[a-z]?)', imgnum).group(1))
    img_link = f"https://files.dharma-treasure.org/degekangyur/degekangyur{img_num_first}/{imgnum}.jpg"
    metadata["pbId"] = pbid
    metadata["Img_name"] = imgnum

    text_len = 0 if len(text) <= 2 else len(text) - 2
    page_annotation = {
        uuid4().hex: Page(span=Span(start=char_walker, end=char_walker + text_len), imgnum=img_num_last, reference=img_link, metadata=metadata)
    }
    added_span = 0 if text_len == 0 else 3
    return page_annotation, (char_walker + text_len + added_span)


def get_img_num(img_num):
    img_num1 = re.search(r"\d+([a-z]?)", img_num).group(1)
    img_num2 = int(re.search(r"(\d+)[a-z]?", img_num).group(1))

    if img_num1 == "a":
        return img_num2 * 2 - 1
    elif img_num1 == "b":
        return img_num2 * 2
    elif img_num1 == "":
        return img_num2


def get_base_text(texts):
    final_base = ""
    for text in texts:
        if len(text["text"]) > 2:
            final_base += text["text"].lstrip("\n").lstrip("\n").lstrip("\n") + "\n"

    return final_base


def get_metadata(opf_path, work):
    global vol_sutra_map

    sutra_ids = sorted(set(vol_sutra_map.values()))
    vol_sutra_maps = {}

    for vol in vol_sutra_map:
        url = sutraBase.format(name=work[0], sutra_id=vol_sutra_map[vol])
        res = get_response(url)
        sutra_id = res.json()["data"]
        vol_sutra_maps[vol] = sutra_id["sutraid"]

    source_metadata = {
        "id": "",
        "title": work[0],
        "language": "bo",
        "author": "",
        "sutra": {},
    }

    for id in sutra_ids:
        url = sutraBase.format(name=work[0], sutra_id=id)
        response = get_response(url)
        sutra_id = response.json()["data"]["sutraid"]
        sutra = response.json()["data"]
        sutra.pop("sutraid")
        source_metadata["sutra"][f"{sutra_id}"] = sutra

    source_metadata["window.__data"] = start_work(opf_path, work)
    instance_meta = PechaMetaData(
        initial_creation_type=InitialCreationEnum.input,
        created_at=datetime.now(),
        last_modified_at=datetime.now(),
        source_metadata=source_metadata)

    return instance_meta


def get_response(url):
    response = requests.get(url)
    response.raise_for_status()

    if response.status_code != 204:
        return response


def start_work(opf_path, work):
    get_page_source(opf_path, work)
    results = load_json(opf_path)
    obj = get_sidebar_data(results, work)

    return obj


def get_last_pbid(work, pbid):
    i = pbid
    while testUrl(work, pbs=i):
        is_last = False if testUrl(work, i + 10) else True
        if is_last:
            url = apiBase.format(name=work[0], pbs=i)
            response = get_response(url).text
            response = json.loads(response)
            objs = response["data"]
            last_pbid = ""
            for obj in objs:
                last_pbid = obj["id"]

            return last_pbid

        i += 10


def get_sidebar_data(cur_obj, work, parent_obj=None):
    obj_li = []
    for index, obj in enumerate(cur_obj):
        if index < len(cur_obj) - 1:
            obj["pbEnd"] = cur_obj[index + 1]["PbId"]
        elif len(cur_obj) == 1 and parent_obj != None:
            obj["pbEnd"] = parent_obj["pbEnd"]
        elif index == len(cur_obj) - 1 and parent_obj != None:
            obj["pbEnd"] = parent_obj["pbEnd"]
        elif parent_obj == None:
            obj["pbEnd"] = get_last_pbid(work, obj["PbId"])

        if "nodes" in obj:
            cur_li = get_sidebar_data(obj["nodes"], work, obj)

            cur_dic = {
                "id": obj["id"],
                "text": str(obj["text"]).replace('"', '').replace("'", ""),
                "bo": str(obj["bo"]).replace('"', '').replace("'", ""),
                "en": str(obj["en"]).replace('"', '').replace("'", ""),
                "zh-TW": obj["zh-TW"] if obj["zh-TW"] else "None",
                "zh-CN": obj["zh-CN"] if obj["zh-CN"] else "None",
                "KdbId": obj["KdbId"] if obj["KdbId"] else "None",
                "SutraId": obj["SutraId"] if obj["SutraId"] else "None",
                "pbStart": obj["PbId"],
                "pbEnd": obj["pbEnd"],
                "nodes": cur_li
            }
            obj_li.append(cur_dic)
        else:

            cur_di = {
                "id": obj["id"],
                "text": str(obj["text"]).replace('"', '').replace("'", ""),
                "bo": str(obj["bo"]).replace('"', '').replace("'", ""),
                "en": str(obj["en"]).replace('"', '').replace("'", ""),
                "zh-TW": obj["zh-TW"] if obj["zh-TW"] else "None",
                "zh-CN": obj["zh-CN"] if obj["zh-CN"] else "None",
                "KdbId": obj["KdbId"] if obj["KdbId"] else "None",
                "SutraId": obj["SutraId"] if obj["SutraId"] else "None",
                "pbStart": obj["PbId"],
                "pbEnd": obj["pbEnd"],
            }
            obj_li.append(cur_di)

    return obj_li


def get_page_source(opf_path, work):
    url = workBase.format(name=work[0])
    r = get_response(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    results = soup.find("script", {"data-reactid": "23"}).text.strip()[14:-1]
    results = json.loads(results)["sidebar"]["data"]

    with open(f"{opf_path}/raw.json", "w") as f:
        f.write(json.dumps(results))


def load_json(opf_path):
    with open(f"{opf_path}/raw.json") as f:
        data = json.load(f)
    return data


def parse_adarsha(ouput_path):
    works = [
        ["degekangyur", 2977724, "Kangyur/"],
        ['lhasakangyur', 2747736, "Kangyur/"],
        ['jiangkangyur', 2561408, "Kangyur/"],
        ['degetengyur', 2843235, "Tengyur/"],
        ['tsongkhapa', 1465969 , "Works_of_Tibetan_Masters/Geden/"],
        ['chodrapal', 2711704 , "Works_of_Tibetan_Masters/Jonang/"],
        ['choglenamgyal', 2973395 , "Works_of_Tibetan_Masters/Jonang/"],
        ['dolpopa', 2969222 , "Works_of_Tibetan_Masters/Jonang/"],
        ['gharungpa', 2715383 , "Works_of_Tibetan_Masters/Jonang/"],
        ['yeshegyatsho', 2728993 , "Works_of_Tibetan_Masters/Jonang/"],
        ['nyadbonkungapal', 2725129 , "Works_of_Tibetan_Masters/Jonang/"],
        ['thugsrjebrtsongrus', 2726404 , "Works_of_Tibetan_Masters/Jonang/"],
        ['lodropal', 2976581 , "Works_of_Tibetan_Masters/Jonang/"],
        ['matipanchen', 2720612 , "Works_of_Tibetan_Masters/Jonang/"],
        ['logrosgragspa', 2715915 , "Works_of_Tibetan_Masters/Jonang/"],
        ['yontenbzangpo', 2967211 , "Works_of_Tibetan_Masters/Jonang/"],
        ['sonamgragpa', 2977266 , "Works_of_Tibetan_Masters/Jonang/"],
        ['tshalminpa', 2727252 , "Works_of_Tibetan_Masters/Jonang/"],
        ['taranatha', 2730006 , "Works_of_Tibetan_Masters/Jonang/"],
        ['8thkarmapa', 1984307 , "Works_of_Tibetan_Masters/Kagyu/"],
        ['gampopa', 1464491 , "Works_of_Tibetan_Masters/Kagyu/"],
        ['bonpokangyur', 2426116, "Texts_of_the_Bön_Tradition/"],
        ['mipam', 1489991 , "Works_of_Tibetan_Masters/Nyingma/"],
        ['gorampa', 1481195 , "Works_of_Tibetan_Masters/Sakya/"]

    ]

    for work in works:
        parse_pecha(ouput_path, work)


def path_exist(output_path):

    if not os.path.exists(output_path):
        os.makedirs(output_path)


def create_description(work, output_path, pecha_id):
    path = f"{output_path}/{pecha_id}/README.md"

    with open(path, "w") as f:
        f.write(f"{work[0]}")


def parse_pecha(output_path, work, is_test=None):
    path_exist(output_path)
    pecha_id = get_pecha_id()
    opf_path = f"{output_path}/{pecha_id}/{pecha_id}.opf"
    getwork(work, opf_path, is_test)
    create_description(work, output_path, pecha_id)
