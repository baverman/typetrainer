from typetrainer.generator import make_char_chain, generate_word
from typetrainer.en.basic import make_lengths_seq, split_to_words

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