"""Cut character frames from the clean PNG master sheet (bubble sprites.png) into sprites.js.
Exact background keying, no palette snapping needed. Frames are 16x16, bottom-aligned within each row band."""
import json, base64, io, os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = r"C:/Users/mirko/Downloads/VIBE CODE GAMES/bubble sprites.png"
im = Image.open(SRC).convert("RGB")
a = np.array(im).astype(int)
BG = np.array([15, 79, 174])
mask = np.abs(a - BG).sum(2) > 0

BANDS = {'bub1':(16,32),'bub2':(36,52),'bub3':(58,85),'zen':(245,261),'mighta1':(278,294),'mighta2':(299,315),
         'monsta':(332,349),'pulpul':(363,379),'banebou':(393,410),'invader':(424,441),'hidegons1':(455,471),
         'hidegons2':(476,492),'drunk1':(507,523),'drunk2':(529,545),'sd1':(598,662),'sd2':(667,735),'giants':(752,784)}

def boxes(band):
    y0, y1 = BANDS[band]
    sub = mask[y0:y1, :645]; cols = sub.any(0); runs = []; inrun = False
    for x, v in enumerate(cols):
        if v and not inrun: s = x; inrun = True
        elif not v and inrun: runs.append((s, x)); inrun = False
    if inrun: runs.append((s, len(cols)))
    out = []
    for s, e in runs:
        if e - s < 3: continue
        ys = np.where(sub[:, s:e].any(1))[0]; out.append((s, y0 + ys[0], e, y0 + ys[-1] + 1))
    return out

BOX = {k: boxes(k) for k in BANDS}

def cell(band, i, w=16, h=16):
    s, t, e, b = BOX[band][i]
    bw = e - s
    x0 = s + (bw - w) // 2 if bw > w else s - (w - bw) // 2
    y0 = b - h                       # bottom-aligned
    rgba = np.zeros((h, w, 4), np.uint8)
    for yy in range(h):
        for xx in range(w):
            X, Y = x0 + xx, y0 + yy
            if 0 <= X < a.shape[1] and 0 <= Y < a.shape[0] and mask[Y, X]:
                rgba[yy, xx, :3] = a[Y, X]; rgba[yy, xx, 3] = 255
    return rgba

def strip(frames):
    return np.concatenate(frames, axis=1)

R = lambda band, lo, hi: [(band, i) for i in range(lo, hi)]
GROUPS = {
    # player one (Bub) and player two (Bob) share the same frame layout
    'bub_walk': R('bub1',0,6),  'bub_jump': R('bub1',7,15), 'bub_blow': R('bub2',0,4),  'bub_idle': R('bub2',8,12),  'bub_die': R('bub3',0,9),
    'bob_walk': R('bub1',15,21),'bob_jump': R('bub1',22,30),'bob_blow': R('bub2',15,19),'bob_idle': R('bub2',23,27),'bob_die': R('bub3',17,26),
    'zen_walk': R('zen',0,4),   'zen_angry': R('zen',4,8),
    'mighta_walk': R('mighta1',0,4),   'mighta_angry': R('mighta1',10,14), 'mighta_throw': R('mighta1',6,8), 'mighta_athrow': R('mighta1',16,18),
    'monsta_walk': R('monsta',0,2),    'monsta_angry': R('monsta',2,4),
    'pulpul_walk': R('pulpul',0,4),    'pulpul_angry': R('pulpul',4,8),
    'banebou_walk': R('banebou',0,4),  'banebou_angry': R('banebou',4,8),
    'invader_walk': R('invader',0,2),  'invader_angry': R('invader',2,4),
    'hidegons_walk': R('hidegons1',0,4),'hidegons_angry': R('hidegons1',6,10),
    'drunk_walk': R('drunk1',0,4),     'drunk_angry': R('drunk1',10,14),   'drunk_throw': R('drunk1',4,6), 'drunk_athrow': R('drunk1',14,16),
    'fx_fire': R('hidegons2',0,3),     'fx_bottle': R('drunk2',0,2),
    # bosses: Super Drunk (64x64) and the giant monsters (32x32)
    'superdrunk_walk': R('sd1',0,4), 'superdrunk_angry': R('sd1',4,6), 'superdrunk_hurt': R('sd2',0,4),
    'giant_zen': R('giants',0,4), 'giant_pulpul': R('giants',4,8), 'giant_banebou': R('giants',8,12),
    'giant_monsta': R('giants',12,14), 'giant_hidegons': R('giants',14,16), 'giant_mighta': R('giants',16,18),
}
SIZES={'superdrunk_':(64,64),'giant_':(32,32)}
def size_for(name):
    for k,v in SIZES.items():
        if name.startswith(k): return v
    return (16,16)

result = {}
previews = []
for name, frames in GROUPS.items():
    w, h = size_for(name)
    arrs = [cell(b, i, w, h) for (b, i) in frames]
    img = Image.fromarray(strip(arrs), 'RGBA')
    buf = io.BytesIO(); img.save(buf, 'PNG', optimize=True)
    result[name] = {'frames': len(arrs), 'data': 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()}
    previews.append((name, img))

pw = max(i.width for _, i in previews) * 4
ph = sum(i.height * 4 + 6 for _, i in previews)
prev = Image.new('RGBA', (pw, ph), (30, 30, 30, 255)); y = 0
for name, i in previews:
    prev.alpha_composite(i.resize((i.width * 4, i.height * 4), Image.NEAREST), (0, y)); y += i.height * 4 + 6
prev.save(os.path.join(HERE, 'sprites_preview.png'))
open(os.path.join(HERE, 'sprites.js'), 'w', encoding='utf-8').write('const SPRITE_DATA = ' + json.dumps(result) + ';\n')
print('done', {k: v['frames'] for k, v in result.items()}, 'bytes', sum(len(v['data']) for v in result.values()))
