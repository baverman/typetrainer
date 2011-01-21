from typetrainer.generator import make_char_chain, generate_word, Parts
from typetrainer.tutors.en.basic import make_lengths_seq, split_to_words

def test_distribution_must_return_word_nplets():
    first, other = make_char_chain(['a', 'word', 'wo', 'luke'], 1)
    assert (other, first) == ({2: {'w': ['o']}, 4:{
        'k': ['e'], 'l': ['u'], 'o': ['r'], 'r': ['d'], 'u': ['k'], 'w': ['o']}},
        {1: ['a'], 2: ['w'], 4: ['w', 'l']})

    first, other = make_char_chain(['a', 'word', 'wo', 'luke'], 2)
    assert (other, first) == ({4: {'wo': ['rd'], 'lu': ['ke']}},
        {1: ['a'], 2: ['wo'], 4: ['wo', 'lu']})

def test_breaker():
    result = split_to_words('Seq of words')
    assert result == ['Seq', 'of', 'words']

def test_generate_huge():
    words = split_to_words(open('/usr/share/fortune/cookie').read())

    first, other = make_char_chain(words, 3)
    lengths = make_lengths_seq(words)

    for l in lengths[:1000]:
        print generate_word(first, other, l, 3),

    print

    assert False

def test_parts_must_return_proper_distribution():
    p = Parts()
    p.add('aaa')
    p.add('aaa')
    p.add('aaa')

    p.add('bbb')
    p.add('bbb')

    p.add('ccc')

    result = {'aaa':0, 'bbb':0, 'ccc':0}
    i = 0
    while i < 1:
        result[p.choice(i)] += 1
        i += 0.001

    assert result == {'aaa': 500, 'bbb': 334, 'ccc': 166}


    choicer = p.make_choicer()
    choicer.adjust('aaa', 0)
    result = {'aaa':0, 'bbb':0, 'ccc':0}

    i = 0
    while i < 1:
        result[choicer.choice(i)] += 1
        i += 0.001

    assert result == {'aaa': 0, 'bbb': 667, 'ccc': 333}


    choicer.adjust('aaa', 0.5)
    result = {'aaa':0, 'bbb':0, 'ccc':0}

    i = 0
    while i < 1:
        result[choicer.choice(i)] += 1
        i += 0.001

    print choicer.dist
    assert result == {'aaa': 500, 'bbb': 334, 'ccc': 166}
