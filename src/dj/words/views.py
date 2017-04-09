# -*- coding: utf-8 -*-
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render

from words.constants import LANGUAGE_ROOT, LANGUAGES
from words.models import Word
from words.utils import split_word


def word(request, from_iso, text, to_iso=None):
    # handle validations
    to_iso = to_iso or from_iso
    if from_iso not in LANGUAGES or to_iso not in LANGUAGES:
        raise Http404

    text, dis = split_word(text)  # text_(disambiguation)

    try:
        word = Word.objects.get(
            language=from_iso, text=text, disambiguation=dis,
        )
    except Word.DoesNotExist:
        if LANGUAGE_ROOT.get(from_iso) != from_iso:
            word = get_object_or_404(
                Word, language=LANGUAGE_ROOT[from_iso], text=text,
                disambiguation=dis,
            )
        else:
            raise Http404

    word_info = word.get_word_info()
    ctx = {
        'success': True,
        'word': word.json(),
        'native': word_info.json() if word_info else None,
        'other': None
    }

    if to_iso != from_iso:
        word_info = word.get_word_info(to_iso)
        ctx['other'] = word_info.json() if word_info else None

    if request.is_ajax():
        return JsonResponse(ctx)

    if word.text != text or word.disambiguation != dis:
        return HttpResponseRedirect(word.url(from_iso, to_iso))

    return render(request, 'word.html', ctx)
