# OpenPecha Toolkit: Corpus Quality Utility Functions
#
# Copyright (C) 2019-2022 NLTK Project
# Author: Edward Loper <edloper@gmail.com>
# URL: <https://www.nltk.org/>
# For license information, see LICENSE.TXT

from typing import Dict

from botok import WordTokenizer
from botok.vars import WordMarkers


def count_non_words(text: str) -> Dict[str, float]:
    """Calulate Non-Word percent of `text` using botok."""
    wt = WordTokenizer()
    tokens = wt.tokenize(text)
    total_non_words = 0
    for token in tokens:
        if token.pos in [WordMarkers.NON_WORD.name, WordMarkers.NO_POS.name]:
            total_non_words += 1
    non_word_ratio = round(total_non_words / len(tokens), 2)
    return {
        "tokens": len(tokens),
        "non_words": total_non_words,
        "non_words_ratio": non_word_ratio,
    }
