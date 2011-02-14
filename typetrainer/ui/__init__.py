import gtk, gobject
import contextlib

def idle_callback(callable, args):
    args, kwargs = args
    callable(*args, **kwargs)
    return False

def idle(callable, *args, **kwargs):
    options = {}
    if 'priority' in kwargs:
        options['priority'] = kwargs['priority']
        del kwargs['priority']
    return gobject.idle_add(idle_callback, callable, (args, kwargs), **options)

def refresh_gui():
    while gtk.events_pending():
        gtk.main_iteration_do(block=False)

@contextlib.contextmanager
def block_handler(obj, handler):
    obj.handler_block_by_func(handler)
    try:
        yield
    finally:
        obj.handler_unblock_by_func(handler)

class BuilderAware(object):
    def __init__(self, glade_file):
        self.gtk_builder = gtk.Builder()
        self.gtk_builder.set_translation_domain('typetrainer')
        self.gtk_builder.add_from_file(glade_file)
        self.gtk_builder.connect_signals(self)

    def __getattr__(self, name):
        obj = self.gtk_builder.get_object(name)
        if not obj:
            raise AttributeError('Builder have no %s object' % name)

        setattr(self, name, obj)
        return obj

class ShortcutActivator(object):
    def __init__(self, window):
        self.window = window
        self.accel_group = gtk.AccelGroup()
        self.window.add_accel_group(self.accel_group)

        self.shortcuts = {}
        self.pathes = {}

    def bind(self, accel, callback, *args):
        key, modifier = gtk.accelerator_parse(accel)
        self.shortcuts[(key, modifier)] = callback, args

        self.accel_group.connect_group(key, modifier, gtk.ACCEL_VISIBLE, self.activate)

    def get_callback_and_args(self, *key):
        return self.shortcuts[key]

    def activate(self, group, window, key, modifier):
        cb, args = self.get_callback_and_args(key, modifier)
        result = cb(*args)
        return result is None or result
