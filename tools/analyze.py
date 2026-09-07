import sys, json, os
from PIL import Image
import numpy as np

SRC = r"C:/Users/mirko/Downloads/VIBE CODE GAMES"
OUT = os.path.dirname(os.path.abspath(__file__))

# ---------- sprite sheet boxes ----------
sheet = np.array(Image.open(SRC + "/673ee6f4eeeaafe0afe4e69da6c92930.jpg").convert("RGB")).astype(int)
bg = np.median(sheet[5:15, 300:340].reshape(-1, 3), axis=0)
print("bg", bg)
dist = np.abs(sheet - bg).sum(axis=2)
mask = dist > 90

def boxes_in(y0, y1, x0, x1, min_w=6):
    sub = mask[y0:y1, x0:x1]
    cols = sub.any(axis=0)
    runs = []
    inrun = False
    for x, v in enumerate(cols):
        if v and not inrun:
            s = x; inrun = True
        elif not v and inrun:
            runs.append((s, x)); inrun = False
    if inrun: runs.append((s, len(cols)))
    out = []
    for s, e in runs:
        if e - s < min_w: continue
        rows = sub[:, s:e].any(axis=1)
        ys = np.where(rows)[0]
        out.append((x0 + s, y0 + ys[0], x0 + e, y0 + ys[-1] + 1))
    return out

regions = {
    "bub_row1": (14, 34, 0, 330),
    "bub_row2": (34, 54, 0, 330),
    "bub_row3": (54, 86, 0, 330),
    "zen_row": (240, 262, 0, 340),
}
allboxes = {}
for name, (y0, y1, x0, x1) in regions.items():
    bx = boxes_in(y0, y1, x0, x1)
    allboxes[name] = bx
    print(name, len(bx), bx)

# render an index sheet for each region
for name, bx in allboxes.items():
    y0, y1, x0, x1 = regions[name]
    crop = Image.fromarray(sheet[y0:y1, x0:x1].astype(np.uint8)).resize(((x1 - x0) * 4, (y1 - y0) * 4), Image.NEAREST)
    from PIL import ImageDraw
    d = ImageDraw.Draw(crop)
    for i, (a, b, c, e) in enumerate(bx):
        d.rectangle([(a - x0) * 4, (b - y0) * 4, (c - x0) * 4 - 1, (e - y0) * 4 - 1], outline=(255, 255, 255))
        d.text(((a - x0) * 4 + 1, (b - y0) * 4 + 1), str(i), fill=(255, 255, 0))
    crop.save(f"{OUT}/idx_{name}.png")
json.dump({k: [list(map(int, b)) for b in v] for k, v in allboxes.items()}, open(f"{OUT}/boxes.json", "w"))

# ---------- arcade screenshot -> tile map ----------
shot = np.array(Image.open(SRC + "/Bubble-Bobble-2.webp").convert("RGB")).astype(int)
Hh, Ww = shot.shape[:2]
# find playfield horizontal extent: columns that are not near-black grey backdrop
# The game area is x in [240,1360] approx. Detect by the border yellow columns.
colmean = shot.mean(axis=(0, 2))
# left border: first column where yellow-ish content starts
yellow = (shot[:, :, 0] > 180) & (shot[:, :, 1] > 120) & (shot[:, :, 2] < 120)
ycols = yellow.sum(axis=0)
xs = np.where(ycols > 200)[0]
print("yellow col range", xs.min(), xs.max())
left, right = xs.min(), xs.max() + 1
tw = (right - left) / 32.0
th = Hh / 28.0
print("tile size", tw, th)
grid = []
for r in range(28):
    row = ""
    for c in range(32):
        cx = int(left + (c + 0.5) * tw); cy = int((r + 0.5) * th)
        patch = shot[cy - 4:cy + 5, cx - 4:cx + 5].reshape(-1, 3)
        m = patch.mean(axis=0)
        isyellow = (m[0] > 150 and m[1] > 90 and m[2] < 140)
        isbright = m.sum() > 200
        row += "#" if isyellow else ("?" if isbright else ".")
    grid.append(row)
print("\n".join(grid))
json.dump(grid, open(f"{OUT}/grid.json", "w"))
# save a zoomed tile crop for style reference
Image.fromarray(shot[225:300, 410:720].astype(np.uint8)).resize((310 * 3, 75 * 3), Image.NEAREST).save(f"{OUT}/tile_zoom.png")
Image.fromarray(shot[60:260, 235:320].astype(np.uint8)).resize((85 * 3, 200 * 3), Image.NEAREST).save(f"{OUT}/border_zoom.png")
