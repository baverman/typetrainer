from random import random
from collections import defaultdict
from bisect import bisect

class Choicer(object):
    def __init__(self, dist):
        self.dist = dist
        self.points = []
        self.points_parts = []

        self.precalculate()

    def precalculate(self):
        self.points[:] = []
        self.points_parts[:] = []

        pp = 0.0
        for part, prob in self.dist.iteritems():
            if prob == 0.0: continue
            self.points_parts.append(part)
            newpp = pp + prob
            self.points.append(newpp)
            pp = newpp

        if self.points:
            del self.points[-1]

    def choice(self, rnd):
        if len(self.points_parts) == 1:
            return self.points_parts[0]

        return self.points_parts[bisect(self.points, rnd)]

    def adjust(self, part, prob):
        self.dist[part] = 0.0
        total = sum(self.dist.values())
        if total != 0:
            mul = (1.0 - prob) / total
            for k in self.dist:
                self.dist[k] *= mul

        self.dist[part] = prob
        self.precalculate()

    def adjust_many(self, parts, prob):
        for p in parts:
            self.dist[p] = 0.0

        total = sum(self.dist.values())
        if total != 0:
            mul = (1.0 - prob) / total
            for k in self.dist:
                self.dist[k] *= mul

        for p in parts:
            self.dist[p] = prob / len(parts)

        self.precalculate()

    def remove(self, part):
        self.adjust(part, 0)
        del self.dist[part]


class Parts(object):
    def __init__(self, dist):
        self.parts = defaultdict(int)
        self.total = 0.0
        self.choicer = None
        self.dist = dist

    def add(self, part):
        self.choicer = None
        self.parts[part] += 1
        self.total += 1.0

    def make_choicer(self):
        ch = Choicer(dict( (p, c / self.total) for p, c in self.parts.iteritems()))
        for k, prob in self.dist.iteritems():
            ch.adjust_many([p for p in self.parts if k in p], prob)

        return ch

    def choice(self, rnd):
        if not self.choicer:
            self.choicer = self.make_choicer()

        return self.choicer.choice(rnd)

    def reset(self):
        self.choicer = None

def make_char_chain(words, seq_len, dist):
    first, other = {'any':Parts(dist)}, {}
    word_chars = set()

    for t, w in words:
        if t != 'w': continue

        map(word_chars.add, w)

        wlen = len(w)
        if wlen <= seq_len:
            if not wlen in first:
                first[wlen] = Parts(dist)
            first[wlen].add(w)
        else:
            pc = w[:seq_len]
            first['any'].add(pc)
            pos = seq_len
            while True:
                next = w[pos:pos+seq_len]
                if not next:
                    break

                if not pc in other:
                    other[pc] = Parts(dist)

                other[pc].add(next)
                pc = next
                pos += seq_len

    return first, other, word_chars

def chain_traversor(choices, other, length):
    copied = False

    while True:
        try:
            head = choices.choice(random())
            tail = get_tail(head, other, length)
            return [head] + tail
        except KeyError:
            if not copied:
                choices = choices.make_choicer()
                copied = True

            choices.remove(head)
            if not choices.dist:
                raise KeyError()

def get_tail(head, other, length):
    hlen = len(head)
    if hlen == length:
        return []
    elif hlen > length:
        raise KeyError()

    choices = other[head]
    return chain_traversor(choices, other, length - hlen)

def generate_word(first, other, length, seq_length):
    if length <= seq_length:
        return first[length].choice(random())

    return ''.join(chain_traversor(first['any'], other, length))

def make_word_chain(words, dist):
    result = {}

    prev = words[0][1]
    for t, w in words[1:]:
        try:
            p = result[prev]
        except KeyError:
            p = result[prev] = Parts(dist)

        p.add(w)
        if t == 'w':
            prev = w

    return result