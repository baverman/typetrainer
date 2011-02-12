import locale
import gettext
import os.path

APP = 'typetrainer'
DIR = os.path.join(os.path.dirname(__file__), 'locale')

if gettext.find(APP, DIR):
    locale.setlocale(locale.LC_ALL, '')
    locale.bindtextdomain(APP, DIR)
    gettext.bindtextdomain(APP, DIR)
    gettext.textdomain(APP)

    lang = gettext.translation(APP, DIR)
else:
    lang = gettext.NullTranslations()

_ = lang.ugettext
N_ = lang.ungettext