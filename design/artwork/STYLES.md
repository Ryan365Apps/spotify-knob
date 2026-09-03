# the 60 - artwork style definitions (2026-09-02)

Derived from design/Inspo: ink ideation sheets, marker render with one accent, mecha pencil,
flat-vector truck on topographic contours, the red-pencil exploded drawing, and the two brand
colour cards (Plasma Magenta #E445FF / Core Black #141418, Void Black #0B0F14 / Neon Cyan #3DF2E0).
All styles run on the same Blender scene (blender/the60_lineart.blend): only backdrop, line
colours/radii and part materials change, so the explode animation works in every one.
Renders: examples/styles/*.png (2400x1600, exploded, frame 100).

| style | ground | lines | fills | what it says | notes |
|---|---|---|---|---|---|
| **blueprint** (chosen earlier) | Prussian blue #1B4FA3, 5/25 mm grid | off-white #EEF3FF, hidden dashed 40 % | none | "engineered, documented" | reel + loop already rendered |
| **drafting** | cream paper #EFE8D6, grain, blotches | ink #1A1714 heavy 0.75 / light 0.22; hidden lines in red #C8352B @55 % as the underdrawing; red construction axis + rim circles (CONSTRUCTION collection) | none | "hand-drafted, work in progress, craft" | closest to the red-pencil reference; add handwritten notes + numbered balloons in the vector editor |
| **flatvector** | slate #3A3D41 with topographic contours #5C6167 | black #141418 heavy 1.1 / light 0.35, no hidden | flat emission per part: knob Plasma Magenta #E445FF, shell #C9CDD1, rings #A9B0B6/#B9C0C5, plate #7F868C, halo #F4F6F7 | "poster, merch, sticker" | the one style with colour on a part - breaks the "colour only from light" law, so keep it for print/merch, not product UI |
| **voidcyan** | Void Black #0B0F14, fine grain, faint radial lift | Neon Cyan #3DF2E0 heavy 0.7, dim cyan #2FB5A8 light 0.25, hidden 25 %, glow layer r2.4 @14 % | none | "brand, night, screen" | cleaner than the earlier neon-hex test; halo can be the second colour |
| neon (earlier test) | hex grid on near-black | cyan + magenta | none | busy | superseded by voidcyan |
| paper | #E7E8E9 | ink | none | neutral proof | default for checking geometry |

Switching: in the Blender Python console, the colours/radii above are the only edits; `set_style()`
in scripts/the60_lineart_pipeline.py covers paper/blueprint/neon and the new three can be added the same way.

## restomod (photographic, not line art) - added 2026-09-02

Scene `STUDIO` in the same .blend. Satin deep-navy clearcoat paint on the knurled knob (#101827, rough 0.22,
metallic 0.35, coat 1.0), matt black shell (#0A0B0D rough 0.62), dark steel plate, glossy black off-screen glass
disc in the bore, halo diffuser as an emissive red bar (#FF1E0A, strength 2.2) plus a red disc light under it for
the floor glow. Studio: warm-grey floor (#B7B2AA rough 0.42), light-grey corner walls, three area lights (key/fill/rim),
grey world at 0.6. Camera 70 mm, low three-quarter from slightly above, f/4 depth of field. EEVEE with raytracing, AgX.
This is the moodboard's "attitude anchor" (matt-black Saab restomod, one continuous red light bar) translated to the device.
Render: examples/styles/the60_style_restomod.png

### restomod dark ("Vader") - 2026-09-02
Same STUDIO scene, now low-key: near-black walls (#0C0D10), charcoal gloss floor (#0E0F12 rough 0.22), world 0.35.
Knob paint black gloss (#070A10 rough 0.12 metallic 0.25 coat 1.0). One long soft strip key above/behind (1400x140,
5.5e5) gives the single bright ring on the top chamfer; cool rim light (#DCE4FF, 9e5) from behind-left; fill nearly off.
Halo is a translucent diffuser (subsurface red + 45 % emission) with a red disc light (3.2e5) under it for the floor pool.
Renders: examples/styles/the60_style_restomod_dark_front.png (three-quarter from slightly above) and _dark_rear.png
(low rear quarter, halo facing camera).

### exploded studio (photographic exploded view, from the "charp" Instagram reference) - 2026-09-02
Scene `EXPLODE_PHOTO`. Light-grey world (0.76) and backdrop plane (#D9DADC) 110 mm below; three square area lights
(key 3.5e6 above front-right, fill 1.2e6, rim 1.5e6). Parts are copies of the studio parts with their own explode
driver on `EXP_CTL["explode"]`: knob +150, display +95, ring B +62, ring A +42, rocker/drive +24, shell 0,
halo -36 (frosted, faint red emission), steel plate -72. Camera 85 mm from high front-right, clip_end 10000
(the default 1000 clipped the lower parts in a mm scene - keep this in mind for every new camera).
Portrait 1600x2000. Render: examples/styles/the60_style_exploded_studio.png

Halo in EXPLODE_PHOTO is lit red (base #FF3A22, emission #FF1E0A strength 2, subsurface 0.8), matching the
studio/dark scenes. Clip: `EXP_CTL["explode"]` keyed 0 at frames 1-25, 1 at 90-140, back to 0 by 195 (210 frames,
30 fps, 1080x1350 4:5) -> examples/the60_exploded_studio_loop.mp4
