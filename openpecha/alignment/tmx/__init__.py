from pathlib import Path
from uuid import uuid4

from openpecha import config
from openpecha.utils import dump_yaml, load_yaml
from openpecha.core.ids import get_alignment_id


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

    def get_segment_of_source(self, source_pecha_path):

        source_meta_yml = load_yaml(
            Path(
                source_pecha_path
                / f"{source_pecha_path.stem}.opf"
                / "meta.yml"
            )
        )
        source_base_id = source_meta_yml["bases"][0]
        
        source_segment_yml = load_yaml(
            Path(
                source_pecha_path
                / f"{source_pecha_path.stem}.opf"
                / f"layers/{source_base_id}/Segment.yml"
            )
        )
        source_segment_ids, nums = self.get_all_ids(source_segment_yml["annotations"])
        segment = {}
        curr_seg = {}
        for num in range(1, nums):
            curr_seg[uuid4().hex] = {
                f"{source_pecha_path.stem}": source_segment_ids[num]["segment_id"]
            }
            segment.update(curr_seg)
            curr_seg = {}
        return segment

    def get_segment_pairs(self, source_pecha, target_pecha):

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

    def update_alignment_repo(self, alignment_path, target_pecha, annotation_map):
        curr_pair = {}
        new_segment_pairs = {}
        target_segment = {}
        segment_source = {}
        target_pecha_id = target_pecha.pecha_id
        alignment_id = alignment_path.stem
        target_meta_yml = load_yaml(
            target_pecha.pecha_path / f"{target_pecha_id}.opf" / "meta.yml"
        )
        alignment_yml = load_yaml(
            alignment_path / f"{alignment_id}.opa" / "Alignment.yml"
        )
        segment_source = alignment_yml["segment_sources"]
        for uid, info in segment_source.items():
            if info["relation"] == "source":
                source_pecha_id = uid
        target_segment[target_pecha_id] = {
            "type": target_meta_yml.get("origin_type", None),
            "relation": "target",
            "lang": target_meta_yml.get("default_lanuguage", {}),
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
        self.write_alignment_repo(alignment_path, alignment_yml)

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

    def write_alignment_repo(self, alignment_path, alignment_yml, meta_yml=None):
        alignment_opa_path = alignment_path / f"{alignment_path.stem}.opa"
        self._mkdir(alignment_opa_path)
        alignment_yml_path = alignment_opa_path / "Alignment.yml"
        meta_path = alignment_opa_path / "meta.yml"
        dump_yaml(alignment_yml, alignment_yml_path)
        if meta_yml:
            dump_yaml(meta_yml, meta_path)

    def create_alignment_meta(self, alignment_id, title, source_metadata, origin_type, pechas):
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
        alignment_id = get_alignment_id()
        if target_pecha:
            segment_pairs, source_base_id, target_base_id = self.get_segment_pairs(source_pecha, target_pecha)
            
            alignment = {
                "segment_sources": {
                    f"{source_pecha.pecha_path.stem}": {
                        "type": origin_type,
                        "relation": "source",
                        "lang": src_lang,
                        "base": source_base_id
                    },
                    f"{target_pecha.pecha_path.stem}": {
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
                    f"{source_pecha.pecha_path.name}": {
                        "type": origin_type,
                        "relation": "source",
                        "lang": src_lang,
                        "base": source_base_id
                    }
                },
                "segment_pairs": segment,
            }
        return alignment_id, alignment

    def create_alignment_repo(
        self,
        source_pecha,
        target_pecha=None,
        title=None,
        source_metadata=None,
        origin_type="translation",
    ):
        if source_metadata:
            src_lang = source_metadata.get("srclang", "")
            tar_lang = source_metadata.get("adminlang", "")
        else:
            src_lang = None
            tar_lang = None

        alignment_id, alignment_yml = self.create_alignment_yml(
            source_pecha, target_pecha, src_lang, tar_lang, origin_type
        )

        alignment_path = config.PECHAS_PATH / alignment_id / f"{alignment_id}.opa"

        pechas = [f"{source_pecha.pecha_id}",f"{target_pecha.pecha_id}"]
        
        meta_yml = self.create_alignment_meta(
            alignment_id, title, source_metadata, origin_type, pechas
        )

        self.write_alignment_repo(alignment_path.parent, alignment_yml, meta_yml)

        readme = self.create_readme_for_opa(alignment_id, meta_yml)
        (alignment_path.parent / "readme.md").write_text(readme, encoding="utf-8")
        return alignment_path.parent
