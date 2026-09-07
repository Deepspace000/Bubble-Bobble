import os
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, 'bubble_template.html')
s = open(p, encoding='utf-8').read()

def rep(a, b, count=1):
    global s
    assert s.count(a) == count, (s.count(a), a[:90])
    s = s.replace(a, b)

# ---- placement (makeLevel): a few non-interactive props on every level, themed by palette ----
rep("  return { def, cols, rows, grid, trees, pal:PALETTES[def.pal]||PALETTES.sunset, spawn:at(def.spawn), enemies, keys, doorIds,",
    """  // props: purely decorative, drawn behind the bricks. Which ones appear depends on the level's palette.
  const THEMES={forest:['grass','grass','flower','flower','smalltree','rock','garden'], cave:['rock','rock','stone','stone','grass','box'],
    stone:['box','lamp','monitor','stone','grass'], ember:['box','box','lamp','monitor','rock'], ocean:['stone','stone','grass','box','flower'],
    sunset:['flower','garden','grass','lamp','box'], grape:['monitor','box','lamp','flower','stone'], ice:['stone','rock','lamp','grass']};
  const decor=[]; { const R=rng(hashStr(def.name)+7), kinds=THEMES[def.pal]||THEMES.sunset; const HEAD={grass:1,flower:1,stone:1,rock:1,box:1,monitor:1,smalltree:3,lamp:3,garden:1};
    for(let r=3;r<rows-1;r++){ let c=2; while(c<=cols-3){
      if(solid(c,r)&&!solid(c,r-1)){ let e=c; while(e+1<=cols-3&&solid(e+1,r)&&!solid(e+1,r-1)) e++; const len=e-c+1;
        const n=len<3?0:len<8?(R()<0.6?1:0):1+ri(R,0,Math.min(3,Math.floor(len/6)));
        for(let k=0;k<n;k++){ const kind=kinds[ri(R,0,kinds.length-1)], tc=ri(R,c,e); let air=0; while(air<4&&r-1-air>2&&!solid(tc,r-1-air)) air++;
          if(air>=HEAD[kind]) decor.push({kind,x:tc*TILE+4,y:r*TILE,seed:Math.floor(R()*100000)}); }
        c=e+1; } else c++; } } }
  return { def, cols, rows, grid, trees, decor, pal:PALETTES[def.pal]||PALETTES.sunset, spawn:at(def.spawn), enemies, keys, doorIds,""")

# ---- drawing (buildLevel) ----
rep("  for(const t of (level.trees||[])) drawTree(g,t);\n",
    "  for(const d of (level.decor||[])) drawProp(g,d);\n  for(const t of (level.trees||[])) drawTree(g,t);\n")
rep("function drawTree(g,t){",
    r"""function drawProp(g,d){
  const R=rng(d.seed), x=d.x, y=d.y, px=(X,Y,w,h,col)=>{ g.fillStyle=col; g.fillRect(Math.round(X),Math.round(Y),w,h); };
  switch(d.kind){
    case 'grass': { const n=3+ri(R,0,3); for(let i=0;i<n;i++){ const h=2+ri(R,0,3); px(x-3+i*1.5,y-h,1,h,i%2?'#3fc04c':'#2a9a3c'); } break; }
    case 'flower': { const h=3+ri(R,0,2), cols=['#ff5f8f','#ffd23c','#ff8a2a','#c070ff','#ffffff']; px(x,y-h,1,h,'#2a9a3c'); px(x-2,y-h+1,2,1,'#2a9a3c');
      const c=cols[ri(R,0,cols.length-1)]; px(x-1,y-h-2,3,3,c); px(x,y-h-1,1,1,'#ffe080'); break; }
    case 'garden': { for(let i=-1;i<=1;i++){ const h=3+ri(R,0,2), cols=['#ff5f8f','#ffd23c','#ff8a2a','#c070ff']; px(x+i*3,y-h,1,h,'#2a9a3c'); px(x+i*3-1,y-h-2,3,3,cols[(i+1+ri(R,0,3))%4]); px(x+i*3,y-h-1,1,1,'#ffe080'); }
      for(let i=0;i<4;i++) px(x-5+i*3,y-2,1,2,'#3fc04c'); break; }
    case 'stone': { px(x-1,y-2,4,2,'#8a8a98'); px(x-1,y-2,2,1,'#c0c0cc'); px(x-2,y-1,1,1,'#6a6a78'); break; }
    case 'rock': { px(x-3,y-4,7,4,'#5a5a68'); px(x-2,y-5,5,1,'#5a5a68'); px(x-2,y-4,3,2,'#9a9aa8'); px(x-4,y-2,1,2,'#5a5a68'); px(x+2,y-1,2,1,'#3a3a48'); break; }
    case 'box': { const two=R()<0.35; const crate=(bx,by)=>{ px(bx-4,by-8,8,8,'#3a2210'); px(bx-3,by-7,6,6,'#a06a30'); px(bx-3,by-7,6,1,'#c88a48'); px(bx-3,by-7,1,6,'#c88a48'); px(bx-1,by-6,1,4,'#6a4218'); px(bx-3,by-4,6,1,'#6a4218'); };
      crate(x,y); if(two) crate(x+(R()<0.5?-3:3),y-8); break; }
    case 'monitor': { px(x-4,y-8,8,7,'#8a8a98'); px(x-3,y-7,6,4,'#123a6a'); px(x-2,y-6,3,1,'#60e0ff'); px(x-2,y-5,2,1,'#60e0ff'); px(x+1,y-5,1,1,'#60e0ff'); px(x-1,y-1,2,1,'#5a5a68'); px(x-2,y-2,4,1,'#5a5a68'); px(x+2,y-3,1,1,'#40ff40'); break; }
    case 'lamp': { px(x,y-18,1,18,'#3a3a48'); px(x-2,y-1,5,1,'#3a3a48'); px(x-2,y-20,5,3,'#5a5a68'); px(x-1,y-19,3,1,'#ffe080'); px(x-3,y-21,7,1,'#3a3a48');
      g.fillStyle='rgba(255,230,120,0.13)'; g.beginPath(); g.arc(x+0.5,y-18,9,0,Math.PI*2); g.fill(); break; }
    case 'smalltree': { px(x,y-8,1,8,'#5a3a1a'); px(x-1,y-8,3,2,'#5a3a1a'); g.fillStyle='#2a9a3c'; g.beginPath(); g.arc(x+0.5,y-11,5,0,Math.PI*2); g.fill(); g.fillStyle='#3fc04c'; g.beginPath(); g.arc(x-1,y-13,3,0,Math.PI*2); g.fill(); px(x+1,y-14,1,1,'#7ee070'); break; }
  }
}
function drawTree(g,t){""")

open(p, 'w', encoding='utf-8').write(s)
print('decor patched OK')
