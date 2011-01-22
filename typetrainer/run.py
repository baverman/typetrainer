def run():
    import sys
    from optparse import OptionParser

    from typetrainer.generator import make_char_chain, generate_word


    parser = OptionParser(usage="usage: %prog [options] file_with_words")
    parser.add_option("-t", "--tutor", dest="tutor", default='en.basic',
        help="Tutor maker to use (en.basic, ru.basic)", metavar="tutor")

    options, args = parser.parse_args()

    def get_chains(tutor, filename):
        package_name = 'typetrainer.tutors.' + tutor
        try:
            __import__(package_name)
        except ImportError:
            parser.error("Can't fint [%s] tutor" % tutor)

        pkg = sys.modules[package_name]

        try:
            words = list(pkg.split_to_words(open(filename).read().decode('utf-8')))
        except IOError:
            parser.error("Can't read %s" % filename)

        first, other = make_char_chain(words, 3)
        lengths = list(pkg.make_lengths_seq(words))

        return first, other, lengths

    if not args:
        parser.error('You should specify file with words to process')

    first, other, lengths = get_chains(options.tutor, args[0])


    import gtk
    import random
    import itertools
    import collections

    from typetrainer.ui import idle
    from typetrainer.ui.main import Main
    from typetrainer.ui.kbd import n130_keyboard, KeyboardDrawer

    old_generated = collections.deque([], 100)

    def filler():
        pos = random.randint(0, len(lengths) - 1)
        left = itertools.islice(lengths, pos, None)
        right = itertools.islice(lengths, 0, pos)

        for t, l in itertools.cycle(itertools.chain(left, right)):
            if t == 'w':
                word = generate_word(first, other, l, 3)
                if word in old_generated:
                    word = generate_word(first, other, l, 3)
                old_generated.append(word)
                yield word
            else:
                yield l

    app = Main(filler, KeyboardDrawer(n130_keyboard))
    app.window.show()
    idle(app.fill)

    try:
        gtk.main()
    except KeyboardInterrupt:
        pass