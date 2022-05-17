from pathlib import Path

import requests
import yaml


def get_non_word_ratio(pecha_id):
    metadata_url = f"https://raw.githubusercontent.com/OpenPecha/{pecha_id}/master/{pecha_id}.opf/meta.yml?token=GHSAT0AAAAAABOO673A4KSRGDJKS3BS5YVCYT6GAOA"
    r = requests.get(metadata_url)
    metadata = yaml.load(r.text, Loader=yaml.CSafeLoader)
    try:
        return metadata["quality"]["non_words_ratio"]
    except KeyError:
        print("[ERROR] quality scrore missing:", pecha_id)
        return ""


def main():
    corpus_url = "https://raw.githubusercontent.com/OpenPecha/corpus_catalog/main/data/literary_bo.csv"
    output_fn = Path("literary_bo.csv")
    new_corpus_csv = ""
    for i, line in enumerate(requests.get(corpus_url).text.splitlines()):
        if i > 0:
            pecha_id = line.strip()
            print(pecha_id)
            line = [
                pecha_id,
                f"https://github.com/OpenPecha/{pecha_id}/archive/refs/heads/botok.zip",
                str(get_non_word_ratio(pecha_id)),
            ]
            line = ",".join(line)
        new_corpus_csv += line + "\n"
    output_fn.write_text(new_corpus_csv)


if __name__ == "__main__":
    main()
