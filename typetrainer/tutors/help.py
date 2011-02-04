# -*- coding: utf-8 -*-
import random
import re

from typetrainer.generator import make_word_chain
from typetrainer.i18n import _

help_text = _(u'Press right mouse button. Click right mouse button to select other tutors. '
    u'Choose a file with words. Click right mouse button at any window spot.')

def split_to_words(text):
    filter_non_word = re.compile(u'(?ui)[^a-zа-я\']+')
    for word in re.findall(u'(?iu)[a-zа-я\',."]+', text):
        non_word_cars = ',.'
        esym = None
        for c in non_word_cars:
            if word.endswith(c):
                esym = c
                break

        word = filter_non_word.sub('', word)
        if word:
            yield 'w', word
            if esym:
                yield 's', esym

class Filler(object):
    def __init__(self, words):
        self.dist = {}
        self.chain = make_word_chain(words, self.dist)
        self.name = 'help'
        self.filename = None

    def get_next_word(self, prev=None):
        try:
            return self.chain[prev].choice(random.random())
        except KeyError:
            return random.choice(self.chain.keys())

    def __iter__(self):
        prev = None
        prev_is_word = False
        while True:
            word = self.get_next_word(prev)

            if word not in ',.':
                prev = word
                prev_is_word = True
            else:
                if not prev_is_word:
                    prev = None
                    continue

                prev_is_word = False

            if prev_is_word:
                yield u' '

            yield word

    def change_distribution(self, seq, prob_factor, replace=False):
        if replace:
            self.dist.clear()

        self.dist[seq] = prob_factor
        self.reset_parts()

    def reset_distribution(self):
        self.dist.clear()
        self.reset_parts()

    def reset_parts(self):
        for p in self.chain.values():
            p.reset()

    filter_non_word = re.compile(u'(?ui)[^a-z\'а-я]+')
    def strip_non_word_chars(self, string):
        return Filler.filter_non_word.sub('', string)

    def get_available_parts_for(self, key):
        return 1.0


def get_filler():
    words = list(split_to_words(help_text))
    return Filler(words)