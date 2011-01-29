import random
import collections
import itertools

from typetrainer.generator import make_char_chain, generate_word

class Filler(object):
    def __init__(self, words, make_lengths_seq):
        self.dist = {}
        self.first, self.other = make_char_chain(words, 3, self.dist)
        self.lengths = list(make_lengths_seq(words))
        self.old_generated = collections.deque([], 100)

    def __iter__(self):
        pos = random.randint(0, len(self.lengths) - 1)
        left = itertools.islice(self.lengths, pos, None)
        right = itertools.islice(self.lengths, 0, pos)

        for t, l in itertools.cycle(itertools.chain(left, right)):
            if t == 'w':
                word = generate_word(self.first, self.other, l, 3)
                if word in self.old_generated:
                    word = generate_word(self.first, self.other, l, 3)
                self.old_generated.append(word)
                yield word
            else:
                yield l

    def change_distribution(self, seq, prob_factor):
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
