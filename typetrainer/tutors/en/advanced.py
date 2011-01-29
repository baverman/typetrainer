import re
from ..common import Filler

def make_lengths_seq(words):
    for t, w in words:
        if t == 'w':
            wlen = len(w)
            yield 'w', wlen if wlen <= 3 else wlen + 3
        else:
            yield t, w

def split_to_words(text):
    filter_non_word = re.compile('(?i)[^a-z\']+')
    for word in re.findall('(?i)[a-z\',.:;"]+', text):
        non_word_cars = ',.:;"'
        esym = None
        for c in non_word_cars:
            if word.endswith(c):
                esym = c
                break

        ssym = '"' if word.startswith('"') else None

        word = filter_non_word.sub('', word)
        if word:
            if ssym:
                yield 's', ssym
            yield 'w', word
            if esym:
                yield 's', esym

            yield 's', ' '

def get_filler(text, options):
    words = list(split_to_words(text))
    return Filler(words, make_lengths_seq)