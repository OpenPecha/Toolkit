import math
from pathlib import Path

import diff_match_patch as dmp_module
import yaml
from git.objects import base


class Blupdate:
    """
    This class represents an update in the base layer. It is used to recompute the existing layers into the new base layer.

    When you want to update the base layer to a new text, initialize the class with the content of the old base layer and the new one.
    Then for each annotation in the layers, you can call get_updated_coord() with the coordinate of the annotation, it will return the
    updated coordinate that you can use to update the annotation.
    """

    def __init__(self, srcbl, dstbl, context_len=16):
        self.srcbl = srcbl
        self.dstbl = dstbl
        self.dmp = dmp_module.diff_match_patch()
        self.cctv = self.compute_cctv()
        self.context_len = context_len

    def compute_cctv(self):
        """
        Computes a cctv from self.srcbl to self.dstbl. This will take some effort but should be reasonable with DMP.

        The cctv should the a list of triples, each triple being:
          - char start in srcbl (int)
          - char end in srcbl (int)
          - char coord diff to the corresponding range in dstbl (int)


        It indicates the areas where no change has occured between srcbl and dstbl and where a simple character
        coordinate translation is possible without looking at the context.

        Here's an example:

        srcbl = abefghijkl
        dstbl = abcdefgkl

        the result will be:
        [
            (0,2,0),
            (2,5,2),
            (8,10,-1)
        ]

        meaning in plain English:
            - from character 0 to 2 in srcbl (meaning "ab"), no character coordinate translation is needed for the equivalent area in dstbl
            - from character 2 to 5 in srcbl (meaning "efg"), character coordinates in srcbl need to be added +2 in order to get their equivalent in dstbl
            - from character 8 to 10 in srcbl (meaning "kl"), character coordinates in srcbl need to be added -1 in order to get their equivalent in dstbl

        """
        diffs = self.dmp.diff_main(self.srcbl, self.dstbl)

        cctv = []

        # src_chunk is the chunk from source text, represented by mode 0 and -1.
        src_chunk_first_idx = 0
        src_chunk_last_idx = 0

        # dst_chunk is the chunk from destination text, represented by mode 0 and 1.
        dst_chunk_first_idx = 0
        dst_chunk_last_idx = 0

        for mode, chunk in diffs:
            if (
                mode == 0
            ):  # says the chunk is common, update the src_chunk and dst_chunk first and last indices.
                src_chunk_first_idx = src_chunk_last_idx
                dst_chunk_first_idx = dst_chunk_last_idx
                src_chunk_last_idx += len(chunk)
                dst_chunk_last_idx += len(chunk)
            elif (
                mode == -1
            ):  # says the chunk is from source text, update src_chunk first and last indices.
                src_chunk_first_idx = src_chunk_last_idx
                src_chunk_last_idx += len(chunk)
            else:  # mode == 1, says the chunks is from destination text, update dst_chunk first and last indices.
                dst_chunk_first_idx = dst_chunk_last_idx
                dst_chunk_last_idx += len(chunk)

            # get char coordinatte (cc) of the common chunk based on source and destination text.
            if mode == 0:
                src_cc = (src_chunk_first_idx, src_chunk_last_idx)
                dst_cc = (dst_chunk_first_idx, dst_chunk_last_idx)

                # contruct CCTV
                cctv.append((*src_cc, dst_cc[0] - src_cc[0]))

        return cctv

    def get_cctv_for_coord(self, srcblcoord):
        """
        Returns the character coordinate in dstbl for a character coordinate in srcbl according to the cctv. It returns two arguments:
          - the character coordinate translation, or an estimate if undefined
          - a boolean: true if the character coordinate is certain, false if it's an estimate

        In the relevant case, the estimate is computed by taking the average of the cctv value for the range before and for the range after.
        For example in the same example if we want the estimate for srcblcoord = 6, we see that for character coords [2-5] we have 2 and for [8-10] we have -1,
        the estimate will be 2+(-1) / 2 = 0.5, for which we take an int value: 1.

        So for a more complete example we would have:
          get_cctv_for_coord(3) == (2, true)
          get_cctv_for_coord(7) == (1, false)
          get_cctv_for_coord(9) == (-1, true)
        """
        prev_cct = 0
        result = None
        for cct in self.cctv:
            if srcblcoord > cct[0] and srcblcoord < cct[1]:  # at inner of the range
                result = (cct[2], True)
            elif (
                srcblcoord == cct[0] or srcblcoord == cct[1] - 1
            ):  # at side of the range
                result = (cct[2], False)
            elif srcblcoord < cct[0]:  # falls between ccts (two range)
                result = (math.ceil((prev_cct + cct[2]) / 2), False)

            if result:
                return result

            prev_cct = cct[2]

        if not result:
            return (-1, False)

    def get_context(self, srcblcoord):
        """
        This returns the left and right context of a character coordinate in srcbl, in the form of a tuple with two strings.
        The length of the context is set by self.context_len.

        format: 0a1b2e3f4g5h6i7

        For instance for contex_len = 4
           get_context(3) == ("abe", "fghi")
        """

        # check for left context size less than context_len
        if srcblcoord >= self.context_len:
            left_context = self.srcbl[srcblcoord - self.context_len : srcblcoord]
        else:
            left_context = self.srcbl[:srcblcoord]

        right_context = self.srcbl[srcblcoord : srcblcoord + self.context_len]
        return left_context, right_context

    def dmp_find(self, context, dstcoordestimate):
        """
        This function uses the dmp lib wizardry to get the a coordinate in dstbl that is:
          - around dstcoordestimate
          - approximately surrounded by context

        This is conceptually simple but might require the most time as it might require understanding the dmp code to
        hook into private functions.
        """
        match = self.dmp.match_main(self.dstbl, context[1], dstcoordestimate)
        return match

    def get_updated_with_dmp(self, srcblcoord, cct):
        """
        This returns the coordinate in dstbl corresponding to srcblcoord using the dmp methods, and an indication from the cctv.

        By convention, the function returns -1 when it is unable to compute the new coordinate.
        """
        if cct == -1:
            return cct
        context = self.get_context(srcblcoord)
        dstcoordestimate = srcblcoord + cct
        return self.dmp_find(context, dstcoordestimate)

    def get_updated_coord(self, srcblcoord):
        """
        This is the main function used to update annotations. Annotations have references to character coordinates in a specific base layer. This function
        allows them to get the corresponding coordinate in the new base layer.

        By convention, the return value -1 means that the function is unable to compute the new coordinate.
        """
        cctvforcoord = self.get_cctv_for_coord(srcblcoord)
        if cctvforcoord[1]:
            return srcblcoord + cctvforcoord[0]
        else:
            return self.get_updated_with_dmp(srcblcoord, cctvforcoord[0])


class PechaBaseUpdate:
    def __init__(self, src_opf_path, dst_opf_path, context_len=10):
        self.src_opf_path = Path(src_opf_path)
        self.dst_opf_path = Path(dst_opf_path)
        self.context_len = context_len

    @property
    def index_path(self):
        return self.dst_opf_path / "index.yml"

    @property
    def layer_path(self):
        return self.dst_opf_path / "layers"

    def dump(self, data, output_fn):
        with output_fn.open("w") as fn:
            yaml.dump(
                data, fn, default_flow_style=False, sort_keys=False, allow_unicode=True
            )

    def load(self, fn):
        return yaml.safe_load(fn.open(encoding="utf-8"))

    @staticmethod
    def get_base(opf_path, vol_id):
        return (opf_path / "base" / f"{vol_id}.txt").read_text(encoding="utf-8")

    @staticmethod
    def update_span(ann, updater):
        start = updater.get_updated_coord(ann["span"]["start"])
        end = updater.get_updated_coord(ann["span"]["end"])
        if start == -1 and end == -1:
            ann["span"]["fail_update"] = "both"
        elif start == -1:
            ann["span"]["fail_update"] = "start"
            ann["span"]["end"] == end
        elif end == -1:
            ann["span"]["fail_update"] = "end"
            ann["span"]["start"] == start
        else:
            ann["span"]["start"] = start
            ann["span"]["end"] = end

    def update_layer(self, layer, updater):
        """
        Update individual layer
        """
        for ann in layer["annotations"]:
            self.update_span(ann, updater)

    def update_layers(self, vol_id, updater):
        """
        Update all the layer annotations
        """
        for layer_fn in (self.layer_path / vol_id).iterdir():
            layer = self.load(layer_fn)
            self.update_layer(layer, updater)
            self.dump(layer, layer_fn)

    def update_vol(self, vol_id):
        src_base = self.get_base(self.src_opf_path, vol_id)
        dst_base = self.get_base(self.dst_opf_path, vol_id)
        self.update_layers(
            vol_id, Blupdate(src_base, dst_base, context_len=self.context_len)
        )

    def update_text_span(self, span):
        for span_vol in span:
            vol_id = span_vol["vol"].split("/")[-1]
            src_base = self.get_base(self.src_opf_path, vol_id)
            dst_base = self.get_base(self.dst_opf_path, vol_id)
            updater = Blupdate(src_base, dst_base, context_len=self.context_len)
            self.update_span(span_vol, updater)

    def update_index_layer(self):
        layer = self.load(self.index_path)
        for ann in layer["annotations"]:
            # update text span
            self.update_text_span(ann["span"])

            # update sub-text span
            for sub_text in ann["parts"]:
                self.update_text_span(sub_text["span"])

        self.dump(layer, self.index_path)

    def update(self):
        for vol_fn in Path(self.dst_opf_path / "base").iterdir():
            self.update_vol(vol_fn.stem)
        self.update_index_layer()
