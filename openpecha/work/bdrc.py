import json

import requests

from openpecha import config


def parse_work_url(work_url):
    """Extract work id from work url

    Args:
        work_url (str): work url

    Returns:
        str: bdrc work id
    """
    work_id = ""
    if work_url:
        work_url_parts = work_url.split("/")
    work_id = work_url_parts[-1]
    return work_id


def get_bdrc_work_id(bdrc_inst_id):
    """Return bdrc work id to which the given bdrc instance id belongs to

    Args:
        bdrc_inst_id (str): bdrc instance id

    Returns:
        str: bdrc work id
    """
    bdrc_work_id = ""
    instance_response = requests.get(
        f"https://purl.bdrc.io/query/graph/OP_info?R_RES=bdr:{bdrc_inst_id}&format=json"
    )
    instance = json.loads(instance_response.content)
    instance_resource = instance.get(f"http://purl.bdrc.io/resource/{bdrc_inst_id}", {})
    instance_work_meta = instance_resource.get(
        "http://purl.bdrc.io/ontology/core/instanceOf", []
    )
    if instance_work_meta:
        work_url = instance_work_meta[0].get("value", "")
        bdrc_work_id = parse_work_url(work_url)
    else:
        print("Instance is not mapped to a work yet!!!")
    return bdrc_work_id


def parse_op2bdrc_work_id(op2bdrc_work_id):
    """Return op work id and bdrc work id

    Args:
        op2bdrc_work_id (str): openpecha work id and bdrc work id

    Returns:
        list: bdrc work id and op work id
    """
    op2bdrc_work_id = str(op2bdrc_work_id)
    work_ids = op2bdrc_work_id.split(",")
    op_work_id = work_ids[0].replace("b'", "")
    bdrc_work_id = work_ids[1].replace("'", "")
    return [bdrc_work_id, op_work_id]


def get_op_work_from_bdrc_work_id(bdrc_work_id, op2bdrc_mapping):
    """Return op work id from bdrc work id

    Args:
        bdrc_work_id (str): bdrc work id
        op2bdrc_mapping (str): op work and bdrc work id mapping

    Returns:
        str: openpecha work id
    """
    op_work_id = ""
    op2bdrc_works = op2bdrc_mapping.splitlines()
    for op2bdrc_work in op2bdrc_works[1:]:
        work_ids = parse_op2bdrc_work_id(op2bdrc_work)
        if work_ids[0] == bdrc_work_id:
            return work_ids[1]
    return op_work_id


def get_op_work_id(bdrc_instance_id):
    """Return openpecha work id of the given bdrc instance id

    Args:
        bdrc_inst_id (str): bdrc instance id

    Returns:
        str: openpecha work id
    """
    op_work_id = ""
    bdrc_work_id = get_bdrc_work_id(bdrc_instance_id)
    op2bdrc_work_mapping = requests.get(config.OP2BDRC_WORK_MAPPING_URL).content
    if bdrc_work_id:
        op_work_id = get_op_work_from_bdrc_work_id(bdrc_work_id, op2bdrc_work_mapping)
    return op_work_id
