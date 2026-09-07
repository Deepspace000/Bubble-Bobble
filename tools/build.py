import os
SCRATCH = os.path.dirname(os.path.abspath(__file__))
DEST_DIR = os.path.dirname(SCRATCH)
os.makedirs(DEST_DIR, exist_ok=True)
tpl = open(f"{SCRATCH}/bubble_template.html", encoding="utf-8").read()
sprites = open(f"{SCRATCH}/sprites.js", encoding="utf-8").read().strip()
assert "/*__SPRITES__*/" in tpl
out = tpl.replace("/*__SPRITES__*/", sprites)
open(f"{DEST_DIR}/index.html", "w", encoding="utf-8").write(out)
print("wrote", f"{DEST_DIR}/index.html", len(out), "bytes")
