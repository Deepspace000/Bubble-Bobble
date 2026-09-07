import os
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, 'bubble_template.html')
s = open(p, encoding='utf-8').read()

def rep(a, b, count=1):
    global s
    assert s.count(a) == count, (s.count(a), a[:90])
    s = s.replace(a, b)

rep("const INFINITE_LIVES=true;", "const INFINITE_LIVES=true;\nconst BOSS_EVERY=5, BONUS_TIME=30*60;")
rep("let exitOpen=false, camSnap=true, roundTotal=0; const cam={x:0,y:0};",
    "let exitOpen=false, camSnap=true, roundTotal=0; const cam={x:0,y:0};\nlet bossRound=false, bossSpawned=false, bonusActive=false, bonusTimer=0, bonusTotal=0;")

# ---- desserts for the treasure rooms (8x8 pixel art drawn at 12x12 like the fruit) ----
rep("function pixmap(rows,pal){",
    r"""const DESSERTS=[
 {name:'Chocolate Pudding',value:500,pal:{W:'#fff4c0',B:'#6a3a1a',b:'#4a2610',p:'#d0d0e0'},rows:["...WW...","..WWWW..",".BBBBBB.","BBBBBBBB","BBBBBBBB","bBBBBBBb",".bbbbbb.","..pppp.."]},
 {name:'Strawberry Shortcake',value:500,pal:{R:'#ff2a4a',W:'#ffffff',P:'#ff9ac0',Y:'#f8e080'},rows:["....R...","...RRR..",".WWWWWW.",".PPPPPP.",".WWWWWW.",".PPPPPP.",".YYYYYY.",".YYYYYY."]},
 {name:'Ice Cream',value:500,pal:{P:'#ff9ac0',W:'#ffffff',C:'#d8a860',c:'#a87838'},rows:["..PPP...",".PPPPP..",".PWPPP..","..PPP...","..CCC...","..cCc...","...C....","...c...."]},
 {name:'Doughnuts',value:500,pal:{P:'#ff80c0',S:'#ffffff',B:'#c08040'},rows:["..PPPP..",".PSPPSP.","PPP..PPP","PP....PP","PPP..PPP",".BBBBBB.","..BBBB..","........"]},
 {name:'Eclairs',value:500,pal:{B:'#5a2e10',W:'#fff4c0',Y:'#e8c070'},rows:["........",".BBBBBB.","BBBBBBBB","WWWWWWWW","YYYYYYYY",".YYYYYY.","........","........"]},
 {name:'Cupcakes',value:500,pal:{R:'#ff2a4a',W:'#ffffff',P:'#ff9ac0',p:'#c06090'},rows:["...R....","..WWW...",".WWWWW..",".WWWWW..",".PPPPP..",".pPpPp..",".PPPPP..","........"]},
 {name:'Pancakes',value:500,pal:{Y:'#f8d060',O:'#c88030',B:'#fff0a0'},rows:["...BB...",".YYYYYY.","OOOOOOOO",".YYYYYY.","OOOOOOOO",".YYYYYY.","OOOOOOOO","........"]},
 {name:'Lollipops',value:500,pal:{R:'#ff2a4a',W:'#ffffff'},rows:["..RRR...",".RWRRR..",".RRRWR..","..RRR...","...W....","...W....","...W....","...W...."]},
 {name:'Jelly',value:500,pal:{G:'#40e060',g:'#a0ffb0',p:'#d0d0e0'},rows:["...GG...","..GGGG..",".GGGGGG.",".GgGGgG.",".GGGGGG.","GGGGGGGG","pppppppp","........"]},
 {name:'Cherry Pie',value:500,pal:{S:'#2fa82f',R:'#d01030',Y:'#e8b860'},rows:["...S....","..RRRR..",".RRRRRR.","YYYYYYYY",".YYYYYY.",".YYYYYY.","..YYYY..","........"]},
 {name:'Cookies',value:500,pal:{B:'#c08040',b:'#5a2e10'},rows:["..BBBB..",".BbBBBB.","BBBBbBBB","BBbBBBBB","BBBBBbBB",".BBbBBB.","..BBBB..","........"]},
 {name:'Candy Floss',value:500,pal:{P:'#ffb0e0',p:'#ff80c0',W:'#ffffff'},rows:["..PPPP..",".PPpPPP.","PPPPPpPP","PpPPPPPP",".PPPpPP.","..PPPP..","...W....","...W...."]},
];
function pixmap(rows,pal){""")
rep("FRUIT_DEFS.forEach(f=>f.img=pixmap(f.rows,f.pal));", "FRUIT_DEFS.forEach(f=>f.img=pixmap(f.rows,f.pal));\nDESSERTS.forEach(f=>f.img=pixmap(f.rows,f.pal));")

# ---- treasure room generator + roster interleave (every 6th slot) ----
rep("const withTrees=d=>{ d.trees=true; return d; };\nconst LEVEL_DEFS=[",
    """const withTrees=d=>{ d.trees=true; return d; };
// Treasure room: a small bonus stage stuffed with one dessert and a 30 second clock. Grab everything for a perfect bonus.
function genTreasure(k){
  const dessert=DESSERTS[k%DESSERTS.length], pals=['sunset','grape','ice','forest'];
  const d=genTower('TREASURE ROOM OF '+dessert.name.toUpperCase(),1,1,pals[k%pals.length],4100+k);
  d.enemies=[]; d.bonus=true; d.dessert=dessert; return d;
}
const BASE_DEFS=[""")
rep("""  ()=>withTrees(genPassage('THE GRAND PASSAGE',3,3,'forest',3060,{spouts:0.3})),      // 60
];
function defOf(i){""",
"""  ()=>withTrees(genPassage('THE GRAND PASSAGE',3,3,'forest',3060,{spouts:0.3})),      // 60
];
// a treasure room after every five levels, so rounds 6, 12, 18 ... are dessert rooms (72 rounds in all)
const LEVEL_DEFS=[]; BASE_DEFS.forEach((d,i)=>{ LEVEL_DEFS.push(d); if((i+1)%5===0){ const k=Math.floor(LEVEL_DEFS.length/6); LEVEL_DEFS.push(()=>genTreasure(k)); } });
function defOf(i){""")

# ---- Super Drunk's triple bottle throw ----
rep("    if(fired){ this.shotCd=rnd(this.type.cd[0],this.type.cd[1])*(this.angry?0.6:1); this.throwT=20; SFX.spawn(); }",
    """    else if(kind==='bottle3' && Math.abs(dx)<170){ this.dir=sgn(dx)||this.dir; for(const k of [-1,0,1]) shots.push({type:'bottle',x:this.x+this.dir*10,y:this.y-30,w:8,h:10,vx:this.dir*(1.0+k*0.35),vy:-2.6-k*0.3,life:240}); fired=true; }
    if(fired){ this.shotCd=rnd(this.type.cd[0],this.type.cd[1])*(this.angry?0.6:1); this.throwT=20; SFX.spawn(); }""")

# ---- Boss class ----
rep("// ---- monster projectiles: rolling rocks, dropped lasers, fire breath, thrown bottles ----",
r"""// ---- bosses: a giant monster every 5th round, Super Drunk every 10th. They can't be bubbled; fresh bubbles burst on them and take a hit point ----
const GIANTS=['zen','pulpul','banebou','monsta','hidegons','mighta'];
class Boss extends Enemy{
  constructor(x,y){
    const superDrunk=(round%10===0), gi=GIANTS[(Math.floor(round/BOSS_EVERY)-1)%GIANTS.length];
    super(x,y, superDrunk?'drunk':gi);
    this.boss=true; this.superDrunk=superDrunk; this.giant=gi;
    if(superDrunk){ this.w=36; this.h=52; this.maxHp=16+2*Math.floor(round/10); this.type=Object.assign({},ENEMY_TYPES.drunk,{kind:'hopper',shoot:'bottle3',cd:[90,150],throwSpr:false}); }
    else { this.w=22; this.h=28; this.maxHp=10+2*Math.floor(round/BOSS_EVERY); this.type=Object.assign({},ENEMY_TYPES[gi]); if(this.type.cd) this.type.cd=[80,150]; }
    this.hp=this.maxHp; this.speed=this.type.speed*0.85+round*0.01; this.hurtT=0; this.dieT=0; this.timer=90; this.shotCd=60;
  }
  update(){
    if(this.state==='dying'){
      this.dieT--;
      if(this.dieT%6===0){ particles.push({type:'ring',x:this.x+rnd(-this.w/2,this.w/2),y:this.y-rnd(0,this.h),r:3,life:12,max:12,color:'#ffffff'}); SFX.pop(this.dieT>>3); }
      if(this.dieT<=0){ const i=enemies.indexOf(this); if(i>=0) enemies.splice(i,1);
        for(let k=0;k<5;k++){ const def=FRUIT_DEFS[k%FRUIT_DEFS.length]; fruits.push({x:this.x+rnd(-20,20),y:this.y-20,w:10,h:12,vx:rnd(-1.5,1.5),vy:rnd(-3,-1.5),def,value:5000,age:0,dead:false,onGround:false,hitWall:false}); }
        addPopup(this.x,this.y-this.h-6,'BOSS DOWN!','#f8e030'); SFX.clear(); }
      return;
    }
    if(this.hurtT>0) this.hurtT--;
    super.update();
    if(this.state==='alive' && this.superDrunk && this.onGround && player && player.state==='alive' && Math.random()<0.5) this.dir=sgn(player.x-this.x)||this.dir;
  }
  hit(b){
    this.hp--; this.hurtT=18; spawnPopParticles(b,'#ffffff'); SFX.kill();
    if(this.hp<=0){ this.state='dying'; this.dieT=100; }
  }
  draw(){
    if(this.state==='spawning' && ((this.timer>>2)&1)) return;
    if(this.hurtT>0 && ((frameCount>>1)&1) && this.state!=='dying' && !this.superDrunk) return;
    if(this.superDrunk){ const name=(this.state==='dying'||this.hurtT>0) ? 'superdrunk_hurt' : (this.angry?'superdrunk_angry':'superdrunk_walk'); const img=frame(name,this.anim>>3,this.dir); if(img) ctx.drawImage(img,Math.round(this.x-32),Math.round(this.y-64)); }
    else { const img=frame('giant_'+this.giant,this.anim>>3,this.dir); if(img) ctx.drawImage(img,Math.round(this.x-16),Math.round(this.y-32)); }
    if(this.state==='dying' && ((frameCount>>2)&1)){ ctx.globalAlpha=0.5; ctx.fillStyle='#fff'; ctx.fillRect(Math.round(this.x-this.w/2),Math.round(this.y-this.h),this.w,this.h); ctx.globalAlpha=1; }
  }
}
function spawnBoss(){
  const d=level.exit; enemies.push(new Boss(d.x+8,d.y+16)); bossSpawned=true; roundTotal++;
  banner={text:'WARNING!  BOSS!',t:150}; SFX.escape();
}
function hitBossCheck(b){
  if(b.enemy) return false;
  for(const e of enemies){ if(!e.boss||e.state!=='alive') continue;
    if(circleRect({x:b.x,y:b.y,r:b.r+1},e,0)){ e.hit(b); const i=bubbles.indexOf(b); if(i>=0) bubbles.splice(i,1); return true; } }
  return false;
}
// ---- monster projectiles: rolling rocks, dropped lasers, fire breath, thrown bottles ----""")

# bubbles: fresh bubbles damage bosses, never trap them
rep("    if(e.state!=='alive'||e.trapped) continue;\n    if(circleRect({x:b.x,y:b.y,r:b.r+1},e,0) || circleRect(probe,e,0)){ trap(b,e); return; }",
    "    if(e.state!=='alive'||e.trapped||e.boss) continue;\n    if(circleRect({x:b.x,y:b.y,r:b.r+1},e,0) || circleRect(probe,e,0)){ trap(b,e); return; }")
rep("    tryTrap(b,px);\n  } else {\n    if(b.age<BUB_ACTIVE && !b.enemy) tryTrap(b,b.x);",
    "    if(hitBossCheck(b)) return;\n    tryTrap(b,px);\n  } else {\n    if(b.age<BUB_ACTIVE && !b.enemy){ if(hitBossCheck(b)) return; tryTrap(b,b.x); }")

# ---- round flow: boss after the last enemy; treasure rooms run on a clock ----
rep("    if(!exitOpen && enemies.length===0 && spawnQueue.length===0){ exitOpen=true; SFX.clear(); banner={text:'EXIT OPEN!',t:150}; }",
    """    if(bonusActive){ bonusTimer--; if(bonusTimer<=0 || fruits.length===0) endBonus(); }
    else if(!exitOpen && enemies.length===0 && spawnQueue.length===0){
      if(bossRound && !bossSpawned) spawnBoss();
      else { exitOpen=true; SFX.clear(); banner={text:'EXIT OPEN!',t:150}; } }""")
rep("enemies=[]; bubbles=[]; fruits=[]; particles=[]; popups=[]; spawnQueue=[]; shots=[]; exitOpen=false;",
    "enemies=[]; bubbles=[]; fruits=[]; particles=[]; popups=[]; spawnQueue=[]; shots=[]; exitOpen=false;\n  bossRound=(round%BOSS_EVERY===0) && !level.def.bonus; bossSpawned=false; bonusActive=false;")
rep("  if(player){ player.reset(); }\n  camSnap=true; updateCamera();\n}",
    """  if(level.def.bonus) setupBonus();
  if(player){ player.reset(); }
  camSnap=true; updateCamera();
}
function setupBonus(){
  bonusActive=true; bonusTimer=BONUS_TIME; spawnQueue=[]; roundTotal=0; fruits=[];
  const food=level.def.dessert;
  for(let r=3;r<LH-1;r++) for(let c=3;c<LW-3;c++){
    if(solidAt(c,r)&&!solidAt(c,r-1)&&!solidAt(c,r-2)&&(c%2===0)&&Math.random()<0.75) fruits.push({x:c*TILE+4,y:r*TILE,w:10,h:12,vx:0,vy:0,def:food,value:food.value,age:100,dead:false,onGround:true,hitWall:false,permanent:true}); }
  bonusTotal=fruits.length;
  banner={text:level.def.name,t:180};
}
function endBonus(){
  const all=fruits.length===0; fruits=[]; bonusActive=false; state='clear'; clearTimer=150;
  banner={text: all?'PERFECT!  +10000':'TIME UP!',t:150}; if(all) player.score+=10000; SFX.clear();
}""")

# bonus fruit never rots
rep("  if(f.age>900) f.dead=true;", "  if(f.age>900 && !f.permanent) f.dead=true;")
rep("    for(const f of fruits){ if(f.age>840 && ((frameCount>>2)&1)) continue;", "    for(const f of fruits){ if(f.age>840 && !f.permanent && ((frameCount>>2)&1)) continue;")

# ---- HUD: timer during the treasure room, boss health bar, arrow toward the boss ----
rep("  } else {\n    // enemy gauge: bar drains and the number counts down to zero",
    "  } else if(bonusActive){\n    text('TIME',214,7,'#f8e030',6,'center'); text(String(Math.max(0,Math.ceil(bonusTimer/60))).padStart(2,'0'),214,16,'#ffffff',8,'center');\n    text((bonusTotal-fruits.length)+'/'+bonusTotal,246,25,'#ffffff',5,'right');\n  } else {\n    // enemy gauge: bar drains and the number counts down to zero")
rep("  if(paused) text('PAUSED',128,120,'#ffffff',8,'center');",
    """  { const bz=state!=='title' && enemies.find(e=>e.boss&&e.state!=='dead'); if(bz){ text('BOSS',128,H-15,'#ff5050',6,'center'); ctx.fillStyle='#181828'; ctx.fillRect(88,H-10,80,7); ctx.fillStyle='#402020'; ctx.fillRect(89,H-9,78,5); ctx.fillStyle=(bz.hurtT>0)?'#ffffff':'#ff4040'; ctx.fillRect(89,H-9,Math.max(0,Math.round(78*bz.hp/bz.maxHp)),5); } }
  if(paused) text('PAUSED',128,120,'#ffffff',8,'center');""")
rep("    if(exitOpen){\n      const ex=level.exit.x+8-cx, ey=level.exit.y+8-cy;",
    "    const bossT=enemies.find(e=>e.boss&&e.state==='alive');\n    if(exitOpen||bossT){\n      const ex=(exitOpen?level.exit.x+8:bossT.x)-cx, ey=(exitOpen?level.exit.y+8:bossT.y-10)-cy;")
rep("        ctx.save(); ctx.translate(ax,ay); ctx.rotate(ang); ctx.fillStyle='#40ff40';",
    "        ctx.save(); ctx.translate(ax,ay); ctx.rotate(ang); ctx.fillStyle=exitOpen?'#40ff40':'#ff5050';")

open(p, 'w', encoding='utf-8').write(s)
print('boss patched OK')
