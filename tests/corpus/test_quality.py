from openpecha.corpus.quality import NonWordsCounter


def test_non_words_counter():
    text = "བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་ཇུག་པའི་རྣམ་པར་བཤད་པ།"

    non_word_count = NonWordsCounter(text)
    non_word_count_dict = non_word_count.dict()

    assert non_word_count_dict["total_tokens"]
    assert non_word_count_dict["total_non_words"]
    assert non_word_count_dict["non_words_ratio"]


def test_add_multiple_non_words_count():
    text = "བྱང་ཆུབ་སེམས་དཔའི་སྤྱོད་པ་ལ་ཇུག་པའི་རྣམ་པར་བཤད་པ།"
    count_a = NonWordsCounter(text)
    count_b = NonWordsCounter(text)

    count_c = count_a + count_b

    assert count_c.total_tokens == count_a.total_tokens + count_b.total_tokens
    assert count_c.total_non_words == count_a.total_non_words + count_b.total_non_words
