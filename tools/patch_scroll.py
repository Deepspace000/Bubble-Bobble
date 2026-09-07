import os
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, 'bubble_template.html')
s = open(p, encoding='utf-8').read()

def rep(a, b, count=1):
    global s
    assert s.count(a) == count, (s.count(a), a[:80])
    s = s.replace(a, b)

def rep_between(start_marker, end_marker, new, include_end=True):
    global s
    i = s.index(start_marker); j = s.index(end_marker, i)
    if include_end: j += len(end_marker)
    s = s[:i] + new + s[j:]

rep("const TILE=8, COLS=32, ROWS=28, W=256, H=224, SCALE=3;",
    "const TILE=8, W=256, H=224, SCALE=3;\nlet level=null, LW=32, LH=28;   // current level and its size in tiles")

# ---- levels block replaces the fixed MAP / spawns / tileAt ----
rep_between("// Round 1 layout", "function tileAt(c,r){ if(c<0||c>=COLS) return 'W'; if(r<0||r>=ROWS) return '.'; return MAP[r][c]; }", r"""// ===================== levels =====================
// Each level is generated from a compact definition. sw/sh = size in screens (a screen is 32 x 26 playfield tiles + 2 HUD rows).
// platforms: [row, c0, c1]   walls: [col, r0, r1]   gaps: [c0, c1] cut into both ceiling and floor (fall through -> reappear at the top)
// spawn / exit / enemies are [col,row] tile positions. The exit is a 2x2 door whose bottom rests on the platform beneath it.
const PALETTES={
  sunset:{Y:'#f8d800',O:'#f87800',M:'#e82868',dark:'#780000',mid:'#a80000',border:'#6a0000',borderMid:'#8a0000'},
  ocean: {Y:'#58b8ff',O:'#2068e0',M:'#c8f4ff',dark:'#0c1a5a',mid:'#183890',border:'#0a1448',borderMid:'#142468'},
  forest:{Y:'#58e058',O:'#20a030',M:'#ecff90',dark:'#0a3c10',mid:'#146020',border:'#08300c',borderMid:'#0f4a14'},
  grape: {Y:'#d070ff',O:'#8838d0',M:'#ffd0ff',dark:'#2c0850',mid:'#48147a',border:'#22083e',borderMid:'#361060'},
};
const LEVEL_DEFS=[
 { name:'ROUND 1', sw:1, sh:1, pal:'sunset', gaps:[[9,12],[19,22]],
   platforms:[[7,5,12],[7,19,26],[12,5,13],[12,18,26],[17,5,14],[17,17,26],[22,2,6],[22,9,11],[22,20,22],[22,25,29]],
   walls:[[5,8,11],[26,8,11],[5,13,16],[26,13,16]],
   spawn:[4,26], exit:[6,5], enemies:[[10,4],[21,4],[14,4],[17,4],[7,4],[24,4]] },
 { name:'THE TOWER', sw:1, sh:2, pal:'ocean', gaps:[[12,19]],
   platforms:[[6,4,11],[6,20,27],[11,13,18],[15,2,9],[15,22,29],[19,11,20],[23,5,12],[23,19,26],[27,2,8],[27,23,29],
              [31,12,19],[35,4,11],[35,20,27],[39,2,9],[39,22,29],[43,13,18],[47,6,12],[47,19,25],[49,2,5],[49,26,29]],
   walls:[], spawn:[4,52], exit:[4,4], enemies:[[10,4],[21,4],[15,9],[8,21],[23,21],[15,29],[15,41],[8,45],[23,45]] },
 { name:'THE SPIRE', sw:1, sh:3, pal:'forest', gaps:[[12,19]],
   platforms:[[6,4,11],[6,20,27],[10,13,18],[14,2,8],[14,23,29],[18,10,21],[22,2,6],[22,25,29],[26,8,13],[26,18,23],
              [30,2,9],[30,22,29],[34,13,18],[38,4,11],[38,20,27],[42,2,6],[42,14,17],[42,25,29],[46,8,23],[50,2,8],[50,23,29],
              [54,11,20],[58,4,9],[58,22,27],[62,13,18],[66,2,9],[66,22,29],[70,11,20],[74,4,9],[74,22,27]],
   walls:[], spawn:[4,78], exit:[4,4], enemies:[[10,4],[21,4],[15,8],[15,24],[5,40],[26,40],[15,52],[15,68],[6,56],[25,56],[8,72],[23,72]] },
 { name:'THE HALLS', sw:2, sh:2, pal:'grape', gaps:[[12,19],[44,51]],
   platforms:[[6,4,13],[6,24,39],[6,50,59],[10,16,21],[10,42,47],[14,2,9],[14,26,37],[14,54,61],[18,12,21],[18,42,51],
              [22,4,9],[22,25,38],[22,54,59],[26,14,19],[26,44,49],[30,2,11],[30,24,39],[30,52,61],[34,14,21],[34,42,49],
              [38,4,9],[38,27,36],[38,54,59],[42,12,19],[42,44,51],[46,2,9],[46,24,39],[46,54,61],[49,13,18],[49,45,50]],
   walls:[[31,10,20],[32,10,20],[31,31,45],[32,31,45]],
   spawn:[4,52], exit:[30,4], enemies:[[10,4],[53,4],[20,8],[43,8],[8,20],[55,20],[31,28],[16,40],[47,40],[31,50],[4,30],[59,30]] },
];
function makeLevel(def){
  const cols=def.sw*32, rows=2+def.sh*26;
  const grid=[]; for(let r=0;r<rows;r++) grid.push(new Array(cols).fill('.'));
  const fill=(c0,r0,c1,r1,ch)=>{ for(let r=r0;r<=r1;r++) for(let c=c0;c<=c1;c++) if(r>=0&&r<rows&&c>=0&&c<cols) grid[r][c]=ch; };
  fill(0,2,1,rows-1,'W'); fill(cols-2,2,cols-1,rows-1,'W');
  fill(2,2,cols-3,2,'W'); fill(2,rows-1,cols-3,rows-1,'W');
  for(const [g0,g1] of def.gaps){ fill(g0,2,g1,2,'.'); fill(g0,rows-1,g1,rows-1,'.'); }
  for(const [r,c0,c1] of def.platforms) fill(c0,r,c1,r,'#');
  for(const [c,r0,r1] of def.walls) fill(c,r0,c,r1,'#');
  const at=([c,r])=>({x:(c+1)*TILE, y:(r+1)*TILE});
  return { def, cols, rows, grid:grid.map(r=>r.join('')), pal:PALETTES[def.pal],
    spawn:at(def.spawn), enemies:def.enemies.map(at),
    exit:{x:def.exit[0]*TILE, y:def.exit[1]*TILE, w:16, h:16} };
}
function tileAt(c,r){ if(c<0||c>=LW) return 'W'; if(r<0||r>=LH) return '.'; return level.grid[r][c]; }""")

# ---- palette-driven level graphics ----
rep_between("const BRICK=pixmap(", "buildLevel();\n", r"""function makeBrick(pal){ return pixmap(["YOYYYYOY","OOYYYYOO","YYYMMYYY","YYMMMMYY","YYMMMMYY","YYYMMYYY","OOYYYYOO","YOYYYYOY"],pal); }
function borderTile(mirror,pal){
  const c=document.createElement('canvas'); c.width=16; c.height=16; const g=c.getContext('2d');
  g.fillStyle=pal.border; g.fillRect(0,0,16,16);
  for(let y=0;y<16;y+=2) for(let x=0;x<4;x+=2){ g.fillStyle=((x+y)/2)%2?pal.Y:pal.O; g.fillRect(x,y,2,2); g.fillRect(12+x,y,2,2); }
  g.fillStyle=pal.borderMid; g.fillRect(4,0,8,16);
  g.fillStyle='#f03070'; g.fillRect(6,7,5,5); g.fillRect(5,8,7,3); g.fillRect(7,6,3,1); g.fillRect(7,12,3,1);
  g.fillStyle='#ffd0e0'; g.fillRect(6,8,1,1);
  g.fillStyle='#20d020'; g.fillRect(8,3,1,3); g.fillRect(9,2,2,2); g.fillRect(6,4,2,2);
  if(mirror){ const m=document.createElement('canvas'); m.width=16; m.height=16; const mg=m.getContext('2d'); mg.translate(16,0); mg.scale(-1,1); mg.drawImage(c,0,0); return m; }
  return c;
}
const levelCanvas=document.createElement('canvas');
function buildLevel(){
  const pal=level.pal, cols=LW, rows=LH;
  levelCanvas.width=cols*TILE; levelCanvas.height=rows*TILE;
  const g=levelCanvas.getContext('2d'); g.clearRect(0,0,levelCanvas.width,levelCanvas.height);
  const brick=makeBrick(pal), bl=borderTile(false,pal), br=borderTile(true,pal);
  const isBrick=(c,r)=> solidAt(c,r) && c>=2 && c<=cols-3;
  g.fillStyle=pal.dark;
  for(let r=2;r<rows;r++) for(let c=2;c<=cols-3;c++) if(isBrick(c,r)) g.fillRect(c*TILE+4,r*TILE+4,TILE,TILE);
  g.fillStyle=pal.mid;
  for(let r=2;r<rows;r++) for(let c=2;c<=cols-3;c++) if(isBrick(c,r)) g.fillRect(c*TILE+2,r*TILE+2,TILE,TILE);
  for(let r=2;r<rows;r++) for(let c=2;c<=cols-3;c++) if(isBrick(c,r)) g.drawImage(brick,c*TILE,r*TILE);
  for(let r=2;r<rows;r+=2){ g.drawImage(bl,0,r*TILE); g.drawImage(br,cols*TILE-16,r*TILE); }
}
level=makeLevel(LEVEL_DEFS[0]); LW=level.cols; LH=level.rows; buildLevel();
""")

# ---- physics: wrap at the level's floor ----
rep("  if(e.y-e.h>H){ e.y=TILE; e.vy=Math.min(e.vy,1); }   // fell through the floor: reappear at the top",
    "  if(e.y-e.h>LH*TILE){ e.y=TILE; e.vy=Math.min(e.vy,1); e.wrapped=true; }   // fell through the floor: reappear at the top")

# ---- state: camera + exit ----
rep("let state='title', paused=false, round=1, frameCount=0, clearTimer=0, hiScore=30000, banner=null;",
    """let state='title', paused=false, round=1, frameCount=0, clearTimer=0, hiScore=30000, banner=null;
let exitOpen=false, camSnap=true; const cam={x:0,y:0};
// smooth camera: keeps Bub inside a central dead zone, clamped to the level; snaps on spawn and wrap-around
function updateCamera(){
  const p=player; if(!p) return;
  let tx=cam.x, ty=cam.y;
  const bx0=cam.x+108, bx1=cam.x+148, by0=cam.y+92, by1=cam.y+140, py=p.y-8;
  if(p.x<bx0) tx=p.x-108; else if(p.x>bx1) tx=p.x-148;
  if(py<by0) ty=py-92; else if(py>by1) ty=py-140;
  tx=clamp(tx,0,LW*TILE-W); ty=clamp(ty,0,LH*TILE-H);
  if(camSnap){ cam.x=tx; cam.y=ty; camSnap=false; }
  else { cam.x+=(tx-cam.x)*0.15; cam.y+=(ty-cam.y)*0.15; }
}
function enterExit(){
  state='clear'; clearTimer=150; banner={text:'ROUND CLEAR!',t:150};
  const bonus=500*level.def.sw*level.def.sh; player.score+=bonus; addPopup(player.x,player.y-20,String(bonus),'#f8e030'); SFX.clear();
}""")

rep("  reset(){ this.x=PLAYER_SPAWN.x; this.y=PLAYER_SPAWN.y; this.vx=0; this.vy=0; this.facing=1; this.onGround=false;",
    "  reset(){ this.x=level.spawn.x; this.y=level.spawn.y; this.vx=0; this.vy=0; this.facing=1; this.onGround=false; camSnap=true;")
rep("    if(this.inv>0) this.inv--;\n    touchBubbles(this);",
    """    if(this.inv>0) this.inv--;
    if(this.wrapped){ this.wrapped=false; camSnap=true; }
    if(exitOpen && state==='playing' && this.onGround){ const d=level.exit; if(Math.abs(this.x-(d.x+8))<5 && this.y>=d.y+8 && this.y<=d.y+17) enterExit(); }
    touchBubbles(this);""")

# ---- bubbles: level bounds ----
rep("  b.x=clamp(b.x,2*TILE+r,W-2*TILE-r);", "  b.x=clamp(b.x,2*TILE+r,LW*TILE-2*TILE-r);")
rep("  for(let i=1;i<=COLS;i++){\n    const c=c0+i*d;\n    if(c<2||c>COLS-3) return Infinity;",
    "  for(let i=1;i<=LW;i++){\n    const c=c0+i*d;\n    if(c<2||c>LW-3) return Infinity;")
rep("        const dx=W/2-b.x;", "        const dx=LW*TILE/2-b.x;")

# ---- rounds ----
rep("""function startRound(){
  enemies=[]; bubbles=[]; fruits=[]; particles=[]; popups=[]; spawnQueue=[];
  const n=Math.min(3+round,ENEMY_SPAWNS.length);
  for(let i=0;i<n;i++){ const s=ENEMY_SPAWNS[i]; spawnQueue.push({t:40+i*30,x:s.x,y:s.y}); }
  banner={text:'ROUND '+round,t:120};
  if(player){ player.reset(); }
}""",
"""function startRound(){
  level=makeLevel(LEVEL_DEFS[(round-1)%LEVEL_DEFS.length]); LW=level.cols; LH=level.rows; buildLevel();
  enemies=[]; bubbles=[]; fruits=[]; particles=[]; popups=[]; spawnQueue=[]; exitOpen=false;
  const screens=level.def.sw*level.def.sh;
  const n=Math.min(level.enemies.length*2, 2+round+2*screens);
  for(let i=0;i<n;i++){ const s=level.enemies[i%level.enemies.length]; spawnQueue.push({t:40+i*30,x:s.x,y:s.y}); }
  banner={text:'ROUND '+round+'  '+level.def.name,t:150};
  if(player){ player.reset(); }
  camSnap=true; updateCamera();
}""")
rep("    if(enemies.length===0 && spawnQueue.length===0 && player.state==='alive'){ state='clear'; clearTimer=200; SFX.clear(); banner={text:'ROUND CLEAR!',t:200}; }",
    """    if(!exitOpen && enemies.length===0 && spawnQueue.length===0){ exitOpen=true; SFX.clear(); banner={text:'EXIT OPEN!',t:150}; }
    updateCamera();""")
rep("""    if(clearTimer%3===0 && bubbles.length){ const b=bubbles[bubbles.length-1]; if(!b.popping) startPop(b,null,false); }
    player.update();
""", """    if(clearTimer%3===0 && bubbles.length){ const b=bubbles[bubbles.length-1]; if(!b.popping) startPop(b,null,false); }
""")

# ---- render with camera ----
rep_between("function render(){", "  // HUD\n", r"""function drawExit(cx,cy){
  const d=level.exit, pal=level.pal;
  ctx.fillStyle=pal.dark; ctx.fillRect(d.x-1,d.y-2,18,18);
  ctx.fillStyle=pal.mid; ctx.fillRect(d.x,d.y-1,16,1); ctx.fillRect(d.x,d.y-1,1,17); ctx.fillRect(d.x+15,d.y-1,1,17);
  if(!exitOpen){
    ctx.fillStyle='#0c0c14'; ctx.fillRect(d.x+1,d.y,14,16);
    ctx.fillStyle='#6a6a80'; for(let i=0;i<4;i++) ctx.fillRect(d.x+2+i*4,d.y,2,16);
    ctx.fillStyle='#9a9ab0'; ctx.fillRect(d.x+1,d.y+7,14,2);
  } else {
    const t=frameCount;
    ctx.fillStyle=`hsl(${(t*3)%360},90%,55%)`; ctx.fillRect(d.x+1,d.y,14,16);
    ctx.fillStyle=`hsl(${(t*3+40)%360},90%,75%)`; ctx.fillRect(d.x+3,d.y+2,10,14);
    ctx.fillStyle='rgba(255,255,255,0.9)'; ctx.fillRect(d.x+4+((t>>3)%3)*3,d.y+3+((t>>4)%4)*3,2,2);
  }
  text('EXIT',d.x+8-cx,d.y-7-cy,exitOpen?'#40ff40':'#9090a0',5,'center');
}
function render(){
  ctx.fillStyle='#000'; ctx.fillRect(0,0,W,H);
  texts.length=0;
  if(state!=='title'){
    const cx=Math.round(cam.x), cy=Math.round(cam.y);
    ctx.save(); ctx.translate(-cx,-cy);
    ctx.drawImage(levelCanvas,0,0);
    drawExit(cx,cy);
    for(const f of fruits){ if(f.age>840 && ((frameCount>>2)&1)) continue; ctx.drawImage(f.def.img,Math.round(f.x-8),Math.round(f.y-16),16,16); }
    for(const e of enemies) e.draw();
    for(const b of bubbles) if(!b.popping) drawBubble(b);
    player.draw();
    for(const p of particles){
      const a=p.life/p.max;
      if(p.type==='ring'){ ctx.strokeStyle=p.color; ctx.globalAlpha=a; ctx.lineWidth=1; ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2); ctx.stroke(); ctx.globalAlpha=1; }
      else { ctx.fillStyle=p.color; ctx.globalAlpha=Math.min(1,a*1.5); ctx.fillRect(Math.round(p.x),Math.round(p.y),1,1); ctx.globalAlpha=1; }
    }
    ctx.restore();
    for(const t of popups) text(t.text,t.x-cx,t.y-cy,t.color,6,'center');
    // lives (bottom-left) and enemies remaining (bottom-right) as screen overlays
    const life=frame('bub_walk',0,1);
    if(life) for(let i=0;i<player.lives-1;i++) ctx.drawImage(life,2+i*9,H-9,8,8);
    const zi=frame('zen_walk',0,-1); const left=enemies.length+spawnQueue.length;
    if(zi && left>0){ ctx.drawImage(zi,W-26,H-10,8,8); text('x'+left,W-11,H-6,'#ffffff',6,'center'); }
    // arrow toward the open exit when it is off-screen
    if(exitOpen){
      const ex=level.exit.x+8-cx, ey=level.exit.y+8-cy;
      if((ex<0||ex>W||ey<16||ey>H) && ((frameCount>>3)&1)){
        const ax=clamp(ex,10,W-10), ay=clamp(ey,26,H-14), ang=Math.atan2(ey-ay,ex-ax);
        ctx.save(); ctx.translate(ax,ay); ctx.rotate(ang); ctx.fillStyle='#40ff40';
        ctx.beginPath(); ctx.moveTo(7,0); ctx.lineTo(-4,-5); ctx.lineTo(-4,5); ctx.closePath(); ctx.fill(); ctx.restore();
      }
    }
  } else {
    ctx.drawImage(levelCanvas,0,0);
  }
  // HUD
""")
open(p, 'w', encoding='utf-8').write(s)
print('patched OK')
