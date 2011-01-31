from util import PySettings

class Config(PySettings):
    FONT = 'sans 16'
    FONT_DOC = 'Font used in text entries'

    KEYBOARD = 'n130'
    KEYBOARD_DOC = 'Keyboard model and zones layout. One of (n130, n130_sdfv, n130_dvp)'

    TUTOR = 'en.basic'
    TUTOR_DOC = 'Tutor generator. One of (en.basic, en.advanced, ru.basic)'

    FILE = None
    FILE_DOC = 'Last opened file with words'

    RECENT_FILES = None
    RECENT_FILES_DOC = 'Last opened file list'

    def add_recent_file(self, filename, limit=5):
        if 'RECENT_FILES' not in self:
            rf = self['RECENT_FILES'] = []
        else:
            rf = self['RECENT_FILES']

        try:
            rf.remove(filename)
        except ValueError:
            pass

        rf.insert(0, filename)
        rf[:] = rf[:limit]