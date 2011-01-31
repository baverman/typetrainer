import os
from os.path import join, dirname, expanduser, exists

def join_to_file_dir(filename, *args):
    return join(dirname(filename), *args)

def join_to_settings_dir(*args):
    config_dir = os.getenv('XDG_CONFIG_HOME', expanduser('~/.config'))
    return join(config_dir, 'typetrainer', *args)

def make_missing_dirs(filename):
    path = dirname(filename)
    if not exists(path):
        os.makedirs(path, mode=0755)

def get_settings_path(name):
    filename = join_to_settings_dir(name)
    make_missing_dirs(filename)
    return filename


class PySettings(object):
    def __init__(self):
        self.data = {}
        self.sources = []

    def clear(self):
        self.data.clear()
        self.sources[:] = []

    def __getitem__(self, name):
        for s in self.sources:
            try:
                return self.data[s][name]
            except KeyError:
                pass

        value = getattr(self.__class__, name, None)
        if value is None:
            raise KeyError()

        return value

    def __setitem__(self, name, value):
        self.data[self.sources[0]][name] = value

    def __contains__(self, name):
        return any(name in self.data[s] for s in self.sources) or \
            ( getattr(self.__class__, name, None) is not None and not self.is_special(name) )

    def is_special(self, name):
        return name.startswith('_') or name.lower().endswith('_doc')

    def is_default(self, source, name):
        return name not in self.data[source] and \
            getattr(self.__class__, name, None) is not None and not self.is_special(name)

    def get_config(self, source, parent_source=None):
        result = ''
        for name in sorted(self.__class__.__dict__):
            if name not in self:
                continue

            doc = getattr(self.__class__, name + '_doc', None)
            if not doc:
                doc = getattr(self.__class__, name + '_DOC', None)
            if doc:
                result += '# ' + doc + '\n'

            write_value = True
            is_default = False

            if name in self.data[source]:
                value = self.data[source][name]
            elif parent_source and name in self.data[parent_source]:
                value = self.data[parent_source][name]
                is_default = True
            else:
                value = getattr(self.__class__, name, None)
                is_default = True
                if value is None:
                    write_value = False

            if write_value:
                value = '%s = %s' % (name, repr(value))
                if is_default:
                    value = '# ' + value

                result += value + '\n\n'

        return result

    def add_source(self, source, data):
        self.sources.insert(0, source)
        self.data[source] = data

    def load(self, name):
        filename = get_settings_path(name)
        data = {}
        try:
            execfile(filename, data)
        except IOError:
            pass
        except SyntaxError, e:
            print 'Error on loading config: %s' % filename, e

        self.add_source(name, data)

    def save(self):
        ps = None
        for s in reversed(self.sources):
            filename = get_settings_path(s)
            with open(filename, 'w') as f:
                f.write(self.get_config(s, ps))

            ps = s
