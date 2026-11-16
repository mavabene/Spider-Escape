
import sys
import pygame
import random
from pygame.locals import *  # eg    K_UP, K_DOWN,K_LEFT,K_RIGHT,K_ESCAPE,KEYDOWN,QUIT
from pygame import mixer


#from P6_classes import *

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

###################################### Change by Chufan ##########################
# Initializing
pygame.init()
clock = pygame.time.Clock()

######################################## Change end #############################################

# play background jungle sounds (recorded in San Pancho, Mexico, 2021)
mixer.music.load('Jungle.mp3')
mixer.music.play(-1)

# Define constants for the screen width and height
DISPLAY_WIDTH = 1200
DISPLAY_HEIGHT = 800

# Degine speed of screen scrolling and other factors based on it
GAMESPEED = 13
PLAYERSPEED = 2*GAMESPEED/3


################################### Change by Chufan #################################################
screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
#Set Title and Icon for Game Window
pygame.display.set_caption("Spanish Racing")
icon = pygame.image.load('steering-wheel.png')   #import image of icon
pygame.display.set_icon(icon)     #display icon
################################# Change end ###########################################################

# Player initiation
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        Player_width=30
        self.surf = pygame.image.load("Jeep.png").convert()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect()
        self.rect.bottom=DISPLAY_HEIGHT
        self.rect.left=DISPLAY_WIDTH/2-Player_width/2

    # Move the vehicle based on keyboard input
    def update(self, pressed_keys):
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -PLAYERSPEED)
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, PLAYERSPEED)
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-PLAYERSPEED, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(PLAYERSPEED, 0)

        # Keep player on the screen - although can go in the bushes.  Can't see spiders in the bushes though!
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > DISPLAY_WIDTH:
            self.rect.right = DISPLAY_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        elif self.rect.bottom >= DISPLAY_HEIGHT:
            self.rect.bottom = DISPLAY_HEIGHT

# Stationary spiders - if touched player is killed
class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super(Obstacle, self).__init__()
        self.surf = pygame.image.load("spider.png").convert()
        self.surf.set_colorkey((0,0,0), RLEACCEL)
        self.rect = self.surf.get_rect(
            center=(
                random.randint(0, DISPLAY_WIDTH),
                random.randint(-50, -1),  # Have obstacles come on screen at random times
            )
        )
        self.speed = GAMESPEED

    # Move the obstacle based on speed so it appears the screen is moving
    # Remove it when it passes the bottom edge of the screen
    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top > DISPLAY_HEIGHT:
            self.kill()

# Walking spiders - walk in random directions
class Obstacle2(pygame.sprite.Sprite):
    def __init__(self, side):
        super(Obstacle2, self).__init__()
        self.surf = pygame.image.load("spider_mirror.png").convert_alpha() # for animated walking effect
        self.surf.set_colorkey((0,0,0), RLEACCEL)
        self.side = side                           # variable used to initiate image switching for walking effect
        self.move=random.randint(-5,5)
        self.rect = self.surf.get_rect(
            center=(
                random.randint(0, DISPLAY_WIDTH),
                random.randint(-50, -1),  # Have obstacles come on screen at random times
            )
        )
        self.speed = GAMESPEED

    # Remove it when it passes the bottom edge of the screen
    def update(self):
        if self.side < 15:      # sets timing of image switching for waking effect
            self.surf=pygame.image.load("spider.png").convert_alpha()
            self.side = self.side + 1
        elif self.side < 30:
            self.surf=pygame.image.load("spider_mirror.png").convert_alpha()
            self.side=self.side+1
        else:
            self.side=0  # resets timer for walking effect
        self.rect.move_ip(self.move, self.speed/1.5+self.move/2)
        if self.rect.top > DISPLAY_HEIGHT:
            self.kill()

# Adding target spiders for bonus round
# Target spiders can be killed by quiz round
# Start at top of screen and slowly descend, allowing time to type in quiz answer and kill spiders
class Target_Spider(pygame.sprite.Sprite):

    def __init__(self, side):
        super(Target_Spider, self).__init__()
        self.surf = pygame.image.load("spider_mirror.png").convert_alpha()
        self.surf.set_colorkey((0,0,0), RLEACCEL)
        self.side = side
        self.move=0
        self.rect = self.surf.get_rect(
            center=(
                random.randint(0, DISPLAY_WIDTH),
                random.randint(-50, -1),  # Have obstacles come on screen at random times
            )
        )
        self.speed = GAMESPEED/4
    # Remove it when it passes the bottom edge of the screen
    def update(self):
        global CORRECT

        # ********************* Quiz add *************************
        # Spider has been splatted, so don't update back to spider
        if CORRECT:
            self.side = 50
            self.speed=GAMESPEED

        # **********************************************************
        # Set up animation
        if self.side < 15:
            self.surf=pygame.image.load("spider.png").convert_alpha()
            self.side = self.side + 1
        elif self.side < 30:
            self.surf=pygame.image.load("spider_mirror.png").convert_alpha()
            self.side=self.side+1
        elif self.side <40:
            self.side=0


        self.rect.move_ip(self.move, self.speed)

        if self.rect.top > DISPLAY_HEIGHT:
            self.kill()

    
    # Remove it when it passes the bottom edge of the screen

#     def update(self):
#         global CORRECT
#         if self.side < 15:
#             self.surf=pygame.image.load("spider.png").convert_alpha()
#             self.side = self.side + 1
#         elif self.side < 30:
#             self.surf=pygame.image.load("spider_mirror.png").convert_alpha()
#             self.side=self.side+1
#         else:
#             self.side=0
#         self.rect.move_ip(self.move, GAMESPEED/4)
#
#         # *********************** Quiz add ***************************
#         # Kill spiders if answer is correct
#         if CORRECT:
#             self.surf=pygame.image.load("splat.png").convert_alpha()
#             #moving_scenery.add(self)
#             #obstacles.remove(self)
#         # ************************************************************
#
#         if self.rect.top > DISPLAY_HEIGHT:
#             self.kill()
#
# # ***** Get this to work *****
# class Target_Spider(Obstacle2):
#     def __init__(self, side):
#         super().__init__('Target_Spider')
#         self.move=0
#         CORRECT=False
#
#     def update(self):
#         if self.side < 15:
#             self.surf=pygame.image.load("spider.png").convert_alpha()
#             self.side = self.side + 1
#         elif self.side < 30:
#             self.surf=pygame.image.load("spider_mirror.png").convert_alpha()
#             self.side=self.side+1
#         else:
#             self.side=0
#         self.rect.move_ip(self.move, -GAMESPEED)
#         if CORRECT:
#             self.surf=pygame.image.load("splat.png").convert_alpha()
#         if self.rect.top > DISPLAY_HEIGHT:
#             self.kill()


#  Trees added for scenery.  Jeep can drive in trees, but can't see spiders there.
class Tree1(pygame.sprite.Sprite):
    def __init__(self, side, width):
        super(Tree1, self).__init__()
        self.surf = pygame.image.load("Tree1sm.png").convert()  #  created from photo of desk plant
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)

        # The starting position is randomly generated to fill jungle with random pattern of foliage
        if side > 0:                         # used to swap filling in left and right of screen edge each cycle
            self.rect = self.surf.get_rect(
                center=(
                    random.randint(0, width),
                    random.randint(-width, -20 ),
                    )
                )
        else:
            self.rect = self.surf.get_rect(
                center=(
                    random.randint(DISPLAY_WIDTH-width, DISPLAY_WIDTH),
                    random.randint(-60, -20 ),
                    )
                )

        self.speed = GAMESPEED  # set speed of trees equal to speed of travel of game

    # Remove tree when it passes off the bottom of screen (no longer needed)
    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top > DISPLAY_HEIGHT:
            self.kill()

# Random trees introduced more as level increases - sometimes hide spiders, but mostly decoration and distraction.
class Tree2(pygame.sprite.Sprite):
    def __init__(self):
        super(Tree2, self).__init__()
        self.surf = pygame.image.load("Tree1sm.png").convert()  # ***** add image *****
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        # The starting position is randomly generated

        self.rect = self.surf.get_rect(
            center=(
                random.randint(0, DISPLAY_WIDTH),
                random.randint(-60, -1),
            )
        )

        self.speed = GAMESPEED

    # Remove tree when it passes off the bottom of screen
    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top > DISPLAY_HEIGHT:
            self.kill()

#***************** Quiz Code added *****************************




# ---------------------James Quiz ---------------------
class InputBox():

    def __init__(self, x, y, w, h, text = ''):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.COLOR_INACTIVE = pygame.Color('lightskyblue3')
        self.COLOR_ACTIVE = pygame.Color('dodgerblue2')
        self.FONT = time_font
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.color = self.COLOR_INACTIVE
        self.text = text
        #self.txt_surface = self.FONT.render(text, True, self.color)
        self.active = False
        self.show = True
        

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
            # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = self.COLOR_ACTIVE if self.active else self.COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            #if self.active and not self.end:
            if event.key == pygame.K_RETURN:
                # print(self.text)
                # self.text = ''
                Quiz1.answer=self.text
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode

         # Re-render the text.
    def draw(self):
        if not CORRECT:
            self.txt_surface = self.FONT.render(self.text, True, self.color)
            screen.blit(self.txt_surface, (self.x +20, self.y + 10))
        

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    #def draw(self, screen):
        # Blit the rect.
        
        # Blit the text.
        #screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))

class Quiz():
    def __init__(self):

        words = ['gato', 'perro','caballo','naranja','facil','lapiz']
        answers = ['cat','dog','horse','orange','easy','pencil']
        idxlen=len(words)-1
        idx = random.randint(0, idxlen)
        self.spanword = words[idx]
        self.engword = answers[idx]
        self.answer=''
        self.show = True
        # self.screen = pygame.display.set_mode((640, 480))  # don't want to change game screen . .

        global CORRECT  # used to transition quiz modes and implement side effects of successful answer in sprite groups
        CORRECT = False

        global QUIZ  # initiates updating call where code calls updates for classes
        QUIZ = True

        #self.quiz_box = InputBox(DISPLAY_WIDTH+20,DISPLAY_HEIGHT-20,DISPLAY_WIDTH/2, DISPLAY_HEIGHT/10,self.spanword)

    def update(self):
        global CORRECT

        if self.show:
        # update quiz_box
        #self.quiz_box.handle_event(event)
        #self.quiz_box.update()
            quiz_text = time_font.render('Translate “' + self.spanword + '” :', True, grey)
            draw_rect_alpha(screen, (255, 255, 255, 200), (270, 25, 450, 100), 10)
            pygame.draw.rect(screen, blackish, (270, 22, 450, 106), 3, 10)

            screen.blit(quiz_text, (290, 32))

        # self.quiz_box.draw(self.screen)
        # pygame.display.flip()

            if self.answer == self.engword:
                CORRECT = True
                self.show = False
            

#

#***************************************************************

########################################## Change by Chufan ############################################################


################  Initialize font and color  ################
time_font = pygame.font.Font("digital-7.ttf", 40) # The milometer font
welcome_font = pygame.font.Font("Grindcore Records.otf", 100)
start_font = pygame.font.SysFont("freesansbold.ttf", 100)
retry_font = pygame.font.SysFont("freesansbold.ttf", 70)
over_font = pygame.font.Font('Scary Font.ttf', 80)
over_font_outline = pygame.font.Font('Scary Font.ttf', 85)
score_font = pygame.font.Font('Scary Font.ttf', 40)
direction_font = pygame.font.SysFont("freesansbold.ttf", 50)

slategrey = (112, 128, 144)
lightgrey = (165, 175, 185)
blackish = (10, 10, 10)
yellow = (222, 192, 100)
red = (204, 0, 0)
dark_red = (102, 0, 0)
dark_yellow = (180, 95, 6)
orange = (252, 173, 3) 
white = (255, 255, 255)
brown = (102, 51, 0)
grey = (64, 64, 64)

################ Function to create a button ###############################
def create_button(x, y, width, height, hovercolor, defaultcolor):
    mouse = pygame.mouse.get_pos()
    #Mouse get pressed can run without an integer, but needs a 3 or 5 to indicate how many buttons
    click = pygame.mouse.get_pressed(3) 
    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        pygame.draw.rect(screen, hovercolor, (x, y, width, height), border_radius= 15)
        if click[0] == 1:
            return True
    else:
        pygame.draw.rect(screen, defaultcolor, (x, y, width, height), border_radius= 15)

################### Create a start menu ###########################################
def start_menu():
    global game_start_time

    game_start_time = None

    startText = welcome_font.render('Escape the Yucatan Jungle!', True, yellow)
    startbuttontext = start_font.render('START!', True, yellow)
    DirectionText = direction_font.render('Direction : Dodge spiders using', True, yellow)
    DirectionText_2 = direction_font.render('arrow keys', True, yellow)
    DirectionText_3 = direction_font.render('Be careful of poor visibility in the trees!', True, yellow)
    #DirectionText_4 = direction_font.render('- Visibility is poor!', True, yellow)
    background = pygame.image.load('background.jpg')
    right_arrow = pygame.image.load('right_arrow.png')
    up_arrow = pygame.transform.rotate(right_arrow, 90)
    left_arrow = pygame.transform.rotate(right_arrow, 180)
    down_arrow = pygame.transform.rotate(right_arrow, 270)

    running = True

    while running:

        # set framerate and speed of game to be consistent across platforms
        clock.tick(30)
        

        # cycle events and take actions:
        for event in pygame.event.get():
            # Key pressed?
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:  # ending game if escape pressed
                    running = False
                    pygame.quit()
                    quit()

            # If window close button clicked:
            elif event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()

        # Draw background
        screen.blit(background, (0, 0))

        # Draw Title
        screen.blit(startText, ((DISPLAY_WIDTH)/2 - 370, (DISPLAY_HEIGHT)/2 - 250))

        # Draw direction
        draw_rect_alpha(screen, (180, 95, 6, 200), (DISPLAY_WIDTH/2 - 350, DISPLAY_HEIGHT/2 + 100, 690, 210), 15)
        screen.blit(DirectionText, ((DISPLAY_WIDTH)/2 - 270, (DISPLAY_HEIGHT)/2 + 120))
        screen.blit(DirectionText_2, ((DISPLAY_WIDTH)/2 + 70, (DISPLAY_HEIGHT)/2 + 190))
        screen.blit(DirectionText_3, ((DISPLAY_WIDTH)/2 - 325, (DISPLAY_HEIGHT)/2 + 260))
        screen.blit(right_arrow, ((DISPLAY_WIDTH)/2 - 10, (DISPLAY_HEIGHT)/2 + 170))
        screen.blit(up_arrow, ((DISPLAY_WIDTH)/2 - 250, (DISPLAY_HEIGHT)/2 + 170))
        screen.blit(left_arrow, ((DISPLAY_WIDTH)/2 - 90, (DISPLAY_HEIGHT)/2 + 170))
        screen.blit(down_arrow, ((DISPLAY_WIDTH)/2 - 170, (DISPLAY_HEIGHT)/2 + 170))
        
        
        
        #Draw start button
        start_button = create_button(DISPLAY_WIDTH/2-150, (DISPLAY_HEIGHT)/2 - 70, 300, 100, red, dark_red)
        screen.blit(startbuttontext, (DISPLAY_WIDTH/2 - 120, DISPLAY_HEIGHT/2 -50 ))

        # When start button is pressed, jump to the game
        if start_button:
            game_start_time = pygame.time.get_ticks()
            main()
            
        #Start Button Text
        
        
        pygame.display.update()
        clock.tick(15)

######################### Scoring ######################################################
##### Transparent Rectangle ############
def draw_rect_alpha(surface, color, rect, border): 
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect(), border_radius = border)
    surface.blit(shape_surf, rect)

###### Milometer Dashboard ###############
def score():
    #global counting_seconds
    #counting_time = pygame.time.get_ticks() - game_start_time
    #counting_seconds = str((counting_time%60000)//1000)
    #counting_text = time_font.render( str(counting_seconds) + " m", True, grey)
    milometer = pygame.image.load('steering-wheel.png')
    draw_rect_alpha(screen, (255, 255, 255, 100), (50, 25, 180, 50), 10) # Draw tranparent dashboard
    pygame.draw.rect(screen, blackish, (50, 22, 181, 56), 3, border_radius= 15)
    screen.blit(milometer, (15, 18))
    pygame.display.update()

######################## End Page #####################################################
#Game Over

def show_score():
    global game_start_time
    over_text_outline = over_font_outline.render('SPIDER ATTACK!', True, dark_red)
    over_text = over_font.render('SPIDER ATTACK!', True, white)
    score = score_font.render('Traveled  ' + str(meter) + '  Meters', True, white)
    retrybuttontext = retry_font.render('Try Again!', True, yellow)

    
    running = True

    while running:

        # cycle events and take actions:
        for event in pygame.event.get():
            # Key pressed?
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:  # ending game if escape pressed
                    running = False
                    pygame.display.quit()
                    quit()

            # If window close button clicked:
            elif event.type == pygame.QUIT:
                running = False
                pygame.display.quit()
                quit()

        #Draw start button
        retry_button = create_button(DISPLAY_WIDTH/2-165, (DISPLAY_HEIGHT)/2 + 130, 300, 90, red, dark_red)
        screen.blit(retrybuttontext, (DISPLAY_WIDTH/2 - 130, DISPLAY_HEIGHT/2 + 150 ))

        # When start button is pressed, jump to the game
        if retry_button:
            game_start_time = pygame.time.get_ticks()
            main()

        screen.blit(over_text_outline, (150, 255))
        screen.blit(over_text, (170, 240))
        screen.blit(score, (DISPLAY_WIDTH/2-225, DISPLAY_HEIGHT/2 + 15))
        pygame.display.update()
        
    

########################################################## Change end ##########################################################################

def main():

    global LEVEL, meter

    #************************** Quiz add **************************
    # global so update only called during Quiz levels
    global QUIZ, Quiz1
    QUIZ = False
    global CORRECT  # used to transition quiz modes and implement side effects of successful answer in sprite groups
    CORRECT = False
    #**************************************************************

#############################################   Change by Chufan, debug score reset and width error #####################################
    # Variable to keep our main loop running
    running = True
    side=1
    mileage = 0 # Total mileage the player runs
    LEVEL = 1 # Move LEVEL assignment here to reset level each game
################################################  Change end ##########################################################################

    

    # Create events.
    AddObstacle = pygame.USEREVENT + 1        # ensure individual index for event
    AddTree1 = pygame.USEREVENT + 2
    AddObstacle2 = pygame.USEREVENT + 3
    AddTree2 = pygame.USEREVENT + 4
    AddTargetSpider = pygame.USEREVENT + 5

    # Initialize difficulty
    # if LEVEL < 500:
    if LEVEL < 500: # !!!!!!!!!!!!!!!!!!!! temp for Quiz test - return to 500 !!!!!!!!!!!!!!!!!!!!!!!!!
        pygame.time.set_timer(AddObstacle, 700)  # interval for adding obstacles in ms
        pygame.time.set_timer(AddObstacle2, 0)    ############ Changed by Chufan to reset for a new game #############################
        pygame.time.set_timer(AddTree1, 20)
        pygame.time.set_timer(AddTree2, 4000)
        pygame.time.set_timer(AddTargetSpider, 0) ############ Changed by Chufan to reset for a new game #############################
        width=60

    # Create our 'player'
    player = Player()


    # Create groups to hold sprites for group management
    # - all_sprites is used for rendering
    obstacles = pygame.sprite.Group()  # obstacles kill player upon contact - must be avoided
    scenery = pygame.sprite.Group()
    moving_scenery = pygame.sprite.Group()     # for screen scrolling - traveling effect.  scenery does not hurt player
    all_sprites = pygame.sprite.Group()  # used to update display each cycle
    all_sprites.add(player)  # player always added to all_sprites
    type_box = InputBox(290, 64, 400, 50)
    

    # Game loop
    while running:

        # set framerate and speed of game to be consistent across platforms
        clock.tick(30)

        # Check for key presses
        pressed_keys = pygame.key.get_pressed()
        player.update(pressed_keys)

        # Update the position of objects ----------------------------------------------------------UPDATE
        obstacles.update()
        moving_scenery.update()


        # create a dirt colored background
        screen.fill((131, 105, 83))
        

        # Draw objects
        for entity in all_sprites:
            screen.blit(entity.surf, entity.rect)

############################################## Change by Chufan ##########################################################
        # Display mileage the player runs
        mileage += 0.5
        meter = int(mileage)
        mileage_text = time_font.render(str(meter) + " m", True, grey)
        milometer = pygame.image.load('steering-wheel.png')
        draw_rect_alpha(screen, (255, 255, 255, 100), (50, 25, 180, 50), 10) # Draw tranparent dashboard
        pygame.draw.rect(screen, blackish, (50, 22, 181, 56), 3, border_radius= 15)
        screen.blit(milometer, (15, 18))
        screen.blit(mileage_text, (95,32))


################################################ Change end #################################################################

################################# Display the quiz #######################################################
        if QUIZ:
            Quiz1.update()

        # cycle events and take actions:
            for event in pygame.event.get():
                # Key pressed?
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:  # ending game if escape pressed
                        running = False
                        pygame.display.quit()
                        quit()

                # If window close button clicked:
                elif event.type == pygame.QUIT:
                    running = False
                    pygame.display.quit()
                    quit()

                # If it is time to add object:
                elif event.type == AddObstacle:  # Add spiders if it's time
                    new_obstacle = Obstacle()
                    moving_scenery.add(new_obstacle)
                    all_sprites.add(new_obstacle)

                elif event.type == AddObstacle2:  # Add walking spider if it's time
                    new_obstacle = Obstacle2(1)
                    obstacles.add(new_obstacle)
                    all_sprites.add(new_obstacle)

                elif event.type == AddTargetSpider:  # Add target spider if it's time
                    new_spider = Target_Spider(1)
                    moving_scenery.add(new_spider)
                    all_sprites.add(new_spider)

                elif event.type == AddTree1:  # Add scenery trees if it's time
                    new_tree = Tree1(side, width)
                    moving_scenery.add(new_tree)
                    all_sprites.add(new_tree)
                    side=side*(-1)

                elif event.type == AddTree2: # Add distraction trees if it's time
                    new_tree = Tree2()
                    moving_scenery.add(new_tree)
                    all_sprites.add(new_tree)
#splat
                type_box.handle_event(event)
            type_box.draw()

        else:

            CORRECT = False
            for event in pygame.event.get():
                # Key pressed?
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:  # ending game if escape pressed
                        running = False
                        pygame.display.quit()
                        quit()

                # If window close button clicked:
                elif event.type == pygame.QUIT:
                    running = False
                    pygame.display.quit()
                    quit()

                # If it is time to add object:
                elif event.type == AddObstacle:  # Add spiders if it's time
                    new_obstacle = Obstacle()
                    moving_scenery.add(new_obstacle)
                    all_sprites.add(new_obstacle)

                elif event.type == AddObstacle2:  # Add walking spider if it's time
                    new_obstacle = Obstacle2(1)
                    obstacles.add(new_obstacle)
                    all_sprites.add(new_obstacle)

                elif event.type == AddTargetSpider:  # Add target spider if it's time
                    new_spider = Target_Spider(1)
                    moving_scenery.add(new_spider)
                    all_sprites.add(new_spider)

                elif event.type == AddTree1:  # Add scenery trees if it's time
                    new_tree = Tree1(side, width)
                    moving_scenery.add(new_tree)
                    all_sprites.add(new_tree)
                    side=side*(-1)

                elif event.type == AddTree2: # Add distraction trees if it's time
                    new_tree = Tree2()
                    moving_scenery.add(new_tree)
                    all_sprites.add(new_tree)

        if CORRECT:
            for item in obstacles:
                item.speed = GAMESPEED
                angle=random.randint(0, 359)
                rot_image=pygame.image.load("splat.png").convert_alpha()
                item.surf = pygame.transform.rotate(rot_image, angle)
                moving_scenery.add(item)
                obstacles.remove(item)
                # Quiz1 = Quiz()


###########################################################################################################

        
        # Check if player has collided with any obstacles and end game if so
        if pygame.sprite.spritecollideany(player, obstacles):
            print("You are spider lunch!!")
            player.kill()


            show_score()

        # Leveling - keep track of and implement next levels
        LEVEL=LEVEL+1
        # level_text = start_font.render(str(LEVEL), True, dark_red)
        # screen.blit(level_text, (95,32))

        if LEVEL == 500: # Quiz Level  # !!!!!!!!!!!!!!!!!!!! temp for Quiz test - return to 500 !!!!!!!!!!!!!!!!!!!!!!!!!
            pygame.time.set_timer(AddTree1, 20)
            pygame.time.set_timer(AddTargetSpider, 1200)
            pygame.time.set_timer(AddObstacle, 80000)  # interval for adding obstacles in ms
            pygame.time.set_timer(AddObstacle2, 20000)
            pygame.time.set_timer(AddTree2, 3000)
            width=100
            Quiz1=Quiz()
            # Quiz1=Translation()

        if LEVEL == 1000:
            QUIZ = False
            pygame.time.set_timer(AddTree1, 20)
            pygame.time.set_timer(AddObstacle, 600)  # interval for adding obstacles in ms
            pygame.time.set_timer(AddObstacle2, 2000)
            pygame.time.set_timer(AddTree2, 3000)
            pygame.time.set_timer(AddTargetSpider, 20000)
            width=100

        if LEVEL == 1500: # Quiz Level
            pygame.time.set_timer(AddTree1, 15)
            pygame.time.set_timer(AddObstacle, 400000)  # interval for adding obstacles in ms
            pygame.time.set_timer(AddObstacle2, 1000)
            pygame.time.set_timer(AddTree2, 2000)
            pygame.time.set_timer(AddTargetSpider, 1000)
            width=120
            Quiz1 = Quiz()

        if LEVEL == 2000:
            QUIZ=False
            pygame.time.set_timer(AddTree1, 20)
            pygame.time.set_timer(AddObstacle, 600)  # interval for adding obstacles in ms
            pygame.time.set_timer(AddObstacle2, 1500)
            pygame.time.set_timer(AddTree2, 3000)
            pygame.time.set_timer(AddTargetSpider, 20000)
            width = 120

        if LEVEL == 2500: # Quiz Level
            pygame.time.set_timer(AddTree1, 10)
            pygame.time.set_timer(AddObstacle, 40000)  # interval for adding obstacles in ms
            pygame.time.set_timer(AddObstacle2, 70000)
            pygame.time.set_timer(AddTree2, 1000)
            pygame.time.set_timer(AddTargetSpider, 800)
            width = 140
            Quiz1 = Quiz()

        if LEVEL == 3000:
            QUIZ=False
            pygame.time.set_timer(AddTree1, 10)
            pygame.time.set_timer(AddObstacle, 400000)  # interval for adding obstacles in ms
            pygame.time.set_timer(AddObstacle2, 600)
            pygame.time.set_timer(AddTree2, 1000)
            pygame.time.set_timer(AddTargetSpider, 20000)
            width = 140

        if LEVEL == 3500:  # Quiz Level
            pygame.time.set_timer(AddTree1, 3)
            pygame.time.set_timer(AddObstacle, 20000)  # interval for adding obstacles in ms
            pygame.time.set_timer(AddObstacle2, 50000)
            pygame.time.set_timer(AddTree2, 400)
            pygame.time.set_timer(AddTargetSpider, 600)
            width = 160
            Quiz1 = Quiz()

        if LEVEL > 4000:
            QUIZ=False
            if LEVEL%1000==0:
                # set final round to continue increasing in difficulty every 1000 infinitely until Game Over
                final = 4000/LEVEL
                int(round(final))
                pygame.time.set_timer(AddTree1, 3)
                pygame.time.set_timer(AddObstacle, int(round(2000*final)))
                pygame.time.set_timer(AddObstacle2, int(round(500*final)))
                pygame.time.set_timer(AddTree2, int(round(300*final)))
                pygame.time.set_timer(AddTargetSpider, int(round(10000*final)))
                width = 180

        # Display all updates
        pygame.display.flip()

################################### Change by Chufan #############################
#if __name__ == "__main__":
#    main()
running = True

while running:

    # set framerate and speed of game to be consistent across platforms
    clock.tick(30)
    

    # cycle events and take actions:
    for event in pygame.event.get():
        # Key pressed?
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:  # ending game if escape pressed
                running = False
                pygame.display.quit()
                quit()

        # If window close button clicked:
        elif event.type == pygame.QUIT:
            running = False
            pygame.display.quit()
            quit()
                
    start_menu()

    pygame.display.update()
    clock.tick(30)

############################## Change by Chufan ######################################