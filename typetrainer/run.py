def run():
    import sys
    from optparse import OptionParser

    parser = OptionParser(usage="usage: %prog [options] file_with_words")
    parser.add_option("-t", "--tutor", dest="tutor", default='en.basic',
        help="Tutor maker to use (en.basic, en.advanced, ru.basic). Default is 'en.basic'",
        metavar="tutor")

    options, args = parser.parse_args()

    if not args:
        parser.error('You should specify file with words to process')

    def get_filler(tutor, filename):
        package_name = 'typetrainer.tutors.' + tutor
        try:
            __import__(package_name)
        except ImportError:
            parser.error("Can't find [%s] tutor" % tutor)

        pkg = sys.modules[package_name]

        try:
            return pkg.get_filler(open(filename).read().decode('utf-8'), None)
        except IOError:
            parser.error("Can't read [%s]" % filename)

    filler = get_filler(options.tutor, args[0])

    import gtk

    from typetrainer.ui import idle
    from typetrainer.ui.main import Main
    from typetrainer.ui.kbd import n130_keyboard, KeyboardDrawer

    app = Main(filler, KeyboardDrawer(n130_keyboard))
    app.window.show()
    idle(app.fill)

    try:
        gtk.main()
    except KeyboardInterrupt:
        pass