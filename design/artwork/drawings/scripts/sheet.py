"""A3 technical drawing sheets — plain black-on-white, no styling."""
import math, html

A3 = (420.0, 297.0)

# Four hatch patterns. Adjacent cut parts get different ones so a section does
# not read as one solid blob: h0 is the default, h1 the opposite hand, h2 a
# tighter 45 deg for small parts, h3 a steep hand for bought components.
_HATCH = ((0, 45, 1.6, 0.13), (1, -45, 1.6, 0.13), (2, 45, 0.9, 0.11), (3, 75, 1.7, 0.13))
HATCH_DEFS = "".join(
    '<pattern id="h%d" width="%g" height="%g" patternTransform="rotate(%g)" patternUnits="userSpaceOnUse">'
    '<line x1="0" y1="0" x2="0" y2="%g" stroke="#000" stroke-width="%g"/></pattern>' % (i, p, p, a, p, w)
    for (i, a, p, w) in _HATCH)
N_HATCH = len(_HATCH)
FONT = "Helvetica, Arial, sans-serif"

class Sheet:
    def __init__(self, title, number, scale_note, w=A3[0], h=A3[1]):
        self.w, self.h = w, h
        self.title, self.number, self.scale_note = title, number, scale_note
        self.body = []
    def raw(self, s): self.body.append(s)
    def line(self, x1,y1,x2,y2, wgt=0.25, dash=None, col="#000"):
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        self.raw('<path d="M %.3f,%.3f L %.3f,%.3f" stroke="%s" stroke-width="%.2f" fill="none"%s/>'
                 % (x1,y1,x2,y2,col,wgt,d))
    def text(self, x, y, s, size=2.5, anchor="start", weight="normal", col="#000", rot=0):
        t = ' transform="rotate(%g %.2f %.2f)"' % (rot,x,y) if rot else ''
        self.raw('<text x="%.2f" y="%.2f" font-family="%s" font-size="%.2f" font-weight="%s" '
                 'text-anchor="%s" fill="%s"%s>%s</text>' % (x,y,FONT,size,weight,anchor,col,t,html.escape(s)))
    def rect(self, x,y,w,h, wgt=0.25, fill="none"):
        self.raw('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="%s" stroke="#000" stroke-width="%.2f"/>'
                 % (x,y,w,h,fill,wgt))

    # ---- frame and title block ----
    def frame(self, meta):
        m = 10
        self.rect(m, m, self.w-2*m, self.h-2*m, 0.5)
        tw, th = 150.0, 34.0
        x0, y0 = self.w-m-tw, self.h-m-th
        self.rect(x0, y0, tw, th, 0.5)
        self.line(x0, y0+11, x0+tw, y0+11, 0.25)
        self.line(x0, y0+22, x0+tw, y0+22, 0.25)
        self.line(x0+96, y0+11, x0+96, y0+th, 0.25)
        self.line(x0+123, y0+11, x0+123, y0+th, 0.25)
        self.text(x0+3, y0+7.5, self.title, 4.2, weight="bold")
        self.text(x0+3, y0+16.5, meta["project"], 2.6)
        self.text(x0+99, y0+16.5, "DRAWING", 1.9, col="#444")
        self.text(x0+99, y0+20.0, self.number, 2.6)
        self.text(x0+126, y0+16.5, "REV", 1.9, col="#444")
        self.text(x0+126, y0+20.0, meta["rev"], 2.6)
        self.text(x0+3, y0+27, "SCALE", 1.9, col="#444"); self.text(x0+3, y0+31, self.scale_note, 2.4)
        self.text(x0+99, y0+27, "DATE", 1.9, col="#444"); self.text(x0+99, y0+31, meta["date"], 2.4)
        self.text(x0+126, y0+27, "UNITS", 1.9, col="#444"); self.text(x0+126, y0+31, "mm", 2.4)
        self.text(m+2, self.h-m-3, meta["source"], 2.0, col="#444")
        self.text(m+2, self.h-m-7.5, meta["status"], 2.0, col="#444")

    def svg(self):
        head = ('<svg xmlns="http://www.w3.org/2000/svg" width="%gmm" height="%gmm" viewBox="0 0 %g %g">'
                '<rect width="%g" height="%g" fill="#fff"/><defs>'
                % (self.w, self.h, self.w, self.h, self.w, self.h))
        defs = (HATCH_DEFS +
                '<marker id="ar" markerWidth="8" markerHeight="8" refX="7.6" refY="2" orient="auto">'
                '<path d="M 0,0 L 8,2 L 0,4 z" fill="#000"/></marker></defs>')
        return head + defs + "\n".join(self.body) + "</svg>"


def box_centre(v):
    """Centre in the raw path frame (the exporter's viewBox is y-negated)."""
    x0,y0,w,h = v["box"]; return (x0+w/2, -(y0+h/2))


class Port:
    """Places a projected view on the sheet.  Model coords are y-up; paper is y-down."""
    def __init__(self, sheet, cx, cy, scale, ox=0.0, oy=0.0):
        self.s, self.cx, self.cy, self.k, self.ox, self.oy = sheet, cx, cy, scale, ox, oy
    def px(self, x): return self.cx + (x - self.ox) * self.k
    def py(self, y): return self.cy - (y - self.oy) * self.k
    def clip(self, name, x, y, w, h):
        self.s.raw('<clipPath id="%s"><rect x="%.2f" y="%.2f" width="%.2f" height="%.2f"/></clipPath>' % (name,x,y,w,h))
        return name
    def draw(self, v, clip=None, hidden=True, wv=0.32, wh=0.16, hatch_paths=None):
        c = '<g clip-path="url(#%s)">' % clip if clip else '<g>'
        g = (c + '<g transform="translate(%.3f,%.3f) scale(%.5f,%.5f)">'
             % (self.cx - self.ox*self.k, self.cy + self.oy*self.k, self.k, -self.k))
        out = [g]
        if hatch_paths:
            # hatch_paths is either a flat list of path strings, or a list of
            # per-part lists; a per-part list gets its own hatch angle so that
            # two parts meeting at a face do not read as one piece of material.
            groups = hatch_paths if hatch_paths and isinstance(hatch_paths[0], (list, tuple)) else [hatch_paths]
            for gi, grp in enumerate(groups):
                for d in grp:
                    out.append('<path d="%s" fill="url(#h%d)" fill-rule="evenodd" stroke="#000" '
                               'stroke-width="%.4f" stroke-linejoin="round"/>'
                               % (d, gi % N_HATCH, wv / self.k))
        if hidden and v.get("hid"):
            out.append('<g fill="none" stroke="#000" stroke-width="%.4f" stroke-dasharray="%.3f %.3f">'
                       % (wh/self.k, 1.2/self.k, 0.9/self.k))
            for d in v["hid"]: out.append('<path d="%s"/>' % d)
            out.append('</g>')
        out.append('<g fill="none" stroke="#000" stroke-width="%.4f" stroke-linecap="round">' % (wv/self.k))
        for d in v["vis"]: out.append('<path d="%s"/>' % d)
        out.append('</g></g></g>')
        self.s.raw("".join(out))

    # ---- annotation, in paper space, driven by model coordinates ----
    def dim_h(self, x1, x2, y, text=None, off=0.0, tick=2.0, above=True):
        p1, p2, py = self.px(x1), self.px(x2), self.py(y) + off
        s = self.s
        s.line(self.px(x1), self.py(y), p1, py, 0.15)
        s.line(self.px(x2), self.py(y), p2, py, 0.15)
        s.raw('<path d="M %.2f,%.2f L %.2f,%.2f" stroke="#000" stroke-width="0.2" fill="none" '
              'marker-start="url(#ar)" marker-end="url(#ar)"/>' % (p1,py,p2,py))
        t = text if text is not None else "%.4g" % abs(x2-x1)
        s.text((p1+p2)/2, py-1.2 if above else py+3.0, t, 2.4, anchor="middle")
    def dim_v(self, y1, y2, x, text=None, off=0.0, right=True):
        p1, p2, px = self.py(y1), self.py(y2), self.px(x) + off
        s = self.s
        s.line(self.px(x), self.py(y1), px, p1, 0.15)
        s.line(self.px(x), self.py(y2), px, p2, 0.15)
        s.raw('<path d="M %.2f,%.2f L %.2f,%.2f" stroke="#000" stroke-width="0.2" fill="none" '
              'marker-start="url(#ar)" marker-end="url(#ar)"/>' % (px,p1,px,p2))
        t = text if text is not None else "%.4g" % abs(y2-y1)
        s.text(px + (1.5 if right else -1.5), (p1+p2)/2 + 0.9, t, 2.4, anchor="start" if right else "end")
    def leader(self, mx, my, tx, ty, text, anchor="start", size=2.4):
        """mx,my in model coords; tx,ty in paper mm."""
        x0, y0 = self.px(mx), self.py(my)
        self.s.raw('<path d="M %.2f,%.2f L %.2f,%.2f" stroke="#000" stroke-width="0.2" fill="none" '
                   'marker-start="url(#ar)"/>' % (x0,y0,tx,ty))
        dx = 1.2 if anchor == "start" else -1.2
        self.s.text(tx+dx, ty+0.9, text, size, anchor=anchor)
    def mark(self, mx, my, r=0.9):
        self.s.raw('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="#000"/>' % (self.px(mx), self.py(my), r))

def add_balloon(port, mx, my, tx, ty, n, r=3.0):
    """Numbered balloon: leader from a model point to a circled number at paper (tx,ty)."""
    s = port.s
    x0, y0 = port.px(mx), port.py(my)
    s.raw('<path d="M %.2f,%.2f L %.2f,%.2f" stroke="#000" stroke-width="0.2" fill="none" '
          'marker-start="url(#ar)"/>' % (x0, y0, tx, ty))
    s.raw('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="#fff" stroke="#000" stroke-width="0.3"/>' % (tx, ty, r))
    s.text(tx, ty+1.1, str(n), 3.0, anchor="middle", weight="bold")

def note_list(s, x, y, items, w=95, size=2.4, lead=4.2, gap=2.0):
    import textwrap
    for n, txt in items:
        s.raw('<circle cx="%.2f" cy="%.2f" r="2.6" fill="#fff" stroke="#000" stroke-width="0.3"/>' % (x+2.6, y-1.0))
        s.text(x+2.6, y+0.1, str(n), 2.6, anchor="middle", weight="bold")
        lines = textwrap.wrap(txt, int(w/ (size*0.47)))
        for i, ln in enumerate(lines):
            s.text(x+7.5, y + i*lead, ln, size)
        y += max(len(lines),1)*lead + gap
    return y
