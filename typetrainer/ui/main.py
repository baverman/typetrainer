import time
from collections import defaultdict

import gtk
import pango

from typetrainer.i18n import _
from typetrainer.ui import idle, refresh_gui, BuilderAware
from typetrainer.util import join_to_file_dir
from typetrainer.tutors import available_tutors, get_filler
from typetrainer.ui.kbd import n130_dvp_keyboard, n130_keyboard, n130_sdfv_keyboard

available_keyboards = (
    (n130_keyboard, _('ASDF zones'), 'n130'),
    (n130_sdfv_keyboard, _('SDFV zones'), 'n130_sdfv'),
    (n130_dvp_keyboard, _('Programmer Dvorak zones'), 'n130_dvp'),
)

RHITM_ERROR_THRESHOLD = 1.7
RHITM_ERROR_FACTOR = 3.0
ERROR_SINK_VALUE = 3.0
TYPO_ERROR_FACTOR = 5.0
ERROR_RETYPE_THRESHOLD = 7.0

class Main(BuilderAware):
    """glade-file: main.glade"""

    def __init__(self, config, filler, kbd_drawer):
        BuilderAware.__init__(self, join_to_file_dir(__file__, 'main.glade'))

        self.config = config
        self.filler = filler
        self.kbd_drawer = kbd_drawer
        self.typed_chars = []
        self.errors = defaultdict(float)

        self.vbox.pack_start(self.kbd_drawer)
        self.kbd_drawer.set_size_request(-1, 280)
        self.kbd_drawer.show()

        self.update_title()

    def fill(self):
        self.type_entry.set_text('')
        self.start_time = 0
        self.typed_chars[:] = []
        self.last_insert = 0
        self.sink_errors()

        entry = self.totype_entry

        entry.modify_font(pango.FontDescription(self.config['FONT']))
        self.type_entry.modify_font(pango.FontDescription(self.config['FONT']))

        text = ''
        d = entry.get_layout_offsets()[0] * 2

        must_be_word = True
        for w in self.filler:
            if must_be_word and not self.filler.strip_non_word_chars(w):
                continue

            must_be_word = False

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
        self.config.save()
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
            pidx = len(self.totype_text[:idx].encode('utf8'))
            if self.totype_text[idx] == ' ':
                attrs.change(pango.AttrBackground(65535, 0, 0, pidx, pidx+1))
            else:
                attrs.change(pango.AttrForeground(65535, 0, 0, pidx, pidx+1))

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

        if typed[idx][0] and pos > 0:
            key = self.totype_text[pos-1:pos+1]
        else:
            key = self.totype_text[pos]

        key = self.filler.strip_non_word_chars(key)
        if key:
            self.errors[key] += wfactor / self.totype_text.count(char)

    def sink_errors(self):
        for k in self.errors:
            self.errors[k] = max(0, self.errors[k] - ERROR_SINK_VALUE)

    def on_type_entry_activate(self, *args):
        if self.start_time:
            delta = time.time() - self.start_time

            cur_text = unicode(self.type_entry.get_text())

            errors = len(self.totype_text) - len(cur_text)
            for i, c in enumerate(cur_text):
                if c != self.totype_text[i]:
                    errors += 1

            self.collect_rhitm_errors(self.typed_chars)
            self.collect_typo_errors(self.typed_chars)
            err = self.get_errors(self.typed_chars)
            if err:
                #print err[:5]
                key = err[0][0]
                self.filler.change_distribution(key, 0.8, True)
                self.errors[key] = ERROR_RETYPE_THRESHOLD / 2.0
                self.retype_lb.set_text(key)
            else:
                self.filler.reset_distribution()
                self.retype_lb.set_text('')

            self.stat_lb.set_text(
                '%d / %d%%' % (int((len(cur_text) + 1) * 60.0 / delta),
                    int((len(self.totype_text) - errors) * 100.0 / len(self.totype_text))))

        self.fill()

    def get_errors(self, typed):
        self.collect_rhitm_errors(self.typed_chars)
        self.collect_typo_errors(self.typed_chars)
        return sorted((r for r in self.errors.iteritems() if r[1] > ERROR_RETYPE_THRESHOLD),
            key=lambda r:r[1], reverse=True)

    def on_key_event(self, window, event):
        #print event.hardware_keycode, unichr(gtk.gdk.keyval_to_unicode(event.keyval))
        self.kbd_drawer.event(event)
        return False

    def on_type_entry_insert_text(self, entry, text, *args):
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

    def on_type_entry_delete_text(self, *args):
        self.last_insert = 0

    def on_window_button_press_event(self, window, event):
        if event.button != 3:
            return False

        menu = gtk.Menu()

        if self.filler.name in available_tutors:
            item = None
            for id, label in available_tutors.items():
                item = gtk.RadioMenuItem(item, label)
                if id == self.filler.name:
                    item.set_active(True)

                item.connect('activate', self.on_tutor_activate, id)
                menu.append(item)

            menu.append(gtk.SeparatorMenuItem())


        item = None
        for kbd, label, name in available_keyboards:
            item = gtk.RadioMenuItem(item, label)
            if kbd is self.kbd_drawer.kbd:
                item.set_active(True)

            item.connect('activate', self.on_keyboard_activate, kbd)
            menu.append(item)

        menu.append(gtk.SeparatorMenuItem())


        if 'RECENT_FILES' in self.config and self.config['RECENT_FILES']:
            item = None
            for fname in self.config['RECENT_FILES']:
                item = gtk.MenuItem(fname)
                item.connect('activate', self.on_filename_activate, fname)
                menu.append(item)

            menu.append(gtk.SeparatorMenuItem())


        item = gtk.ImageMenuItem(gtk.STOCK_OPEN)
        item.connect('activate', self.on_open_file_activate)
        menu.append(item)

        menu.show_all()
        menu.popup(None, None, None, event.button, event.time)
        return True

    def on_open_file_activate(self, item):
        dialog = gtk.FileChooserDialog(_("Open file..."),
            None,
            gtk.FILE_CHOOSER_ACTION_OPEN,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
            gtk.STOCK_OPEN, gtk.RESPONSE_OK))

        dialog.set_default_response(gtk.RESPONSE_OK)

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            tutor = self.filler.name
            if tutor not in available_tutors:
                tutor = 'en.basic'

            idle(self.update_filler, tutor, dialog.get_filename())

        dialog.destroy()

    def update_filler(self, tutor, filename):
        self.totype_entry.set_text(_('Opening...'))
        refresh_gui()

        self.filler = get_filler(tutor, filename)
        self.fill()
        self.config.add_recent_file(filename)
        self.update_title()

        self.config['TUTOR'] = tutor
        self.config['FILE'] = filename

    def on_tutor_activate(self, item, tutor):
        if item.get_active():
            idle(self.update_filler, tutor, self.filler.filename)

    def on_filename_activate(self, item, filename):
        idle(self.update_filler, self.filler.name, filename)

    def on_keyboard_activate(self, item, kbd):
        if item.get_active():
            for k, label, name in available_keyboards:
                if k is kbd:
                    self.config['KEYBOARD'] = name
                    break
            else:
                self.config['KEYBOARD'] = None

            idle(self.kbd_drawer.set_keyboard, kbd)

    def update_title(self):
        if self.filler.filename:
            self.window.set_title('Typetrainer: ' + self.filler.filename)
        else:
            self.window.set_title('Typetrainer')