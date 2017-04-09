# -*- coding: utf-8 -*-
"""`words` models."""
from django.contrib.postgres import fields as postgres_fields
from django.db import models

from . import constants


class WordRelation(models.Model):
    # plural, present-continuous, past, future, typo,
    # nationality adjective (indian)
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Word(models.Model):
    language = models.CharField(max_length=7, choices=constants.LANGUAGES)

    #
    # Love_(Feeling) vs Love_(Score) - wikipedia style - text_(disambiguation)
    text = models.CharField(max_length=200)
    disambiguation = models.CharField(max_length=200, blank=True)

    # Loves etc are roots
    root = models.ForeignKey("Word", null=True, blank=True)
    root_relation = models.ForeignKey(WordRelation, null=True)

    # {
    #     "ipa": {
    #         "southern": /ˈkwɛst͡ʃən/,
    #         "british": /ˈkwɛʃt͡ʃən/,
    #         "native": "/ˈkwɛʃt͡ʃən/"
    #     },
    #     "native_hi": {
    #         "southern": /ˈkwɛst͡ʃən/,
    #         "british": /ˈkwɛʃt͡ʃən/,
    #     },
    # }
    pronunciation = postgres_fields.JSONField(default=dict)
    # American: /ˈkwɛst͡ʃən/ British: /ˈkwɛʃt͡ʃən/
    # ipa = pg.JSONField(max_length=200)
    # arpa = pg.JSONField(max_length=200)
    # brahmic = pg.JSONField(max_length=200)
    # telugu = pg.JSONField(max_length=200)

    class Meta:
        unique_together = ('language', 'text', 'disambiguation')

    def __str__(self):
        return "{} (language{}, root: {})".format(
            self.text, self.language, self.root.text if self.root else ''
        )

    @property
    def full(self):
        if self.disambiguation:
            return "{}_({})".format(self.text, self.disambiguation)
        else:
            return self.text

    @property
    def full2(self):
        return self.full.replace(" ", "_")

    def url(self, from_iso, to_iso):
        if from_iso == to_iso:
            return "/{}/{}/".format(from_iso, self.full2)
        else:
            return "/{}/{}/{}/".format(from_iso, self.full2, to_iso)

    def get_word_info(self, iso=''):
        if not iso:
            iso = self.language

        try:
            return WordInfo.objects.get(word=self, language=iso)
        except WordInfo.DoesNotExist:
            return None

    def json(self):
        return {
            'word': self.full,
            'language': self.language,
            'root': self.root.full if self.root else '',
            'root_relation': self.root_relation,
            'pronunciation': self.pronunciation,
        }

# like, love
#
# loves, loved, loving
#
# NASA vs N.A.S.A vs
# Nasa /en/NASA_(Space_Organization) vs / en / Nasa_(City)
#      /en/NASA_[Space_Organization]


class WordInfo(models.Model):
    word = models.ForeignKey(Word)
    language = models.CharField(max_length=7, choices=constants.LANGUAGES)
    # all meanings of english word love in hindi
    meanings = models.ManyToManyField(Word, related_name='meanings')
    # all antonyms of english word love in hindi
    antonyms = models.ManyToManyField(Word, related_name='antonyms')
    # all synonyms of english word love in hindi
    synonyms = models.ManyToManyField(Word, related_name='synonyms')
    text = models.TextField(blank=True)

    def __str__(self):
        return "{} (language: {}, info language: {})".format(
            self.word.text, self.word.language, self.language
        )

    def json(self):
        return {
            'word': self.word.full,
            'word_language': self.word.language,
            'language': self.language,
            'meanings': [word.full for word in self.meanings],
            'antonyms': [word.full for word in self.antonyms],
            'synonyms': [word.full for word in self.synonyms],
            'text': self.text,
        }

# URL:
#
# // word URL: /en/love/
# // /en/love/hi/ (I know hindi, so prefer hindi meaning etc)
