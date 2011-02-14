import sys

from typetrainer.i18n import _

from . import en, ru, uk

available_tutors = (en, ru, uk)

def get_filler(tutor, filename):
    fullname = tutor
    tutor, sep, level = tutor.partition('.')

    package_name = 'typetrainer.tutors.' + tutor
    __import__(package_name)
    pkg = sys.modules[package_name]

    if filename:
        text = open(filename).read().decode('utf-8')
    else:
        text = _(u'Choose file with words.')

    filler = pkg.get_filler(text, level)
    filler.filename = filename
    filler.name = tutor
    filler.level = level
    filler.tutor = pkg
    filler.fullname = fullname

    return filler
