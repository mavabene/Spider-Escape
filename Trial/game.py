"""Spider Escape trial: local cooperative mode, zappers and pickups."""
import json, math, os, random, sys
from pathlib import Path
import pygame as pg
from rules import Options, CarState, COLORS

if getattr(sys,'frozen',False): os.chdir(sys._MEIPASS)
else: os.chdir(Path(__file__).resolve().parent.parent/'Finalp6')
pg.init(); W,H=1000,800
PLAYFIELD_WIDTH = 1280
screen=pg.display.set_mode((W,H)); pg.display.set_caption('Spider Escape 2.0.3')
clock=pg.time.Clock(); font=pg.font.Font(None,30)
try: pg.mixer.music.load('Jungle.mp3'); pg.mixer.music.play(-1)
except pg.error: pass
scores=Path.home()/'Library/Application Support/Spider Escape/trial_scores.json'
try: best=json.loads(scores.read_text())
except (OSError,ValueError): best={}
if not isinstance(best, dict):
    best = {}

MODE_NAMES = {'solo': 'Solo', 'two': 'Two-player'}

def text(msg,x,y,color=(255,245,200),f=font): screen.blit(f.render(msg,True,color),(x,y))
def tint(image,color):
    img=image.copy(); overlay=pg.Surface(img.get_size(),pg.SRCALPHA); overlay.fill((*color,0)); img.blit(overlay,(0,0),special_flags=pg.BLEND_RGBA_ADD); return img
palette={'original':(0,0,0),'blue':(0,45,120),'red':(80,0,0),'green':(0,70,0),'yellow':(65,50,0)}
carimage=pg.image.load('Jeep.png').convert(); carimage.set_colorkey((0,0,0))
spiderfiles = [
    pg.transform.grayscale(pg.image.load(name).convert())
    for name in ('spider.png', 'spider_mirror.png')
]
SPIDER_SHADES = (
    ((11, 6, 2), (25, 13, 5), (38, 20, 8), (45, 29, 14), (51, 34, 20)),
    ((0, 0, 0), (12, 12, 12), (26, 26, 26)),
    ((40, 9, 12), (13, 29, 8), (20, 12, 36)),
)


def make_spider_frames(size):
    shades = random.choices(SPIDER_SHADES, weights=(80, 17, 3))[0]
    color = random.choice(shades)
    frames = []
    for base in spiderfiles:
        frame = pg.transform.scale(base, size)
        frame.fill(color, special_flags=pg.BLEND_RGB_ADD)
        # The original black background receives the same color offset.
        frame.set_colorkey(color)
        frames.append(frame)
    return frames


splatimage=pg.image.load('splat.png').convert_alpha()
tree = pg.image.load('Tree1sm.png').convert()
tree.set_colorkey((0, 0, 0))
tree_alpha = pg.Surface(tree.get_size(), pg.SRCALPHA)
tree_alpha.blit(tree, (0, 0))
BUSH_VARIANTS = [
    pg.transform.rotozoom(pg.transform.flip(tree_alpha, mirrored, False), angle, scale)
    for mirrored in (False, True)
    for angle, scale in ((-24, .58), (18, .76), (-9, .92), (34, 1.12), (8, 1.35))
]
options=Options(); coloridx=[COLORS.index(color) for color in options.colors]

# Match the original title screen while keeping the trial's settings visible.
menu_background = pg.transform.scale(pg.image.load('background.JPG').convert(), (W,H))
menu_title_font = pg.font.Font('Grindcore Records.otf', 88)
menu_button_font = pg.font.Font(None, 62)
menu_font = pg.font.Font(None, 30)
menu_small = pg.font.Font(None, 25)
menu_gold = (222,192,100)
start_rect = pg.Rect(350, 240, 300, 82)
menu_rows = [pg.Rect(215 + 290*(i%2), 530 + 48*(i//2), 280, 42) for i in range(4)]

def draw_menu_scores():
    mode = 'two' if options.players == 2 else 'solo'
    last_run = best.get('last_run')
    last_label = 'Last game'
    last_score = '—'
    if last_run:
        last_label += f' · {MODE_NAMES[last_run["mode"]]}'
        last_score = f'{last_run["score"]} m  ·  {last_run["result"]}'
    high_score = best.get(mode)
    high_value = f'{high_score} m' if high_score is not None else '—'
    panel = pg.Surface((590, 69), pg.SRCALPHA)
    pg.draw.rect(panel, (87, 62, 47, 238), panel.get_rect(), border_radius=12)
    pg.draw.rect(panel, (222, 192, 100, 155), panel.get_rect(), 1, border_radius=12)
    pg.draw.line(panel, (222, 192, 100, 100), (304, 12), (304, 57))
    left = (W - panel.get_width()) // 2
    screen.blit(panel, (left, 16))
    for x, label, value in (
        (left + 18, last_label, last_score),
        (left + 322, f'High score · {MODE_NAMES[mode]}', high_value),
    ):
        text(label, x, 26, menu_gold, menu_small)
        text(value, x, 47)


def draw_menu():
    screen.blit(menu_background,(0,0))
    draw_menu_scores()
    title = menu_title_font.render('Escape the Yucatan Jungle!',True,menu_gold)
    screen.blit(title,title.get_rect(center=(W//2,135)))
    hover = start_rect.collidepoint(pg.mouse.get_pos())
    pg.draw.rect(screen,(204,0,0) if hover else (102,0,0),start_rect,border_radius=15)
    label=menu_button_font.render('START!',True,menu_gold)
    screen.blit(label,label.get_rect(center=start_rect.center))
    panel=pg.Surface((590,250),pg.SRCALPHA)
    pg.draw.rect(panel,(112,82,60,230),panel.get_rect(),border_radius=15)
    screen.blit(panel,(205,500))
    heading=menu_font.render('Choose your game',True,menu_gold)
    screen.blit(heading,heading.get_rect(center=(W//2,515)))
    rows=[
        f'1 / 2   Players: {options.players}',
        f'Q   Quiz: {"ON" if options.quiz_enabled else "OFF"}' + (' (2 players)' if options.players==2 else ''),
        f'C   {"Left" if options.players==2 else "Your"} car: {COLORS[coloridx[0]].title()}',
        f'V   Right car: {COLORS[coloridx[1]].title()}',
    ]
    for rect,label in zip(menu_rows,rows):
        color=(140,103,75) if rect.collidepoint(pg.mouse.get_pos()) else (87,62,47)
        pg.draw.rect(screen,color,rect,border_radius=8)
        pg.draw.rect(screen,(222,192,100),rect,1,border_radius=8)
        screen.blit(menu_small.render(label,True,(255,238,180)),(rect.x+9,rect.y+10))
    controls=['Arrow keys + Space: drive and zap',
              'Two players: left car uses WASD + Z',
              'Collect power-ups; zapper charges every 10 seconds',
              'Enter or click START to play   |   Esc to quit']
    for i,label in enumerate(controls):
        rendered=menu_small.render(label,True,(255,238,180))
        screen.blit(rendered,rendered.get_rect(center=(W//2,640+i*25)))

def menu():
    global screen
    if screen.get_size() != (W, H):
        screen = pg.display.set_mode((W, H))
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

SPIDER_MIN_SCALE = 0.5
SPIDER_MAX_SCALE = 1.5
SPLAT_SCALE = (SPIDER_MIN_SCALE + SPIDER_MAX_SCALE) / 2
HEAVY_SPIDER_SCALE = SPIDER_MIN_SCALE + 0.75 * (SPIDER_MAX_SCALE - SPIDER_MIN_SCALE)
IMPACT_SLOW_MS = 500


def car(index,x):
    img=tint(carimage,palette[COLORS[coloridx[index]]]); return {'img':img,'rect':img.get_rect(center=(x,H-80)),'state':CarState(),'alive':True,'impact_slow_until':0,'previous_tires':None,'tire_paint':[None,None],'tire_coverage':[0.0,0.0],'tire_contact':[False,False]}
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
def hit_spider(car, spider, now, splats):
    """Resolve contact and return whether the spider was splatted."""
    if not car['state'].active('armor', now):
        car['alive'] = False
        return False

    scale = spider['scale']
    if scale < SPLAT_SCALE:
        splats.append(make_splat(spider))
        return True

    car_rect, spider_rect = car['rect'], spider['rect']
    if spider_rect.centerx < car_rect.centerx:
        spider_rect.right = car_rect.left - 1
    else:
        spider_rect.left = car_rect.right + 1
    if scale >= HEAVY_SPIDER_SCALE:
        car['impact_slow_until'] = now + IMPACT_SLOW_MS
    return False


def persist(mode, score, result):
    best[mode] = max(score, best.get(mode, 0))
    best['last_run'] = {'mode': mode, 'score': score, 'result': result}
    try:
        scores.parent.mkdir(parents=True, exist_ok=True)
        pending = scores.with_suffix('.tmp')
        pending.write_text(json.dumps(best))
        pending.replace(scores)
    except OSError:
        pass

# Small, distinct illustrations make pickups recognizable without reading text.
def make_pickup_icon(kind):
    icon=pg.Surface((52,52),pg.SRCALPHA)
    colors={'ammo':(224,179,46),'armor':(70,166,220),'slow':(130,104,210),'repellent':(80,173,102),'flame':(175,48,24)}
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
    elif kind=='repellent':
        pg.draw.rect(icon,white,(17,18,19,24),border_radius=4)
        pg.draw.rect(icon,white,(20,12,13,6));pg.draw.line(icon,white,(27,12),(34,8),3)
        for x,y in [(37,8),(41,5),(43,11)]:pg.draw.circle(icon,white,(x,y),2)
    else:
        pg.draw.polygon(icon,(255,155,35),[(26,5),(28,17),(36,12),(40,29),(36,40),(26,46),(16,42),(12,33),(14,23),(20,29)])
        pg.draw.polygon(icon,(255,235,145),[(26,22),(29,31),(33,29),(34,37),(27,43),(20,39),(20,33)])
    return icon

PICKUP_ICONS={kind:make_pickup_icon(kind) for kind in ('ammo','armor','slow','repellent','flame')}
# Keep the other pickups in the same proportions while doubling flame's
# share of all spawns from 1/23 to 2/23.
PICKUP_WEIGHTS = (5, 2, 2, 2, 22 / 21)
FUEL_ICON = pg.transform.smoothscale(PICKUP_ICONS['flame'], (26, 26))


def draw_fuel_gauge(state, x, player_number=None):
    gauge = pg.Rect(x, 133, 30, 122)
    pg.draw.rect(screen, (42, 30, 24), gauge, border_radius=6)
    inner = gauge.inflate(-6, -6)
    fraction = state.flame_fuel / state.flame_capacity
    if state.flame_fuel:
        height = max(1, round(inner.height * fraction))
        fill = pg.Rect(inner.left, inner.bottom - height, inner.width, height)
        pg.draw.rect(screen, (244, 115, 28), fill, border_radius=4)
        pg.draw.line(screen, (255, 205, 106), (fill.left + 3, fill.top),
                     (fill.right - 4, fill.top), 2)
    pg.draw.rect(screen, menu_gold, gauge, 1, border_radius=6)
    screen.blit(FUEL_ICON, FUEL_ICON.get_rect(midbottom=(gauge.centerx, gauge.top - 4)))
    amount = f'{math.ceil(100 * fraction)}%'
    label = f'P{player_number}  {amount}' if player_number is not None else amount
    caption = menu_small.render(label, True, (255, 245, 200))
    label_rect = caption.get_rect(midtop=(gauge.centerx, gauge.bottom + 5))
    pg.draw.rect(screen, (42, 30, 24), label_rect.inflate(10, 4), border_radius=5)
    screen.blit(caption, label_rect)


def roadside_bush(width, side, y):
    image = random.choice(BUSH_VARIANTS)
    # Occasionally let an isolated bush reach farther into the road.
    edge_offset = random.randint(90, 175) if random.random() < .15 else random.randint(-40, 85)
    x = edge_offset if side == 0 else width - edge_offset
    return {'img': image, 'rect': image.get_rect(midbottom=(x, y))}


def road_bush(width, y):
    image = random.choice(BUSH_VARIANTS)
    x = random.randint(width // 4, width * 3 // 4)
    return {'img': image, 'rect': image.get_rect(midbottom=(x, y))}


def bush_spacing(score, in_road=False):
    progress = min(1.0, score / 1000)
    if in_road:
        return round(480 - 310 * progress), round(900 - 550 * progress)
    return round(24 - 6 * progress), round(84 - 39 * progress)


FLAME_RANGE = 140
FLAME_WIDTH = 108
flame_shape = pg.Surface((FLAME_WIDTH, FLAME_RANGE), pg.SRCALPHA)
FLAME_OUTLINE = [(46, 139), (27, 83), (8, 30), (31, 45), (43, 6),
                 (60, 28), (87, 1), (81, 30), (103, 19), (77, 79), (61, 139)]
pg.draw.polygon(flame_shape, 'white', FLAME_OUTLINE)
FLAME_MASK = pg.mask.from_surface(flame_shape)


def charred(target):
    image = pg.Surface(target['rect'].size, pg.SRCALPHA)
    image.blit(target['img'], (0, 0))
    image.fill((68, 55, 45), special_flags=pg.BLEND_RGB_MULT)
    return image, target['rect'].copy()


def burn_targets(flames, targets, ashes):
    for target in targets[:]:
        for flame in flames:
            rect = target['rect']
            if flame.colliderect(rect) and FLAME_MASK.overlap(
                    pg.mask.from_surface(target['img']), (rect.x-flame.x, rect.y-flame.y)):
                ashes.append(charred(target))
                targets.remove(target)
                break


def flame_glow(color, opacity):
    glow = pg.Surface((48, 48), pg.SRCALPHA)
    for radius in range(23, 0, -1):
        alpha = round(opacity * (1 - radius / 24) ** 1.4)
        pg.draw.circle(glow, (*color, alpha), (24, 24), radius)
    return glow


def make_flame_frames():
    # Use a separate random stream so the animation doesn't affect gameplay.
    rng = random.Random(42)
    particles = [(rng.random(), rng.uniform(-1, 1), rng.uniform(.7, 1.35))
                 for _ in range(50)]
    embers = [(rng.random(), rng.uniform(-1, 1)) for _ in range(17)]
    glows = [flame_glow(color, opacity) for color, opacity in (
        ((255, 246, 190), 240),
        ((255, 194, 65), 210),
        ((255, 115, 30), 170),
        ((225, 62, 18), 116),
        ((142, 51, 25), 65),
    )]
    frames = []
    padding = 15
    center = FLAME_WIDTH // 2 + padding
    for frame in range(24):
        canvas = pg.Surface((FLAME_WIDTH + 2 * padding, FLAME_RANGE + padding), pg.SRCALPHA)
        phase = frame / 24
        visible = sorted((((offset + phase) % 1, drift, size)
                          for offset, drift, size in particles), reverse=True)
        for age, drift, size in visible:
            spread = 4 + age * 38
            curl = math.sin(age * 8 + drift * 5 + phase * math.tau) * 9 * age
            x = center + drift * spread + curl
            y = canvas.get_height() - 5 - age * (FLAME_RANGE - 2)
            diameter = round((16 + 41 * age) * size)
            plume = pg.transform.smoothscale(glows[min(4, int(age * 5))],
                                             (diameter, round(diameter * 1.35)))
            canvas.blit(plume, plume.get_rect(center=(round(x), round(y))))
        for offset, drift in embers:
            age = (offset + phase) % 1
            x = center + drift * (14 + age * 47)
            y = canvas.get_height() - 35 - age * (FLAME_RANGE - 18)
            pg.draw.circle(canvas, (255, 156 + round(76 * (1 - age)), 76,
                                    round(210 * (1 - age))), (round(x), round(y)),
                           2 if age < .55 else 1)
        frames.append(canvas.convert_alpha())
    return frames


FLAME_FRAMES = make_flame_frames()


def draw_flame(flame, frame):
    plume = FLAME_FRAMES[frame % len(FLAME_FRAMES)]
    screen.blit(plume, plume.get_rect(midbottom=flame.midbottom))


def make_zap_frames():
    rng = random.Random(202)
    frames = []
    for _ in range(8):
        glow = pg.Surface((44, 58), pg.SRCALPHA)
        arc = [(22, 7), (22 + rng.randint(-6, 6), 15),
               (22 + rng.randint(-8, 8), 24), (22 + rng.randint(-8, 8), 33),
               (22 + rng.randint(-6, 6), 43), (22, 51)]
        branches = []
        for index, direction in ((2, -1), (3, 1)):
            x, y = arc[index]
            branches.append([(x, y), (x + 5 * direction, y - 4),
                             (x + rng.randint(8, 12) * direction, y - rng.randint(7, 13))])
        for path in [arc, *branches]:
            pg.draw.lines(glow, (58, 91, 247, 48), False, path, 7)
        for path in [arc, *branches]:
            pg.draw.lines(glow, (101, 165, 255, 150), False, path, 3)
        for branch in branches:
            pg.draw.aalines(glow, (186, 217, 255), False, branch)
        pg.draw.aalines(glow, (238, 251, 255), False, arc)
        frames.append(glow)
    return frames


ZAP_FRAMES = make_zap_frames()


def recharge_zapper(cars, now, next_charge):
    if now>=next_charge:
        charges=(now-next_charge)//10000+1
        for c in cars:
            if c['alive']: c['state'].ammo+=charges
        next_charge+=charges*10000
    return next_charge


def hold_final_frame(score, collision):
    label = pg.font.Font(None, 104).render(f'Final score  {score} m', True, (255, 239, 196))
    label.set_alpha(132)
    position = label.get_rect(center=screen.get_rect().center)
    if position.colliderect(collision.inflate(24, 24)):
        if collision.centery >= screen.get_height() // 2:
            position.bottom = collision.top - 16
        else:
            position.top = collision.bottom + 16
    position.clamp_ip(screen.get_rect())
    screen.blit(label, position)
    pg.display.flip()

    deadline = pg.time.get_ticks() + 5000
    while pg.time.get_ticks() < deadline:
        if any(event.type == pg.QUIT for event in pg.event.get()):
            return False
        clock.tick(30)
    return True


def play():
    global screen
    width = PLAYFIELD_WIDTH
    if screen.get_size() != (width, H):
        screen = pg.display.set_mode((width, H))
    cars = [car(0, width * 35 // 100 if options.players == 2 else width // 2)]
    if options.players == 2:
        cars.append(car(1, width * 65 // 100))
    spiders=[]; splats=[]; pickups=[]; shots=[]; bushes=[]; trails=[]
    ashes = []
    frame=0; score=0; quiz=None; answer=''; paused_until=0
    next_charge=pg.time.get_ticks()+10000
    bush_gap = [0, 0]
    for edge in (0, 1):
        y = random.randint(0, 42)
        while y < H + 150:
            bushes.append(roadside_bush(width, edge, y))
            y += random.randint(*bush_spacing(0))
    bushes.append(road_bush(width, random.randint(180, 420)))
    road_bush_gap = random.randint(*bush_spacing(0, in_road=True))
    words=[('gato','cat'),('perro','dog'),('caballo','horse'),('naranja','orange'),('facil','easy'),('lapiz','pencil')]
    mode = 'two' if options.players == 2 else 'solo'
    result = 'Spider attack!'
    running=True
    while running:
        dt=min(clock.tick(30),80); now=pg.time.get_ticks(); frame+=1; score+=0.5; level=int(score//250)+1
        for e in pg.event.get():
            if e.type==pg.QUIT: return False
            if e.type!=pg.KEYDOWN: continue
            if e.key==pg.K_ESCAPE:
                result = 'Run ended'
                running=False
                break
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
                    if c['alive'] and not c['state'].flame_fuel and c['state'].fire():
                        shots.append(pg.Rect(c['rect'].centerx-4,c['rect'].top-14,8,18))
        if not running: break
        next_charge=recharge_zapper(cars,now,next_charge)
        keys=pg.key.get_pressed()
        for i,c in enumerate(cars):
            if not c['alive']:continue
            controls=(pg.K_w,pg.K_s,pg.K_a,pg.K_d) if options.players==2 and i==0 else (pg.K_UP,pg.K_DOWN,pg.K_LEFT,pg.K_RIGHT)
            u,d,l,r=controls
            drive_speed = 5 if now < c['impact_slow_until'] else 9
            c['old'] = c['rect'].copy()
            c['rect'].move_ip((keys[r]-keys[l])*drive_speed,(keys[d]-keys[u])*drive_speed)
            c['rect'].clamp_ip(screen.get_rect())
        if len(cars)==2 and all(c['alive'] for c in cars) and cars[0]['rect'].colliderect(cars[1]['rect']):
            cars[0]['rect']=cars[0]['old'];cars[1]['rect']=cars[1]['old']
            cars[0]['rect'].x-=8;cars[1]['rect'].x+=8
            for c in cars:c['rect'].clamp_ip(screen.get_rect())
        if frame%max(15,45-level*2)==0:
            scale = max(SPIDER_MIN_SCALE, min(SPIDER_MAX_SCALE, random.gauss(1, .18)))
            side = random.randrange(2)
            frames = make_spider_frames((round(135 * scale), round(123 * scale)))
            img = frames[side]
            spiders.append({
                'frames': frames, 'img': img,
                'rect': img.get_rect(center=(random.randrange(30, width - 30), -50)),
                'scale': scale, 'side': side, 'dx': random.choice([-2, 2]),
                'chase': level >= 3 and random.random() < min(.65, .2 + level * .03),
            })
        if frame%100==0:
            kind = random.choices(tuple(PICKUP_ICONS), PICKUP_WEIGHTS)[0]
            pickups.append({'rect': pg.Rect(random.randrange(70,width-100),-52,52,52), 'kind': kind})
        if options.quiz_enabled and frame%1000==0: quiz=random.choice(words);answer='';paused_until=now+10000
        if quiz and now>=paused_until:quiz=None;answer=''
        slowed=any(c['alive'] and c['state'].active('slow',now) for c in cars);speed=6 if slowed else 13
        for edge in (0, 1):
            bush_gap[edge] -= speed
            if bush_gap[edge] <= 0:
                bushes.append(roadside_bush(width, edge, bush_gap[edge]))
                bush_gap[edge] += random.randint(*bush_spacing(score))
        road_bush_gap -= speed
        if road_bush_gap <= 0:
            bushes.append(road_bush(width, road_bush_gap))
            road_bush_gap += random.randint(*bush_spacing(score, in_road=True))
        for bush in bushes:
            bush['rect'].y += speed
        bushes[:] = [bush for bush in bushes if bush['rect'].top < H]
        for _, rect in ashes:
            rect.y += speed
        ashes[:] = [(image, rect) for image, rect in ashes if rect.top < H]
        flames = []
        for i, c in enumerate(cars):
            fire_key = pg.K_z if options.players == 2 and i == 0 else pg.K_SPACE
            if c['alive'] and keys[fire_key] and c['state'].use_flame(dt):
                flames.append(flame_shape.get_rect(midbottom=c['rect'].midtop))

        for sp in spiders[:]:
            alive=[c for c in cars if c['alive']]
            if sp['chase'] and alive:
                target=min(alive,key=lambda c:abs(c['rect'].centerx-sp['rect'].centerx)); delta=target['rect'].centerx-sp['rect'].centerx
                sp['dx']=max(-4,min(4,delta/25))
                # A mirrored frame faces the direction of movement.
                sp['side']=int(sp['dx']>0)
            sp['img']=sp['frames'][(sp['side'] + (frame//15)%2)%2]
            sp['rect'].move_ip(sp['dx'],speed*.65)
            if sp['rect'].top>H:spiders.remove(sp)
        if flames:
            burn_targets(flames, bushes, ashes)
            burn_targets(flames, spiders, ashes)
        crash_car = None
        crash_area = None
        for sp in spiders[:]:
            for c in cars:
                if c['alive'] and c['state'].active('repellent',now) and math.dist(c['rect'].center,sp['rect'].center)<180: sp['rect'].x+=-8 if sp['rect'].centerx<c['rect'].centerx else 8
                if c['alive'] and maskhit(c, sp):
                    if hit_spider(c, sp, now, splats):
                        spiders.remove(sp)
                        break
                    if not any(player['alive'] for player in cars):
                        crash_car = c
                        crash_area = c['rect'].union(sp['rect'])
                        break
            if crash_car is not None:
                break
        if crash_car is None:
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
            for mark in trails[:]:
                mark[1].y+=speed
                if mark[1].top>H: trails.remove(mark)
            for c in cars:
                if c['alive']: leave_tire_tracks(c,splats,trails,speed)
        screen.fill((131,105,83))
        for image,rect in ashes: screen.blit(image,rect)
        for surface,rect in trails: screen.blit(surface,rect)
        for img,x,y,alpha,mask,color in splats: screen.blit(img,img.get_rect(center=(x,y)))
        for c in cars:
            if c['alive'] or c is crash_car:
                screen.blit(c['img'],c['rect'])
                if c['state'].armor_visible(now):
                    pg.draw.ellipse(screen,c['state'].armor_color(now),c['rect'].inflate(16,16),3)
        for bush in bushes:
            image = bush['img']
            if crash_area is not None and bush['rect'].colliderect(crash_area):
                image = image.copy()
                image.set_alpha(72)
            screen.blit(image, bush['rect'])
        for sp in spiders:screen.blit(sp['img'],sp['rect'])
        for p in pickups:
            screen.blit(PICKUP_ICONS[p['kind']],p['rect'])
        for shot in shots:
            arc = ZAP_FRAMES[(frame + shot.centerx) % len(ZAP_FRAMES)]
            screen.blit(arc, arc.get_rect(center=shot.center))
        for flame in flames: draw_flame(flame,frame)
        for i,c in enumerate(cars):
            active=' '.join(k.upper()+':'+str(math.ceil((v-now)/1000)) for k,v in c['state'].effects.items() if v>now)
            text(f'P{i+1} ammo {c["state"].ammo} {active}',10,50+i*28)
            player_number = i + 1 if len(cars) == 2 else None
            gauge_x = 31 if player_number == 1 else width - 61
            draw_fuel_gauge(c['state'], gauge_x, player_number)
        text(f'{int(score)} m   Level {level}',10,10)
        text(f'Next shot: {max(0,math.ceil((next_charge-now)/1000))}s',width-190,10)
        if quiz and crash_car is None:
            quiz_left = (width - 500) // 2
            pg.draw.rect(screen,(45,45,45),(quiz_left,15,500,115),border_radius=8)
            text(f'Translate {quiz[0]}: {answer}',quiz_left+20,30)
            text(f'Time left: {max(0,math.ceil((paused_until-now)/1000))}',quiz_left+20,70)
        if crash_area is not None:
            persist(mode, int(score), result)
            return hold_final_frame(int(score), crash_area)
        pg.display.flip()
    persist(mode, int(score), result)
    return True

if __name__=='__main__':
    while menu():
        if not play():break
    pg.quit()
