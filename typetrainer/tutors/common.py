import random
import collections
import itertools

from typetrainer.generator import make_char_chain, generate_word

class Filler(object):
    def __init__(self, words, make_lengths_seq):
        self.dist = {}
        self.first, self.other, self.word_chars = make_char_chain(words, 3, self.dist)
        self.lengths = list(make_lengths_seq(words))
        self.old_generated = collections.deque([], 100)

        pos = random.randint(0, len(self.lengths) - 1)
        left = itertools.islice(self.lengths, pos, None)
        right = itertools.islice(self.lengths, 0, pos)
        self.liter = itertools.cycle(itertools.chain(left, right))

    def __iter__(self):
        skip_to_word = False
        while True:
            t, l = self.liter.next()

            if skip_to_word:
                while t != 'w':
                    t, l = self.liter.next()

                skip_to_word = False

            if t == 'w':
                word = None
                for _ in range(50):
                    try:
                        word = generate_word(self.first, self.other, l, 3)
                    except KeyError:
                        break

                    if word not in self.old_generated:
                        break

                if not word:
                    skip_to_word = True
                    continue

                self.old_generated.append(word)

                yield word
            else:
                yield l

    def change_distribution(self, seq, prob_factor, replace=False):
        if replace:
            self.dist.clear()

        self.dist[seq] = prob_factor
        self.reset_parts()

    def reset_distribution(self):
        self.dist.clear()
        self.reset_parts()

    def reset_parts(self):
        for p in self.other.values():
            p.reset()

        for p in self.first.values():
            p.reset()

    def strip_non_word_chars(self, string):
        result = ''
        for c in string:
            if c in self.word_chars:
                result += c

        return result