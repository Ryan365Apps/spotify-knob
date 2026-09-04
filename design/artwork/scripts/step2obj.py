import sys, os, math
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.TDataStd import TDataStd_Name
from OCP.TopAbs import TopAbs_SOLID, TopAbs_SHELL, TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.gp import gp_Trsf

src, out_obj = sys.argv[1], sys.argv[2]

doc = TDocStd_Document(TCollection_ExtendedString("d"))
rd = STEPCAFControl_Reader()
rd.SetNameMode(True)
rd.SetColorMode(False)
rd.SetLayerMode(False)
if not rd.ReadFile(src):
    raise SystemExit("read failed")
rd.Transfer(doc)
st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())

def label_name(lab):
    from OCP.TDataStd import TDataStd_Name
    n = TDataStd_Name()
    if lab.FindAttribute(TDataStd_Name.GetID_s(), n):
        return n.Get().ToExtString()
    return None

items = []   # (name, TopoDS_Shape located)
def walk(lab, loc, prefix):
    nm = label_name(lab) or "unnamed"
    if st.IsAssembly_s(lab):
        seq = TDF_LabelSequence()
        st.GetComponents_s(lab, seq)
        for i in range(1, seq.Length()+1):
            c = seq.Value(i)
            cl = st.GetLocation_s(c)
            walk(c, loc.Multiplied(cl) if loc is not None else cl, prefix)
    else:
        ref = TDF_Label()
        if st.GetReferredShape_s(lab, ref):
            walk(ref, loc, prefix)
            return
        sh = st.GetShape_s(lab)
        if sh is None or sh.IsNull():
            return
        sh = sh.Moved(loc) if loc is not None else sh
        items.append((nm, sh))

roots = TDF_LabelSequence()
st.GetFreeShapes(roots)
for i in range(1, roots.Length()+1):
    lab = roots.Value(i)
    walk(lab, st.GetLocation_s(lab), "")

print("bodies:", len(items))

# tessellate + write obj
vcount = 0
seen = {}
with open(out_obj, "w") as f:
    f.write("# the 60 v9 assembly\n")
    for nm, sh in items:
        base = nm
        seen[base] = seen.get(base, 0) + 1
        name = base if seen[base] == 1 else f"{base}__{seen[base]}"
        name = "".join(ch if (ch.isalnum() or ch in "_-.") else "_" for ch in name)
        BRepMesh_IncrementalMesh(sh, 0.12, False, 0.35, True)
        verts = []
        tris = []
        exp = TopExp_Explorer(sh, TopAbs_FACE)
        while exp.More():
            face = TopoDS.Face_s(exp.Current())
            l = TopLoc_Location()
            tri = BRep_Tool.Triangulation_s(face, l)
            if tri is not None:
                trsf = l.Transformation()
                off = len(verts)
                n = tri.NbNodes()
                for i in range(1, n+1):
                    p = tri.Node(i).Transformed(trsf)
                    verts.append((p.X(), p.Y(), p.Z()))
                rev = face.Orientation() == 1  # TopAbs_REVERSED
                for i in range(1, tri.NbTriangles()+1):
                    t = tri.Triangle(i)
                    a, b, c = t.Value(1), t.Value(2), t.Value(3)
                    if rev: b, c = c, b
                    tris.append((off+a, off+b, off+c))
            exp.Next()
        if not tris:
            continue
        f.write(f"o {name}\n")
        for (x, y, z) in verts:
            f.write(f"v {x:.4f} {y:.4f} {z:.4f}\n")
        for (a, b, c) in tris:
            f.write(f"f {vcount+a} {vcount+b} {vcount+c}\n")
        vcount += len(verts)
print("wrote", out_obj, os.path.getsize(out_obj))
