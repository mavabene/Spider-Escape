"""Spider Escape trial: local cooperative mode, zappers and pickups."""
import json, math, os, random, sys
from pathlib import Path
import pygame as pg
from rules import Options, CarState, COLORS

if getattr(sys,'frozen',False): os.chdir(sys._MEIPASS)
else: os.chdir(Path(__file__).resolve().parent.parent/'Finalp6')
pg.init(); W,H=1000,800
screen=pg.display.set_mode((W,H)); pg.display.set_caption('Spider Escape Trial')
clock=pg.time.Clock(); font=pg.font.Font(None,30); large=pg.font.Font(None,58)
try: pg.mixer.music.load('Jungle.mp3'); pg.mixer.music.play(-1)
except pg.error: pass
scores=Path.home()/'Library/Application Support/Spider Escape/trial_scores.json'
try: best=json.loads(scores.read_text())
except (OSError,ValueError): best={}

def text(msg,x,y,color=(255,245,200),f=font): screen.blit(f.render(msg,True,color),(x,y))
def tint(image,color):
    img=image.copy(); overlay=pg.Surface(img.get_size(),pg.SRCALPHA); overlay.fill((*color,0)); img.blit(overlay,(0,0),special_flags=pg.BLEND_RGBA_ADD); return img
palette={'original':(0,0,0),'blue':(0,45,120),'red':(80,0,0),'green':(0,70,0),'yellow':(65,50,0)}
carimage=pg.image.load('Jeep.png').convert(); carimage.set_colorkey((0,0,0))
spiderfiles=[pg.image.load(x).convert() for x in ('spider.png','spider_mirror.png')]
for img in spiderfiles: img.set_colorkey((0,0,0))
splatimage=pg.image.load('splat.png').convert_alpha(); tree=pg.image.load('Tree1sm.png').convert(); tree.set_colorkey((0,0,0))
options=Options(); coloridx=[1,0]
def menu():
    while True:
        for e in pg.event.get():
            if e.type==pg.QUIT: return False
            if e.type==pg.KEYDOWN:
                if e.key==pg.K_ESCAPE:return False
                if e.key==pg.K_1: options.players=1
                if e.key==pg.K_2: options.players=2
                if e.key==pg.K_q: options.spanish_quiz=not options.spanish_quiz
                if e.key==pg.K_c: coloridx[0]=(coloridx[0]+1)%len(COLORS)
                if e.key==pg.K_v: coloridx[1]=(coloridx[1]+1)%len(COLORS)
                if e.key in (pg.K_RETURN,pg.K_SPACE): return True
        screen.fill((45,65,38)); text('SPIDER ESCAPE — TRIAL',150,80,f=large)
        text(f'1 or 2: players  [{options.players}]',160,190)
        text(f'Q: Spanish quiz  [{"ON" if options.quiz_enabled else "OFF"}]',160,230)
        text('Two-player mode always turns the quiz off.',160,265)
        text(f'C: left / solo car color  [{COLORS[coloridx[0]]}]',160,315)
        text(f'V: right car color  [{COLORS[coloridx[1]]}]',160,350)
        text('Solo/right: arrow keys + SPACE to zap',160,420)
        text('Left player: W A S D + Z to zap',160,455)
        text('Drive over pickups: AMMO, ARMOR, SLOW, REPEL',160,500)
        text('ENTER to start — ESC to quit',160,570)
        pg.display.flip();clock.tick(30)

def car(index,x):
    img=tint(carimage,palette[COLORS[coloridx[index]]]); return {'img':img,'rect':img.get_rect(center=(x,H-80)),'state':CarState(),'alive':True,'last':None,'paint':None}
def maskhit(a,b):
    return bool(a['rect'].colliderect(b['rect']) and pg.mask.from_surface(a['img']).overlap(pg.mask.from_surface(b['img']),(b['rect'].x-a['rect'].x,b['rect'].y-a['rect'].y)))
def persist(mode,score):
    if score>best.get(mode,0):
        best[mode]=score
        try: scores.parent.mkdir(parents=True,exist_ok=True);scores.write_text(json.dumps(best))
        except OSError: pass

def play():
    cars=[car(0,W//2 if options.players==1 else 350)]
    if options.players==2: cars.append(car(1,650))
    spiders=[]; splats=[]; pickups=[]; shots=[]; trees=[]; trails=[]
    frame=0; score=0; quiz=None; answer=''; paused_until=0
    words=[('gato','cat'),('perro','dog'),('caballo','horse'),('naranja','orange'),('facil','easy'),('lapiz','pencil')]
    running=True
    while running:
        dt=min(clock.tick(30),80); now=pg.time.get_ticks(); frame+=1; score+=0.5; level=int(score//250)+1
        for e in pg.event.get():
            if e.type==pg.QUIT: return False
            if e.type!=pg.KEYDOWN: continue
            if e.key==pg.K_ESCAPE: running=False; break
            if quiz and e.key==pg.K_RETURN:
                if answer.strip().lower()==quiz[1]:
                    for sp in spiders: splats.append([pg.transform.rotozoom(splatimage,random.randrange(360),sp['scale']),sp['rect'].centerx,sp['rect'].centery,random.randint(130,255)])
                    spiders.clear();quiz=None
                answer=''
            elif quiz and e.key==pg.K_BACKSPACE: answer=answer[:-1]
            elif quiz and e.unicode.isprintable(): answer+=e.unicode
            else:
                firing=[]
                if e.key==pg.K_z and options.players==2: firing.append(cars[0])
                if e.key==pg.K_SPACE: firing.append(cars[-1])
                for c in firing:
                    if c['alive'] and c['state'].fire(): shots.append(pg.Rect(c['rect'].centerx-4,c['rect'].top-14,8,18))
        if not running: break
        keys=pg.key.get_pressed()
        for i,c in enumerate(cars):
            if not c['alive']:continue
            controls=(pg.K_w,pg.K_s,pg.K_a,pg.K_d) if options.players==2 and i==0 else (pg.K_UP,pg.K_DOWN,pg.K_LEFT,pg.K_RIGHT)
            u,d,l,r=controls; old=c['rect'].copy(); c['rect'].move_ip((keys[r]-keys[l])*9,(keys[d]-keys[u])*9);c['rect'].clamp_ip(screen.get_rect());c['old']=old
        if len(cars)==2 and all(c['alive'] for c in cars) and cars[0]['rect'].colliderect(cars[1]['rect']):
            cars[0]['rect']=cars[0]['old'];cars[1]['rect']=cars[1]['old']
            cars[0]['rect'].x-=8;cars[1]['rect'].x+=8
            for c in cars:c['rect'].clamp_ip(screen.get_rect())
        if frame%max(15,45-level*2)==0:
            scale=max(.5,min(1.5,random.gauss(1,.18)));side=random.randrange(2);img=pg.transform.scale(spiderfiles[side],(round(135*scale),round(123*scale)))
            color=random.choice([(0,0,0),(35,0,0),(0,25,0),(0,0,35)]); frames=[tint(pg.transform.scale(base,img.get_size()),color) for base in spiderfiles];img=frames[side];spiders.append({'frames':frames,'img':img,'rect':img.get_rect(center=(random.randrange(30,970),-50)),'scale':scale,'side':side,'dx':random.choice([-2,2]),'chase':level>=3 and random.random()<min(.65,.2+level*.03)})
        if frame%300==0: pickups.append({'rect':pg.Rect(random.randrange(70,900),-30,90,30),'kind':random.choices(['ammo','armor','slow','repellent'],[5,2,2,2])[0]})
        if frame%30==0: trees.append([random.choice([random.randrange(0,70),random.randrange(900,960)]),-80])
        if options.quiz_enabled and frame%1000==0: quiz=random.choice(words);answer='';paused_until=now+10000
        if quiz and now>=paused_until:quiz=None;answer=''
        slowed=any(c['alive'] and c['state'].active('slow',now) for c in cars);speed=6 if slowed else 13
        for sp in spiders[:]:
            alive=[c for c in cars if c['alive']]
            if sp['chase'] and alive:
                target=min(alive,key=lambda c:abs(c['rect'].centerx-sp['rect'].centerx)); delta=target['rect'].centerx-sp['rect'].centerx
                sp['dx']=max(-4,min(4,delta/25))
                # A mirrored frame faces the direction of movement.
                sp['side']=int(sp['dx']>0)
            sp['img']=sp['frames'][(sp['side'] + (frame//15)%2)%2]
            sp['rect'].move_ip(sp['dx'],speed*.65)
            if sp['rect'].top>H:spiders.remove(sp);continue
            for c in cars:
                if c['alive'] and c['state'].active('repellent',now) and math.dist(c['rect'].center,sp['rect'].center)<180: sp['rect'].x+=-8 if sp['rect'].centerx<c['rect'].centerx else 8
                if c['alive'] and maskhit(c,sp) and not c['state'].active('armor',now):c['alive']=False
        for shot in shots[:]:
            shot.y-=24
            hit=next((sp for sp in spiders if sp['rect'].colliderect(shot)),None)
            if hit:
                splats.append([pg.transform.rotozoom(splatimage,random.randrange(360),hit['scale']),hit['rect'].centerx,hit['rect'].centery,random.randint(130,255)]);spiders.remove(hit);shots.remove(shot)
            elif shot.bottom<0:shots.remove(shot)
        for p in pickups[:]:
            p['rect'].y+=speed
            for c in cars:
                if c['alive'] and c['rect'].colliderect(p['rect']):c['state'].collect(p['kind'],now);pickups.remove(p);break
            else:
                if p['rect'].top>H:pickups.remove(p)
        for sp in splats[:]:
            sp[2]+=speed
            if sp[2]>H+200:splats.remove(sp)
        for t in trees[:]:
            t[1]+=speed
            if t[1]>H+100:trees.remove(t)
        for c in cars:
            if not c['alive']: continue
            for img,x,y,alpha in splats:
                rect=img.get_rect(center=(x,y))
                if c['rect'].colliderect(rect): c['paint']=[random.uniform(.5,1)*c['rect'].height,alpha]
            if c['paint'] and c['paint'][0]>0:
                c['paint'][0]-=speed
                trails.append([c['rect'].centerx,c['rect'].bottom,c['paint'][1]*max(0,c['paint'][0]/c['rect'].height),c['rect'].width])
        screen.fill((131,105,83))
        for t in trails[:]:
            t[1]+=speed
            if t[1]>H:trails.remove(t);continue
            layer=pg.Surface((max(4,t[3]),speed),pg.SRCALPHA)
            for x in (2,max(2,t[3]-4)):pg.draw.rect(layer,(150,25,8,int(t[2])),(x,0,3,speed))
            screen.blit(layer,(t[0]-t[3]//2,t[1]))
        for img,x,y,alpha in splats: img.set_alpha(alpha);screen.blit(img,img.get_rect(center=(x,y)))
        for t in trees:screen.blit(tree,t)
        for sp in spiders:screen.blit(sp['img'],sp['rect'])
        for p in pickups:
            pg.draw.rect(screen,(50,80,110),p['rect'],border_radius=6); text(p['kind'].upper(),p['rect'].x+5,p['rect'].y+4)
        for shot in shots:pg.draw.rect(screen,(255,240,80),shot)
        for i,c in enumerate(cars):
            if c['alive']:
                screen.blit(c['img'],c['rect'])
                if c['state'].active('armor',now):pg.draw.ellipse(screen,(100,210,255),c['rect'].inflate(16,16),3)
            active=' '.join(k.upper()+':'+str(math.ceil((v-now)/1000)) for k,v in c['state'].effects.items() if v>now)
            text(f'P{i+1} ammo {c["state"].ammo} {active}',10,50+i*28)
        text(f'{int(score)} m   Level {level}',10,10)
        if quiz:
            pg.draw.rect(screen,(45,45,45),(250,15,500,115),border_radius=8)
            text(f'Translate {quiz[0]}: {answer}',270,30);text(f'Time left: {max(0,math.ceil((paused_until-now)/1000))}',270,70)
        pg.display.flip()
        if not any(c['alive'] for c in cars):break
    mode='two' if options.players==2 else 'solo';persist(mode,int(score))
    while True:
        for e in pg.event.get():
            if e.type==pg.QUIT:return False
            if e.type==pg.KEYDOWN and e.key in (pg.K_RETURN,pg.K_ESCAPE):return True
        screen.fill((45,35,32));text('SPIDER ATTACK!',250,200,f=large)
        text(f'{"Shared" if mode=="two" else "Solo"} score: {int(score)} m',300,300)
        text(f'{"Two-player" if mode=="two" else "Solo"} best: {best.get(mode,0)} m',300,345)
        text('ENTER: menu',300,420);pg.display.flip();clock.tick(30)

if __name__=='__main__':
    while menu():
        if not play():break
    pg.quit()
