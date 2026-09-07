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

# ------------------------------------------------------------------ enemy types, class, projectiles
rep_between("class Enemy{", "\n\n// ===================== bubbles =====================", r"""// Every monster from the sheet, each with its own way of moving and (for some) attacking.
// Walkers use the platform physics; Monsta bounces around like a ball; Pulpul hovers toward Bub; Banebou is a spring.
const ENEMY_TYPES={
  zen:      {spr:'zen',      kind:'walker', speed:0.55},
  mighta:   {spr:'mighta',   kind:'walker', speed:0.5,  shoot:'rock',   cd:[150,260], throwSpr:true},
  monsta:   {spr:'monsta',   kind:'bouncer',speed:0.8},
  pulpul:   {spr:'pulpul',   kind:'hover',  speed:0.5},
  banebou:  {spr:'banebou',  kind:'hopper', speed:0.6},
  invader:  {spr:'invader',  kind:'walker', speed:0.5,  shoot:'laser',  cd:[110,200]},
  hidegons: {spr:'hidegons', kind:'walker', speed:0.55, shoot:'fire',   cd:[120,220]},
  drunk:    {spr:'drunk',    kind:'walker', speed:0.6,  shoot:'bottle', cd:[140,240], throwSpr:true},
};
const TYPE_ORDER=['zen','mighta','monsta','pulpul','banebou','invader','hidegons','drunk'];
function typePool(){ const n=Math.min(TYPE_ORDER.length, 1+Math.floor((round-1)/2)); return TYPE_ORDER.slice(0,n); }
let shots=[];
class Enemy{
  constructor(x,y,type){
    this.type=ENEMY_TYPES[type]||ENEMY_TYPES.zen;
    this.x=x; this.y=y; this.w=10; this.h=15; this.vx=0; this.vy=0; this.dir=Math.random()<0.5?-1:1;
    this.speed=this.type.speed+round*0.02; this.state='spawning'; this.timer=60; this.trapped=false; this.angry=false; this.think=60; this.onGround=false; this.anim=0; this.edgeFlag=false; this.hitWall=false;
    this.shotCd=this.type.cd? rnd(this.type.cd[0],this.type.cd[1]) : 0; this.throwT=0; this.fvy=(Math.random()<0.5?-1:1)*0.6; this.hop=0; this.tyDir=0;
  }
  get spd(){ return this.speed*(this.angry?1.7:1); }
  update(){
    if(this.state==='spawning'){ this.timer--; if(this.timer<=0) this.state='alive'; return; }
    if(this.state!=='alive'||this.trapped) return;
    this.anim++; if(this.throwT>0) this.throwT--;
    const k=this.type.kind;
    if(k==='bouncer') this.moveBouncer(); else if(k==='hover') this.moveHover(); else this.moveWalker(k==='hopper');
    if(this.type.shoot) this.tryShoot();
  }
  moveWalker(hopper){
    this.hitWall=false; this.vx=this.dir*this.spd; physicsStep(this);
    if(this.hitWall) this.dir=-this.dir;
    if(this.onGround){
      if(hopper){ this.hop++; this.vy=(this.hop%3===0)? -JUMP_V : -2.4; this.onGround=false; if(Math.random()<0.2) this.dir=-this.dir; return; }
      const aheadC=col(this.x+this.dir*(this.w/2+1)), belowR=row(this.y+1);
      const atEdge=!solidAt(aheadC,belowR);
      if(atEdge && !this.edgeFlag && Math.random()<0.4) this.dir=-this.dir;
      this.edgeFlag=atEdge;
      if(--this.think<=0){
        this.think=40+Math.random()*90;
        const p=player;
        if(p && p.state==='alive'){
          const dy=this.y-p.y, dx=Math.abs(p.x-this.x);
          if(dy>24 && dx<90 && Math.random()<0.65){ this.vy=-JUMP_V; this.onGround=false; }
          if(Math.random()<0.35) this.dir=sgn(p.x-this.x)||this.dir;
        } else if(Math.random()<0.25){ this.vy=-JUMP_V; }
      }
    }
  }
  // Monsta: no gravity, flies diagonally and rebounds off anything solid
  moveBouncer(){
    const sp=this.spd; if(Math.abs(this.fvy)<0.05) this.fvy=0.6;
    const nx=this.x+this.dir*sp; if(!this.blocked(nx,this.y)) this.x=nx; else this.dir=-this.dir;
    const ny=this.y+this.fvy*sp; if(!this.blocked(this.x,ny)) this.y=ny; else this.fvy=-this.fvy;
  }
  // Pulpul: no gravity, drifts toward Bub with a lazy wave
  moveHover(){
    const p=player, sp=this.spd*0.9;
    if(p && p.state==='alive' && this.anim%6===0){ this.dir=sgn(p.x-this.x)||this.dir; this.tyDir=sgn((p.y-8)-(this.y-8)); }
    const ty=Math.sin(this.anim*0.05)*0.6+this.tyDir*0.5;
    const nx=this.x+this.dir*sp*0.8; if(!this.blocked(nx,this.y)) this.x=nx; else this.dir=-this.dir;
    const ny=this.y+ty*sp; if(!this.blocked(this.x,ny)) this.y=ny;
  }
  blocked(x,y){
    if(x-this.w/2<2*TILE || x+this.w/2>LW*TILE-2*TILE || y-this.h<3*TILE || y>LH*TILE-TILE) return true;
    const cL=col(x-this.w/2), cR=col(x+this.w/2-1), rT=row(y-this.h), rB=row(y-1);
    for(let r=rT;r<=rB;r++) for(let c=cL;c<=cR;c++) if(solidAt(c,r)) return true;
    return false;
  }
  tryShoot(){
    if(this.shotCd>0){ this.shotCd--; return; }
    const p=player; if(!p||p.state!=='alive') return;
    const dx=p.x-this.x, dy=p.y-this.y, kind=this.type.shoot; let fired=false;
    if(kind==='rock' && Math.abs(dy)<20 && Math.abs(dx)<110 && this.onGround){ this.dir=sgn(dx)||this.dir; shots.push({type:'rock',x:this.x+this.dir*8,y:this.y,w:8,h:8,vx:this.dir*1.3,vy:-1.2,life:360,onGround:false,hitWall:false}); fired=true; }
    else if(kind==='laser' && dy>10 && Math.abs(dx)<30){ shots.push({type:'laser',x:this.x,y:this.y+2,w:2,h:10,vx:0,vy:2.6,life:200}); fired=true; }
    else if(kind==='fire' && Math.abs(dy)<16 && Math.abs(dx)<70 && sgn(dx)===this.dir){ shots.push({type:'fire',x:this.x+this.dir*12,y:this.y,w:14,h:12,vx:this.dir*1.1,vy:0,life:48,dir:this.dir}); fired=true; }
    else if(kind==='bottle' && Math.abs(dx)<130 && dy>-40){ this.dir=sgn(dx)||this.dir; shots.push({type:'bottle',x:this.x+this.dir*6,y:this.y-8,w:8,h:10,vx:this.dir*clamp(Math.abs(dx)/70,0.6,1.6),vy:-2.8,life:240}); fired=true; }
    if(fired){ this.shotCd=rnd(this.type.cd[0],this.type.cd[1])*(this.angry?0.6:1); this.throwT=20; SFX.spawn(); }
  }
  sprite(i){
    const base=this.type.spr;
    const name=(this.throwT>0 && this.type.throwSpr) ? base+(this.angry?'_athrow':'_throw') : base+(this.angry?'_angry':'_walk');
    return frame(name,i,this.dir);
  }
  draw(){
    if(this.trapped) return;
    if(this.state==='spawning'){ if(((this.timer>>2)&1)) return; const img=frame(this.type.spr+'_walk',0,this.dir); if(img) ctx.drawImage(img,Math.round(this.x-8),Math.round(this.y-16)); return; }
    const img=this.sprite(this.anim>>3); if(img) ctx.drawImage(img,Math.round(this.x-8),Math.round(this.y-16));
  }
}
// ---- monster projectiles: rolling rocks, dropped lasers, fire breath, thrown bottles ----
function updateShots(){
  for(const sh of shots){
    sh.life--;
    if(sh.type==='rock'){ sh.hitWall=false; physicsStep(sh); if(sh.hitWall) sh.vx=-sh.vx*0.7; if(sh.onGround && Math.abs(sh.vx)<0.2) sh.life=Math.min(sh.life,20); }
    else if(sh.type==='bottle'){ sh.vy+=0.12; sh.x+=sh.vx; sh.y+=sh.vy;
      if(solidAt(col(sh.x),row(sh.y-1)) || solidAt(col(sh.x+sgn(sh.vx)*4),row(sh.y-5))){ sh.life=0; for(let i=0;i<5;i++) particles.push({type:'dot',x:sh.x,y:sh.y-4,vx:rnd(-1,1),vy:rnd(-1.5,0),life:14,max:14,color:'#a0e0ff'}); } }
    else if(sh.type==='laser'){ sh.y+=sh.vy; if(solidAt(col(sh.x),row(sh.y))) sh.life=0; }
    else if(sh.type==='fire'){ sh.x+=sh.vx; if(solidAt(col(sh.x+sh.dir*6),row(sh.y-6))) sh.life=0; }
    if(sh.y-sh.h>LH*TILE) sh.life=0;
    const p=player; if(p && p.state==='alive' && p.inv<=0 && sh.life>0 && rectOverlap(p,{x:sh.x,y:sh.y,w:sh.w,h:sh.h},1)) p.die();
  }
  shots=shots.filter(sh=>sh.life>0);
}
function drawShots(){
  for(const sh of shots){
    if(sh.type==='rock'){ ctx.fillStyle='#3a3a44'; ctx.beginPath(); ctx.arc(sh.x,sh.y-4,4,0,Math.PI*2); ctx.fill(); ctx.fillStyle='#8a8a98'; ctx.beginPath(); ctx.arc(sh.x-1,sh.y-5,2.2,0,Math.PI*2); ctx.fill(); }
    else if(sh.type==='laser'){ ctx.fillStyle=(frameCount&2)?'#80f0ff':'#ffffff'; ctx.fillRect(Math.round(sh.x)-1,Math.round(sh.y-sh.h),2,sh.h); }
    else if(sh.type==='fire'){ const img=frame('fx_fire',Math.min(2,Math.floor((48-sh.life)/16)),sh.dir); if(img) ctx.drawImage(img,Math.round(sh.x-8),Math.round(sh.y-14)); }
    else if(sh.type==='bottle'){ const img=frame('fx_bottle',(frameCount>>3)%2,sgn(sh.vx)||1); if(img) ctx.drawImage(img,Math.round(sh.x-8),Math.round(sh.y-14)); }
  }
}

// ===================== bubbles =====================""")

# hook projectiles into the loop and renderer
rep("    for(const e of enemies) e.update();\n", "    for(const e of enemies) e.update();\n    updateShots();\n")
rep("    for(const e of enemies) e.draw();\n", "    for(const e of enemies) e.draw();\n    drawShots();\n")
# spawn with a type drawn from the round's pool
rep("  for(let i=0;i<n;i++){ const s=level.enemies[i%level.enemies.length]; spawnQueue.push({t:40+i*30,x:s.x,y:s.y}); }",
    "  const pool=typePool();\n  for(let i=0;i<n;i++){ const s=level.enemies[i%level.enemies.length]; spawnQueue.push({t:40+i*30,x:s.x,y:s.y,type:pool[Math.floor(Math.random()*pool.length)]}); }")
rep("enemies=[]; bubbles=[]; fruits=[]; particles=[]; popups=[]; spawnQueue=[]; exitOpen=false;",
    "enemies=[]; bubbles=[]; fruits=[]; particles=[]; popups=[]; spawnQueue=[]; shots=[]; exitOpen=false;")
rep("enemies.push(new Enemy(s.x,s.y)); s.done=true;", "enemies.push(new Enemy(s.x,s.y,s.type)); s.done=true;")
# trapped captive uses its own sprite
rep("    const img=frame('zen_walk',(b.trapT>>3)%2? 1:0, wob2>0?1:-1);",
    "    const img=frame(b.enemy.type.spr+'_walk',(b.trapT>>3)%2? 1:0, wob2>0?1:-1);")

# ------------------------------------------------------------------ trees (decoration behind the platforms)
rep("  return { def, cols, rows, grid, pal:PALETTES[def.pal]||PALETTES.sunset, spawn:at(def.spawn), enemies, keys, doorIds,",
    """  // bushy trees on platforms that have headroom (levels flagged trees:true)
  const trees=[];
  if(def.trees){ const R=rng(hashStr(def.name));
    for(let r=3;r<rows-1;r++){ let c=2; while(c<=cols-3){
      if(solid(c,r)&&!solid(c,r-1)){ let e=c; while(e+1<=cols-3&&solid(e+1,r)&&!solid(e+1,r-1)) e++; const len=e-c+1;
        if(len>=3){ const n=len>=10?2:1; for(let k=0;k<n;k++){ if(R()<0.7){ const tc=ri(R,c+1,e-1); let air=0;
          while(air<7 && r-1-air>2 && !solid(tc,r-1-air)&&!solid(tc-1,r-1-air)&&!solid(tc+1,r-1-air)) air++;
          if(air>=3) trees.push({x:tc*TILE+4,y:r*TILE,h:Math.min(air,3+ri(R,0,3))*TILE-3,rad:ri(R,7,11),seed:Math.floor(R()*100000)}); } } }
        c=e+1; } else c++; } } }
  return { def, cols, rows, grid, trees, pal:PALETTES[def.pal]||PALETTES.sunset, spawn:at(def.spawn), enemies, keys, doorIds,""")
rep("function tileAt(c,r){ if(c<0||c>=LW) return 'W'; if(r<0||r>=LH) return '.'; return level.grid[r][c]; }",
    """function hashStr(str){ let h=2166136261; for(let i=0;i<str.length;i++){ h^=str.charCodeAt(i); h=Math.imul(h,16777619); } return (h>>>0)%100000; }
function tileAt(c,r){ if(c<0||c>=LW) return 'W'; if(r<0||r>=LH) return '.'; return level.grid[r][c]; }""")
rep("  const isSurface=(c,r)=> isBrick(c,r) && !(solidAt(c+1,r)&&solidAt(c,r+1)&&solidAt(c+1,r+1));\n  g.fillStyle=pal.dark;",
    "  const isSurface=(c,r)=> isBrick(c,r) && !(solidAt(c+1,r)&&solidAt(c,r+1)&&solidAt(c+1,r+1));\n  for(const t of (level.trees||[])) drawTree(g,t);\n  g.fillStyle=pal.dark;")
rep("function buildLevel(){",
    """function drawTree(g,t){
  const R=rng(t.seed), top=t.y-t.h;
  g.fillStyle='#4a2e14'; g.fillRect(t.x-1,top+3,3,t.h-3); g.fillStyle='#8a5a2a'; g.fillRect(t.x,top+3,1,t.h-3);
  if(t.h>20){ g.fillStyle='#4a2e14'; g.fillRect(t.x-4,top+10,4,2); g.fillRect(t.x+1,top+14,4,2); }
  const greens=['#1c6e2a','#2a9a3c','#3fc04c'];
  for(let i=0;i<8;i++){ const ang=R()*Math.PI*2, d=R()*t.rad*0.75; const cx=t.x+Math.cos(ang)*d, cy=top+2+Math.sin(ang)*d*0.6;
    g.fillStyle=greens[i%3]; g.beginPath(); g.arc(cx,cy,t.rad*(0.4+R()*0.4),0,Math.PI*2); g.fill(); }
  g.fillStyle='#7ee070'; for(let i=0;i<6;i++){ g.fillRect(Math.round(t.x+(R()-0.5)*t.rad*1.3),Math.round(top-2+(R()-0.5)*t.rad*0.9),2,1); }
}
function buildLevel(){""")

# ------------------------------------------------------------------ 30 more rounds: small levels for contrast, forests with trees
rep("const LEVEL_DEFS=[", "const withTrees=d=>{ d.trees=true; return d; };\nconst LEVEL_DEFS=[")
rep("];\nfunction defOf(i){", r"""  // ---- rounds 31-60: small quick rounds between the big ones, and forests ----
  ()=>genPassage('NOOK',0.5,0.5,'forest',3031),                                        // 31 one cell
  ()=>withTrees(genTower('GLADE',1,1,'forest',3032)),                                 // 32
  ()=>genPassage('BURROW',1,0.5,'cave',3033),                                          // 33
  ()=>withTrees(genJumps('TREETOPS',1,1,'forest',3034,{dir:'up'})),                   // 34
  ()=>genMaze('COTTAGE',1,1,'sunset',3035,{roomW:7,roomH:5,doors:1}),                 // 35
  ()=>genPassage('THE BEND',0.5,1,'stone',3036),                                       // 36
  ()=>genCave('GROTTO',1,1,'ice',3037),                                                // 37
  ()=>withTrees(genTower('OAK TOWER',0.5,2,'forest',3038)),                           // 38
  ()=>genPassage('CROOKED WAY',1,1,'grape',3039,{spouts:0.3}),                         // 39
  ()=>withTrees(genHall('ORCHARD WALK',3,'forest',3040)),                             // 40
  ()=>genPassage('CELLAR',1,0.5,'ember',3041,{water:0.6}),                             // 41
  ()=>genJumps('LILY PADS',1,1,'ocean',3042,{dir:'right'}),                            // 42
  ()=>withTrees(genTower('PINE SPIRE',1,3,'forest',3043,{falls:2})),                  // 43
  ()=>genPassage('RABBIT HOLE',0.5,2,'cave',3044,{flows:0.7}),                         // 44
  ()=>withTrees(genMaze('HEDGE MAZE',2,1,'forest',3045,{roomW:8,roomH:5,doors:1})),   // 45
  ()=>genCave('WISHING WELL',1,1,'ocean',3046),                                        // 46
  ()=>genPassage('TWIST',1,1,'ice',3047),                                              // 47
  ()=>genTower('WATCHTOWER',1,1,'stone',3048),                                         // 48
  ()=>withTrees(genJumps('CANOPY',2,1,'forest',3049,{dir:'right'})),                  // 49
  ()=>genPassage('THE KNOT',2,1,'sunset',3050),                                        // 50
  ()=>withTrees(genMaze('ROOTS',1,2,'forest',3051,{roomW:9,roomH:6,water:0.2})),      // 51
  ()=>genPassage('DRIP',0.5,0.5,'ocean',3052,{flows:1,water:0.8}),                     // 52
  ()=>withTrees(genCave('MOSSY CAVE',1,2,'forest',3053)),                             // 53
  ()=>genTower('BELFRY',0.5,1,'ember',3054),                                           // 54
  ()=>genPassage('SWITCHBACK',1,2,'grape',3055),                                       // 55
  ()=>genJumps('BROKEN BRIDGE',1,1,'stone',3056,{dir:'right'}),                        // 56
  ()=>withTrees(genHall('GREAT OAKS',4,'forest',3057)),                               // 57
  ()=>genPassage('WARREN',2,2,'cave',3058),                                            // 58
  ()=>genMaze('FORTRESS',2,2,'ember',3059,{roomW:8,roomH:6,doors:3}),                 // 59
  ()=>withTrees(genPassage('THE GRAND PASSAGE',3,3,'forest',3060,{spouts:0.3})),      // 60
];
function defOf(i){""")

open(p, 'w', encoding='utf-8').write(s)
print('monsters patched OK')
