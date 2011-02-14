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