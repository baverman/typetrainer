from random import choice

def make_char_chain(words, seq_len):
    first, other = {}, {}

    for t, w in words:
        if t != 'w': continue

        wlen = len(w)
        if wlen <= seq_len:
            first.setdefault(wlen, []).append(w)
        else:
            pc = w[:seq_len]
            first.setdefault('any', []).append(pc)
            pos = seq_len
            while True:
                next = w[pos:pos+seq_len]
                if not next:
                    break

                other.setdefault(pc, []).append(next)
                pc = next
                pos += seq_len

    return first, other

def chain_traversor(choices, other, length):
    copied = False

    while True:
        try:
            head = choice(choices)
            tail = get_tail(head, other, length)
            return [head] + tail
        except KeyError:
            if not copied:
                choices = choices[:]
                copied = True

            choices.remove(head)
            if not choices:
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
        return choice(first[length])

    return ''.join(chain_traversor(first['any'], other, length))