def run():
    from optparse import OptionParser
    from typetrainer import VERSION
    from typetrainer.i18n import _
    from typetrainer.config import Config

    parser = OptionParser(usage=_("%prog [options] [file_with_words]"),
        version="%prog " + VERSION)
    parser.add_option("-t", "--tutor", dest="tutor",
        help=_("Tutor maker to use (en.basic, en.advanced, ru.basic). Default is '%default'"),
        metavar="tutor")
    parser.add_option("-k", "--keyboard", dest="keyboard", type='choice',
        choices=['n130', 'n130_sdfv', 'n130_dvp'], metavar="keyboard",
        help=_("Onscreen keyboard type (n130, n130_sdfv, n130_dvp). Default is %default"))

    options, args = parser.parse_args()
    config = Config()
    config.load('config')

    if options.tutor:
        config['TUTOR'] = options.tutor

    if options.keyboard:
        config['KEYBOARD'] = options.keyboard

    if args:
        config['FILE'] = args[0]

    if 'FILE' in config:
        from typetrainer.tutors import get_filler
        try:
            filler = get_filler(config['TUTOR'], config['FILE'])
        except ImportError:
            parser.error(_("Can't find [%s] tutor") % config['TUTOR'])
        except IOError:
            parser.error(_("Can't read [%s]") % config['FILE'])
    else:
        import tutors.help
        filler = tutors.help.get_filler()

    import gtk

    from typetrainer.ui import idle
    from typetrainer.ui.main import Main
    from typetrainer.ui import kbd

    kbd_layout = getattr(kbd, config['KEYBOARD'] + '_keyboard')
    app = Main(config, filler, kbd.KeyboardDrawer(kbd_layout))
    app.window.show()
    idle(app.fill)

    try:
        gtk.main()
    except KeyboardInterrupt:
        pass