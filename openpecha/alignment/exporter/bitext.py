from pathlib import Path

from openpecha.alignment.exporter import Exporter


class BitextExporter(Exporter):
    def serialize_segment_pair(self, pair_id, segment_pair, segment_texts):
        """Generate bitext segment using alignment information

        Args:
            pair_id (uuid): segment pair id
            segment_pair (dict): key as pecha id and value as segment id of the pecha
            segment_texts (dict): key as pecha id and value as another dict whose key as segment pair id and value as segment text

        Returns:
            str: bitext segment text where segments were separated by newline
        """
        segment_pair_text = ""
        for pair_c, (pecha_id, segment_id) in enumerate(segment_pair.items(), 1):
            segment_text = segment_texts[pecha_id][pair_id]
            segment_text = segment_text.replace("\n", "")
            if pair_c == 1:
                segment_pair_text += f"{segment_text}\n"
            else:
                segment_pair_text += f"\t{segment_text}\n"
        return segment_pair_text

    def export(self, output_file_path):
        """Export alignment to bitext

        Args:
            output_file_path (str): output file path
        """
        bi_text = ""
        segment_srcs = self.alignment.get("segment_sources", {})
        segment_texts = {}
        for seg_src_id, seg_src in segment_srcs.items():
            segment_texts[seg_src_id] = self.get_segment_texts(seg_src_id)
        segment_pairs = self.alignment.get("segment_pairs", {})
        for pair_id, segment_pair in segment_pairs.items():
            bi_text += self.serialize_segment_pair(pair_id, segment_pair, segment_texts)
        Path(output_file_path).write_text(bi_text, encoding="utf-8")
