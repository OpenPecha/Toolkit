from botok.tokenizers.sentencetokenizer import sentence_tokenizer
from botok.tokenizers.wordtokenizer import WordTokenizer


def serialize_sentence(sentence):
    new_line = ""
    for token in sentence:
        new_line += f"{token.text}"
    new_line = new_line.strip()
    return new_line


def get_sentence_segments(text):
    wt = WordTokenizer()
    tokens = wt.tokenize(text, split_affixes=True)
    sentences = sentence_tokenizer(tokens)
    new_bo_txt = ""
    for sentence in sentences:
        new_bo_txt += serialize_sentence(sentence["tokens"]) + "\n"
    return new_bo_txt
