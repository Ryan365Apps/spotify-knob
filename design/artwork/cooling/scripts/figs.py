import json, math, os
import numpy as np
V="/home/claude/dwg/views"; OUT="/home/claude/dwg/fig"; os.makedirs(OUT, exist_ok=True)
def load(n): return json.load(open(os.path.join(V,n+".json")))
def paths(v): return "".join('<path d="%s"/>' % d for d in v["vis"])

def vbox(v, pad):
    """viewBox for content drawn inside <g transform='scale(1,-1)'>"""
    x0,y0,w,h = v["box"]
    return (x0-pad, -(y0+h)-pad, w+2*pad, h+2*pad)

def projector(direction, look_up=(0,0,1)):
    z=np.array(direction,float); z/=np.linalg.norm(z)
    up=np.array(look_up,float)
    x=np.cross(up,z); x/=np.linalg.norm(x)
    y=np.cross(z,x)
    def f(px,py,pz):
        p=np.array((px,py,pz),float)
        return (float(np.dot(p,x)), -float(np.dot(p,y)))   # path space
    return f

MARK=('<defs>'
 '<marker id="ac" viewBox="0 0 10 10" refX="9.2" refY="5" markerWidth="4.6" markerHeight="4.6" orient="auto-start-reverse"><path d="M 0 1.2 L 10 5 L 0 8.8 z" class="fc"/></marker>'
 '<marker id="aw" viewBox="0 0 10 10" refX="9.2" refY="5" markerWidth="4.6" markerHeight="4.6" orient="auto-start-reverse"><path d="M 0 1.2 L 10 5 L 0 8.8 z" class="fw"/></marker>'
 '</defs>')

def txt(x, y, s, cls, anchor="middle"):
    """text in unflipped space: pass path-space coords, they are negated here"""
    return '<text class="%s" x="%.2f" y="%.2f" text-anchor="%s">%s</text>' % (cls, x, -y, anchor, s)

# ============================================================ 1. BOTTOM FACE
# path space for direction (0,0,-1), look_up (0,1,0):  (px,py) = (-X,-Y)
def bp(az, r):
    a=math.radians(az); return (-r*math.cos(a), -r*math.sin(a))
def band(az0, az1, r0, r1, cls):
    xo0,yo0=bp(az0,r1); xo1,yo1=bp(az1,r1); xi1,yi1=bp(az1,r0); xi0,yi0=bp(az0,r0)
    lg = 1 if (az1-az0)%360>180 else 0
    return ('<path class="%s" d="M %.3f,%.3f A %.3f,%.3f 0 %d 1 %.3f,%.3f L %.3f,%.3f A %.3f,%.3f 0 %d 0 %.3f,%.3f Z"/>'
            % (cls,xo0,yo0,r1,r1,lg,xo1,yo1,xi1,yi1,r0,r0,lg,xi0,yi0))
def arrow(az, r0, r1, cls, mk):
    x0,y0=bp(az,r0); x1,y1=bp(az,r1)
    return '<path class="%s" d="M %.3f,%.3f L %.3f,%.3f" marker-end="url(#%s)"/>' % (cls,x0,y0,x1,y1,mk)

ring=load("bottom_ring"); core=load("bottom_core")
b=(-238,-134,476,268)
R_OUT, R_WALL = 87.704, 84.0
def leader(az, r, x_paper, y_paper):
    """leader from the arc at (az,r) to a label anchor given in PAPER coords"""
    x0,y0 = bp(az,r)
    return '<path class="ldr" d="M %.2f,%.2f L %.2f,%.2f"/>' % (x0, y0, x_paper, -y_paper)
s=['<svg viewBox="%.1f %.1f %.1f %.1f" role="img" aria-label="Underside of the dial: which rim openings take air in and which let it out" xmlns="http://www.w3.org/2000/svg">'%b, MARK]
s.append('<g transform="scale(1,-1)">')
for a0,a1,cls in ((60,300,"bc"),(300,342,"bc"),(18,60,"bw"),(342,18,"bn")):
    s.append(band(a0,a1,R_WALL,R_OUT+0.5,cls))
s.append('<g class="geo">'+paths(core)+paths(ring)+'</g>')
for az in list(range(66,300,16))+[306,318,330,339]:
    s.append(arrow(az, R_OUT+15, R_OUT+3.2, "ln-c", "ac"))
for az in (22,30,39,48,56):
    s.append(arrow(az, R_OUT+3.2, R_OUT+17, "ln-w", "aw"))
s.append(leader(180, R_OUT+14, 106, 0))
s.append(leader(321, R_OUT+14, -108, 76))
s.append(leader(39,  R_OUT+16, -108, -76))
s.append(leader(0,   R_OUT+8, -108, 0))
s.append('</g>')
def tp(x, y, t, cls, anchor="middle"):
    return '<text class="%s" x="%.2f" y="%.2f" text-anchor="%s">%s</text>' % (cls, x, y, anchor, t)
s.append(tp(112, -3, "AIR IN", "t-c", "start"))
s.append(tp(112, 8, "80 openings, 60\u2013300\u00b0", "t-s", "start"))
s.append(tp(112, 17, "the front and both sides", "t-s", "start"))
s.append(tp(-114, -79, "AIR IN", "t-c", "end"))
s.append(tp(-114, -68, "28 openings, 300\u2013342\u00b0", "t-s", "end"))
s.append(tp(-114, -59, "pulled in by the blower", "t-s", "end"))
s.append(tp(-114, 73, "AIR OUT", "t-w", "end"))
s.append(tp(-114, 84, "28 openings, 18\u201360\u00b0", "t-s", "end"))
s.append(tp(-114, 93, "the only exhaust", "t-s", "end"))
s.append(tp(-114, -3, "SOCKETS", "t-m", "end"))
s.append(tp(-114, 8, "12 positions, not cut", "t-s", "end"))
s.append(tp(60, 3, "front", "t-m"))
s.append(tp(-46, 3, "back", "t-m"))
s.append('</svg>')
open(OUT+"/fig_bottom.svg","w").write("".join(s))
print("bottom", round(os.path.getsize(OUT+"/fig_bottom.svg")/1024),"kB")

# ============================================================ 2. THE DUCT
duct=load("bottom_duct")
b2=(-238,-134,476,268)
s=['<svg viewBox="%.1f %.1f %.1f %.1f" role="img" aria-label="The same underside with the closing plate removed: the fin channels, the two plenums and the blower trench" xmlns="http://www.w3.org/2000/svg">'%b2, MARK]
s.append('<g transform="scale(1,-1)">')
s.append(band(61,310,66.0,70.2,"bc-s"))
s.append(band(22,66,55.0,70.2,"bw-s"))
s.append(band(308,338,55.0,70.2,"bc-s"))
s.append('<g class="geo">'+paths(duct)+'</g>')
s.append(leader(185, 68, 106, 0))
s.append(leader(323, 60, -108, 76))
s.append(leader(44, 60, -108, -76))
s.append(leader(46, 90, 104, -74))
s.append('</g>')
s.append(tp(112, -3, "COLLECTOR", "t-c", "start"))
s.append(tp(112, 8, "feeds all 19 fin channels", "t-s", "start"))
s.append(tp(-114, -79, "PASSIVE PLENUM", "t-c", "end"))
s.append(tp(-114, -68, "7 channels end here", "t-s", "end"))
s.append(tp(-114, 73, "BLOWER PLENUM", "t-w", "end"))
s.append(tp(-114, 84, "12 channels, and the inlet", "t-s", "end"))
s.append(tp(112, -77, "TRENCH OUT", "t-w", "start"))
s.append(tp(112, -66, "under a sealed lid", "t-s", "start"))
s.append(tp(60, 3, "front", "t-m"))
s.append(tp(-46, 3, "back", "t-m"))
s.append('</svg>')
open(OUT+"/fig_duct.svg","w").write("".join(s))
print("duct", round(os.path.getsize(OUT+"/fig_duct.svg")/1024),"kB")

# ============================================================ 3 and 4. ISOMETRICS
def iso(name, viewname, direction, arcs, aria, pad=40):
    v=load(viewname); f=projector(direction)
    b=vbox(v,pad)
    out=['<svg viewBox="%.1f %.1f %.1f %.1f" role="img" aria-label="%s" xmlns="http://www.w3.org/2000/svg">'%(b+(aria,)), MARK]
    out.append('<g transform="scale(1,-1)">')
    out.append('<g class="geo">'+paths(v)+'</g>')
    cx,cy=f(0,0,4.0)
    for az, cls, mk, outward in arcs["arrows"]:
        px,py=f(87.704*math.cos(math.radians(az)), 87.704*math.sin(math.radians(az)), 3.8)
        dx,dy=px-cx,py-cy; L=math.hypot(dx,dy) or 1; dx,dy=dx/L,dy/L
        if outward: p0=(px+dx*3.0,py+dy*3.0); p1=(px+dx*19,py+dy*19)
        else:       p0=(px+dx*19,py+dy*19);   p1=(px+dx*3.0,py+dy*3.0)
        out.append('<path class="%s" d="M %.2f,%.2f L %.2f,%.2f" marker-end="url(#%s)"/>'%(cls,p0[0],p0[1],p1[0],p1[1],mk))
    out.append('</g>')
    for az, dist, t, c in arcs["labels"]:
        px,py=f(87.704*math.cos(math.radians(az)), 87.704*math.sin(math.radians(az)), 3.8)
        dx,dy=px-cx,py-cy; L=math.hypot(dx,dy) or 1
        out.append(txt(px+dx/L*dist, py+dy/L*dist, t, c))
    out.append('</svg>')
    open(OUT+"/"+name+".svg","w").write("".join(out))
    print(name, round(os.path.getsize(OUT+"/"+name+".svg")/1024),"kB", [round(x) for x in b])

iso("fig_iso_in","iso_front",(-0.75,1.0,0.62),
    {"arrows":[(az,"ln-c","ac",False) for az in (256,271,286,301,316,331)],
     "labels":[(293,38,"room air in, all round","t-c")]},
    "The dial from the front: room air is drawn in through the openings around the front and sides")

iso("fig_iso_out","iso_exh",(-0.777,-0.629,0.62),
    {"arrows":[(az,"ln-w","aw",True) for az in (21,30,39,48,57)] +
              [(az,"ln-c","ac",False) for az in (309,321,333)] +
              [(az,"ln-c","ac",False) for az in (75,90,105)],
     "labels":[(39,40,"warm air out","t-w"),(321,34,"in","t-c"),(90,34,"in","t-c"),(0,30,"sockets","t-m")]},
    "The dial from the back right: warm air leaves through one arc of openings, with the sockets between it and the intake")
