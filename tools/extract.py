import json, base64, io, os
from PIL import Image
import numpy as np

SRC = r"C:/Users/mirko/Downloads/VIBE CODE GAMES/673ee6f4eeeaafe0afe4e69da6c92930.jpg"
OUT = os.path.dirname(os.path.abspath(__file__))
sheet = np.array(Image.open(SRC).convert("RGB")).astype(float)
boxes = json.load(open(f"{OUT}/boxes.json"))
BG = np.array([15., 80., 174.])

def cell(box, ytop, h=16):
    x0 = box[0]
    w = box[2] - box[0]
    if w > 16: x0 = x0 + (w - 16) // 2
    return sheet[ytop:ytop + h, x0:x0 + 16].copy()

# palettes: list of (rgb) - the final clean colours
PAL = {
    "bub": [(40, 220, 40), (160, 250, 90), (10, 120, 30), (250, 250, 250), (10, 20, 10), (250, 150, 160), (250, 230, 60)],
    "zen": [(190, 200, 235), (150, 140, 210), (255, 255, 255), (5, 5, 30), (170, 50, 160), (90, 100, 230)],
    "zen_angry": [(240, 140, 145), (230, 200, 235), (215, 30, 110), (70, 5, 10), (255, 255, 255), (5, 5, 30)],
    "zen_bubbled": [(30, 180, 250), (60, 130, 250), (230, 240, 255), (10, 30, 70), (100, 40, 200), (150, 210, 255)],
}
# clusters seen in the JPEG that should map to bg (kill) per group
KILL = {
    "bub": [],
    "zen": [],
    "zen_angry": [(34, 170, 238), (1, 20, 66)],   # stray blue puffs
    "zen_bubbled": [],
}

def clean(c, who, bg_thresh=115):
    pal = np.array(PAL[who], float)
    flat = c.reshape(-1, 3)
    dbg = np.abs(flat - BG).sum(1)
    dpal = np.sqrt(((flat[:, None, :] - pal[None]) ** 2).sum(-1))
    idx = dpal.argmin(1)
    dmin = dpal.min(1)
    dbg_e = np.sqrt(((flat - BG) ** 2).sum(1))
    alpha = (dbg > bg_thresh) & (dbg_e > dmin * 0.85)
    for k in KILL[who]:
        alpha &= np.sqrt(((flat - np.array(k, float)) ** 2).sum(1)) > 45
    idx = idx.reshape(16, 16); alpha = alpha.reshape(16, 16)
    # majority denoise: a pixel whose colour index differs from all 4-neighbours takes the mode of its 8-neighbourhood
    out = idx.copy()
    for y in range(16):
        for x in range(16):
            if not alpha[y, x]: continue
            nb = []
            same4 = 0
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dy == 0 and dx == 0: continue
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < 16 and 0 <= xx < 16 and alpha[yy, xx]:
                        nb.append(idx[yy, xx])
                        if (dy == 0 or dx == 0) and idx[yy, xx] == idx[y, x]: same4 += 1
            if same4 == 0 and nb:
                vals, counts = np.unique(nb, return_counts=True)
                out[y, x] = vals[counts.argmax()]
    # drop isolated alpha specks
    a = alpha.copy()
    for y in range(16):
        for x in range(16):
            if not alpha[y, x]: continue
            n = 0
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dy == 0 and dx == 0: continue
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < 16 and 0 <= xx < 16 and alpha[yy, xx]: n += 1
            if n <= 1: a[y, x] = False
    rgba = np.zeros((16, 16, 4), np.uint8)
    rgba[..., :3] = pal[out].astype(np.uint8)
    rgba[..., 3] = a.astype(np.uint8) * 255
    return rgba

groups = {
    "bub_walk": ("bub", [("bub_row1", i, 17) for i in range(0, 6)]),
    "bub_jump": ("bub", [("bub_row1", i, 17) for i in range(7, 15)]),
    "bub_blow": ("bub", [("bub_row2", i, 37) for i in range(0, 4)]),
    "bub_idle": ("bub", [("bub_row2", i, 37) for i in range(8, 12)]),
    "bub_die": ("bub", [("bub_row3", i, 69) for i in range(0, 9)]),
    "zen_walk": ("zen", [("zen_row", i, 246) for i in range(0, 4)]),
    "zen_angry": ("zen_angry", [("zen_row", 4, 246), ("zen_row", 5, 246), ("zen_row", "x116", 246), ("zen_row", "x134", 246)]),
    "zen_bubbled": ("zen_bubbled", [("zen_row", i, 246) for i in range(7, 11)]),
}

def get_box(reg, i):
    if isinstance(i, str) and i.startswith("x"):
        x = int(i[1:]); return [x, 0, x + 16, 0]
    return boxes[reg][i]

result = {}
previews = []
for name, (who, frames) in groups.items():
    arrs = [clean(cell(get_box(reg, i), yt), who) for (reg, i, yt) in frames]
    if name == "zen_angry":
        for a in arrs: a[:, 13:, 3] = 0   # strip the puff-of-smoke pixels to the right of the body
    strip = np.concatenate(arrs, axis=1)
    im = Image.fromarray(strip, "RGBA")
    buf = io.BytesIO(); im.save(buf, "PNG", optimize=True)
    result[name] = {"frames": len(arrs), "data": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()}
    previews.append((name, im))

pw = max(im.width for _, im in previews) * 5
ph = sum(im.height * 5 + 8 for _, im in previews)
prev = Image.new("RGBA", (pw, ph), (30, 30, 30, 255))
y = 0
for name, im in previews:
    big = im.resize((im.width * 5, im.height * 5), Image.NEAREST)
    prev.alpha_composite(big, (0, y))
    y += im.height * 5 + 8
prev.save(f"{OUT}/sprites_preview.png")
with open(f"{OUT}/sprites.js", "w") as f:
    f.write("const SPRITE_DATA = " + json.dumps(result) + ";\n")
print("done", {k: v["frames"] for k, v in result.items()}, "bytes", sum(len(v["data"]) for v in result.values()))
