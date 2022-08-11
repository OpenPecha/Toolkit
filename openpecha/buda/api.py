import rdflib
import requests
import pyewts
import csv

TEST_MODE = True
LDSPDIBASEURL = "https://ldspdi.bdrc.io/"
CONVERTER = pyewts.pyewts()

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

# TODO: get from s3

def get_imagelist_simple(image_group_lname):
    r = requests.get(f"http://iiifpres.bdrc.io/il/v:bdr:{vol_name}")
    img2seq = {}
    for i, img in enumerate(r.json(), start=1):
        name, ext = img["filename"].split(".")
        img2seq[name] = {"num": i, "ext": ext}
    return img2seq

def get_buda_scan_info(wlname):
    if TEST_MODE:
        return {
            "source_metadata": {
              "id": "http://purl.bdrc.io/resource/"+wlname,
              "reproduction_of": "http://purl.bdrc.io/resource/M"+wlname,
              "title": "ཨ་གྲགས་གཟི་རྫོང་།",
              "author": "",
              "access": "http://purl.bdrc.io/admindata/AccessOpen",
              "restrictedInChina": True,
              "copyrightStatus": "http://purl.bdrc.io/resource/CopyrightUndetermined",
              "status": "http://purl.bdrc.io/admindata/StatusReleased"
            },
            "image_groups": {
              "I"+wlname[1:]: {
                "volume_number": 1,
                "total_pages": 72,
                "title": "volume 1",
                "id": "http://purl.bdrc.io/resource/I"+wlname[1:]
              }
            }
        }

    headers = {"Accept": "text/turtle"}
    params = {"R_RES": "bdr:"+wlname}
    res = {
        "source_metadata": {
            "id": "http://purl.bdrc.io/resource/"+wlname
        },
        "image_groups": {}
    }
    g = Graph()
    try:
        req = requests.get(
            ldspdibaseurl + "/query/graph/OP_info",
            headers=headers,
            params=params,
        )
        g.parse(data=req.text, format="ttl")
        wres = BDR[wlname]
        adm = g.value(predicate=ADM.adminAbout, object=wres)
        res["source_metadata"]["status"] = str(g.value(adm, ADM.status))
        res["source_metadata"]["access"] = str(g.value(adm, ADM.access))
        if (adm, ADM.restrictedInChina, Literal(True)) in g:
            res["source_metadata"]["restrictedInChina"] = True
        mwres = g.value(wres, BDO.instanceReproductionOf)
        res["source_metadata"]["reproduction_of"] = str(mwres)
        for _, _, cs in g.triples((mwres, BDO.copyright, None)):
            res["source_metadata"]["copyrightStatus"] = str(cs)
        if "copyrightStatus" not in res["source_metadata"]:
            res["source_metadata"]["copyrightStatus"] = "http://purl.bdrc.io/resource/CopyrightPublicDomain"
        res["source_metadata"]["reproduction_of"] = str(mwres)
        for _, _, l in g.triples((mwres, SKOS.prefLabel, None)):
            if l.language == "bo-x-ewts":
                res["source_metadata"]["title"] = CONVERTER.toUnicode(l.value)
            else:
                res["source_metadata"]["title"] = l.value
        for _, _, wa in g.triples((mwres, BDO.instanceOf, None)):
            for _, _, aac in g.triples((wa, BDO.creator, None)):
                if (aac, BDO.role, BDR.R0ER0009) or (aac, BDO.role, BDR.R0ER0009) in g:
                    for _, _, p in g.triples((aac, BDO.agent, None)):
                        for _, _, l in g.triples((p, SKOS.prefLabel, None)):
                            if l.language == "bo-x-ewts":
                                res["source_metadata"]["author"] = CONVERTER.toUnicode(l.value)
                            else:
                                res["source_metadata"]["author"] = l.value
        for _, _, ig in g.triples((wres, BDO.instanceOf, None)):
            iglname = str(ig)[str(ig).rfind('/'):]
            res["image_groups"][iglname] = {}
            iginfo = res["image_groups"][iglname]
            iginfo["id"] = str(ig)
            iginfo["total_pages"] = int(g.value(ig, BDO.volumePagesTotal))
            iginfo["volume_number"] = int(g.value(ig, BDO.volumeNumber))
            iginfo["volume_pages_bdrc_intro"] = int(g.value(ig, BDO.volumePagesTbrcIntro))
            for _, _, l in g.triples((ig, SKOS.prefLabel, None)):
                if l.language == "bo-x-ewts":
                    iginfo["title"] = CONVERTER.toUnicode(l.value)
                else:
                    iginfo["title"] = l.value
    finally:
        return res