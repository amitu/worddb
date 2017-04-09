# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.postgres.fields import JSONField

from prettyjson import PrettyJSONWidget

from words.models import Word, WordInfo, WordRelation


@admin.register(WordRelation)
class WordRelationAdmin(admin.ModelAdmin):
    pass


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget}
    }


@admin.register(WordInfo)
class WordInfoAdmin(admin.ModelAdmin):
    pass
