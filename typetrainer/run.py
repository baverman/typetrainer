def run():
    import sys
    from optparse import OptionParser
    from typetrainer import VERSION

    parser = OptionParser(usage="usage: %prog [options] file_with_words",
        version="%prog " + VERSION)
    parser.add_option("-t", "--tutor", dest="tutor", default='en.basic',
        help="Tutor maker to use (en.basic, en.advanced, ru.basic). Default is '%default'",
        metavar="tutor")
    parser.add_option("-k", "--keyboard", dest="keyboard", default="n130", type='choice',
        choices=['n130', 'n130_sdfv'], metavar="keyboard",
        help="Onscreen keyboard type (n130, n130_sdfv). Default is %default")

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
    from typetrainer.ui import kbd

    kbd_layout = getattr(kbd, options.keyboard + '_keyboard')
    app = Main(filler, kbd.KeyboardDrawer(kbd_layout))
    app.window.show()
    idle(app.fill)

    try:
        gtk.main()
    except KeyboardInterrupt:
        pass