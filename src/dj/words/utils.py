# -*- coding: utf-8 -*-

import re

DISAMBIGUATION_REGEX = re.compile(".*?\((.*?)\)")


def normalize_text(text):
    return ''.join(filter(
        bool, re.findall('[a-zA-Z0-9\-\s\_\.]+', text)
    )).replace("_", " ").strip()


def split_word(text):

    if not text:
        return text, ''

    word, disambiguation = normalize_text(
        re.sub(r'\(.*?\)', '', text).strip()
    ), ''

    disambiguations = re.findall(DISAMBIGUATION_REGEX, text)
    if disambiguations:
        disambiguation = normalize_text(disambiguations[-1])
    return word, disambiguation


# for inp, text, dis in [
#     ("Word", "Word", ""),
#     ("Word Pattern", "Word Pattern", ""),
#     ("Word_Pattern", "Word Pattern", ""),
#     ("Word_Pattern_", "Word Pattern", ""),
#     ("Word_Pattern_(Hello)", "Word Pattern", "Hello"),
#     ("Word_Pattern_(Hello_World)", "Word Pattern", "Hello World"),
#     ("Word_Pattern_(Hello World)", "Word Pattern", "Hello World"),
#     ("Word_Pattern_(Hello-World)", "Word Pattern", "Hello-World"),
#     ("Word-Pattern_(Hello-World)", "Word-Pattern", "Hello-World"),
#     ("N.A.S.A._Pattern_(Hello-World)", "N.A.S.A. Pattern", "Hello-World"),
# ]:
#     assert split_word(inp) == (text, dis)
