from django.db import models


class Language(models.Model):
    iso = models.CharField(max_length=3)


class WordRelation(models.Model):
    name = models.CharField()  # plural, present-contineous, past, future, typo


class Accent(models.Model):
    name = models.CharField()  # American, British, Wales


class System(models.Model):
    name = models.CharField()  # IPA vs ARPA vs "Native"
    code = models.CharField()  # ipa vs native_hi
    language = models.ForeignKey(Language, null=True)


class Word(models.Model):
    language = models.ForeignKey(Language)
    text = models.CharField(
        max_length=200)  # /en/Love_(Feeling) vs /en/Love_(Score): wikipedia style
    pronunciation = pg.JSONField()
    {
        "ipa": {
            "American": "asdasdasd",
        }
    }
    # ipa = pg.JSONField(max_length=200) # American: /ˈkwɛst͡ʃən/ British: /ˈkwɛʃt͡ʃən/
    # arpa = pg.JSONField(max_length=200)
    # brahmic = pg.JSONField(max_length=200)
    # telugu = pg.JSONField(max_length=200)
    root = models.ForeignKey("Word", null=True,
                             blank=True)  # Loves etc are roots
    root_relation = models.ForeignKey(WordRelation)
    disambiguation = models.CharField(max_length=200, blank=True)
    pos = models.BitField(bits=VERB | NOUN | ADJECTIVE)
    # unique_together: (language, text, disambiguation)


# like, love
#
# loves, loved, loving
#
# NASA vs N.A.S.A vs
# Nasa / en / NASA_(Space_Organization) vs / en / Nasa_(City)


class WordInfo(models.Model):
    word = models.ForeignKey(Word)
    language = models.ForeignKey(Language)
    meanings = models.ManyToManyField(
        Word)  ## all meanings of english word love in hindi
    antonyms = models.ManyToManyField(
        Word)  ## all anotnyms of english word love in hindi
    synonyms = models.ManyToManyField(Word)
    text = models.TextField(blank=True)


# URL:
#
# // word URL: /en/love/
# // /en/love/hi/ (I know hindi, so prefer hindi meaning etc)
