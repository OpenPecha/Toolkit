import random
from uuid import uuid4


def get_uuid():
    return uuid4().hex


def get_id(prefix, length):
    return prefix + "".join(random.choices(uuid4().hex, k=length)).upper()


def get_base_id():
    return get_id("", length=4)


# Types of pechas


def get_initial_pecha_id():
    return get_id(prefix="I", length=8)


def get_open_pecha_id():
    return get_id(prefix="O", length=8)


def get_diplomatic_id():
    return get_id(prefix="D", length=8)


def get_work_id():
    return get_id(prefix="W", length=8)


def get_alignment_id():
    return get_id(prefix="A", length=8)


def get_collection_id():
    return get_id(prefix="C", length=8)
