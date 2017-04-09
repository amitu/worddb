# -*- coding: utf-8 -*-
"""`words` constants."""

from django.utils.text import ugettext_lazy as _

ENGLISH_US = "en_US"
ENGLISH_GB = "en_GB"
HINDI = "hi"

# TODO: load this from babel library
LANGUAGES_LIST = [ENGLISH_US, ENGLISH_GB, HINDI]
LANGUAGES = {
    ENGLISH_US: _("English (United States)"),
    ENGLISH_GB: _("English (United Kingdom)"),
    HINDI: _("Hindi"),
}

SYSTEMS = [
    ("ipa", _("IPA")),
] + [
    ("native_" + x[0], _("Native " + str(x[1]))) for x in LANGUAGES
]

LANGUAGE_ROOT = {
    "en": "en_US",
    "en_GB": "en_US",
}

ACCENTS = {
    "en_US": [
        ("southern", _("Southern US")),
        ("british", _("British")),
    ],
}

RELATIONS = [
    ("nationality", _("Nationality Relationship")),
]

# TODO:
#     1. populate all constants
#         - generate languages.po file, containing
#           (i). LANGUAGES (614)
#           (ii). Native Systems (614)
#           (iii). Language root maps
#           (iv). accents
#     2. populate sample data of cmudict's first 30 words with the
#        following pronunciations
#         {
#             "ipa": {
#                 "southern": /ˈkwɛst͡ʃən/,
#                 "british": /ˈkwɛʃt͡ʃən/,
#                 "native": "/ˈkwɛʃt͡ʃən/"
#             },
#             "native_hi": {
#                 "native": /ˈkwɛst͡ʃən/,
#             },
#         }
#     3. create a sample UI to view the data
#     4. load all cmudict data

# TODO:. generate languages.po file, containing
#           (i). LANGUAGES (614)
#           (ii). Native Systems (614)
