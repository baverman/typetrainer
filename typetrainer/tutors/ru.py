# -*- coding: utf-8 -*-
import re
from .common import Filler

from typetrainer.i18n import _

name = 'ru'
label = _('Russian')

levels = (
    ('basic', _('Basic')),
#    ('advanced', _('Advanced')),
#    ('superb', _('Superb')),
)

def make_lengths_seq(words):
    for t, w in words:
        if t == 'w':
            wlen = len(w)
            yield 'w', wlen
        else:
            yield t, w

def split_to_words(text):
    for word in re.findall(u'(?iu)[а-я]+', text.lower()):
        syms = []
        if word.endswith(','):
            syms.append(',')

        word = word.strip(',')
        if word:
            yield 'w', word
            if syms:
                for s in syms:
                    yield 's', s

            yield 's', ' '

def get_filler(text, level):
    words = list(split_to_words(text))
    if not words:
        words = list(split_to_words(u'Пустое упражнение. Выберите другое или загрузите '
            u'соответствующий файл'))
    return Filler(words, make_lengths_seq)