from pathlib import Path
from uuid import uuid4

from openpecha import config
from openpecha.utils import dump_yaml, load_yaml
from openpecha.core.ids import get_alignment_id, get_base_id


class TMXAlignment:
    
    def get_all_ids(self, annotations):
        curr_segment = {}
        final_segments = {}
        num = 1
        for uid, _ in annotations.items():
            curr_segment[num] = {"segment_id": uid}
            final_segments.update(curr_segment)
            curr_segment = {}
            num += 1
        return final_segments, num

    def get_segment_of_source(self, source_pecha):

        for _id, source_segment_yml in source_pecha.layers.items():
            source_base_id = _id
            for _, _value in source_segment_yml.items():
                source_annotations = _value.annotations
                
        source_segment_ids, nums = self.get_all_ids(source_annotations)
        segment = {}
        curr_seg = {}
        for num in range(1, nums):
            curr_seg[uuid4().hex] = {
                f"{source_pecha.pecha_id}": source_segment_ids[num]["segment_id"]
            }
            segment.update(curr_seg)
            curr_seg = {}
        return segment, source_base_id

    def get_segment_pairs(self, source_pecha, target_pecha):
        """_summary_

        Args:
            source_pecha (object): _description_
            target_pecha (object): _description_

        Returns:
            _type_: _description_
        """
        for _id, source_segment_yml in source_pecha.layers.items():
            source_base_id = _id
            for _, _value in source_segment_yml.items():
                source_annotations = _value.annotations
        for id_, target_segment_yml in target_pecha.layers.items():
            target_base_id = id_
            for _, value_ in target_segment_yml.items():
                target_annotations = value_.annotations

        source_segment_ids, s_nums = self.get_all_ids(source_annotations)
        target_segment_ids, t_nums = self.get_all_ids(target_annotations)

        curr_pair = {}
        segment_pairs = {}
        if s_nums == t_nums:
            for num in range(1, s_nums):
                curr_pair[uuid4().hex] = {
                    f"{source_pecha.pecha_id}": source_segment_ids[num]["segment_id"],
                    f"{target_pecha.pecha_id}": target_segment_ids[num]["segment_id"],
                }
                segment_pairs.update(curr_pair)
                curr_pair = {}
        return segment_pairs, source_base_id, target_base_id

    def update_alignment_repo(self, alignment_path, target_pecha_path, annotation_map):
        curr_pair = {}
        new_segment_pairs = {}
        target_segment = {}
        segment_source = {}
        target_pecha_id = target_pecha_path.stem
        alignment_id = alignment_path.stem
        target_meta_yml = load_yaml(
            target_pecha_path / f"{target_pecha_id}.opf" / "meta.yml"
        )
        alignment_yml = load_yaml(
            alignment_path / f"{alignment_id}.opa" / "Alignment.yml"
        )
        segment_source = alignment_yml["segment_sources"]
        for uid, info in segment_source.items():
            if info["relation"] == "source":
                source_pecha_id = uid
        for id, _ in target_meta_yml['bases'].items(): base_id = id
        target_segment[target_pecha_id] = {
            "type": target_meta_yml.get("origin_type", None),
            "relation": "target",
            "lang": target_meta_yml.get("default_lanuguage", None),
            "base": base_id
        }
        segment_source.update(target_segment)
        segment_pairs = alignment_yml["segment_pairs"]
        if annotation_map:
            for alignment_id, annotation_id in annotation_map.items():
                segment_pair = segment_pairs[alignment_id]
                curr_pair[alignment_id] = {
                    f"{source_pecha_id}": segment_pair[source_pecha_id],
                    f"{target_pecha_id}": annotation_id["annotation_id"],
                }
                new_segment_pairs.update(curr_pair)
                curr_pair = {}
        alignment_yml["segment_sources"] = segment_source
        alignment_yml["segment_pairs"] = new_segment_pairs
        self.write_alignment(alignment_path, alignment_yml)

    def create_readme_for_opa(self, alignment_id, meta_yml):
        source_metadata = meta_yml["source_metadata"]
        type = meta_yml["type"]
        alignment = f"|Alignment id | {alignment_id}"
        Table = "| --- | --- "
        Title = f"|Title | {meta_yml['title']} "
        type = f"|Type | {type}"
        if source_metadata:
            srclang = f"|Source Language | {meta_yml['source_metadata']['srclang']}"
            tarlang = f"|Target Language | {meta_yml['source_metadata']['adminlang']}"
        else:
            srclang = None
            tarlang = None
        readme = f"{alignment}\n{Table}\n{Title}\n{type}\n{srclang}\n{tarlang}"
        return readme

    def _mkdir(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def get_alignment_to_base(self, alignment, base_id):
        curr = {}
        final = {}
        for id, info in alignment['segment_sources'].items():
            key = str(id+"/"+info['base'])
            curr[key]= base_id
            final.update(curr)
            curr = {}
        return final

    def write_alignment(self, alignment_path, alignment_yml, meta_yml={}):
        alignment_opa_path = alignment_path / f"{alignment_path.stem}.opa"
        self._mkdir(alignment_opa_path)
        base_id = get_base_id()
        alignment_yml_path = alignment_opa_path / f"{base_id}.yml"
        alignment_to_base = self.get_alignment_to_base(alignment_yml, base_id)
        meta_yml['alignment_to_base'] = alignment_to_base
        meta_path = alignment_opa_path / "meta.yml"
        dump_yaml(alignment_yml, alignment_yml_path)
        if meta_yml:
            dump_yaml(meta_yml, meta_path)


    def create_alignment_meta(self, alignment_id, title, source_metadata, origin_type, pechas):
        """creates the meta of the alignment and return the meta dict

        Args:
            alignment_id (str): name of the alignment repo
            title (str): title of the TMX
            source_metadata (dict): it contains the source_metadata from TMX and the title
            origin_type (str): type of alignment
            pechas (list): list of the pecha_ids that are used in the alignment.

        Returns:
            dict: metadata of the alignment repo
        """
        metadata = {
            "id": alignment_id,
            "title": title,
            "type": origin_type,
            "pechas": pechas,
            "source_metadata": source_metadata,
        }
        return metadata


    def create_alignment_yml(
        self, source_pecha, target_pecha, src_lang, tar_lang, origin_type
    ):
        """Create the alignment between source pecha and target pecha if present,
        else create the alginment of source pecha only and return the alignment dict

        Args:
            source_pecha (_type_): _description_
            target_pecha (_type_): _description_
            src_lang (str): source language
            tar_lang (str): target language
            origin_type (str): type of 

        Returns:
            alignment: dict of alignment created
        """
        if target_pecha:
            segment_pairs, source_base_id, target_base_id = self.get_segment_pairs(source_pecha, target_pecha)
            
            alignment = {
                "segment_sources": {
                    f"{source_pecha.pecha_id}": {
                        "type": origin_type,
                        "relation": "source",
                        "lang": src_lang,
                        "base": source_base_id
                    },
                    f"{target_pecha.pecha_id}": {
                        "type": origin_type,
                        "relation": "target",
                        "lang": tar_lang,
                        "base": target_base_id
                    },
                },
                "segment_pairs": segment_pairs,
            }
        else:
            segment, source_base_id = self.get_segment_of_source(source_pecha)
            alignment = {
                "segment_sources": {
                    f"{source_pecha.pecha_id}": {
                        "type": origin_type,
                        "relation": "source",
                        "lang": src_lang,
                        "base": source_base_id
                    }
                },
                "segment_pairs": segment,
            }
        return alignment

    def create_alignment_repo(
        self,
        source_pecha,
        target_pecha=None,
        title=None,
        source_metadata=None,
        origin_type="translation",
    ):
        """Creates the alignment repo using source_pecha and target_pecha and returns its path

        Args:
            source_pecha (obj): OpenpechaGitRepo object of source opf
            target_pecha (obj, optional): OpenpechaGitRepo object of source opf
            title (str, optional): title of the TMX. Defaults to None.
            source_metadata (_type_, optional): source_metadata of the source TMX. Defaults to None.
            origin_type (str, optional): type of alignment. Defaults to "translation".

        Returns:
            object: path of alignment repo
        """
        if source_metadata:
            src_lang = source_metadata.get("srclang", "")
            tar_lang = source_metadata.get("adminlang", "")
        else:
            src_lang = None
            tar_lang = None

        alignment_id = get_alignment_id()
        
        alignment_yml = self.create_alignment_yml(
            source_pecha, target_pecha, src_lang, tar_lang, origin_type
        )

        alignment_path = config.PECHAS_PATH / alignment_id / f"{alignment_id}.opa"

        if target_pecha:
            pechas = [f"{source_pecha.pecha_id}",f"{target_pecha.pecha_id}"]
        else:
            pechas = [f"{source_pecha.pecha_id}"]
        
        
        meta_yml = self.create_alignment_meta(
            alignment_id, title, source_metadata, origin_type, pechas
        )

        self.write_alignment(alignment_path.parent, alignment_yml, meta_yml)

        readme = self.create_readme_for_opa(alignment_id, meta_yml)
        (alignment_path.parent / "readme.md").write_text(readme, encoding="utf-8")
        return alignment_path.parent
