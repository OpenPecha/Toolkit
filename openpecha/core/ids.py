import random
from uuid import uuid4


def get_uuid():
    return uuid4().hex


def get_id(prefix, length):
    return prefix + "".join(random.choices(uuid4().hex, k=length)).upper()


def get_pecha_id():
    return get_id(prefix="P", length=8)


def get_work_id():
    return get_id(prefix="W", length=8)


def get_alignment_id():
    return get_id(prefix="A", length=8)


def get_collection_id():
    return get_id(prefix="C", length=8)
