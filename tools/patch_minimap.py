import os
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, 'bubble_template.html')
s = open(p, encoding='utf-8').read()

def rep(a, b, count=1):
    global s
    assert s.count(a) == count, (s.count(a), a[:90])
    s = s.replace(a, b)

# minimap image (1 px per tile) rebuilt with the level
rep("const levelCanvas=document.createElement('canvas');",
    "const levelCanvas=document.createElement('canvas');\nconst miniCanvas=document.createElement('canvas');")
rep("""  for(let r=2;r<rows;r+=2){ g.drawImage(bl,0,r*TILE); g.drawImage(br,cols*TILE-16,r*TILE); }
}""",
"""  for(let r=2;r<rows;r+=2){ g.drawImage(bl,0,r*TILE); g.drawImage(br,cols*TILE-16,r*TILE); }
  // minimap: one pixel per tile
  miniCanvas.width=cols; miniCanvas.height=rows-2;
  const m=miniCanvas.getContext('2d'); m.fillStyle='rgba(0,0,0,0.7)'; m.fillRect(0,0,cols,rows-2);
  for(let r=2;r<rows;r++) for(let c=0;c<cols;c++){ const t=level.grid[r][c]; if(t==='.') continue;
    m.fillStyle= t==='w'?'#2860e0' : t==='F'?'#80c8ff' : t==='D'?'#c08040' : pal.Y; m.fillRect(c,r-2,1,1); }
}""")

# overlay drawn in screen space after the world; AUTO label moves next to the lives
rep("  if(autofire && state!=='title') text('AUTO',W-16,H-16,'#f8e030',5,'center');",
    "  if(autofire && state!=='title') text('AUTO',34,H-6,'#f8e030',5,'center');")
rep("""    // arrow toward the open exit when it is off-screen""",
"""    drawMinimap(cx,cy);
    // arrow toward the open exit when it is off-screen""")
rep("function drawFluids(cx,cy){",
"""function drawMinimap(cx,cy){
  if(LW*TILE<=W && LH*TILE<=H) return;               // the whole level is already on screen
  const cols=LW, rows=LH-2, sc=Math.min(60/cols,46/rows);
  const mw=Math.max(8,Math.round(cols*sc)), mh=Math.max(8,Math.round(rows*sc)), mx=W-4-mw, my=H-4-mh;
  ctx.fillStyle='rgba(0,0,0,0.75)'; ctx.fillRect(mx-2,my-2,mw+4,mh+4);
  ctx.imageSmoothingEnabled=false; ctx.drawImage(miniCanvas,mx,my,mw,mh);
  const px=(x)=>mx+x/TILE*sc, py=(y)=>my+(y/TILE-2)*sc;
  // camera viewport
  ctx.strokeStyle='rgba(255,255,255,0.55)'; ctx.lineWidth=1;
  ctx.strokeRect(Math.round(px(Math.max(0,cx)))+0.5, Math.round(py(Math.max(16,cy)))+0.5, Math.max(2,Math.round(Math.min(W,LW*TILE)/TILE*sc))-1, Math.max(2,Math.round(Math.min(H,LH*TILE-16)/TILE*sc))-1);
  // exit (blinks once open), enemies, player
  const d=level.exit; ctx.fillStyle= exitOpen ? (((frameCount>>3)&1)?'#40ff40':'#ffffff') : '#f8e030'; ctx.fillRect(Math.round(px(d.x+8))-1,Math.round(py(d.y+8))-1,3,3);
  for(const e of enemies){ if(e.state==='dead') continue; ctx.fillStyle= e.trapped?'#ff90d0': e.angry?'#ff3030':'#ff6060'; ctx.fillRect(Math.round(px(e.x))-1,Math.round(py(e.y-8))-1,2,2); }
  ctx.fillStyle= ((frameCount>>2)&1)?'#40ff40':'#c0ffc0'; ctx.fillRect(Math.round(px(player.x))-1,Math.round(py(player.y-8))-1,3,3);
  ctx.strokeStyle='#606070'; ctx.strokeRect(mx-1.5,my-1.5,mw+3,mh+3);
}
function drawFluids(cx,cy){""")

open(p, 'w', encoding='utf-8').write(s)
print('minimap patched OK')
