"""Shared title-block metadata for the v9 sheet set."""
import os
import engine
from engine import P

REV  = "v9"
DATE = "2026-09-04"

META = dict(
    project="the 60 (Cadrane) — desk dial",
    rev=REV, date=DATE,
    source="Projected from docs/v9/the60_v9/src/params.py + model.py (build123d) by hidden-line projection. "
           "No hand drafting; dimension text is written from the parameter values.",
    status="MODELLED, NOT PRINTED — no v9 part has been made. Dimensions are model values, not inspection results. "
           "Bodies tagged ENVELOPE or ASSUMED in the model are drawn as envelopes, not as the real part.")

OUT = os.environ.get("THE60_OUT", "/root/work/out")
os.makedirs(OUT, exist_ok=True)

def n(v, d=2):
    """A dimension string straight from a parameter, so a sheet cannot disagree with the model."""
    return ("%%.%df" % d) % v

def save(sheet, stem):
    path = os.path.join(OUT, stem + ".svg")
    open(path, "w").write(sheet.svg())
    print("wrote", path)
    return path
