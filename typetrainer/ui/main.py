import os.path
import time

import gtk
import pango

def attach_glade(obj, filename, *names):
    builder = gtk.Builder()
    builder.add_from_file(filename)

    for name in names:
        setattr(obj, name, builder.get_object(name))

    builder.connect_signals(obj)

class Main(object):
    """glade-file: main.glade"""

    def __init__(self, filler):
        self.filler = filler

        attach_glade(self, os.path.join(os.path.dirname(__file__), 'main.glade'),
            'window', 'totype_entry', 'type_entry', 'cpm_lb', 'accuracy_lb')

    def fill(self):
        self.type_entry.set_text('')
        self.start_time = 0

        entry = self.totype_entry

        entry.modify_font(pango.FontDescription('sans 16'))
        self.type_entry.modify_font(pango.FontDescription('sans 16'))

        text = ''
        d = entry.get_layout_offsets()[0] * 2

        for w in self.filler():
            text += w

            entry.set_text(text)
            if entry.allocation.width - d < entry.get_layout().get_pixel_size()[0]:
                break

        while entry.allocation.width - d < entry.get_layout().get_pixel_size()[0]:
            text = text[:-1].strip()
            entry.set_text(text)

        self.type_entry.set_max_length(entry.get_text_length())

    def on_window_delete_event(self, *args):
        gtk.main_quit()

    def on_type_entry_changed(self, *args):
        if not self.start_time:
            self.start_time = time.time()

        ref_text = unicode(self.totype_entry.get_text())
        cur_text = unicode(self.type_entry.get_text())

        bad_idx = []
        for i, c in enumerate(cur_text):
            if c != ref_text[i]:
                bad_idx.append(i)

        attrs = pango.AttrList()
        for idx in bad_idx:
            # Pango layout needs byte index not char one O_o
            idx = len(ref_text[:idx].encode('utf8'))
            attrs.change(pango.AttrForeground(65535, 0, 0, idx, idx+1))

        self.totype_entry.get_layout().set_attributes(attrs)
        self.totype_entry.queue_draw()

    def on_type_entry_activate(self, *args):
        if self.start_time:
            delta = time.time() - self.start_time

            ref_text = unicode(self.totype_entry.get_text())
            cur_text = unicode(self.type_entry.get_text())

            self.cpm_lb.set_text("%d" % int((len(cur_text) + 1) * 60.0 / delta))

            errors = len(ref_text) - len(cur_text)
            for i, c in enumerate(cur_text):
                if c != ref_text[i]:
                    errors += 1

            self.accuracy_lb.set_text(
                '%d%%' % int((len(ref_text) - errors) * 100.0 / len(ref_text)))

        self.fill()