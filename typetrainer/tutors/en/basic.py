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
    for word in re.findall('(?i)[a-z\',]+', text.lower()):
        syms = []
        if word.endswith(','):
            syms.append(',')

        word = word.replace(',', '').strip("'")
        if word:
            yield 'w', word
            if syms:
                for s in syms:
                    yield 's', s

            yield 's', ' '

def get_filler(text, options):
    words = list(split_to_words(text))
    if not words:
        words = list(split_to_words(u'Tutor is empty. Select another or choose appropriate file.'))
    return Filler(words, make_lengths_seq)