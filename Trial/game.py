"""Spider Escape trial: local cooperative mode, zappers and pickups."""
import json, math, os, random, sys
from pathlib import Path
import pygame as pg
from rules import Options, CarState, COLORS

if getattr(sys,'frozen',False): os.chdir(sys._MEIPASS)
else: os.chdir(Path(__file__).resolve().parent.parent/'Finalp6')
pg.init(); W,H=1000,800
screen=pg.display.set_mode((W,H)); pg.display.set_caption('Spider Escape 2.0.2')
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

# Match the original title screen while keeping the trial's settings visible.
menu_background = pg.transform.scale(pg.image.load('background.JPG').convert(), (W,H))
menu_title_font = pg.font.Font('Grindcore Records.otf', 88)
menu_button_font = pg.font.Font(None, 62)
menu_font = pg.font.Font(None, 30)
menu_small = pg.font.Font(None, 25)
menu_gold = (222,192,100)
start_rect = pg.Rect(350, 240, 300, 82)
menu_rows = [pg.Rect(180, 384 + 43*i, 640, 40) for i in range(4)]

def draw_menu():
    screen.blit(menu_background,(0,0))
    title = menu_title_font.render('Escape the Yucatan Jungle!',True,menu_gold)
    screen.blit(title,title.get_rect(center=(W//2,135)))
    hover = start_rect.collidepoint(pg.mouse.get_pos())
    pg.draw.rect(screen,(204,0,0) if hover else (102,0,0),start_rect,border_radius=15)
    label=menu_button_font.render('START!',True,menu_gold)
    screen.blit(label,label.get_rect(center=start_rect.center))
    panel=pg.Surface((700,380),pg.SRCALPHA)
    pg.draw.rect(panel,(180,95,6,215),panel.get_rect(),border_radius=15)
    screen.blit(panel,(150,350))
    heading=menu_font.render('Choose your game',True,menu_gold)
    screen.blit(heading,heading.get_rect(center=(W//2,365)))
    rows=[
        f'1 / 2   Players: {options.players}',
        f'Q   Spanish quiz: {"ON" if options.quiz_enabled else "OFF"}' + (' (two players: off)' if options.players==2 else ''),
        f'C   {"Left" if options.players==2 else "Your"} car: {COLORS[coloridx[0]].title()}',
        f'V   Right car: {COLORS[coloridx[1]].title()}',
    ]
    for rect,label in zip(menu_rows,rows):
        if rect.collidepoint(pg.mouse.get_pos()):
            pg.draw.rect(screen,(150,66,5),rect,border_radius=7)
        screen.blit(menu_font.render(label,True,(255,238,180)),(rect.x+14,rect.y+7))
    controls=['Arrow keys + Space: drive and zap',
              'Two players: left car uses WASD + Z',
              'Collect power-ups; zapper charges every 10 seconds',
              'Enter or click START to play   |   Esc to quit']
    for i,label in enumerate(controls):
        rendered=menu_small.render(label,True,(255,238,180))
        screen.blit(rendered,rendered.get_rect(center=(W//2,590+i*29)))

def menu():
    while True:
        for e in pg.event.get():
            if e.type==pg.QUIT: return False
            if e.type==pg.MOUSEBUTTONDOWN and e.button==1:
                if start_rect.collidepoint(e.pos): return True
                if menu_rows[0].collidepoint(e.pos): options.players=3-options.players
                elif menu_rows[1].collidepoint(e.pos): options.spanish_quiz=not options.spanish_quiz
                elif menu_rows[2].collidepoint(e.pos): coloridx[0]=(coloridx[0]+1)%len(COLORS)
                elif menu_rows[3].collidepoint(e.pos): coloridx[1]=(coloridx[1]+1)%len(COLORS)
            if e.type==pg.KEYDOWN:
                if e.key==pg.K_ESCAPE:return False
                if e.key==pg.K_1: options.players=1
                if e.key==pg.K_2: options.players=2
                if e.key==pg.K_q: options.spanish_quiz=not options.spanish_quiz
                if e.key==pg.K_c: coloridx[0]=(coloridx[0]+1)%len(COLORS)
                if e.key==pg.K_v: coloridx[1]=(coloridx[1]+1)%len(COLORS)
                if e.key in (pg.K_RETURN,pg.K_SPACE): return True
        draw_menu()
        pg.display.flip();clock.tick(30)

def car(index,x):
    img=tint(carimage,palette[COLORS[coloridx[index]]]); return {'img':img,'rect':img.get_rect(center=(x,H-80)),'state':CarState(),'alive':True,'previous_tires':None,'tire_paint':[None,None],'tire_coverage':[0.0,0.0],'tire_contact':[False,False]}
def make_splat(spider):
    # Match the original game: size the mark to the spider before rotating it.
    original=pg.transform.smoothscale(splatimage,spider['rect'].size)
    image=pg.transform.rotozoom(original,random.randrange(360),1.0)
    color=tuple(original.get_at((original.get_width()//2,original.get_height()//2)))[:3]
    mask=pg.mask.from_surface(image)
    opacity=round(255*(1-min(0.5,abs(random.gauss(0,0.18)))))
    image.set_alpha(opacity)
    return [image,spider['rect'].centerx,spider['rect'].centery,opacity,mask,color]


def track_segment(start,end,color,start_alpha,end_alpha,width):
    padding=width+1
    left=math.floor(min(start[0],end[0]))-padding
    top=math.floor(min(start[1],end[1]))-padding
    rect=pg.Rect(left,top,math.ceil(abs(end[0]-start[0]))+padding*2+1,
                 math.ceil(abs(end[1]-start[1]))+padding*2+1)
    surface=pg.Surface(rect.size,pg.SRCALPHA)
    dx,dy=end[0]-start[0],end[1]-start[1]
    squared=dx*dx+dy*dy
    radius=max(1,width/2)
    for y in range(rect.height):
        for x in range(rect.width):
            px,py=x+left,y+top
            t=((px-start[0])*dx+(py-start[1])*dy)/squared if squared else 0
            t=max(0.0,min(1.0,t))
            if math.dist((px,py),(start[0]+dx*t,start[1]+dy*t))<=radius:
                surface.set_at((x,y),(*color,round(start_alpha+(end_alpha-start_alpha)*t)))
    return [surface,rect]


def leave_tire_tracks(car,splats,trails,speed):
    rect=car['rect']
    points=[(rect.left+round(rect.width*fraction),rect.bottom-3) for fraction in (0.2,0.8)]
    previous=car['previous_tires'] or points
    for index,point in enumerate(points):
        start=(previous[index][0],previous[index][1]+speed)
        distance=math.dist(start,point)
        paint=car['tire_paint'][index]
        if paint is not None and distance>0:
            length=min(distance,paint['remaining'])
            fraction=length/distance
            end=(start[0]+(point[0]-start[0])*fraction,start[1]+(point[1]-start[1])*fraction)
            alpha=paint['alpha']*paint['remaining']/paint['length']
            paint['remaining']-=length
            end_alpha=paint['alpha']*paint['remaining']/paint['length']
            trails.append(track_segment(start,end,paint['color'],alpha,end_alpha,max(2,round(rect.width*.12))))
            if paint['remaining']<=0: car['tire_paint'][index]=None
        # Sample the traversed path across the tire width, including transparent pixels.
        steps=max(1,math.ceil(distance))
        tire_width=max(2,round(rect.width*.12))
        coverage=0.0
        strongest=None
        for step in range(steps):
            t=(step+.5)/steps
            sx=start[0]+(point[0]-start[0])*t
            sy=start[1]+(point[1]-start[1])*t
            for offset in range(tire_width):
                px=round(sx+offset-(tire_width-1)/2)
                py=round(sy)
                for image,x,y,opacity,mask,color in reversed(splats):
                    splat_rect=image.get_rect(center=(x,y))
                    local=(px-splat_rect.left,py-splat_rect.top)
                    if not (0<=local[0]<splat_rect.width and 0<=local[1]<splat_rect.height):
                        continue
                    pixel=image.get_at(local)
                    pigment=max(0,pixel.r-max(pixel.g,pixel.b))/255 * (pixel.a/255) * (opacity/255)
                    if pigment>0:
                        coverage+=pigment*distance/(steps*tire_width)
                        if strongest is None or opacity>strongest[0]: strongest=(opacity,color)
                        break
        if coverage>0 and strongest:
            if not car['tire_contact'][index]: car['tire_coverage'][index]=0.0
            car['tire_coverage'][index]+=coverage
            car['tire_contact'][index]=True
            # A richly coated path of about 35% of a car length reaches the maximum.
            amount=min(1.0,car['tire_coverage'][index]/(rect.height*.35))
            length=rect.height*(.1+.9*amount)
            car['tire_paint'][index]={'length':length,'remaining':length,
                'alpha':strongest[0],'color':strongest[1]}
        else:
            car['tire_contact'][index]=False
    car['previous_tires']=points

def maskhit(a,b):
    return bool(a['rect'].colliderect(b['rect']) and pg.mask.from_surface(a['img']).overlap(pg.mask.from_surface(b['img']),(b['rect'].x-a['rect'].x,b['rect'].y-a['rect'].y)))
def persist(mode,score):
    if score>best.get(mode,0):
        best[mode]=score
        try: scores.parent.mkdir(parents=True,exist_ok=True);scores.write_text(json.dumps(best))
        except OSError: pass

# Small, distinct illustrations make pickups recognizable without reading text.
def make_pickup_icon(kind):
    icon=pg.Surface((52,52),pg.SRCALPHA)
    colors={'ammo':(224,179,46),'armor':(70,166,220),'slow':(130,104,210),'repellent':(80,173,102)}
    pg.draw.circle(icon,(35,35,35),(26,26),25)
    pg.draw.circle(icon,colors[kind],(26,26),22)
    white=(255,255,240)
    if kind=='ammo':
        pg.draw.polygon(icon,white,[(29,5),(14,29),(24,29),(21,47),(39,21),(29,21)])
    elif kind=='armor':
        pg.draw.polygon(icon,white,[(26,7),(41,13),(39,29),(26,44),(13,29),(11,13)],3)
        pg.draw.line(icon,white,(26,14),(26,35),3)
    elif kind=='slow':
        pg.draw.circle(icon,white,(26,27),15,3)
        pg.draw.line(icon,white,(26,27),(26,16),3);pg.draw.line(icon,white,(26,27),(34,31),3)
        pg.draw.rect(icon,white,(22,6,8,4))
    else:
        pg.draw.rect(icon,white,(17,18,19,24),border_radius=4)
        pg.draw.rect(icon,white,(20,12,13,6));pg.draw.line(icon,white,(27,12),(34,8),3)
        for x,y in [(37,8),(41,5),(43,11)]:pg.draw.circle(icon,white,(x,y),2)
    return icon

PICKUP_ICONS={kind:make_pickup_icon(kind) for kind in ('ammo','armor','slow','repellent')}

def recharge_zapper(cars, now, next_charge):
    if now>=next_charge:
        charges=(now-next_charge)//10000+1
        for c in cars:
            if c['alive']: c['state'].ammo+=charges
        next_charge+=charges*10000
    return next_charge

def play():
    cars=[car(0,W//2 if options.players==1 else 350)]
    if options.players==2: cars.append(car(1,650))
    spiders=[]; splats=[]; pickups=[]; shots=[]; trees=[]; trails=[]
    frame=0; score=0; quiz=None; answer=''; paused_until=0
    next_charge=pg.time.get_ticks()+10000
    # Start with foliage already lining both sides of the road.
    for y in range(-100,H+80,45):
        for edge in (0,1):
            x=random.randrange(-55,30) if edge==0 else random.randrange(W-120,W-35)
            trees.append([x,y+random.randrange(-18,19)])
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
                    for sp in spiders: splats.append(make_splat(sp))
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
        next_charge=recharge_zapper(cars,now,next_charge)
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
        if frame%100==0: pickups.append({'rect':pg.Rect(random.randrange(70,900),-52,52,52),'kind':random.choices(['ammo','armor','slow','repellent'],[5,2,2,2])[0]})
        if frame%3==0:
            trees.append([random.randrange(-55,30),-100])
            trees.append([random.randrange(W-120,W-35),-100])
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
                splats.append(make_splat(hit));spiders.remove(hit);shots.remove(shot)
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
        for mark in trails[:]:
            mark[1].y+=speed
            if mark[1].top>H: trails.remove(mark)
        for c in cars:
            if c['alive']: leave_tire_tracks(c,splats,trails,speed)
        screen.fill((131,105,83))
        for surface,rect in trails: screen.blit(surface,rect)
        for img,x,y,alpha,mask,color in splats: screen.blit(img,img.get_rect(center=(x,y)))
        for t in trees:screen.blit(tree,t)
        for sp in spiders:screen.blit(sp['img'],sp['rect'])
        for p in pickups:
            screen.blit(PICKUP_ICONS[p['kind']],p['rect'])
        for shot in shots:pg.draw.rect(screen,(255,240,80),shot)
        for i,c in enumerate(cars):
            if c['alive']:
                screen.blit(c['img'],c['rect'])
                if c['state'].active('armor',now):pg.draw.ellipse(screen,(100,210,255),c['rect'].inflate(16,16),3)
            active=' '.join(k.upper()+':'+str(math.ceil((v-now)/1000)) for k,v in c['state'].effects.items() if v>now)
            text(f'P{i+1} ammo {c["state"].ammo} {active}',10,50+i*28)
        text(f'{int(score)} m   Level {level}',10,10)
        text(f'Next shot: {max(0,math.ceil((next_charge-now)/1000))}s',W-190,10)
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
