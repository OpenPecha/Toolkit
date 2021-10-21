import re
from pathlib import Path

from openpecha.blupdate import *
from openpecha.utils import download_pecha, dump_yaml, load_yaml


def get_meta(pecha_id, branch="main", pecha_path=None):
    """Return meta data of pecha

    Args:
        pecha_id (str): pecha id
        pecha_path (path, optional): pecha path. Defaults to None.

    Returns:
        dict: meta data of pecha
    """
    if not pecha_path:
        pecha_path = download_pecha(pecha_id, branch=branch)
    meta = load_yaml(Path(f"{pecha_path}/{pecha_id}.opf/meta.yml"))
    return meta


def get_pagination_layer(pecha_id, vol_meta, branch="main", pecha_path=None):
    """Return pagination layer of a volume from pecha opf of mentioned pecha id

    Args:
        pecha_id (str): pecha id
        vol_meta (dict): volume meta data
        pecha_path (path, optional): pecha path. Defaults to None.

    Returns:
        dict: pagination layer of the volume passed in parameter from mentioned pecha_id in parameter
    """
    vol_id = re.sub(r"\..+", "", vol_meta["base_file"])
    if not pecha_path:
        pecha_path = download_pecha(pecha_id, branch=branch)
    pagination_layer = load_yaml(
        Path(f"{pecha_path}/{pecha_id}.opf/layers/{vol_id}/Pagination.yml")
    )
    return pagination_layer


def get_vol_info(pecha_id, branch="main", pecha_path=None):
    """Return volumes information in pecha
    Args:
        pecha_id (str): pecha id
        pecha_path (path, optional): pecha path. Defaults to None.

    Returns:
        list: list of dict containing each volume's detail
    """
    vols = []
    meta_data = get_meta(pecha_id, branch=branch, pecha_path=pecha_path)
    for vol_uuid, vol_info in meta_data["source_metadata"]["volumes"].items():
        cur_vol = {
            "id": vol_uuid,
            "title": vol_info["title"],
            "image_group_id": vol_info["image_group_id"],
        }
        vols.append(cur_vol)
    return vols


def get_pages_info(pecha_id, vol_id, branch="main", pecha_path=None):
    """Return page annotation's uuids in mentioned volume number

    Args:
        pecha_id (str): pecha id
        vol_id (str): volume uuid
        pecha_path (path, optional): pecha path. Defaults to None.

    Returns:
        list: page annotation's uuids in mentioned volume number in sorted order
    """

    pages = []
    pecha_meta = get_meta(pecha_id, branch=branch, pecha_path=pecha_path)
    vol_meta = pecha_meta["source_metadata"]["volumes"][vol_id]
    pagination_layer = get_pagination_layer(
        pecha_id, vol_meta, branch=branch, pecha_path=pecha_path
    )
    pages = [ann_uuid for ann_uuid, ann in pagination_layer["annotations"].items()]
    return pages


def get_base_text(pecha_id, vol_meta, branch="main", pecha_path=None):
    """Return base text of the mentioned volume number

    Args:
        pecha_id (str): pecha id
        vol_meta (dict): volume meta data
        pecha_path (path, optional): pecha path. Defaults to None.

    Returns:
        str: base text of volume
    """
    base_text = ""
    base_fn = vol_meta["base_file"]
    if not pecha_path:
        pecha_path = download_pecha(pecha_id, branch=branch)
    base_text = Path(f"{pecha_path}/{pecha_id}.opf/base/{base_fn}").read_text(
        encoding="utf-8"
    )
    return base_text


def get_page_content(page_ann, base_text):
    """Return page content from base text

    Args:
        page_ann (dict): span of page, page reference, page index are included
        base_text (str): base text

    Returns:
        str: page content
    """
    page_span = page_ann["span"]
    page_start_idx = page_span["start"]
    page_end_idx = page_span["end"]
    page_content = base_text[page_start_idx : page_end_idx + 1]
    return page_content


def get_page_image_url(page_ann, vol_meta):
    """Return image url of the page

    Args:
        page_ann (dict): page annotation
        vol_meta (dict): volume meta data

    Returns:
        str: image url of page
    """
    cur_image_grp_id = ""
    cur_image_grp_id = vol_meta["image_group_id"]
    image_ref = page_ann["reference"]
    image_url = f"https://iiif.bdrc.io/bdr:{cur_image_grp_id}::{image_ref}/full/max/0/default.jpg"
    return image_url


def get_page(pecha_id, vol_id, page_id, branch="main", pecha_path=None):
    """Return page detail of mentioned page id

    Args:
        pecha_id (strt): pecha id
        vol_id (str): volume uuid
        page_id (uuid): uuid of page
        pecha_path (path, optional): pecha path. Defaults to None.

    Returns:
        dict: page content and image url of page will be return
    """
    page_info = {"content": None, "image_url": None}
    pecha_meta = get_meta(pecha_id, branch=branch, pecha_path=pecha_path)
    vol_meta = pecha_meta["source_metadata"]["volumes"][vol_id]
    pagination_layer = get_pagination_layer(
        pecha_id, vol_meta, branch=branch, pecha_path=pecha_path
    )
    base_text = get_base_text(pecha_id, vol_meta, branch=branch, pecha_path=pecha_path)
    cur_page_ann = pagination_layer["annotations"][page_id]
    page_info["content"] = get_page_content(cur_page_ann, base_text)
    page_info["image_url"] = get_page_image_url(cur_page_ann, vol_meta)
    return page_info


def get_new_vol(old_vol, old_page, new_page_content):
    """Return new volume content by replacing old page with new page in old volume

    Args:
        old_vol (str): old base text
        old_page (str): old page content
        new_page_content (str): new page content

    Returns:
        str: new base text
    """
    old_page = old_page.strip()
    new_page = new_page_content.strip()
    new_vol = old_vol.replace(old_page, new_page)
    return new_vol


def update_layer(pecha_path, pecha_id, vol_id, old_layers, updater):
    """Save updated layer using updater object

    Args:
        pecha_path (path): pecha path
        pecha_id (str): pecha id
        vol_id (str): volume id
        old_layers (dict): contains layer name and layer details
        updater (obj): BaseLayerUpdate object
    """
    for layer_name, old_layer in old_layers.items():
        update_ann_layer(old_layer, updater)
        new_layer_path = Path(
            f"{pecha_path}/{pecha_id}.opf/layers/{vol_id}/{layer_name}.yml"
        )
        dump_yaml(old_layer, new_layer_path)
        print(f"INFO: {vol_id} {layer_name} has been updated...")


def get_old_layers(pecha_path, pecha_id, vol_id):
    """Return old layer of the mentioned volume id

    Args:
        pecha_path (path): pecha path
        pecha_id (str): pecha id
        vol_id (str): volume id

    Returns:
        dict: layer name as key and its detail as value
    """
    old_layers = {}
    layer_paths = list(Path(f"{pecha_path}/{pecha_id}.opf/layers/{vol_id}").iterdir())
    for layer_path in layer_paths:
        layer_name = layer_path.stem
        layer_content = load_yaml(layer_path)
        old_layers[layer_name] = layer_content
    return old_layers


def update_old_layers(pecha_path, pecha_id, old_vol, new_vol, vol_meta):
    """Update old layer while change recorded in base text

    Args:
        pecha_path (path): pecha path
        pecha_id (str): pecah id
        old_vol (str): old base text
        new_vol (str): new base text
        vol_meta (dict): volume meta data
    """
    vol_id = re.sub(r"\..+", "", vol_meta["base_file"])
    updater = Blupdate(old_vol, new_vol)
    old_layers = get_old_layers(pecha_path, pecha_id, vol_id)
    update_layer(pecha_path, pecha_id, vol_id, old_layers, updater)


def update_base(pecha_path, pecha_id, vol_meta, new_vol):
    """Update old base text by overwriting the new base text

    Args:
        pecha_path (path): pecha path
        pecha_id (str): pecha id
        vol_meta (dict): volume meta data
        new_vol (str): updated base text
    """
    base_fn = vol_meta["base_file"]
    Path(f"{pecha_path}/{pecha_id}.opf/base/{base_fn}").write_text(
        new_vol, encoding="utf-8"
    )
    print(f"INFO: {base_fn} base updated..")


def update_sub_text(old_pecha_idx, text_info, vol_num, vol_offset, page_start):
    """Update span of sub text acording to offset

    Args:
        old_pecha_idx (dict): old pecha index
        text_info (list): contains text uuid and text annotation details
        vol_num (int): volume number
        vol_offset (int): offset between new and old base text
        page_start (int): starting span of the page which you want to save

    Returns:
        dict: old pecha with updated sub text span
    """
    new_pecha_idx = old_pecha_idx
    check_next_sub_text = True
    text_uuid = text_info[0]
    text_ann = text_info[1]
    for sub_text_uuid, sub_text_ann in text_ann["parts"].items():
        sub_text_span = sub_text_ann["span"]
        for vol_walker, vol_span in enumerate(sub_text_span):
            if vol_span["vol"] == vol_num and vol_span["start"] > page_start:
                new_pecha_idx["annotations"][text_uuid]["parts"][sub_text_uuid]["span"][
                    vol_walker
                ]["start"] += vol_offset
            if vol_span["vol"] == vol_num and vol_span["end"] >= page_start:
                new_pecha_idx["annotations"][text_uuid]["parts"][sub_text_uuid]["span"][
                    vol_walker
                ]["end"] += vol_offset
            elif vol_span["vol"] > vol_num:
                check_next_sub_text = False
                break
        if not check_next_sub_text:
            break
    return new_pecha_idx


def update_index(vol_offset, vol_meta, page_start, old_pecha_idx):
    """Return updated index

    Args:
        vol_offset (int): length difference between old base text and new base text
        vol_meta (dict): volume meta data
        page_start (int): starting index of page that has been affected
        old_pecha_idx (dict): old pecha index

    Returns:
        dict: new index with new span using offset to adjust
    """
    new_pecha_idx = old_pecha_idx
    vol_num = int(re.search(r"\d+", vol_meta["base_file"])[0])
    check_next_text = True
    if vol_offset != 0:
        for text_uuid, text_ann in new_pecha_idx["annotations"].items():
            if text_ann["parts"]:
                text_info = [text_uuid, text_ann]
                new_pecha_idx = update_sub_text(
                    new_pecha_idx, text_info, vol_num, vol_offset, page_start
                )
            text_span = text_ann["span"]
            for vol_walker, vol_span in enumerate(text_span):
                if vol_span["vol"] == vol_num and vol_span["start"] > page_start:
                    new_pecha_idx["annotations"][text_uuid]["span"][vol_walker][
                        "start"
                    ] += vol_offset
                if vol_span["vol"] == vol_num and vol_span["end"] >= page_start:
                    new_pecha_idx["annotations"][text_uuid]["span"][vol_walker][
                        "end"
                    ] += vol_offset
                elif vol_span["vol"] > vol_num:
                    check_next_text = False
                    break
            if not check_next_text:
                break
    return new_pecha_idx


def save_page(pecha_id, vol_id, page_id, page_content, branch="main", pecha_path=None):
    """Save new page in opf

    Args:
        pecha_id (str): pecha id
        vol_id (str): volume uuid
        page_id (str): uuid of the page that needs to be saved
        page_content (str): new page content that needs to be saved
        pecha_path (path, optional): pecha path. Defaults to None.

    Returns:
        path: pecha path of updated opf
    """
    pecha_meta = get_meta(pecha_id, branch=branch, pecha_path=pecha_path)
    vol_meta = pecha_meta["source_metadata"]["volumes"][vol_id]
    if not pecha_path:
        pecha_path = download_pecha(pecha_id, branch=branch)
    old_pecha_idx = load_yaml(Path(f"{pecha_path}/{pecha_id}.opf/index.yml"))
    pagination_layer = get_pagination_layer(
        pecha_id, vol_meta, branch=branch, pecha_path=pecha_path
    )
    old_vol = get_base_text(pecha_id, vol_meta, branch=branch, pecha_path=pecha_path)
    cur_page_ann = pagination_layer["annotations"][page_id]
    old_page = get_page_content(cur_page_ann, old_vol)
    new_vol = get_new_vol(old_vol, old_page, new_page_content=page_content)
    vol_offset = len(new_vol) - len(old_vol)
    new_pecha_idx = update_index(
        vol_offset, vol_meta, cur_page_ann["span"]["start"], old_pecha_idx
    )
    update_old_layers(pecha_path, pecha_id, old_vol, new_vol, vol_meta)
    update_base(pecha_path, pecha_id, vol_meta, new_vol)
    new_pecha_idx_path = dump_yaml(
        new_pecha_idx, Path(f"{pecha_path}/{pecha_id}.opf/index.yml")
    )
    return pecha_path
