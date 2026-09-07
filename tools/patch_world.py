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

# =====================================================================================
# 1. Level toolkit: palettes, tile types, hand-made levels, generators, 20-level roster
# =====================================================================================
rep_between("// ===================== levels =====================",
            "function tileAt(c,r){ if(c<0||c>=LW) return 'W'; if(r<0||r>=LH) return '.'; return level.grid[r][c]; }",
r"""// ===================== levels =====================
// Tiles: W hard wall  # brick (thin bricks are jump-through)  D locked door (hard until its key is taken)
//        w water (swim, slow)  F waterfall spout (strong updraft that launches you)  . air
// A level def has sw/sh (size in screens; sw may be 0.5 for a narrow diorama), and lists of
// platforms [row,c0,c1], walls [col,r0,r1], blocks/water/doors rects [c0,r0,c1,r1(,id)], falls [col,r0,r1],
// gaps [c0,c1] cut into ceiling+floor (wrap-around), clears (rects forced to air), keys [col,row,id],
// spawn/exit/enemies [col,row]. Levels can also be generator functions (seeded, so they are stable).
const PALETTES={
  sunset:{Y:'#f8d800',O:'#f87800',M:'#e82868',dark:'#780000',mid:'#a80000',border:'#6a0000',borderMid:'#8a0000'},
  ocean: {Y:'#58b8ff',O:'#2068e0',M:'#c8f4ff',dark:'#0c1a5a',mid:'#183890',border:'#0a1448',borderMid:'#142468'},
  forest:{Y:'#58e058',O:'#20a030',M:'#ecff90',dark:'#0a3c10',mid:'#146020',border:'#08300c',borderMid:'#0f4a14'},
  grape: {Y:'#d070ff',O:'#8838d0',M:'#ffd0ff',dark:'#2c0850',mid:'#48147a',border:'#22083e',borderMid:'#361060'},
  stone: {Y:'#b8b8cc',O:'#707090',M:'#ecedf8',dark:'#1c1c2c',mid:'#34344c',border:'#161624',borderMid:'#26263c'},
  ember: {Y:'#ff9a40',O:'#c84418',M:'#ffe890',dark:'#3c1000',mid:'#6c2200',border:'#2c0c00',borderMid:'#4c1800'},
  cave:  {Y:'#9a7a58',O:'#644838',M:'#d4b890',dark:'#161008',mid:'#2a2014',border:'#120c04',borderMid:'#22180a'},
  ice:   {Y:'#a8ecff',O:'#4898e0',M:'#ffffff',dark:'#0e3060',mid:'#1e5090',border:'#0c2850',borderMid:'#184070'},
};
function rng(seed){ let a=seed>>>0; return ()=>{ a|=0; a=a+0x6D2B79F5|0; let t=Math.imul(a^a>>>15,1|a); t=t+Math.imul(t^t>>>7,61|t)^t; return ((t^t>>>14)>>>0)/4294967296; }; }
const ri=(R,a,b)=>a+Math.floor(R()*(b-a+1));
function blankDef(name,sw,sh,pal){ return {name,sw,sh,pal,gaps:[],platforms:[],walls:[],blocks:[],water:[],falls:[],doors:[],clears:[],keys:[],enemies:[],spawn:null,exit:null}; }

// ---- generators ----
// Tower: overlapping zig-zag ledges climbing to a top shelf; waterfall spouts give shortcuts up.
function genTower(name,sw,sh,pal,seed,opts={}){
  const R=rng(seed), d=blankDef(name,sw,sh,pal); const cols=Math.round(sw*32), rows=2+sh*26, L=2, Rt=cols-3, iw=cols-4;
  const lo=Math.ceil(iw*0.55), hi=Math.floor(iw*0.7);
  let side=0;
  for(let r=rows-5;r>=10;r-=4){
    const len=ri(R,lo,hi);
    d.platforms.push(side? [r,Rt-len+1,Rt] : [r,L,L+len-1]);
    if(iw>=28 && R()<0.45){ const m=ri(R,3,6), c=ri(R,L+4,Rt-4-m); d.platforms.push([r-2,c,c+m-1]); }
    if(opts.merlons && R()<0.5){ const c=side? Rt-len+1+ri(R,1,3) : L+len-2-ri(R,1,3); d.blocks.push([c,r-1,c,r-1]); }
    side^=1;
  }
  d.platforms.push([6,L,L+Math.min(8,iw-2)]); d.exit=[L+2,4]; d.spawn=[L+1,rows-2];
  const nf=opts.falls??Math.max(1,Math.floor(sh/2));
  for(let i=0;i<nf;i++){ const base=ri(R,14,rows-6), c=ri(R,L+2,Rt-2), top=Math.max(7,base-ri(R,10,16)); d.falls.push([c,top,base]); }
  const n=opts.enemies||Math.max(4,Math.round(sh*3.5*Math.max(1,sw)));
  for(let i=0;i<n;i++){ const pl=d.platforms[ri(R,0,d.platforms.length-2)]; d.enemies.push([ri(R,pl[1],pl[2]),pl[0]-1]); }
  return d;
}
// Cave: rough walls, descending ledges, pools, a locked floor-hatch near the bottom, exit at the very bottom.
function genCave(name,sw,sh,pal,seed,opts={}){
  const R=rng(seed), d=blankDef(name,sw,sh,pal); const cols=Math.round(sw*32), rows=2+sh*26, L=2, Rt=cols-3, iw=cols-4;
  for(let r=5;r<rows-4;r+=ri(R,2,4)){ const w=ri(R,1,3), h=ri(R,0,1); if(R()<0.5) d.blocks.push([L,r,L+w-1,r+h]); else d.blocks.push([Rt-w+1,r,Rt,r+h]); }
  const lo=Math.ceil(iw*0.5), hi=Math.floor(iw*0.68);
  let side=R()<0.5?0:1;
  for(let r=10;r<=rows-9;r+=ri(R,4,5)){ const len=ri(R,lo,hi); d.platforms.push(side? [r,Rt-len+1,Rt] : [r,L,L+len-1]); side^=1; }
  const pools=Math.max(1,Math.floor(sh/2));
  for(let i=0;i<pools;i++){ const pl=d.platforms[ri(R,1,d.platforms.length-2)]; if(pl[2]-pl[1]<9) continue; const a=pl[1]+2, b=pl[2]-2;
    d.blocks.push([a-1,pl[0]-2,a-1,pl[0]-1],[b+1,pl[0]-2,b+1,pl[0]-1]); d.water.push([a,pl[0]-2,b,pl[0]-1]); }
  d.platforms.push([6,L,L+6]); d.spawn=[L+1,5];
  const hatchRow=rows-7; d.platforms.push([hatchRow,L,Rt]);
  const gap=ri(R,L+4,Rt-6); d.doors.push([gap,hatchRow,gap+1,hatchRow,1]);
  const kp=d.platforms[ri(R,1,Math.max(1,d.platforms.length-4))]; d.keys.push([ri(R,kp[1],kp[2]),kp[0]-1,1]);
  d.water.push([L+1,rows-3,Math.floor(cols/2)-2,rows-2]); d.blocks.push([Math.floor(cols/2)-1,rows-3,Math.floor(cols/2)-1,rows-2]);
  d.exit=[Rt-4,rows-3];
  d.falls.push([Rt-1,9,hatchRow-1]);   // a spout along the right wall to get back up
  const n=opts.enemies||Math.max(4,Math.round(sh*3*Math.max(1,sw)));
  for(let i=0;i<n;i++){ const pl=d.platforms[ri(R,0,d.platforms.length-1)]; d.enemies.push([ri(R,pl[1],pl[2]),pl[0]-1]); }
  return d;
}
// Maze: a grid of rooms joined by a spanning tree (plus a few loops); locked doors on true bridges with keys on the near side.
function genMaze(name,sw,sh,pal,seed,opts={}){
  const R=rng(seed), d=blankDef(name,sw,sh,pal); const cols=Math.round(sw*32), rows=2+sh*26;
  const roomW=opts.roomW||10, roomH=opts.roomH||6, Wt=cols-4, Ht=rows-4;
  const nx=Math.max(1,Math.floor((Wt+1)/(roomW+1))), ny=Math.max(1,Math.floor((Ht+1)/(roomH+1)));
  const split=(total,n)=>{ const inner=total-(n-1), base=Math.floor(inner/n); let rem=inner-base*n; const out=[]; let st=0; for(let i=0;i<n;i++){ const w=base+(rem>0?1:0); if(rem>0) rem--; out.push([st,st+w-1]); st+=w+1; } return out; };
  const cxs=split(Wt,nx).map(([a,b])=>[a+2,b+2]), rys=split(Ht,ny).map(([a,b])=>[a+3,b+3]);
  for(let i=0;i<nx-1;i++) d.walls.push([cxs[i][1]+1,3,rows-2]);
  for(let j=0;j<ny-1;j++) d.platforms.push([rys[j][1]+1,2,cols-3]);
  const reach=[];
  for(let i=0;i<nx;i++){ reach.push([]); for(let j=0;j<ny;j++){ const [x0,x1]=cxs[i],[y0,y1]=rys[j], h=y1-y0+1; let span=[x0,x1];
    if(h>6){ let sd=R()<0.5; for(let r=y1-3;r>y0+1;r-=4){ const len=Math.max(3,Math.floor((x1-x0+1)*ri(R,45,65)/100)); const seg= sd? [r,x0,x0+len-1] : [r,x1-len+1,x1]; d.platforms.push(seg); span=[seg[1],seg[2]]; sd=!sd; } }
    else if(h>=5 && R()<0.4){ const len=ri(R,2,4), c=ri(R,x0+1,Math.max(x0+1,x1-len-1)); if(c+len-1<x1) d.platforms.push([y0+2,c,c+len-1]); }
    reach[i].push(span); } }
  const key=(i,j)=>i+','+j, seen=new Set(), edges=[]; const spawnRoom=[0,ny-1], exitRoom=opts.exitRoom||[nx-1,0];
  const stack=[spawnRoom.slice()]; seen.add(key(...spawnRoom));
  while(stack.length){ const [i,j]=stack[stack.length-1]; const nb=[[i+1,j,'h'],[i-1,j,'h'],[i,j+1,'v'],[i,j-1,'v']].filter(([a,b])=>a>=0&&a<nx&&b>=0&&b<ny&&!seen.has(key(a,b)));
    if(!nb.length){ stack.pop(); continue; } const [a,b,dir]=nb[ri(R,0,nb.length-1)]; seen.add(key(a,b)); edges.push({a:[i,j],b:[a,b],dir,tree:true}); stack.push([a,b]); }
  const same=(e,p2,q)=>(e.a[0]===p2[0]&&e.a[1]===p2[1]&&e.b[0]===q[0]&&e.b[1]===q[1])||(e.a[0]===q[0]&&e.a[1]===q[1]&&e.b[0]===p2[0]&&e.b[1]===p2[1]);
  const loops=opts.loops??0.15;
  for(let i=0;i<nx;i++) for(let j=0;j<ny;j++){
    if(i<nx-1 && R()<loops && !edges.some(e=>same(e,[i,j],[i+1,j]))) edges.push({a:[i,j],b:[i+1,j],dir:'h',tree:false});
    if(j<ny-1 && R()<loops && !edges.some(e=>same(e,[i,j],[i,j+1]))) edges.push({a:[i,j],b:[i,j+1],dir:'v',tree:false}); }
  for(const e of edges){
    if(e.dir==='h'){ const lo=e.a[0]<e.b[0]?e.a:e.b, wallC=cxs[lo[0]][1]+1, y1=rys[lo[1]][1]; e.cells=[wallC,y1-2,wallC,y1]; }
    else { const up=e.a[1]<e.b[1]?e.a:e.b, floorR=rys[up[1]][1]+1, lower=[up[0],up[1]+1]; let [sa,sb]=reach[lower[0]][lower[1]];
      const isExit=(up[0]===exitRoom[0]&&up[1]===exitRoom[1]); if(isExit) sa=Math.max(sa,cxs[up[0]][0]+4);
      sa=Math.max(sa,cxs[up[0]][0]+1); sb=Math.min(sb,cxs[up[0]][1]-3); if(sb<sa){ sa=cxs[up[0]][0]+4; sb=cxs[up[0]][1]-3; }
      const c=ri(R,sa,Math.max(sa,sb)); e.cells=[c,floorR,c+2,floorR]; }
    d.clears.push(e.cells);
  }
  d.spawn=[cxs[0][0]+1,rys[ny-1][1]]; d.exit=[cxs[exitRoom[0]][0]+1,rys[exitRoom[1]][1]-1];
  const adj=(closed)=>{ const m={}; for(const e of edges){ if(closed.includes(e)) continue; (m[key(...e.a)]=m[key(...e.a)]||[]).push(key(...e.b)); (m[key(...e.b)]=m[key(...e.b)]||[]).push(key(...e.a)); } return m; };
  const reachable=(closed)=>{ const m=adj(closed), st=[key(...spawnRoom)], out=new Set(st); while(st.length){ const k=st.pop(); for(const n2 of (m[k]||[])) if(!out.has(n2)){ out.add(n2); st.push(n2); } } return out; };
  const placed=[]; const cand=edges.filter(e=>e.tree).sort(()=>R()-0.5);
  for(const e of cand){ if(placed.length>=(opts.doors||0)) break; const side=reachable([...placed,e]); if(side.has(key(...exitRoom))||side.size<2) continue;
    const id=placed.length+1; e.doorId=id; placed.push(e);
    const roomsSide=[...side].filter(k=>k!==key(...spawnRoom)); const pool=roomsSide.length?roomsSide:[...side]; const kr=pool[ri(R,0,pool.length-1)].split(',').map(Number);
    const [x0,x1]=cxs[kr[0]], y1=rys[kr[1]][1]; d.keys.push([ri(R,x0+1,x1-1),y1,id]); }
  for(const e of placed) d.doors.push([...e.cells,e.doorId]);
  for(let i=0;i<nx;i++) for(let j=0;j<ny;j++){ const [x0,x1]=cxs[i],[y0,y1]=rys[j]; const isSpawn=(i===0&&j===ny-1), isExit=(i===exitRoom[0]&&j===exitRoom[1]);
    if(!isSpawn&&!isExit&&R()<(opts.water||0)) d.water.push([x0,y1-1,x1,y1]);
    if(!isExit&&R()<(opts.falls||0)) d.falls.push([ri(R,x0+1,x1-1),y0,y1]); }
  const n=opts.enemies||Math.round(nx*ny*0.8);
  for(let k=0;k<n;k++){ const i=ri(R,0,nx-1), j=ri(R,0,ny-1); if(i===0&&j===ny-1) continue; d.enemies.push([ri(R,cxs[i][0]+1,cxs[i][1]-1),rys[j][1]]); }
  return d;
}
// Jumps: a chain of small platforms over a water pit; fall in and you swim back to the ladder. dir 'right' or 'up'.
function genJumps(name,sw,sh,pal,seed,opts={}){
  const R=rng(seed), d=blankDef(name,sw,sh,pal); const cols=Math.round(sw*32), rows=2+sh*26, dir=opts.dir||'right';
  d.water.push([2,rows-3,cols-3,rows-2]);
  let c=3, r=rows-6; d.platforms.push([r,2,7]); d.spawn=[3,r-1];
  let last=[r,2,7];
  for(let guard=0;guard<400;guard++){
    const len=ri(R,2,3); let nc,nr;
    if(dir==='right'){ nc=last[2]+ri(R,3,4)+1; nr=clamp(r+ri(R,-3,2),8,rows-7); if(nc+len>cols-4) break; }
    else { const dx=ri(R,3,4)+len, goRight=(last[1]+dx+len<cols-4) && (last[1]-dx<3 || R()<0.5); nc= goRight? last[2]+ri(R,3,4)+1 : last[1]-ri(R,3,4)-len; nr=r-ri(R,3,4); if(nr<8) break; nc=clamp(nc,3,cols-4-len); }
    const seg=[nr,nc,nc+len-1]; d.platforms.push(seg); last=seg; c=nc; r=nr;
  }
  d.platforms.push([last[0],last[1],last[1]+3]); d.exit=[last[1]+1,last[0]-2];
  for(let rr=rows-7;rr>rows-20;rr-=4) d.platforms.push([rr,2,ri(R,3,5)]);        // rescue ladder by the left wall
  for(let i=0;i<Math.max(2,Math.round(sw*sh*2));i++){ const c2=ri(R,6,cols-8); d.falls.push([c2,ri(R,10,rows-14),rows-4]); }   // spouts out of the pit
  const n=opts.enemies||Math.max(4,Math.round(d.platforms.length*0.35));
  for(let i=0;i<n;i++){ const pl=d.platforms[ri(R,1,d.platforms.length-1)]; d.enemies.push([ri(R,pl[1],pl[2]),pl[0]-1]); }
  return d;
}
// Hall: a long castle walk - battlement platforms, towers with doorways, moats and spouts.
function genHall(name,sw,pal,seed,opts={}){
  const R=rng(seed), d=blankDef(name,sw,1,pal); const cols=Math.round(sw*32), rows=28;
  let c=6;
  while(c<cols-40){
    const t=c+ri(R,24,34); if(t>cols-30) break;
    d.blocks.push([t,3,t+1,26]); d.clears.push([t,24,t+1,26]); d.clears.push([t,12,t+1,14]);    // tower with a ground door and a high door
    d.platforms.push([15,t-8,t-1],[15,t+2,t+9],[19,t-14,t-9],[23,t-6,t-1]);
    d.platforms.push([11,t+3,t+12]);
    if(R()<0.6){ const m0=c+ri(R,4,8), m1=Math.min(t-12,m0+ri(R,5,8)); if(m1>m0+2) d.water.push([m0,25,m1,26]); }
    if(R()<0.6) d.platforms.push([ri(R,6,8),c+ri(R,2,6),c+ri(R,10,14)]);
    d.falls.push([t+ri(R,12,16),8,26]);
    c=t+2;
  }
  d.platforms.push([22,cols-10,cols-4],[18,cols-14,cols-8],[14,cols-10,cols-4],[10,cols-14,cols-8],[6,cols-10,cols-3]);
  d.spawn=[3,26]; d.exit=[cols-6,4];
  const n=opts.enemies||Math.round(sw*3);
  for(let i=0;i<n;i++){ const pl=d.platforms[ri(R,0,d.platforms.length-1)]; d.enemies.push([ri(R,pl[1],pl[2]),pl[0]-1]); }
  for(let i=0;i<Math.round(sw);i++) d.enemies.push([ri(R,8,cols-8),26]);
  return d;
}

// ---- hand-made levels ----
const L_ROUND1={ name:'ROUND 1', sw:1, sh:1, pal:'sunset', gaps:[[9,12],[19,22]],
   platforms:[[7,5,12],[7,19,26],[12,5,13],[12,18,26],[17,5,14],[17,17,26],[22,2,6],[22,9,11],[22,20,22],[22,25,29]],
   walls:[[5,8,11],[26,8,11],[5,13,16],[26,13,16]],
   spawn:[4,26], exit:[6,5], enemies:[[10,4],[21,4],[14,4],[17,4],[7,4],[24,4]] };
const L_TOWER={ name:'THE TOWER', sw:1, sh:2, pal:'ocean', gaps:[[12,19]],
   platforms:[[6,4,11],[6,20,27],[11,13,18],[15,2,9],[15,22,29],[19,11,20],[23,5,12],[23,19,26],[27,2,8],[27,23,29],
              [31,12,19],[35,4,11],[35,20,27],[39,2,9],[39,22,29],[43,13,18],[47,6,12],[47,19,25],[49,2,5],[49,26,29]],
   spawn:[4,52], exit:[4,4], enemies:[[10,4],[21,4],[15,9],[8,21],[23,21],[15,29],[15,41],[8,45],[23,45]] };
const L_WELL={ name:'THE WELL', sw:0.5, sh:2, pal:'cave',
   platforms:[[6,2,7],[10,8,13],[14,2,7],[18,8,13],[22,2,6],[26,9,13],[30,2,7],[34,8,13],[38,2,6],[42,8,13],[46,2,7]],
   blocks:[[2,8,3,8],[12,13,13,13],[2,24,4,24],[13,20,13,21],[9,50,9,52]],
   water:[[2,50,8,52]], falls:[[12,36,49]],
   spawn:[3,5], exit:[11,51], enemies:[[5,9],[10,13],[4,21],[10,29],[4,37],[10,45]] };
const L_SPIRE={ name:'THE SPIRE', sw:1, sh:3, pal:'forest', gaps:[[12,19]],
   platforms:[[6,4,11],[6,20,27],[10,13,18],[14,2,8],[14,23,29],[18,10,21],[22,2,6],[22,25,29],[26,8,13],[26,18,23],
              [30,2,9],[30,22,29],[34,13,18],[38,4,11],[38,20,27],[42,2,6],[42,14,17],[42,25,29],[46,8,23],[50,2,8],[50,23,29],
              [54,11,20],[58,4,9],[58,22,27],[62,13,18],[66,2,9],[66,22,29],[70,11,20],[74,4,9],[74,22,27]],
   spawn:[4,78], exit:[4,4], enemies:[[10,4],[21,4],[15,8],[15,24],[5,40],[26,40],[15,52],[15,68],[6,56],[25,56],[8,72],[23,72]] };
const L_KEEP={ name:'CASTLE KEEP', sw:1, sh:1, pal:'stone',
   walls:[[13,3,23],[20,3,23]], doors:[[13,24,13,26,1],[20,24,20,26,2]],
   platforms:[[22,2,8],[17,5,12],[12,2,8],[7,5,12],[21,14,19],[16,14,19],[11,14,19],[6,14,19],[22,23,29],[17,21,27],[12,23,29],[7,21,27]],
   keys:[[10,6,1],[16,5,2]], spawn:[3,26], exit:[22,5], enemies:[[6,4],[17,4],[26,4],[6,14],[26,14],[16,18]] };
const L_HALLS={ name:'THE HALLS', sw:2, sh:2, pal:'grape', gaps:[[12,19],[44,51]],
   platforms:[[6,4,13],[6,24,39],[6,50,59],[10,16,21],[10,42,47],[14,2,9],[14,26,37],[14,54,61],[18,12,21],[18,42,51],
              [22,4,9],[22,25,38],[22,54,59],[26,14,19],[26,44,49],[30,2,11],[30,24,39],[30,52,61],[34,14,21],[34,42,49],
              [38,4,9],[38,27,36],[38,54,59],[42,12,19],[42,44,51],[46,2,9],[46,24,39],[46,54,61],[49,13,18],[49,45,50]],
   walls:[[31,10,20],[32,10,20],[31,31,45],[32,31,45]],
   spawn:[4,52], exit:[30,4], enemies:[[10,4],[53,4],[20,8],[43,8],[8,20],[55,20],[31,28],[16,40],[47,40],[31,50],[4,30],[59,30]] };

const LEVEL_DEFS=[
  L_ROUND1,                                                                   // 1  the arcade round
  L_TOWER,                                                                    // 2  two screens tall
  L_WELL,                                                                     // 3  narrow diorama, down into a pool
  L_SPIRE,                                                                    // 4  three tall
  L_KEEP,                                                                     // 5  rooms, two locked doors, two keys
  L_HALLS,                                                                    // 6  2x2 with a spine wall
  ()=>genTower('NARROW PASS',0.5,3,'ice',1007),                              // 7  half-screen tower with a spout
  ()=>genCave('DEEP CAVE',1,8,'cave',1008),                                  // 8  eight screens down, pools, hatch + key
  ()=>genJumps('STEPPING STONES',2,1,'ocean',1009,{dir:'right'}),            // 9  precarious hops over water
  ()=>genMaze('THE LABYRINTH',2,2,'stone',1010,{roomW:10,roomH:6,doors:2,water:0.15}),
  ()=>genTower('TURRETS',1,8,'ember',1011,{falls:4,merlons:true}),           // 11 eight screens up
  ()=>genMaze('FLOODED VAULT',1,2,'ocean',1012,{roomW:9,roomH:6,water:0.6,falls:0.25,doors:1}),
  ()=>genHall('THE LONG HALL',8,'sunset',1013),                              // 13 eight screens long
  ()=>genCave('CRYSTAL CAVERN',2,3,'ice',1014),
  ()=>genJumps('SKY BRIDGES',3,1,'forest',1015,{dir:'right'}),
  ()=>genMaze('THE DUNGEON',2,2,'cave',1016,{roomW:7,roomH:5,doors:3,loops:0.1}),   // 16 close quarters
  ()=>genJumps('THE CHASM',1,8,'grape',1017,{dir:'up'}),                     // 17 climb eight screens on tiny ledges
  ()=>genMaze('GREAT LABYRINTH',3,3,'stone',1018,{roomW:10,roomH:6,doors:3,water:0.1,falls:0.1,loops:0.2}),
  ()=>genTower('THE CATHEDRAL',2,4,'ember',1019,{falls:5}),
  ()=>genMaze('THE WORLD',8,8,'grape',1020,{roomW:14,roomH:12,doors:3,water:0.15,falls:0.12,loops:0.25,enemies:40}),   // 20 vast
];
function defOf(i){ const e=LEVEL_DEFS[i%LEVEL_DEFS.length]; return typeof e==='function'? e() : e; }
const KEY_COLORS={1:'#f8d800',2:'#c8d8ff',3:'#ff7070',4:'#80ff80'};

function makeLevel(def){
  for(const k of ['gaps','platforms','walls','blocks','water','falls','doors','clears','keys','enemies']) if(!def[k]) def[k]=[];
  const cols=Math.round(def.sw*32), rows=2+def.sh*26;
  const grid=[]; for(let r=0;r<rows;r++) grid.push(new Array(cols).fill('.'));
  const inb=(c,r)=>r>=0&&r<rows&&c>=0&&c<cols;
  const fill=(c0,r0,c1,r1,ch,onlyAir=false)=>{ for(let r=r0;r<=r1;r++) for(let c=c0;c<=c1;c++) if(inb(c,r) && (!onlyAir||grid[r][c]==='.')) grid[r][c]=ch; };
  fill(0,2,1,rows-1,'W'); fill(cols-2,2,cols-1,rows-1,'W');
  fill(2,2,cols-3,2,'W'); fill(2,rows-1,cols-3,rows-1,'W');
  for(const [g0,g1] of def.gaps){ fill(g0,2,g1,2,'.'); fill(g0,rows-1,g1,rows-1,'.'); }
  for(const [r,c0,c1] of def.platforms) fill(c0,r,c1,r,'#');
  for(const [c,r0,r1] of def.walls) fill(c,r0,c,r1,'#');
  for(const [c0,r0,c1,r1] of def.blocks) fill(c0,r0,c1,r1,'#');
  for(const [c0,r0,c1,r1] of def.clears) fill(c0,r0,c1,r1,'.');
  const doorIds={};
  for(const [c0,r0,c1,r1,id] of def.doors){ for(let r=r0;r<=r1;r++) for(let c=c0;c<=c1;c++) if(inb(c,r)){ grid[r][c]='D'; doorIds[c+','+r]=id; } }
  for(const [c0,r0,c1,r1] of def.water) fill(c0,r0,c1,r1,'w',true);
  for(const [c,r0,r1] of def.falls) fill(c,r0,c,r1,'F',true);
  const solid=(c,r)=>{ const t=inb(c,r)?grid[r][c]:'W'; return t==='W'||t==='#'||t==='D'; };
  // exit: clear the doorway and make sure something holds it up
  const [ec,er]=def.exit; fill(ec,er,ec+1,er+1,'.'); if(!solid(ec,er+2)||!solid(ec+1,er+2)) fill(ec,er+2,ec+1,er+2,'#');
  // spawn: clear headroom, make sure there is ground
  const [sc,sr]=def.spawn; fill(sc,sr-1,sc+1,sr,'.'); if(!solid(sc,sr+1)) fill(sc,sr+1,sc+1,sr+1,'#');
  const at=([c,r])=>({x:(c+1)*TILE,y:(r+1)*TILE});
  const lift=([c,r])=>{ let g=0; while(g++<rows && (solid(c,r)||solid(c,r-1)||solid(c+1,r))) r--; return [c,r]; };
  const enemies=def.enemies.map(lift).filter(([c,r])=>r>2).map(at);
  const keys=def.keys.map(([c,r,id])=>{ const [c2,r2]=lift([c,r]); return {x:(c2+0.5)*TILE,y:(r2+1)*TILE,id,taken:false}; });
  return { def, cols, rows, grid, pal:PALETTES[def.pal]||PALETTES.sunset, spawn:at(def.spawn), enemies, keys, doorIds,
    exit:{x:ec*TILE, y:er*TILE, w:16, h:16} };
}
function tileAt(c,r){ if(c<0||c>=LW) return 'W'; if(r<0||r>=LH) return '.'; return level.grid[r][c]; }""")

rep("function solidAt(c,r){ const t=tileAt(c,r); return t==='W'||t==='#'; }",
    "function solidAt(c,r){ const t=tileAt(c,r); return t==='W'||t==='#'||t==='D'; }\nconst hard=t=>t==='W'||t==='D';   // never passable, even when rising")

# =====================================================================================
# 2. Level graphics: doors drawn in the static layer; initial level via defOf
# =====================================================================================
rep("""  for(let r=2;r<rows;r++) for(let c=2;c<=cols-3;c++) if(isBrick(c,r)) g.drawImage(brick,c*TILE,r*TILE);
  for(let r=2;r<rows;r+=2){ g.drawImage(bl,0,r*TILE); g.drawImage(br,cols*TILE-16,r*TILE); }
}
level=makeLevel(LEVEL_DEFS[0]); LW=level.cols; LH=level.rows; buildLevel();""",
"""  for(let r=2;r<rows;r++) for(let c=2;c<=cols-3;c++) if(isBrick(c,r)){
    if(level.grid[r][c]==='D'){ const id=level.doorIds[c+','+r]||1; g.fillStyle='#3a2210'; g.fillRect(c*TILE,r*TILE,TILE,TILE); g.fillStyle='#8a5a28'; g.fillRect(c*TILE+1,r*TILE+1,TILE-2,TILE-2); g.fillStyle='#5a3818'; g.fillRect(c*TILE+4,r*TILE+1,1,TILE-2); g.fillStyle=KEY_COLORS[id]||'#f8d800'; g.fillRect(c*TILE+2,r*TILE+3,2,3); g.fillRect(c*TILE+5,r*TILE+3,2,3); }
    else g.drawImage(brick,c*TILE,r*TILE);
  }
  for(let r=2;r<rows;r+=2){ g.drawImage(bl,0,r*TILE); g.drawImage(br,cols*TILE-16,r*TILE); }
}
level=makeLevel(defOf(0)); LW=level.cols; LH=level.rows; buildLevel();
const KEY_IMG=pixmap(["..KKK...",".K...K..",".K...K..","..KKK...","...K....","...KK...","...K....","...KK..."],{K:'#ffffff'});""")

# =====================================================================================
# 3. Physics: water, waterfall updraft, hard doors
# =====================================================================================
rep("""function physicsStep(e){
  e.vy=Math.min(e.vy+GRAV,MAXFALL);""",
"""function physicsStep(e){
  const mid=tileAt(col(e.x),row(e.y-e.h/2));
  e.inWater = mid==='w'; e.inFall = mid==='F';
  if(e.inFall) e.vy=Math.max(e.vy-0.5,-4.4);                 // waterfall spout: launched upward
  else if(e.inWater) e.vy=Math.min(e.vy+0.05,0.8);           // swimming: gentle sink
  else e.vy=Math.min(e.vy+GRAV,MAXFALL);""")
rep("      if(t==='W'||(t==='#'&&!thinAt(c,rHead))){ ny=(rHead+1)*TILE+e.h; e.vy=0; break; }",
    "      if(hard(t)||(t==='#'&&!thinAt(c,rHead))){ ny=(rHead+1)*TILE+e.h; e.vy=0; break; }")
rep("      if(t==='W'){ blocked=true; break; }\n      if(t==='#'){",
    "      if(hard(t)){ blocked=true; break; }\n      if(t==='#'){")

# =====================================================================================
# 4. Player: swim, spout, keys
# =====================================================================================
rep("    this.vx = left&&!right ? -MOVE : right&&!left ? MOVE : 0;",
    "    this.vx = (left&&!right ? -MOVE : right&&!left ? MOVE : 0) * (this.inWater?0.65:1);")
rep("    if(anyPressed(K.jump) && this.onGround){ this.vy=-JUMP_V; this.onGround=false; SFX.jump(); }",
    """    if(anyPressed(K.jump)){
      if(this.onGround){ this.vy=-JUMP_V; this.onGround=false; SFX.jump(); }
      else if(this.inWater){ const atSurface = tileAt(col(this.x),row(this.y-this.h-1))!=='w'; this.vy = atSurface? -JUMP_V*0.9 : -1.7; SFX.jump(); }
    }""")
rep("    if(this.wrapped){ this.wrapped=false; camSnap=true; }",
    """    if(this.wrapped){ this.wrapped=false; camSnap=true; }
    for(const k of level.keys){ if(!k.taken && Math.abs(k.x-this.x)<9 && k.y>this.y-this.h-4 && k.y-8<this.y+4){ k.taken=true; unlockDoors(k.id); } }""")
rep("function enterExit(){",
    """function unlockDoors(id){
  let n=0, sx=0, sy=0;
  for(const k in level.doorIds){ if(level.doorIds[k]!==id) continue; const [c,r]=k.split(',').map(Number); level.grid[r][c]='.'; n++; sx=c*TILE+4; sy=r*TILE+4;
    for(let i=0;i<5;i++) particles.push({type:'dot',x:c*TILE+4,y:r*TILE+4,vx:rnd(-1,1),vy:rnd(-1.5,0),life:25,max:25,color:KEY_COLORS[id]||'#f8d800'}); }
  if(n){ buildLevel(); banner={text:'DOOR OPENED!',t:90}; player.score+=500; addPopup(player.x,player.y-20,'500','#f8e030'); }
  SFX.fruit();
}
function enterExit(){""")

# bubbles ride waterfall spouts
rep("    const targetVy = b.enemy? -0.22 : -0.3;",
    "    const targetVy = b.enemy? -0.22 : -0.3;\n    if(tileAt(col(b.x),row(b.y))==='F') b.vy=Math.max(b.vy-0.3,-2.4);")

# =====================================================================================
# 5. Camera: centre levels narrower than the screen (diorama)
# =====================================================================================
rep("  tx=clamp(tx,0,LW*TILE-W); ty=clamp(ty,0,LH*TILE-H);",
    "  tx = LW*TILE<=W ? (LW*TILE-W)/2 : clamp(tx,0,LW*TILE-W);\n  ty = LH*TILE<=H ? 0 : clamp(ty,0,LH*TILE-H);")

# =====================================================================================
# 6. Rounds: pick def by round, cap enemies sensibly
# =====================================================================================
rep("  level=makeLevel(LEVEL_DEFS[(round-1)%LEVEL_DEFS.length]); LW=level.cols; LH=level.rows; buildLevel();",
    "  level=makeLevel(defOf(round-1)); LW=level.cols; LH=level.rows; buildLevel();")
rep("  const n=Math.min(level.enemies.length*2, 2+round+2*screens);",
    "  const n=Math.max(3,Math.min(level.enemies.length, level.def.sw*level.def.sh>=16 ? 40 : Math.round(3+round*0.5+screens*2.5)));")

# =====================================================================================
# 7. Render: keys, water and spouts
# =====================================================================================
rep("""    drawExit(cx,cy);
    for(const f of fruits){""",
"""    drawExit(cx,cy);
    for(const k of level.keys){ if(k.taken) continue; const bob=Math.round(Math.sin(frameCount*0.1+k.x)*1.5); ctx.save(); ctx.translate(Math.round(k.x-4),Math.round(k.y-8+bob)); ctx.drawImage(KEY_IMG,0,0); ctx.globalCompositeOperation='source-atop'; ctx.fillStyle=KEY_COLORS[k.id]||'#f8d800'; ctx.fillRect(0,0,8,8); ctx.restore(); if(((frameCount>>3)&1)) { ctx.fillStyle='#ffffff'; ctx.fillRect(Math.round(k.x-4)+(frameCount>>2)%7,Math.round(k.y-9+bob),1,1); } }
    for(const f of fruits){""")
rep("""    player.draw();
    for(const p of particles){""",
"""    player.draw();
    drawFluids(cx,cy);
    for(const p of particles){""")
rep("function render(){",
"""function drawFluids(cx,cy){
  const c0=Math.max(0,col(cx)), c1=Math.min(LW-1,col(cx+W)+1), r0=Math.max(0,row(cy)), r1=Math.min(LH-1,row(cy+H)+1);
  for(let r=r0;r<=r1;r++) for(let c=c0;c<=c1;c++){
    const t=level.grid[r][c]; if(t!=='w'&&t!=='F') continue; const x=c*TILE, y=r*TILE;
    if(t==='w'){
      ctx.fillStyle='rgba(40,110,255,0.42)'; ctx.fillRect(x,y,TILE,TILE);
      if(tileAt(c,r-1)!=='w'){ const ph=Math.sin(frameCount*0.08+c*0.9)>0?0:1; ctx.fillStyle='rgba(210,245,255,0.85)'; ctx.fillRect(x,y+ph,TILE,1); }
    } else {
      ctx.fillStyle='rgba(120,200,255,0.28)'; ctx.fillRect(x,y,TILE,TILE);
      ctx.fillStyle='rgba(255,255,255,0.8)';
      const o=(frameCount*3+c*5)%8, o2=(o+4)%8; ctx.fillRect(x+2,y+7-o,1,1); ctx.fillRect(x+5,y+7-o2,1,1); ctx.fillRect(x+3,y+7-((o+2)%8),1,1);
    }
  }
}
function render(){""")

open(p, 'w', encoding='utf-8').write(s)
print('patched OK')
