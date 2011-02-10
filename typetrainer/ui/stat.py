from datetime import datetime

import gtk

from . import BuilderAware
from ..util import join_to_file_dir

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
        gap = maxcpm - mincpm

        mincpm = int(max(mincpm - gap * 0.3, 0) / 10.0) * 10
        maxcpm = int( (maxcpm + gap * 0.3) / 10.0 + 0.9 ) * 10

        wfactor = width / float(maxdt - mindt + 2)
        hfactor = (height - wfactor*1.5) / float(mincpm - maxcpm) / wfactor

        cr.scale(wfactor, wfactor)
        cr.translate(-float(mindt - 1.5), -maxcpm * hfactor)

        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.paint()

        self.draw_grid(cr, mindt, maxdt, mincpm, maxcpm, hfactor)

        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.set_line_width(0.1)

        moved = False
        for dt in sorted(self.data):
            x, y = float(dt.toordinal()), float(self.data[dt][0]) * hfactor
            if not moved:
                cr.move_to(x, y)
                moved = True
            else:
                cr.line_to(x, y)

        cr.stroke()

    def draw_grid(self, cr, mindt, maxdt, mincpm, maxcpm, hfactor):
        cr.set_source_rgb(0.8, 0.8, 0.8)
        cr.set_line_width(0.03)
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
            self.draw_label(cr, str(y), mindt, y*hfactor+0.5, 1.5, 1.0, -1.2, -0.5)

    def get_text_pos(self, cr, label, x, y, w, h, xalign, yalign):
        fascent, fdescent, fheight, fxadvance, fyadvance = cr.font_extents()
        xbearing, ybearing, width, height, xadvance, yadvance = (cr.text_extents(label))
        return x + w * xalign - xbearing - width * xalign, y + h * yalign - fdescent - fheight * yalign

    def draw_label(self, cr, label, x, y, w, h, xalign, yalign):
        cr.move_to(*self.get_text_pos(cr, label, x, y, w, h, xalign, yalign))
        cr.show_text(label)


class StatWindow(BuilderAware):
    """glade-file: stat.glade"""

    def __init__(self, parent, stat):
        BuilderAware.__init__(self, join_to_file_dir(__file__, 'stat.glade'))

        self.stat = stat

        self.window.set_transient_for(parent)

        self.drawer = StatDrawer()
        self.frame.add(self.drawer)

        self.acc_adj.value = 97

    def on_acc_adj_value_changed(self, adj):
        self.drawer.set_data(self.stat.get('en.basic', adj.value))
