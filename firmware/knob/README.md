# knob - dependency check

Builds the full library set for Dial4Spotify without touching any hardware.
It is not the firmware; it exists to catch version clashes early.

```powershell
cd firmware\knob
idf.py set-target esp32s3
idf.py build
```

**Passing** means "Project build complete" with no errors. That is the whole test.

If a component fails to download, look it up at components.espressif.com and
correct the version in `main/idf_component.yml`. If one fails to compile, note
which and stop - it means the version constraint needs loosening, not that the
design is wrong.

Flashing this to the board (once it arrives) prints the LVGL and IDF versions
and how much PSRAM was found, which is also Wave 2's Checkpoint A test.
