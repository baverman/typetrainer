from bisect import bisect

import gtk
from gtk import keysyms as s

brkl, brkr = s.bracketleft, s.bracketright
caps = s.Caps_Lock
smc = s.semicolon
cma = s.comma
prd = s.period
slh = s.slash

n130_keyboard = {
 'keys': [
  [s.grave, s._1, s._2, s._3, s._4, s._5, s._6, s._7, s._8, s._9, s._0, s.minus, s.equal, s.BackSpace],
  [s.Tab,    s.q,  s.w,  s.e,  s.r,  s.t,  s.y,  s.u,  s.i,  s.o,  s.p,  brkl,    brkr, s.backslash  ],
  [caps,      s.a,  s.s,  s.d,  s.f,  s.g,  s.h,  s.j,  s.k,  s.l,  smc,  s.apostrophe, s.Return],
  [s.Shift_L,   s.z,  s.x,  s.c,  s.v,  s.b,  s.n,  s.m,  cma,  prd,  slh,  s.Shift_R],
  [                           s.space]
 ],
 'gap': 0.08,
 'sizes': {
    (0, 0): 0.7,
    (0, 13): -1,
    (2, 0): 1.3,
    (2, 12): -1,
    (3, 0): 1.85,
    (3, 11): -1,
    (4, 0): 4 + 5*0.08
 },
 'offsets': {
    (4, 0): 4.5
 },
 'width': 14 + 13*0.08,
 'height': 5 + 4*0.08,
 'zones': [
    ([3, 4, 5, 7, 8, 9, 10, 13], [1, 2, 3, 4, 5, 1, 2, 3, 0]),
    ([1, 2, 3, 4, 6, 8, 9, 10], [0, 1, 2, 3, 4, 5, 1, 2, 3]),
    ([1, 2, 3, 4, 6, 8, 9, 10, 12 ], [0, 1, 2, 3, 4, 5, 1, 2, 3, 0]),
    ([1, 2, 3, 4, 6, 8, 9, 10, 11 ], [0, 1, 2, 3, 4, 5, 1, 2, 3, 0]),
    ([], [6]),
 ]
}

lc, hc = 0.68627, 0.88627
button_colors = [
    (hc, hc, hc), # grey
    (hc, lc, lc), # red
    (hc, hc, lc), # yellow
    (lc, hc, lc), # green
    (lc, hc, hc), # blue
    (hc, lc, hc), # magenta
    (lc, lc, hc), # deep blue
]

class KeyboardDrawer(gtk.DrawingArea):
    __gsignals__ = { "expose-event": "override" }

    def __init__(self, kbd):
        self.kbd = kbd
        gtk.DrawingArea.__init__(self)

        self.level = 0
        self.group = 0
        self.cur_state = 0

        self.connect('key-release-event', self.on_key_event)
        self.connect('key-press-event', self.on_key_event)

    def do_expose_event(self, event):
        cr = self.window.cairo_create()

        cr.rectangle(event.area.x, event.area.y,
                event.area.width, event.area.height)
        cr.clip()

        self.draw(cr, *self.window.get_size())

    def draw(self, cr, width, height):
        kw = self.kbd['width']
        kh = self.kbd['height']
        lwidth = 0.03

        cr.scale(width / ( kw + lwidth ), height / ( kh + lwidth ))
        cr.translate(lwidth / 2.0, lwidth / 2.0)

        cr.set_line_width(lwidth)
        cr.set_font_size(0.5)

        y = 0.0
        for r, row in enumerate(self.kbd['keys']):
            x = 0.0
            h = 1.0
            zones, icolors = self.kbd['zones'][r]

            for n, keyval in enumerate(row):
                w = 1.0

                if (r, n) in self.kbd['sizes']:
                    w = self.kbd['sizes'][(r, n)]
                    if w == -1:
                        w = kw - x

                if (r, n) in self.kbd['offsets']:
                    x += self.kbd['offsets'][(r, n)]

                roundedrec(cr, x, y, w, h, 0.3)

                cr.set_source_rgb(*button_colors[icolors[bisect(zones, n)]])
                cr.fill_preserve()

                cr.set_source_rgb(0.2, 0.2, 0.2)
                cr.stroke()

                self.draw_label(cr, keyval, x, y, w, h)

                x += w + self.kbd['gap']

            y += h + self.kbd['gap']

    def get_hcode(self, kmap, keyval):
        entries = kmap.get_entries_for_keyval(keyval)
        for code, group, level in entries:
            if level == group == 0:
                return code

        return entries[0][0]

    def draw_label(self, cr, keyval, x, y, w, h):
        kmap = gtk.gdk.keymap_get_default()
        keyval = kmap.translate_keyboard_state(
            self.get_hcode(kmap, keyval), self.cur_state, self.group)[0]

        ucode = gtk.gdk.keyval_to_unicode(keyval)
        if not ucode:
            return

        label = unichr(ucode)
        xbearing, ybearing, width, height, xadvance, yadvance = (cr.text_extents(label))
        cr.move_to(x + w / 2.0 - xbearing - width / 2, y + h / 2.0 - ybearing - height / 2)
        cr.show_text(label)

    def on_key_event(self, widget, event):
        st = event.state
        if event.keyval in (s.Shift_L, s.Shift_R):
            st = st ^ gtk.gdk.SHIFT_MASK

        if (event.group, st) != (self.group, self.cur_state):
            self.group = event.group
            self.cur_state = st
            self.queue_draw()

        return False


def roundedrec(context, x, y, w, h, r = 10):
    context.move_to(x+r,y)                      # Move to A
    context.line_to(x+w-r,y)                    # Straight line to B
    context.curve_to(x+w,y,x+w,y,x+w,y+r)       # Curve to C, Control points are both at Q
    context.line_to(x+w,y+h-r)                  # Move to D
    context.curve_to(x+w,y+h,x+w,y+h,x+w-r,y+h) # Curve to E
    context.line_to(x+r,y+h)                    # Line to F
    context.curve_to(x,y+h,x,y+h,x,y+h-r)       # Curve to G
    context.line_to(x,y+r)                      # Line to H
    context.curve_to(x,y,x,y,x+r,y)             # Curve to A