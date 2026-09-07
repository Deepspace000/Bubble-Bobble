Bubble Bobble prototype - build tooling
---------------------------------------
index.html (one folder up) is the playable game with sprite data inlined.
To regenerate it after editing the sprites or the template:

  python analyze.py    # (optional) re-detect sprite boxes from the JPEG sheet -> boxes.json, and derive the tile map
  python extract.py    # crop + clean Bub / Zen-Chan frames -> sprites.js (+ sprites_preview.png)
  python build.py      # inject sprites.js into bubble_template.html -> ../index.html

Source sheets live in the VIBE CODE GAMES folder:
  673ee6f4eeeaafe0afe4e69da6c92930.jpg  characters/enemies sheet (JPEG, noisy)
  14012.png                             items sheet (not used yet)
  Bubble-Bobble-2.webp                  arcade Round 1 screenshot (layout reference)

Patch history (one-off scripts already applied to bubble_template.html, kept for reference):
  patch_scroll.py   multi-size levels, camera, sealed exit door
  patch_world.py    tile types (water w, spout F, door D), generators (tower/cave/maze/jumps/hall), 20-level roster
  patch_minimap.py  minimap overlay
Level roster and generators live in the "levels" section of the template (LEVEL_DEFS). Generators are seeded, so a level is identical every run;
change the seed number to get a different layout of the same type.
  patch_passages.py passage generator (rock with carved half-screen corridors, falling water 'f'), 30-level roster, title level selector
Later small patches (infinite lives, S+jump drop-through) were applied inline to bubble_template.html.
