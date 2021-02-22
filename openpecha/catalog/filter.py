import logging
import random


def _sample_text_chunk(text):
    start_idx = random.randint(0, 100000)
    text_chunk = text[start_idx : start_idx + 1000]
    first_syl_idx = text_chunk.find("་")
    last_syl_idx = text_chunk.rfind("་")
    return text_chunk[first_syl_idx + 1 : last_syl_idx]


def is_text_good_quality(text, strategy=None, threshold=0.2):
    if not strategy:
        try:
            from bonltk.text_quality import non_words_ratio

            strategy = non_words_ratio
        except Exception:
            msg = (
                "bonltk not installed. Install it with `pip install bonltk` "
                "or from https://github.com/10zinten/bonltk"
            )
            raise ImportError(msg)
    text_chunk = _sample_text_chunk(text)
    ratio = strategy(text_chunk)
    text_quality = 1 - ratio
    logging.info(f"Text quality: {text_quality}")
    if text_quality <= threshold:
        return True
    else:
        return False
