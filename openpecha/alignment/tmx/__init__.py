from pathlib import Path
from uuid import uuid4

from openpecha import config
from openpecha.utils import dump_yaml, load_yaml


class TMXAlignment:
    def create_alignment_meta(self, alignment_id, title, source_metadata, origin_type):
        metadata = {
            "id": alignment_id,
            "title": title,
            "type": origin_type,
            "source_metadata": source_metadata,
        }
        return metadata

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

        source_segment_yml = load_yaml(
            Path(
                source_pecha_path
                / f"{source_pecha_path.stem}.opf"
                / "layers/0001/Segment.yml"
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

    def get_segment_pairs(self, source_pecha_path, target_pecha_path):

        source_segment_yml = load_yaml(
            Path(
                source_pecha_path
                / f"{source_pecha_path.stem}.opf"
                / "layers/0001/Segment.yml"
            )
        )
        target_segment_yml = load_yaml(
            Path(
                target_pecha_path
                / f"{target_pecha_path.stem}.opf"
                / "layers/0001/Segment.yml"
            )
        )

        source_segment_ids, s_nums = self.get_all_ids(source_segment_yml["annotations"])
        target_segment_ids, t_nums = self.get_all_ids(target_segment_yml["annotations"])

        curr_pair = {}
        segment_pairs = {}
        if s_nums == t_nums:
            for num in range(1, s_nums):
                curr_pair[uuid4().hex] = {
                    f"{source_pecha_path.stem}": source_segment_ids[num]["segment_id"],
                    f"{target_pecha_path.stem}": target_segment_ids[num]["segment_id"],
                }
                segment_pairs.update(curr_pair)
                curr_pair = {}
        return segment_pairs

    def create_alignment_yml(
        self, source_pecha_path, target_pecha_path, src_lang, tar_lang, origin_type
    ):
        alignment_id = uuid4().hex
        if target_pecha_path:
            segment_pairs = self.get_segment_pairs(source_pecha_path, target_pecha_path)
            alignment = {
                "segment_sources": {
                    f"{source_pecha_path.stem}": {
                        "type": origin_type,
                        "lang": src_lang,
                    },
                    f"{target_pecha_path}": {"type": origin_type, "lang": tar_lang},
                },
                "segment_pairs": segment_pairs,
            }
        else:
            segment = self.get_segment_of_source(source_pecha_path)
            alignment = {
                "segment_sources": {
                    f"{source_pecha_path.stem}": {"type": origin_type, "lang": src_lang}
                },
                "segment_pairs": segment,
            }
        return alignment_id, alignment

    def _mkdir(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)
        return path

    def create_readme_for_opa(self, alignment_id):
        meta_yml = load_yaml(
            (config.PECHAS_PATH / alignment_id / f"{alignment_id}.opa/meta.yml")
        )
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

    def update_alignment_repo(
        self, alignment_id, target_pecha_id, annotation_map, lan, type
    ):
        curr_pair = {}
        new_segment_pairs = {}
        target_segment = {}
        segment_source = {}
        alignment_yml = load_yaml(
            (config.PECHAS_PATH / alignment_id / f"{alignment_id}.opa/Alignment.yml")
        )
        meta_yml = load_yaml(
            (config.PECHAS_PATH / alignment_id / f"{alignment_id}.opa/meta.yml")
        )
        segment_source = alignment_yml["segment_sources"]
        for pecha_id in segment_source:
            source_pecha_id = pecha_id
        target_segment[target_pecha_id] = {"type": type, "lang": lan}
        segment_source.update(target_segment)
        segment_pairs = alignment_yml["segment_pairs"]
        if annotation_map:
            for alignment_id, annotation_id in annotation_map.items():
                segment_pair = segment_pairs[alignment_id]
                curr_pair[alignment_id] = {
                    f"{source_pecha_id}": segment_pair[source_pecha_id],
                    f"{target_pecha_id}": annotation_id,
                }
                new_segment_pairs.update(curr_pair)
                curr_pair = {}
        alignment_yml["segment_sources"] = segment_source
        alignment_yml["segment_pairs"] = new_segment_pairs
        meta_yml["segment_sources"] = segment_source
        self.write_alignment_repo(alignment_id, alignment_yml, meta_yml)

    def write_alignment_repo(self, alignment_id, alignment_yml, meta_yml):
        repo_path = config.PECHAS_PATH / alignment_id / f"{alignment_id}.opa"
        self._mkdir(repo_path)
        alignment_path = repo_path / "Alignment.yml"
        meta_path = repo_path / "meta.yml"
        dump_yaml(alignment_yml, alignment_path)
        dump_yaml(meta_yml, meta_path)
        return Path(repo_path.parent)

    def create_alignment_repo(
        self,
        source_pecha_path,
        target_pecha_path=None,
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
            source_pecha_path, target_pecha_path, src_lang, tar_lang, origin_type
        )
        meta_yml = self.create_alignment_meta(
            alignment_id, title, source_metadata, origin_type
        )
        alignment_path = self.write_alignment_repo(
            alignment_id, alignment_yml, meta_yml
        )
        readme = self.create_readme_for_opa(alignment_id)
        (alignment_path / "readme.md").write_text(readme, encoding="utf-8")
        return alignment_path
