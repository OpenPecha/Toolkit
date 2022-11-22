import rdflib
import requests
import pyewts
import csv
from rdflib import BNode, Literal, URIRef
from rdflib.namespace import OWL, RDF, RDFS, SKOS, XSD, Namespace, NamespaceManager
import boto3
import botocore
import gzip
import hashlib
import io
import json
import logging

LDSPDIBASEURL = "https://ldspdi.bdrc.io/"
CONVERTER = pyewts.pyewts()

SESSION = boto3.Session()
S3 = SESSION.client('s3')

BDR = Namespace("http://purl.bdrc.io/resource/")
BDO = Namespace("http://purl.bdrc.io/ontology/core/")
BDA = Namespace("http://purl.bdrc.io/admindata/")
ADM = Namespace("http://purl.bdrc.io/ontology/admin/")

def fetch_op_commits(ldspdibaseurl="http://ldspdi.bdrc.io/"):
    """
    Fetches the list of all openpecha commits on BUDA
    """
    res = {}
    headers = {"Accept": "text/csv"}
    params = {"format": "csv"}
    with closing(
        requests.get(
            ldspdibaseurl + "/query/table/OP_allCommits",
            stream=True,
            headers=headers,
            params=params,
        )
    ) as r:
        reader = csv.reader(codecs.iterdecode(r.iter_lines(), "utf-8"))
        for row in reader:
            if not row[0].startswith("http://purl.bdrc.io/resource/IE0OP"):
                logging.error("cannot interpret csv line starting with " + row[0])
                continue
            res[row[0][34:]] = row[1]
    return res


def get_s3_folder_prefix(wlname, image_group_lname):
    """
    gives the s3 prefix (~folder) in which the volume will be present.
    inpire from https://github.com/buda-base/buda-iiif-presentation/blob/master/src/main/java/
    io/bdrc/iiif/presentation/ImageInfoListService.java#L73
    Example:
       - wlname=W22084, image_group_lname=I0886
       - result = "Works/60/W22084/images/W22084-0886/
    where:
       - 60 is the first two characters of the md5 of the string W22084
       - 0886 is:
          * the image group ID without the initial "I" if the image group ID is in the form I\\d\\d\\d\\d
          * or else the full image group ID (incuding the "I")
    """
    md5 = hashlib.md5(str.encode(wlname))
    two = md5.hexdigest()[:2]

    pre, rest = image_group_lname[0], image_group_lname[1:]
    if pre == 'I' and rest.isdigit() and len(rest) == 4:
        suffix = rest
    else:
        suffix = image_group_lname

    return 'Works/{two}/{RID}/images/{RID}-{suffix}/'.format(two=two, RID=wlname, suffix=suffix)

def gets3blob(s3Key):
    f = io.BytesIO()
    try:
        S3.download_fileobj('archive.tbrc.org', s3Key, f)
        return f
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            return None
        else:
            raise

def get_image_list_s3(wlname, image_group_lname):
    s3key = get_s3_folder_prefix(wlname, image_group_lname)+"dimensions.json"
    blob = gets3blob(s3key)
    if blob is None:
        return None
    blob.seek(0)
    b = blob.read()
    ub = gzip.decompress(b)
    s = ub.decode('utf8')
    data = json.loads(s)
    return data

def get_image_list_iiifpres(wlname, image_group_lname):
    r = requests.get(f"http://iiifpres.bdrc.io/il/v:bdr:{vol_name}")
    return r.json()

def get_image_list(wlname, image_group_lname, source="s3", reorder_with_bvm=False):
    il = None
    if source == "s3":
        il = get_image_list_s3(wlname, image_group_lname)
    else:
        il = get_image_list_iiifpres(wlname, image_group_lname)
    return il

def _res_from_model(g, wlname):
    res = {
        "source_metadata": {
            "id": "http://purl.bdrc.io/resource/"+wlname
        },
        "image_groups": {}
    }
    wres = BDR[wlname]
    try:
        adm = g.value(predicate=ADM.adminAbout, object=wres)
        res["source_metadata"]["status"] = str(g.value(adm, ADM.status))
        res["source_metadata"]["access"] = str(g.value(adm, ADM.access))
        if (adm, ADM.restrictedInChina, Literal(True)) in g:
            res["source_metadata"]["geo_restriction"] = ["CN"]
        mwres = g.value(wres, BDO.instanceReproductionOf)
        res["source_metadata"]["reproduction_of"] = str(mwres)
        for _, _, cs in g.triples((mwres, BDO.copyright, None)):
            res["source_metadata"]["copyright_status"] = str(cs)
        if "copyright_status" not in res["source_metadata"]:
            res["source_metadata"]["copyright_status"] = "http://purl.bdrc.io/resource/CopyrightPublicDomain"
        res["source_metadata"]["reproduction_of"] = str(mwres)
        for _, _, l in g.triples((mwres, SKOS.prefLabel, None)):
            if l.language == "bo-x-ewts":
                res["source_metadata"]["title"] = CONVERTER.toUnicode(l.value)
                break
            else:
                res["source_metadata"]["title"] = l.value
        res["source_metadata"]["languages"] = set()
        for _, _, wa in g.triples((mwres, BDO.instanceOf, None)):
            for _, _, l in g.triples((wa, BDO.language, None)):
                for _, _, lt in g.triples((l, BDO.langBCP47Lang, None)):
                    res["source_metadata"]["languages"].add(lt.value)
            for _, _, aac in g.triples((wa, BDO.creator, None)):
                if (aac, BDO.role, BDR.R0ER0009) or (aac, BDO.role, BDR.R0ER0009) in g:
                    for _, _, p in g.triples((aac, BDO.agent, None)):
                        for _, _, l in g.triples((p, SKOS.prefLabel, None)):
                            if l.language == "bo-x-ewts":
                                res["source_metadata"]["author"] = CONVERTER.toUnicode(l.value)
                                break
                            else:
                                res["source_metadata"]["author"] = l.value
        res["source_metadata"]["languages"] = list(res["source_metadata"]["languages"])
        for _, _, ig in g.triples((wres, BDO.instanceHasVolume, None)):
            if g.value(ig, BDO.volumeNumber) is None or g.value(ig, BDO.volumePagesTotal) is None:
                continue
            iglname = str(ig)[str(ig).rfind('/')+1:]
            res["image_groups"][iglname] = {}
            iginfo = res["image_groups"][iglname]
            iginfo["id"] = str(ig)
            iginfo["total_pages"] = int(g.value(ig, BDO.volumePagesTotal))
            iginfo["volume_number"] = int(g.value(ig, BDO.volumeNumber))
            iginfo["volume_pages_bdrc_intro"] = int(g.value(ig, BDO.volumePagesTbrcIntro))
            for _, _, l in g.triples((ig, SKOS.prefLabel, None)):
                if l.language == "bo-x-ewts":
                    iginfo["title"] = CONVERTER.toUnicode(l.value)
                    break
                else:
                    iginfo["title"] = l.value
    finally:
        return res

def get_buda_scan_info(wlname):
    headers = {"Accept": "text/turtle"}
    params = {"R_RES": "bdr:"+wlname}
    res = None
    g = rdflib.Graph()
    try:
        req = requests.get(
            LDSPDIBASEURL + "query/graph/OP_info",
            headers=headers,
            params=params,
        )
        g.parse(data=req.text, format="ttl")
        res = _res_from_model(g, wlname)
    except Exception as e:
        logging.error("get_buda_scan_info failed for "+wlname+": "+str(e))
    finally:
        return res

def image_group_to_folder_name(scan_id, image_group_id):
    image_group_folder_part = image_group_id
    pre, rest = image_group_id[0], image_group_id[1:]
    if pre == "I" and rest.isdigit() and len(rest) == 4:
        image_group_folder_part = rest
    return scan_id+"-"+image_group_folder_part