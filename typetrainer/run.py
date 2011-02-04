def run():
    from optparse import OptionParser
    from typetrainer import VERSION
    from typetrainer.i18n import _
    from typetrainer.config import Config

    parser = OptionParser(usage=_("%prog [options] [file_with_words]"),
        version="%prog " + VERSION)
    parser.add_option("-t", "--tutor", dest="tutor",
        help=_("Tutor maker to use (en.basic, en.advanced, ru.basic). Default is en.basic"),
        metavar="tutor")

    options, args = parser.parse_args()
    config = Config()
    config.load('config')

    if options.tutor:
        config['TUTOR'] = options.tutor

    if args:
        config['FILE'] = args[0]

    if 'FILE' in config:
        from typetrainer.tutors import get_filler
        try:
            filler = get_filler(config['TUTOR'], config['FILE'])
            config._add_recent_file(config['FILE'])
        except ImportError:
            parser.error(_("Can't find [%s] tutor") % config['TUTOR'])
        except IOError:
            parser.error(_("Can't read [%s]") % config['FILE'])
    else:
        import tutors.help
        filler = tutors.help.get_filler()

    import gtk
    import os.path

    from typetrainer.ui import idle
    from typetrainer.ui.main import Main
    from typetrainer.ui import kbd
    from typetrainer.stat import FileStatistic
    from typetrainer.util import make_missing_dirs, join_to_data_dir

    fake_stat = join_to_data_dir('fake_stat')
    make_missing_dirs(fake_stat)
    stat = FileStatistic(os.path.dirname(fake_stat))

    kbd_layout = getattr(kbd, config['KEYBOARD'] + '_keyboard')
    app = Main(config, filler, stat, kbd.KeyboardDrawer(kbd_layout))
    app.window.show()
    idle(app.fill)

    try:
        gtk.main()
    except KeyboardInterrupt:
        pass