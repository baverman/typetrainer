def run():
    from optparse import OptionParser
    from typetrainer import VERSION
    from typetrainer.i18n import _

    parser = OptionParser(usage=_("%prog [options] [file_with_words]"),
        version="%prog " + VERSION)
    parser.add_option("-t", "--tutor", dest="tutor", default='en.basic',
        help=_("Tutor maker to use (en.basic, en.advanced, ru.basic). Default is '%default'"),
        metavar="tutor")
    parser.add_option("-k", "--keyboard", dest="keyboard", default="n130", type='choice',
        choices=['n130', 'n130_sdfv', 'n130_dvp'], metavar="keyboard",
        help=_("Onscreen keyboard type (n130, n130_sdfv, n130_dvp). Default is %default"))

    options, args = parser.parse_args()

    if args:
        from typetrainer.tutors import get_filler
        try:
            filler = get_filler(options.tutor, args[0])
        except ImportError:
            parser.error(_("Can't find [%s] tutor") % options.tutor)
        except IOError:
            parser.error(_("Can't read [%s]") % args[0])
    else:
        import tutors.help
        filler = tutors.help.get_filler()

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