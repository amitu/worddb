# -*- coding: utf-8 -*-

from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render

from words.constants import LANGUAGE_ROOT, LANGUAGES
from words.models import Word
from words.utils import split_word


def get_language(language):
    if language in LANGUAGES:
        return language
    elif language in LANGUAGE_ROOT:
        return LANGUAGE_ROOT[language]
    raise Http404


def word(request, from_iso, text, to_iso=None):
    # handle validations
    to_iso = to_iso or from_iso
    _from_iso = get_language(from_iso)
    _to_iso = get_language(to_iso)

    if from_iso != _from_iso or to_iso != _to_iso:
        return HttpResponseRedirect(
            '/{}/{}/{}/'.format(_from_iso, text, _to_iso)
        )

    text, dis = split_word(text)  # text_(disambiguation)
    try:
        word = Word.objects.get(
            language=from_iso, text__iexact=text, disambiguation=dis,
        )
    except Word.DoesNotExist:
        if _from_iso != from_iso:
            word = get_object_or_404(
                Word, language=LANGUAGE_ROOT[from_iso], text__iexact=text,
                disambiguation=dis,
            )
        else:
            raise Http404

    word_info = word.get_word_info()
    ctx = {
        'success': True,
        'word': word.json(),
        'native': word_info.json() if word_info else None,
        'other': None,

        'native_pronunciation': word.pronunciation.get(
            "native_{}".format(to_iso), {}
        ).get('native'),
        'foreign_pronunciation': word.pronunciation.get(
            'ipa', {}
        ).get('native'),

        'foreign_iso': from_iso,
        'native_iso': to_iso,

        'foreign_language': LANGUAGES[from_iso],
        'native_language': LANGUAGES[to_iso],
    }

    if to_iso != from_iso:
        word_info = word.get_word_info(to_iso)
        ctx['other'] = word_info.json() if word_info else None

    if request.is_ajax():
        return JsonResponse(ctx)

    if word.text != text or word.disambiguation != dis:
        return HttpResponseRedirect(word.url(from_iso, to_iso))

    return render(request, 'words/word.html', ctx)


def home(request):
    return render(request, 'words/home.html', {})
