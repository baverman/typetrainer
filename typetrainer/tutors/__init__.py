import sys

from typetrainer.i18n import _

available_tutors = {
    'en.basic': _('Basic English'),
    'en.advanced': _('Advanced English'),
    'ru.basic': _('Basic Russian'),
}

def get_filler(tutor, filename):
    package_name = 'typetrainer.tutors.' + tutor
    __import__(package_name)
    pkg = sys.modules[package_name]

    if filename:
        text = open(filename).read().decode('utf-8')
    else:
        text = _(u'Choose file with words.')

    filler = pkg.get_filler(text, None)
    filler.filename = filename
    filler.name = tutor

    return filler
