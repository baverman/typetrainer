import os, os.path
from datetime import datetime
import math

import gtk

from . import BuilderAware, idle, refresh_gui
from ..util import join_to_file_dir

def median(values):
    values = sorted(values)
    a = int((len(values) + 1) / 2)
    b = a - len(values) % 2

    return ( values[a-1] + values[b] ) / 2.0

def avg(values):
    return sum(values) / float(len(values))

class StatDrawer(gtk.DrawingArea):
    __gsignals__ = { "expose-event": "override" }

    def __init__(self):
        gtk.DrawingArea.__init__(self)
        self.data = None

    def do_expose_event(self, event):
        cr = self.window.cairo_create()

        cr.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
        cr.clip()

        wh = self.window.get_size()
        self.draw(cr, *wh)

    def set_data(self, data):
        self.data = data
        self.queue_draw()

    def draw(self, cr, width, height):
        if not self.data or len(self.data) < 2:
            return

        maxdt = max(self.data).toordinal()
        mindt = maxdt - 30

        mincpm = min(self.data.values(), key=lambda r: r[0])[0]
        maxcpm = max(self.data.values(), key=lambda r: r[0])[0]
        gap = max(maxcpm - mincpm, 34)

        mincpm = int(max(mincpm - gap * 0.3, 0) / 10.0) * 10
        maxcpm = int( (maxcpm + gap * 0.3) / 10.0 + 0.9 ) * 10

        wfactor = width / float(maxdt - mindt + 2)
        hfactor = (height - wfactor*1.5) / float(mincpm - maxcpm) / wfactor

        cr.scale(wfactor, wfactor)
        cr.translate(-float(mindt - 1.5), -maxcpm * hfactor)

        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.paint()

        self.draw_grid(cr, mindt, maxdt, mincpm, maxcpm, hfactor)

        data = sorted(self.data.iteritems(), key=lambda r: r[0])

        cr.set_source_rgb(0.2, 0.4, 0.2)
        cr.set_line_width(0.1)

        data.insert(0, (None, (data[0][1][0], None)))
        data.insert(0, (None, (data[0][1][0], None)))
        data.append((None, (data[-1][1][0], None)))
        data.append((None, (data[-1][1][0], None)))
        cr.new_sub_path()
        for i in range(len(data)-4):
            x = float(data[i+2][0].toordinal())
            y = avg([r[1][0] for r in data[i:i+5]])
            cr.line_to(x, y*hfactor)

        cr.stroke()

        cr.set_line_width(0.02)
        cr.new_sub_path()
        for dt, (cpm, cnt) in data[2:-2]:
            x, y = float(dt.toordinal()), cpm * hfactor
            cr.arc(x, y, 0.2, 0, math.pi*2)
            cr.set_source_rgb(0.88627, 0.68627, 0.88627)
            cr.fill_preserve()
            cr.set_source_rgb(0.2, 0.2, 0.2)
            cr.stroke()

    def draw_grid(self, cr, mindt, maxdt, mincpm, maxcpm, hfactor):
        cr.set_source_rgb(0.8, 0.8, 0.8)
        cr.set_line_width(0.02)
        for x in range(mindt, maxdt+1):
            cr.move_to(x, mincpm*hfactor)
            cr.line_to(x, maxcpm*hfactor)
            cr.stroke()

        for y in range(mincpm, maxcpm, 10):
            cr.move_to(mindt, y*hfactor)
            cr.line_to(maxdt + 0.5, y*hfactor)
            cr.stroke()

        cr.set_source_rgb(0.3, 0.3, 0.3)
        cr.set_line_width(0.08)
        cr.move_to(mindt, maxcpm*hfactor)
        cr.line_to(mindt, mincpm*hfactor)
        cr.line_to(maxdt+0.5, mincpm*hfactor)
        cr.stroke()

        cr.set_source_rgb(0.0, 0.0, 0.0)
        cr.set_font_size(0.4)
        for x in range(mindt, maxdt+1):
            y = mincpm*hfactor + 1
            dt = datetime.fromordinal(x)
            if dt.weekday() >= 5:
                cr.set_source_rgb(0.8, 0.0, 0.0)
            else:
                cr.set_source_rgb(0.0, 0.0, 0.0)

            self.draw_label(cr, str(dt.day), x-0.5, y, 1.0, 1.0, 0.5, -0.8)

            if dt.day == 1:
                cr.set_font_size(0.6)
                cr.set_source_rgb(0.0, 0.3, 0.0)
                x, _ = self.get_text_pos(cr, '1', x-0.5, y, 1.0, 1.0, 0.5, -0.8)
                self.draw_label(cr, dt.strftime('%B'), x, y, 5.0, 1.0, 0.0, 1.0)
                cr.set_font_size(0.4)

        cr.set_source_rgb(0.0, 0.0, 0.0)
        for y in range(mincpm, maxcpm, 10):
            self.draw_label(cr, str(y), mindt-1.5, y*hfactor+0.5, 1.5, 1.0, 0.8, -0.5)

    def get_text_pos(self, cr, label, x, y, w, h, xalign, yalign):
        fascent, fdescent, fheight, fxadvance, fyadvance = cr.font_extents()
        xbearing, ybearing, width, height, xadvance, yadvance = (cr.text_extents(label))
        return x + w * xalign - xbearing - width * xalign, y + h * yalign - fdescent - fheight * yalign

    def draw_label(self, cr, label, x, y, w, h, xalign, yalign):
        cr.move_to(*self.get_text_pos(cr, label, x, y, w, h, xalign, yalign))
        cr.show_text(label)


class StatWindow(BuilderAware):
    """glade-file: stat.glade"""

    def __init__(self, parent, stat, tutor):
        BuilderAware.__init__(self, join_to_file_dir(__file__, 'stat.glade'))

        self.stat = stat

        self.window.set_transient_for(parent)

        self.drawer = StatDrawer()
        self.frame.add(self.drawer)

        self.tutor = tutor
        self.acc_adj.value = 97
        idle(self.fill_tutor_cb)

    def on_acc_adj_value_changed(self, adj):
        self.refresh()

    def refresh(self):
        self.drawer.set_data(self.stat.get(self.tutor, self.acc_adj.value))

    def fill_tutor_cb(self):
        root = self.stat.root
        for name in os.listdir(root):
            fname = os.path.join(root, name)
            try:
                with open(fname) as f:
                    tname = f.readline().strip()
                    if fname == self.stat.get_filename(tname):
                        self.tutor_ls.append((fname, tname))
            except IOError:
                pass

            refresh_gui()

        for i, (fname, tname) in enumerate(self.tutor_ls):
            if tname == self.tutor:
                self.tutor_cb.set_active(i)

    def on_tutor_cb_changed(self, cb):
        it = cb.get_active_iter()
        if it:
            self.tutor = self.tutor_ls.get_value(it, 1)
            self.refresh()