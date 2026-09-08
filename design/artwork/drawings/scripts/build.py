"""Build the whole v15 sheet set: SVG from the assembly, then PDF and PNG.

    pip install build123d cairosvg
    python build.py

Geometry comes from docs/v15/the60_v15_assembly.step (and the free-spin export for
the released clutch), not from a rebuild of model.py: the vendor STEP files model.py
needs are not all in the repo. Dimension text still comes from
docs/v15/the60_v15/src/params.py, so a number on a sheet is the number in params.

Override with THE60_ASM, THE60_ASMF, THE60_SRC, THE60_OUT, THE60_CACHE if the repo
is laid out differently. The first run reads the 31 MB STEP (about 25 seconds) and
caches every body as a BREP file; later runs take seconds. The cache invalidates
itself when the STEP is re-exported.
"""
import os, runpy, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import engine                                    # noqa: E402  (fails early if the model is not reachable)
from meta import OUT                             # noqa: E402

SHEETS = ["sheet1.py", "sheet2.py", "sheet3.py", "sheet4.py", "sheet5.py"]

def main():
    engine.parts(True)                           # build or load the cache once, for every sheet
    for f in SHEETS:
        runpy.run_path(os.path.join(HERE, f), run_name="__main__")
    try:
        import cairosvg
    except ImportError:
        print("cairosvg not installed: SVG only, no PDF or PNG")
        return
    for f in sorted(os.listdir(OUT)):
        if not f.endswith(".svg"):
            continue
        src = os.path.join(OUT, f)
        cairosvg.svg2pdf(url=src, write_to=src[:-4] + ".pdf")
        cairosvg.svg2png(url=src, write_to=src[:-4] + ".png", output_width=2480)
        print("wrote", src[:-4] + ".pdf and .png")

if __name__ == "__main__":
    main()
