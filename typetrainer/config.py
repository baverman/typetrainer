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

    FILE2TUTOR = None
    FILE2TUTOR_DOC = 'Map which stores last tutor used for file'

    def _add_recent_file(self, filename, limit=5):
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

    def _set_tutor_for_file(self, filename, tutor):
        if 'FILE2TUTOR' not in self:
            f2t = self['FILE2TUTOR'] = {}
        else:
            f2t = self['FILE2TUTOR']

        f2t[filename] = tutor

    def _get_tutor_for_file(self, filename, default):
        if 'FILE2TUTOR' in self:
            return self['FILE2TUTOR'].get(filename, default)

        return default