"""Shared title-block metadata for the v15 sheet set."""
import os
import engine
from engine import P

REV  = "v15"
DATE = "2026-09-07"

META = dict(
    project="the 60 (Cadrane) — desk dial",
    rev=REV, date=DATE,
    source="Projected from docs/v15/the60_v15_assembly.step by hidden-line projection, with dimension text written "
           "from docs/v15/the60_v15/src/params.py. No hand drafting. The knob is drawn on its turned profile: the "
           "knurl is on the part but is not drawn.",
    status="MODELLED, NOT MADE — no v15 part has been produced. Dimensions are model values, not inspection results. "
           "Bodies tagged ENVELOPE or ASSUMED in the model are drawn as envelopes, not as the real part.")

OUT = os.environ.get("THE60_OUT", os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
os.makedirs(OUT, exist_ok=True)

def n(v, d=2):
    """A dimension string straight from a parameter, so a sheet cannot disagree with the model."""
    return ("%%.%df" % d) % v

def save(sheet, stem):
    path = os.path.join(OUT, stem + ".svg")
    open(path, "w").write(sheet.svg())
    print("wrote", path)
    return path
