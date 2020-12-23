import re
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel


# Shared properties
class PageBase(BaseModel):
    id: str
    page_no: int
    content: str
    link: str


class Page(PageBase):
    name: str
    notes_page_id: Optional[str]


class NotesPage(PageBase):
    pass


class Text(BaseModel):
    id: str
    pages: List[Page]
    notes: Optional[List[NotesPage]]


def get_pages(vol_text):
    result = []
    pg_text = ""
    pages = re.split(r"(\[[0-9]+[a-z]{1}\])", vol_text)
    for i, page in enumerate(pages[1:]):
        if i % 2 == 0:
            pg_text += page
        else:
            pg_text += page
            result.append(pg_text)
            pg_text = ""
    return result


def get_body_text(text_with_durchen):
    durchen_starting = re.search("<d", text_with_durchen).start()
    text_content = text_with_durchen[:durchen_starting]
    return text_content


def get_durchen(text_with_durchen):
    durchen_start = re.search("<d", text_with_durchen).start()
    durchen_end = re.search("d>", text_with_durchen).start()
    durchen = text_with_durchen[durchen_start:durchen_end]
    durchen = add_first_page_ann(durchen)
    return durchen


def add_first_page_ann(text):
    lines = text.splitlines()
    line_pat = re.search(r"\[(\w+)\.(\d+)\]", lines[1])
    page_ann = f"[{line_pat.group(1)}]"
    line_ann = f"[{line_pat.group(1)}.{int(line_pat.group(2))-1}]"
    new_text = f"{page_ann}\n{line_ann}{text}"
    return new_text


def get_link(pg_num, text_meta):
    vol = text_meta["vol"]
    work = text_meta["work_id"]
    img_group_offset = text_meta["img_grp_offset"]
    pref = text_meta["pref"]
    igroup = f"{pref}{img_group_offset+vol}"
    link = f"https://www.tbrc.org/browser/ImageService?work={work}&igroup={igroup}&image={pg_num}&first=1&last=2000&fetchimg=yes"
    return link


def get_page_num(page_ann):
    pg_num = int(page_ann[:-1]) * 2
    pg_face = page_ann[-1]
    if pg_face == "a":
        pg_num -= 1
    return pg_num


def get_page_obj(page, text_meta, tag):
    if tag == "note":
        page_obj = NotesPage()
    else:
        page_obj = Page()
    page_index = re.search(r"\[([𰵀-󴉱])?([0-9]+[a-z]{1})\]", page).group(2)
    page_content = re.sub(r"\[([𰵀-󴉱])?[0-9]+[a-z]{1}\]", "", page)
    page_content = re.sub(r"\[(\w+)\.(\d+)\]", "", page_content)
    pg_num = get_page_num(page_index)
    page_link = get_link(pg_num, text_meta)
    if page_content != "\n":
        page_obj.page_no = pg_num
        page_obj.content = page_content
        page_obj.link = page_link
    return page_obj


def get_page_obj_list(text, text_meta, tag="text"):
    page_obj_list = []
    pages = get_pages(text)
    for page in pages:
        pg_obj = get_page_obj(page, text_meta, tag)
        page_obj_list.append(pg_obj)
    return page_obj_list


def get_text(text_id, text_content, text_meta):
    text = Text()
    text_content = add_first_page_ann(text_content)
    text_content = re.sub("[𰵀-󴉱]", "", text_content)
    text = get_text(text_content)
    durchen = get_durchen(text_content)
    pages = get_page_obj_list(text, text_meta, tag="text")
    notes = get_page_obj_list(durchen, text_meta, tag="note")
    text.pages = pages
    text.notes = notes
    return text
