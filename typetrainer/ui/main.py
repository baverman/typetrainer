import os.path
import time
from collections import defaultdict

import gtk
import pango

RHITM_ERROR_THRESHOLD = 1.7
RHITM_ERROR_FACTOR = 3.0
ERROR_SINK_VALUE = 2.0
TYPO_ERROR_FACTOR = 5.0

def attach_glade(obj, filename, *names):
    builder = gtk.Builder()
    builder.add_from_file(filename)

    for name in names:
        setattr(obj, name, builder.get_object(name))

    builder.connect_signals(obj)

class Main(object):
    """glade-file: main.glade"""

    def __init__(self, filler, kbd_drawer):
        self.filler = filler
        self.kbd_drawer = kbd_drawer
        self.typed_chars = []
        self.errors = defaultdict(float)

        attach_glade(self, os.path.join(os.path.dirname(__file__), 'main.glade'),
            'window', 'totype_entry', 'type_entry', 'cpm_lb', 'accuracy_lb', 'vbox1')

        self.window.connect('key-release-event', self.on_key_event)
        self.window.connect('key-press-event', self.on_key_event)

        self.type_entry.connect('insert-text', self.on_entry_insert)
        self.type_entry.connect('delete-text', self.on_entry_delete)

        self.vbox1.pack_start(self.kbd_drawer)
        self.kbd_drawer.set_size_request(-1, 280)
        self.kbd_drawer.show()

    def fill(self):
        self.type_entry.set_text('')
        self.start_time = 0
        self.typed_chars[:] = []
        self.last_insert = 0
        self.sink_errors()

        entry = self.totype_entry

        entry.modify_font(pango.FontDescription('sans 16'))
        self.type_entry.modify_font(pango.FontDescription('sans 16'))

        text = ''
        d = entry.get_layout_offsets()[0] * 2

        for w in self.filler:
            text += w

            entry.set_text(text)
            if entry.allocation.width - d < entry.get_layout().get_pixel_size()[0]:
                break

        while entry.allocation.width - d < entry.get_layout().get_pixel_size()[0]:
            text = text[:-1].strip()
            entry.set_text(text)

        self.type_entry.set_max_length(entry.get_text_length())
        self.totype_text = unicode(entry.get_text())

    def on_window_delete_event(self, *args):
        gtk.main_quit()

    def on_type_entry_changed(self, *args):
        if not self.start_time:
            self.start_time = time.time()

        cur_text = unicode(self.type_entry.get_text())

        bad_idx = []
        for i, c in enumerate(cur_text):
            if c != self.totype_text[i]:
                bad_idx.append(i)

        attrs = pango.AttrList()
        for idx in bad_idx:
            # Pango layout needs byte index not char one O_o
            idx = len(self.totype_text[:idx].encode('utf8'))
            if self.totype_text[idx] == ' ':
                attrs.change(pango.AttrBackground(65535, 0, 0, idx, idx+1))
            else:
                attrs.change(pango.AttrForeground(65535, 0, 0, idx, idx+1))

        self.totype_entry.get_layout().set_attributes(attrs)
        self.totype_entry.queue_draw()

    def collect_rhitm_errors(self, typed):
        gaps = [r + (i,) for i, r in enumerate(typed) if r[0] and self.totype_text[r[1]] == r[2]]
        if gaps:
            avg = sum(g[0] for g in gaps) / len(gaps)
            for g, pos, char, idx in gaps:
                if g / avg > RHITM_ERROR_THRESHOLD:
                    self.add_error(pos, typed, idx, g / avg * RHITM_ERROR_FACTOR)

    def collect_typo_errors(self, typed):
        prev_is_error = False
        for idx, (_, pos, char) in enumerate(typed):
            if char != self.totype_text[pos] and not prev_is_error:
                prev_is_error = True
                self.add_error(pos, typed, idx, TYPO_ERROR_FACTOR)
            else:
                prev_is_error = False

    def add_error(self, pos, typed, idx, wfactor):
        char = self.totype_text[pos]
        if char == ' ':
            return

        def weight_func(key):
            return 1.0/self.totype_text.count(char)

        if typed[idx][0] and pos > 0 and self.totype_text[pos-1] != ' ':
            key = self.totype_text[pos-1:pos+1]
        else:
            key = self.totype_text[pos]

        self.errors[key] += weight_func(key)*wfactor

    def sink_errors(self):
        for k in self.errors:
            self.errors[k] = max(0, self.errors[k] - ERROR_SINK_VALUE)

    def on_type_entry_activate(self, *args):
        if self.start_time:
            delta = time.time() - self.start_time

            cur_text = unicode(self.type_entry.get_text())

            self.cpm_lb.set_text("%d" % int((len(cur_text) + 1) * 60.0 / delta))

            errors = len(self.totype_text) - len(cur_text)
            for i, c in enumerate(cur_text):
                if c != self.totype_text[i]:
                    errors += 1

            self.collect_rhitm_errors(self.typed_chars)
            self.collect_typo_errors(self.typed_chars)

            print sorted((r for r in self.errors.iteritems()), key=lambda r:r[1], reverse=True)[:5]
            #print self.totype_text

            self.accuracy_lb.set_text(
                '%d%%' % int((len(self.totype_text) - errors) * 100.0 / len(self.totype_text)))

        self.fill()

    def on_key_event(self, window, event):
        #print event.hardware_keycode, unichr(gtk.gdk.keyval_to_unicode(event.keyval))
        self.kbd_drawer.event(event)
        return False

    def on_entry_insert(self, entry, text, *args):
        tm = time.time()
        pos = entry.get_position()
        if pos < len(self.totype_text):
            if self.last_insert:
                self.typed_chars.append((tm - self.last_insert, pos, text))
            else:
                self.typed_chars.append((None, pos, unicode(text)))

            self.last_insert = tm
        else:
            self.last_insert = 0

    def on_entry_delete(self, *args):
        self.last_insert = 0