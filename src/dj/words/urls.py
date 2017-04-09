# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<from_iso>\w+)/(?P<text>\w+)/$', views.word, name='words'),
    url(r'^(?P<from_iso>\w+)/(?P<text>\w+)/(?P<to_iso>\w+)/$', views.word, name='word'),

    # TODO: create transliteration end point which takes a word and
    # returns it's transliteration details.
]
