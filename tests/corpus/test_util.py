from openpecha.corpus.util import count_non_words


def test_count_non_words():
    text = "བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་ཇུག་པའི་རྣམ་པར་བཤད་པ།"

    non_word_count = count_non_words(text)

    assert type(non_word_count["tokens"]) is int
    assert type(non_word_count["non_words"]) is int
    assert type(non_word_count["non_words_ratio"]) is float
    assert non_word_count["non_words_ratio"] >= 0
