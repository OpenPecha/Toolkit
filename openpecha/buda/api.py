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
BDR_uri = "http://purl.bdrc.io/resource/"
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
        o = g.value(predicate=BDO.outlineOf, object=wres)
        if o:
            res["source_metadata"]["outline"] = str(o)
        mwres = g.value(wres, BDO.instanceReproductionOf)
        res["source_metadata"]["reproduction_of"] = str(mwres)
        for _, _, cs in g.triples((mwres, BDO.copyrightStatus, None)):
            res["source_metadata"]["copyright_status"] = str(cs)
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
            iginfo["volume_pages_bdrc_intro"] = int(g.value(ig, BDO.volumePagesTbrcIntro, default=Literal(0)))
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

class OutlinePageLookup:
    """
    Defines an efficient lookup structure that get built with the outline content location information
    and then returns a list of texts (mw) present on an image (defined by volume number + image number)
    """

    def __init__(self, outline_graph, w_lname, w_info):
        # Initialize a dictionary to store content locations
        self.lookup = {}
        # Additional structure to keep track of open-ended ranges
        self.open_ranges = {}
        self.vnum_to_mws = {}
        self.outline_graph = outline_graph
        self.w_lname = w_lname
        self.w_info = w_info # same format as returned by get_buda_scan_info()
        self.volnum_to_volmw = {} # volume number to mw
        self.process()

    def get_nb_img_intro(self, vnum):
        if self.w_info is None:
            return 0
        for _, ig_info in self.w_info["image_groups"].items():
            if ig_info["volume_number"] == vnum:
                return ig_info["volume_pages_bdrc_intro"]
        return 0

    def _children(self, node):
        """Discover children"""
        g = self.outline_graph
        uniq = set()

        # Primary: hasPart
        for _, _, child in g.triples((node, BDO.hasPart, None)):
            uniq.add(child)

        # Fallback/union: partOf
        for child, _, _ in g.triples((None, BDO.partOf, node)):
            uniq.add(child)

        # Freeze and memoize
        lst = list(uniq)
        return lst

    def process(self):
        """
        traverse the outline, pruning as soon as we have a contentLocation
        """
        g = self.outline_graph

        # Root = any object of BDO.inRootInstance
        try:
            root = next(g.objects(None, BDO.inRootInstance))
        except StopIteration:
            logging.error("could not find root instance in outline")
            return

        stack = [root]
        visited = set()

        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)

            partType = g.value(node, BDO.partType, None)

            # Record volume markers (don’t prune; keep traversing)
            if partType in (BDR.PartTypeVolume, BDR.PartTypeCodicologicalVolume):
                for _, _, cl in g.triples((node, BDO.contentLocation, None)):
                    if (cl, BDO.contentLocationInstance, BDR[self.w_lname]) in g:
                        vnum = g.value(cl, BDO.contentLocationVolume, None)
                        if vnum:
                            mw = str(node)[len(BDR_uri):]
                            self.volnum_to_volmw[int(vnum)] = mw
                # continue traversal below the volume
                stack.extend(self._children(node))
                continue

            # Prune on Text / Editorial / Chapter (chapter is promoted implicitly)
            if partType in (BDR.PartTypeText, BDR.PartTypeEditorial, BDR.PartTypeChapter):
                cl_for_this = None
                for _, _, cl in g.triples((node, BDO.contentLocation, None)):
                    if (cl, BDO.contentLocationInstance, BDR[self.w_lname]) in g:
                        cl_for_this = cl
                        break
                if cl_for_this is not None:
                    mw = str(node)[len(BDR_uri):]
                    vnum_start = g.value(cl_for_this, BDO.contentLocationVolume, None)
                    vnum_end   = g.value(cl_for_this, BDO.contentLocationEndVolume, None)
                    imgnum_end = g.value(cl_for_this, BDO.contentLocationEndPage, None)
                    imgnum_start = g.value(cl_for_this, BDO.contentLocationPage, None)
                    self.add_content_location(mw, vnum_start, vnum_end, imgnum_start, imgnum_end)
                else:
                    logging.warning("missing content location for text")
                continue  # PRUNE: don’t visit descendants

            # Structural-only node: just traverse its (lazily fetched) children
            stack.extend(self._children(node))

    def add_content_location(self, mw, vnum_start, vnum_end, imgnum_start, imgnum_end):
        """
        add content location information (start volume number, end volume number, start image number, end image number)
        We don't always know in advance the total number of images per volume, or the number of volumes
        imgnum_start can be None, in which case we consider it is 1 (there is no image number 0)
        imgnum_end can be None, in which case all the images after imgnum_start get associated with the mw
        there can be multiple mw associated with the same image
        """
        if vnum_start is None:
            vnum_start = 1
        if vnum_end is None:
            vnum_end = vnum_start

        if imgnum_start is None:
            imgnum_start = 1
        nb_intro_imgs = self.get_nb_img_intro(int(vnum_start))
        if int(imgnum_start) < nb_intro_imgs + 1:
            imgnum_start = nb_intro_imgs + 1

        for vnum in range(int(vnum_start), int(vnum_end) + 1):
            if vnum not in self.vnum_to_mws:
                self.vnum_to_mws[vnum] = set()
            self.vnum_to_mws[vnum].add(mw)
            vol_imgnum_end = int(imgnum_end) if vnum == int(vnum_end) and imgnum_end is not None else None
            vol_imgnum_start = int(imgnum_start) if vnum == int(vnum_start) else self.get_nb_img_intro(vnum) + 1
            if vnum not in self.lookup:
                self.lookup[vnum] = {}

            if vol_imgnum_end is None:
                if vnum not in self.open_ranges:
                    self.open_ranges[vnum] = []
                self.open_ranges[vnum].append((vol_imgnum_start, mw))
            else:
                for imgnum in range(vol_imgnum_start, vol_imgnum_end + 1):
                    if imgnum not in self.lookup[vnum]:
                        self.lookup[vnum][imgnum] = set()
                    self.lookup[vnum][imgnum].add(mw)

    def get_mw_list(self, volnum, imgnum=None):
        """
        returns a list of mws associated with a specific image
        """
        if imgnum is None:
            if volnum not in self.vnum_to_mws:
                return []
            else:
                return self.vnum_to_mws[volnum]

        mw_list = set()
        
        # Check specific image assignments
        if volnum in self.lookup and imgnum in self.lookup[volnum]:
            mw_list.update(self.lookup[volnum][imgnum])
        
        # Check open-ended ranges
        if volnum in self.open_ranges:
            for start_imgnum, mw in self.open_ranges[volnum]:
                if imgnum >= start_imgnum:
                    mw_list.add(mw)

        return mw_list

def image_group_to_folder_name(scan_id, image_group_id):
    image_group_folder_part = image_group_id
    pre, rest = image_group_id[0], image_group_id[1:]
    if pre == "I" and rest.isdigit() and len(rest) == 4:
        image_group_folder_part = rest
    return scan_id+"-"+image_group_folder_part