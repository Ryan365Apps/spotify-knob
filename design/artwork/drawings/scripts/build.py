"""Build the whole v9 sheet set: SVG from the model, then PDF and PNG.

    pip install build123d cairosvg
    export THE60_SRC=/path/to/the60_v9/src        # holds params.py and model.py
    export THE60_OUT=/path/to/design/artwork/drawings
    python build.py

The first run builds the assembly (about two minutes) and caches every body as a
BREP file under THE60_CACHE (default /root/work/cache); later runs take seconds.
The cache invalidates itself when model.py, params.py or knurl.py changes.
"""
import os, runpy, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import engine                                    # noqa: E402  (fails early if the model is not reachable)
from meta import OUT                             # noqa: E402

SHEETS = ["sheet1.py", "sheet2.py", "sheet3.py", "sheet4.py"]

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
