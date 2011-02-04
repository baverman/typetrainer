import time
from collections import defaultdict, deque

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

RHYTHM_ERROR_THRESHOLD = 1.7   # Miss value from average time gap between chars
TYPO_ERROR_WEIGHT = 1.0
RHYTHM_ERROR_WEIGHT = 0.7
CORRECT_WEIGHT = 1.0
CHARS_HISTORY_LENGTH = 500
RETYPE_THRESHOLD = 0.3        # error/correct relation

class Main(BuilderAware):
    """glade-file: main.glade"""

    def __init__(self, config, filler, stat, kbd_drawer):
        BuilderAware.__init__(self, join_to_file_dir(__file__, 'main.glade'))

        self.config = config
        self.filler = filler
        self.stat = stat
        self.kbd_drawer = kbd_drawer
        self.typed_chars = deque([], CHARS_HISTORY_LENGTH)
        self.errors = defaultdict(float)

        self.vbox.pack_start(self.kbd_drawer)
        self.kbd_drawer.set_size_request(-1, 280)
        self.kbd_drawer.show()

        self.update_title()

    def fill(self):
        self.type_entry.set_text('')
        self.start_time = 0
        self.last_insert = 0

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
            pidx = len(self.totype_text[:idx].encode('utf-8'))
            Attr = pango.AttrBackground if self.totype_text[idx] == ' ' else pango.AttrForeground
            attrs.change(Attr(65535, 0, 0, pidx, pidx+1))

        self.totype_entry.get_layout().set_attributes(attrs)
        self.totype_entry.queue_draw()

    def on_type_entry_activate(self, *args):
        if self.start_time:
            delta = time.time() - self.start_time

            cur_text = unicode(self.type_entry.get_text())

            errors = len(self.totype_text) - len(cur_text)
            for i, c in enumerate(cur_text):
                if c != self.totype_text[i]:
                    errors += 1

            err = self.get_error(self.typed_chars)
            if err:
                self.filler.change_distribution(err, 0.8, True)
                self.retype_lb.set_text(err)
            else:
                self.filler.reset_distribution()
                self.retype_lb.set_text('')

            cpm = int((len(cur_text) + 1) * 60.0 / delta)
            accuracy = int((len(self.totype_text) - errors) * 100.0 / len(self.totype_text))
            self.stat_lb.set_text('%d / %d%%' % (cpm, accuracy))

            if self.filler.name:
                self.stat.log(self.filler.name, cpm, accuracy)

        self.fill()

    def get_error(self, typed):
        errors = {}

        gaps = [r[3] for r in typed if r[0] and r[3]]
        if gaps:
            avg = sum(gaps)/len(gaps)
        else:
            avg = 100000.0

        for is_correct, correct_char, prev_char, gap in typed:
            try:
                err = errors[correct_char]
            except KeyError:
                err = errors[correct_char] = {'bad':0.0, 'all':0.0, 'prevs':defaultdict(int)}

            if not is_correct or gap / avg > RHYTHM_ERROR_THRESHOLD:
                err['bad'] += RHYTHM_ERROR_WEIGHT if is_correct else TYPO_ERROR_WEIGHT
                if prev_char:
                    err['prevs'][prev_char] += 1

            err['all'] += CORRECT_WEIGHT

        max_value = 0
        err_char = prevs = None
        for ch, r in errors.iteritems():
            if r['all'] > 2:
                #print ch, r['bad'] / r['all'], r['prevs']
                value = r['bad'] / r['all']
                if value > max_value:
                    max_value = value
                    err_char, prevs = ch, r['prevs']

        #print

        if max_value > RETYPE_THRESHOLD:
            pchar = ''
            mx = max(prevs.values()) if prevs else 0
            if mx > 1:
                pchars = [p for p, c in prevs.iteritems() if c == mx]
                if len(pchars) == 1:
                    pchar = pchars[0]

            return pchar + err_char
        else:
            return None

    def on_key_event(self, window, event):
        #print event.hardware_keycode, unichr(gtk.gdk.keyval_to_unicode(event.keyval))
        self.kbd_drawer.event(event)
        return False

    def on_type_entry_insert_text(self, entry, text, *args):
        tm = time.time()
        pos = entry.get_position()
        if pos < len(self.totype_text):
            correct_char = self.filler.strip_non_word_chars(self.totype_text[pos])
            if correct_char:
                typed_char = unicode(text)
                prev_char = self.filler.strip_non_word_chars(self.totype_text[pos-1]) if pos > 0 else None
                if typed_char != correct_char:
                    self.typed_chars.append((False, correct_char, prev_char, 0.0))
                else:
                    if self.last_insert:
                        self.typed_chars.append((True, correct_char, prev_char, tm - self.last_insert))
                    else:
                        self.typed_chars.append((True, correct_char, prev_char, 0.0))

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
            idle(self.update_filler, self.get_tutor_for_file(dialog.get_filename()),
                dialog.get_filename())

        dialog.destroy()

    def update_filler(self, tutor, filename):
        self.totype_entry.set_text(_('Opening...'))
        refresh_gui()

        self.filler = get_filler(tutor, filename)
        self.fill()
        self.config._add_recent_file(filename)
        self.update_title()

        self.config['TUTOR'] = tutor
        self.config['FILE'] = filename

    def get_tutor_for_file(self, filename):
        tutor = self.filler.name
        if tutor not in available_tutors:
            tutor = 'en.basic'

        return self.config._get_tutor_for_file(filename, tutor)

    def on_tutor_activate(self, item, tutor):
        if item.get_active():
            self.config._set_tutor_for_file(self.filler.filename, tutor)
            idle(self.update_filler, tutor, self.filler.filename)

    def on_filename_activate(self, item, filename):
        idle(self.update_filler, self.get_tutor_for_file(filename), filename)

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