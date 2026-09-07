import os
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, 'bubble_template.html')
s = open(p, encoding='utf-8').read()

def rep(a, b, count=1):
    global s
    assert s.count(a) == count, (s.count(a), a[:90])
    s = s.replace(a, b)

def rep_between(start_marker, end_marker, new, include_end=True):
    global s
    i = s.index(start_marker); j = s.index(end_marker, i)
    if include_end: j += len(end_marker)
    s = s[:i] + new + s[j:]

# ---------------------------------------------------------------- passage generator
rep("// ---- hand-made levels ----",
r"""// Passage: solid rock with half-screen corridors carved through it as a winding maze of shafts and tunnels.
// Each cell is 12 x 11 tiles of air. Vertical shafts get zig-zag ledges (or a spout); tunnels get a step, a moat,
// and water that pours off a ledge stub down the shaft below as falling water ('f').
function genPassage(name,sw,sh,pal,seed,opts={}){
  const R=rng(seed), d=blankDef(name,sw,sh,pal); d.rock=true; d.flows=[];
  const nx=Math.max(1,Math.round(sw*2)), ny=Math.max(1,Math.round(sh*2));
  const cx0=i=>i*16+2, cx1=i=>i*16+13, ry0=j=>3+j*13, ry1=j=>ry0(j)+10;
  for(let i=0;i<nx;i++) for(let j=0;j<ny;j++) d.clears.push([cx0(i),ry0(j),cx1(i),ry1(j)]);
  const key=(i,j)=>i+','+j, depth=new Map(), conn={}; const start=[0,ny-1]; depth.set(key(...start),0);
  const link=(a,b)=>{ (conn[key(...a)]=conn[key(...a)]||[]).push(b); (conn[key(...b)]=conn[key(...b)]||[]).push(a); };
  const stack=[start]; let far=start, farD=0;
  while(stack.length){ const cur=stack[stack.length-1], [i,j]=cur;
    const nb=[[i+1,j],[i-1,j],[i,j+1],[i,j-1]].filter(([a,b])=>a>=0&&a<nx&&b>=0&&b<ny&&!depth.has(key(a,b)));
    if(!nb.length){ stack.pop(); continue; }
    const nxt=nb[ri(R,0,nb.length-1)], dep=depth.get(key(i,j))+1; depth.set(key(...nxt),dep); link(cur,nxt); if(dep>farD){ farD=dep; far=nxt; } stack.push(nxt); }
  const has=(i,j,di,dj)=>(conn[key(i,j)]||[]).some(([a,b])=>a===i+di&&b===j+dj);
  for(let i=0;i<nx;i++) for(let j=0;j<ny;j++){
    if(has(i,j,1,0)) d.clears.push([cx1(i)+1,ry1(j)-6,cx1(i)+4,ry1(j)]);          // tunnel, 7 tall
    if(has(i,j,0,1)) d.clears.push([cx0(i)+2,ry1(j)+1,cx0(i)+9,ry1(j)+2]);         // shaft opening, 8 wide, leaves stubs
  }
  d.spawn=[cx0(0)+1,ry1(ny-1)]; d.exit=[cx1(far[0])-1,ry1(far[1])-1];
  for(let i=0;i<nx;i++) for(let j=0;j<ny;j++){
    const X0=cx0(i),X1=cx1(i),Y0=ry0(j),Y1=ry1(j), up=has(i,j,0,-1), down=has(i,j,0,1);
    const isExit=(i===far[0]&&j===far[1]), isSpawn=(i===0&&j===ny-1);
    if(up||down){
      if(up && !isExit && R()<(opts.spouts??0.25)) d.falls.push([X0+5,Y0,Y1]);
      else { let sd=R()<0.5; for(const r of [Y1-3,Y1-7]){ d.platforms.push(sd? [r,X0,X0+6] : [r,X1-6,X1]); sd=!sd; } }
    } else {
      if(R()<0.6){ const len=ri(R,3,5), c=ri(R,X0+1,X1-len-1); d.platforms.push([Y1-4,c,c+len-1]); }
      if(!isExit&&!isSpawn&&R()<(opts.water??0.35)){ const a=ri(R,X0+2,X0+4), b=Math.min(X1-2,a+ri(R,3,5)); d.water.push([a,Y1,b,Y1]); }
    }
    if(down && !isExit && R()<(opts.flows??0.55)){
      if(R()<0.5){ d.water.push([X0,Y1,X0+1,Y1]); d.flows.push([X0+2,Y1]); } else { d.water.push([X0+10,Y1,X1,Y1]); d.flows.push([X0+9,Y1]); }
    }
    if(!isSpawn && R()<(opts.enemyChance??0.7)) d.enemies.push([ri(R,X0+1,X1-1),Y1]);
  }
  return d;
}

// ---- hand-made levels ----""")

# ---------------------------------------------------------------- roster (30 rounds)
rep_between("const LEVEL_DEFS=[", "];\nfunction defOf(i){", r"""const LEVEL_DEFS=[
  L_ROUND1,                                                                        // 1
  L_WELL,                                                                          // 2  narrow, down to a pool
  L_TOWER,                                                                         // 3
  ()=>genPassage('CATACOMBS',1,1,'cave',2004),                                     // 4  first winding passages
  L_SPIRE,                                                                         // 5
  L_KEEP,                                                                          // 6  rooms, doors, keys
  ()=>genTower('NARROW PASS',0.5,3,'ice',1007),                                    // 7
  ()=>genPassage('THE CORRIDOR',3,0.5,'stone',2008,{water:0.5}),                   // 8  half-height tunnel going right
  ()=>genPassage('WINDING WAY',2,2,'forest',2009),                                 // 9
  L_HALLS,                                                                         // 10
  ()=>genPassage('THE SHAFT',0.5,4,'ocean',2011,{flows:0.8,spouts:0.35}),          // 11 a single shaft, water pouring down
  ()=>genCave('DEEP CAVE',1,8,'cave',1008),                                        // 12
  ()=>genJumps('STEPPING STONES',2,1,'ocean',1009,{dir:'right'}),                  // 13
  ()=>genPassage('SEWERS',3,1,'ocean',2014,{water:0.7,flows:0.8}),                 // 14
  ()=>genMaze('THE LABYRINTH',2,2,'stone',1010,{roomW:10,roomH:6,doors:2,water:0.15}),
  ()=>genTower('TURRETS',1,8,'ember',1011,{falls:4,merlons:true}),                 // 16
  ()=>genPassage('AQUEDUCT',1,3,'ice',2017,{flows:0.9,water:0.5,spouts:0.4}),      // 17
  ()=>genMaze('FLOODED VAULT',1,2,'ocean',1012,{roomW:9,roomH:6,water:0.6,falls:0.25,doors:1}),
  ()=>genHall('THE LONG HALL',8,'sunset',1013),                                    // 19
  ()=>genPassage('SNAKE PIT',2,3,'grape',2020),                                    // 20
  ()=>genCave('CRYSTAL CAVERN',2,3,'ice',1014),                                    // 21
  ()=>genJumps('SKY BRIDGES',3,1,'forest',1015,{dir:'right'}),                     // 22
  ()=>genMaze('THE DUNGEON',2,2,'cave',1016,{roomW:7,roomH:5,doors:3,loops:0.1}),  // 23
  ()=>genPassage('UNDERCROFT',4,1,'cave',2024,{water:0.4}),                        // 24 long low tunnels
  ()=>genJumps('THE CHASM',1,8,'grape',1017,{dir:'up'}),                           // 25
  ()=>genMaze('GREAT LABYRINTH',3,3,'stone',1018,{roomW:10,roomH:6,doors:3,water:0.1,falls:0.1,loops:0.2}),
  ()=>genTower('THE CATHEDRAL',2,4,'ember',1019,{falls:5}),                        // 27
  ()=>genPassage('WARRENS',3,3,'sunset',2028,{spouts:0.3}),                        // 28
  ()=>genMaze('THE WORLD',8,8,'grape',1020,{roomW:14,roomH:12,doors:3,water:0.15,falls:0.12,loops:0.25,enemies:40}),
  ()=>genPassage('THE DEEP WARREN',4,4,'ember',2030,{flows:0.6,spouts:0.3}),       // 30 64 passage cells
];
function defOf(i){""")

# level names/sizes for the selector (generators are cheap and seeded)
rep("const KEY_COLORS={1:'#f8d800',2:'#c8d8ff',3:'#ff7070',4:'#80ff80'};",
    "const KEY_COLORS={1:'#f8d800',2:'#c8d8ff',3:'#ff7070',4:'#80ff80'};\nconst LEVEL_INFO=LEVEL_DEFS.map((e,i)=>{ const d=defOf(i); return {name:d.name,size:d.sw+'x'+d.sh}; });")

# ---------------------------------------------------------------- makeLevel: fractional height, rock fill, flows
rep("  const cols=Math.round(def.sw*32), rows=2+def.sh*26;\n  const grid=[]; for(let r=0;r<rows;r++) grid.push(new Array(cols).fill('.'));\n  const inb=",
    "  const cols=Math.round(def.sw*32), rows=2+Math.round(def.sh*26);\n  const grid=[]; for(let r=0;r<rows;r++) grid.push(new Array(cols).fill('.'));\n  const inb=")
rep("  for(const [g0,g1] of def.gaps){ fill(g0,2,g1,2,'.'); fill(g0,rows-1,g1,rows-1,'.'); }\n  for(const [r,c0,c1] of def.platforms) fill(c0,r,c1,r,'#');",
    "  for(const [g0,g1] of def.gaps){ fill(g0,2,g1,2,'.'); fill(g0,rows-1,g1,rows-1,'.'); }\n  if(def.rock) fill(2,3,cols-3,rows-2,'W');\n  for(const [r,c0,c1] of def.platforms) fill(c0,r,c1,r,'#');")
rep("  for(const [c,r0,r1] of def.falls) fill(c,r0,c,r1,'F',true);",
    """  for(const [c,r0,r1] of def.falls) fill(c,r0,c,r1,'F',true);
  // falling water: pours from a start cell straight down through air until it meets something, then puddles
  for(const [c,r0] of (def.flows||[])){ let r=r0; while(inb(c,r) && (grid[r][c]==='.'||grid[r][c]==='f')){ grid[r][c]='f'; r++; }
    if(inb(c,r) && grid[r][c]!=='w' && r-1>r0){ for(let cc=c-1;cc<=c+1;cc++) if(inb(cc,r-1) && (grid[r-1][cc]==='.'||grid[r-1][cc]==='f')) grid[r-1][cc]='w'; } }""")

# ---------------------------------------------------------------- physics + bubbles in falling water
rep("  if(e.inFall) e.vy=Math.max(e.vy-0.5,-4.4);                 // waterfall spout: launched upward",
    "  e.inFlow = mid==='f';\n  if(e.inFall) e.vy=Math.max(e.vy-0.5,-4.4);                 // waterfall spout: launched upward\n  else if(e.inFlow) e.vy=Math.min(e.vy+0.3,3.6);              // falling water: swept downward")
rep("    if(tileAt(col(b.x),row(b.y))==='F') b.vy=Math.max(b.vy-0.3,-2.4);",
    "    const bt=tileAt(col(b.x),row(b.y)); if(bt==='F') b.vy=Math.max(b.vy-0.3,-2.4); else if(bt==='f') b.vy=Math.min(b.vy+0.2,1.6);")

# ---------------------------------------------------------------- drawing: falling water, rock shading, minimap colour
rep("    const t=level.grid[r][c]; if(t!=='w'&&t!=='F') continue; const x=c*TILE, y=r*TILE;\n    if(t==='w'){",
    "    const t=level.grid[r][c]; if(t!=='w'&&t!=='F'&&t!=='f') continue; const x=c*TILE, y=r*TILE;\n    if(t==='f'){\n      ctx.fillStyle='rgba(90,170,255,0.32)'; ctx.fillRect(x,y,TILE,TILE);\n      ctx.fillStyle='rgba(235,250,255,0.85)'; const o=(frameCount*3+c*5)%8; ctx.fillRect(x+2,y+o,1,2); ctx.fillRect(x+5,y+(o+4)%8,1,2); ctx.fillRect(x+3,y+(o+6)%8,1,1);\n    } else if(t==='w'){")
rep("      if(tileAt(c,r-1)!=='w'){ const ph=Math.sin(frameCount*0.08+c*0.9)>0?0:1; ctx.fillStyle='rgba(210,245,255,0.85)'; ctx.fillRect(x,y+ph,TILE,1); }",
    "      const above=tileAt(c,r-1); if(above!=='w'&&above!=='f'){ const ph=Math.sin(frameCount*0.08+c*0.9)>0?0:1; ctx.fillStyle='rgba(210,245,255,0.85)'; ctx.fillRect(x,y+ph,TILE,1); }")
rep("    m.fillStyle= t==='w'?'#2860e0' : t==='F'?'#80c8ff' : t==='D'?'#c08040' : pal.Y; m.fillRect(c,r-2,1,1); }",
    "    m.fillStyle= t==='w'?'#2860e0' : (t==='F'||t==='f')?'#80c8ff' : t==='D'?'#c08040' : (t==='W'&&c>1&&c<cols-2&&r>2&&r<rows-1)?pal.mid : pal.Y; m.fillRect(c,r-2,1,1); }")
# rock interiors: buried wall tiles are drawn flat and dark so only the carved surfaces look like brickwork
rep("    else g.drawImage(brick,c*TILE,r*TILE);\n  }",
    """    else if(level.grid[r][c]==='W' && solidAt(c-1,r)&&solidAt(c+1,r)&&solidAt(c,r-1)&&solidAt(c,r+1)&&solidAt(c-1,r-1)&&solidAt(c+1,r-1)&&solidAt(c-1,r+1)&&solidAt(c+1,r+1)){ g.fillStyle=pal.dark; g.fillRect(c*TILE,r*TILE,TILE,TILE); g.fillStyle=pal.mid; if(((c*7+r*13)%5)===0) g.fillRect(c*TILE+2,r*TILE+3,2,1); }
    else g.drawImage(brick,c*TILE,r*TILE);
  }""")
# shadows only for surface tiles (buried rock would just paint over itself)
rep("  const isBrick=(c,r)=> solidAt(c,r) && c>=2 && c<=cols-3;",
    "  const isBrick=(c,r)=> solidAt(c,r) && c>=2 && c<=cols-3;\n  const isSurface=(c,r)=> isBrick(c,r) && !(solidAt(c+1,r)&&solidAt(c,r+1)&&solidAt(c+1,r+1));")
rep("  for(let r=2;r<rows;r++) for(let c=2;c<=cols-3;c++) if(isBrick(c,r)) g.fillRect(c*TILE+4,r*TILE+4,TILE,TILE);\n  g.fillStyle=pal.mid;\n  for(let r=2;r<rows;r++) for(let c=2;c<=cols-3;c++) if(isBrick(c,r)) g.fillRect(c*TILE+2,r*TILE+2,TILE,TILE);",
    "  for(let r=2;r<rows;r++) for(let c=2;c<=cols-3;c++) if(isSurface(c,r)) g.fillRect(c*TILE+4,r*TILE+4,TILE,TILE);\n  g.fillStyle=pal.mid;\n  for(let r=2;r<rows;r++) for(let c=2;c<=cols-3;c++) if(isSurface(c,r)) g.fillRect(c*TILE+2,r*TILE+2,TILE,TILE);")

# ---------------------------------------------------------------- camera: centre short levels below the HUD
rep("  ty = LH*TILE<=H ? 0 : clamp(ty,0,LH*TILE-H);",
    "  ty = LH*TILE<=H ? (LH*TILE<H-16 ? LH*TILE/2-(16+(H-16)/2) : 0) : clamp(ty,0,LH*TILE-H);")

# ---------------------------------------------------------------- level selector on the title screen
rep("let autofire=false; try{ autofire=localStorage.getItem('bb_autofire')==='1'; }catch(e){}",
    "let autofire=false; try{ autofire=localStorage.getItem('bb_autofire')==='1'; }catch(e){}\nlet selLevel=0; try{ selLevel=clamp(parseInt(localStorage.getItem('bb_level')||'0',10)||0,0,LEVEL_DEFS.length-1); }catch(e){}")
rep("  if(e.code==='Enter' && (state==='title'||state==='gameover')) startGame();",
    """  if(state==='title' && (e.code==='KeyW'||e.code==='ArrowUp'||e.code==='KeyS'||e.code==='ArrowDown')){
    const N=LEVEL_DEFS.length; selLevel=(selLevel+((e.code==='KeyW'||e.code==='ArrowUp')?-1:1)+N)%N; try{ localStorage.setItem('bb_level',String(selLevel)); }catch(err){} }
  if(e.code==='Enter' && (state==='title'||state==='gameover')) startGame(selLevel+1);""")
rep("function startGame(){\n  player=new Player(); round=1;",
    "function startGame(startAt=1){\n  player=new Player(); round=startAt;")
rep_between("  if(state==='title'){\n    ctx.fillStyle='rgba(0,0,0,0.55)';", "    if(!ready) text('LOADING...',128,120,'#ffffff',6,'center');\n  }",
r"""  if(state==='title'){
    ctx.fillStyle='rgba(0,0,0,0.6)'; ctx.fillRect(16,16,W-32,H-32);
    text('BUBBLE BOBBLE',128,34,'#f8e030',12,'center');
    text('PROTOTYPE',128,48,'#ff80c0',6,'center');
    const b=frame('bub_walk',0,1); if(b) ctx.drawImage(b,26,64,24,24);
    const z=frame('zen_walk',0,-1); if(z) ctx.drawImage(z,206,64,24,24);
    text('SELECT LEVEL  W / S',128,62,'#a0a0a0',5,'center');
    const N=LEVEL_INFO.length, show=8, first=clamp(selLevel-3,0,Math.max(0,N-show));
    for(let k=0;k<show && first+k<N;k++){ const i=first+k, y=76+k*12, sel=i===selLevel;
      if(sel){ ctx.fillStyle='rgba(255,255,255,0.14)'; ctx.fillRect(52,y-6,152,12); }
      text(String(i+1).padStart(2,'0')+'  '+LEVEL_INFO[i].name,56,y,sel?'#40ff40':'#ffffff',6,'left');
      text(LEVEL_INFO[i].size,200,y,sel?'#40ff40':'#808080',5,'right'); }
    text('A/D MOVE   SPACE JUMP (HOLD = BOUNCE)   E BUBBLE',128,180,'#ffffff',5,'center');
    text('F AUTOFIRE: '+(autofire?'ON':'OFF')+'   M MUTE   P PAUSE',128,192,'#a0a0a0',5,'center');
    if((frameCount>>4)&1) text('PRESS ENTER',128,208,'#40ff40',7,'center');
    if(!ready) text('LOADING...',128,120,'#ffffff',6,'center');
  }""")

open(p, 'w', encoding='utf-8').write(s)
print('passages patched OK')
