import pygame as pg
pg.init()
vec = pg.math.Vector2
# Algumas core usáveis
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
AQUA_BLUE = (24,35,71)
# Configurações da tela
WIDTH = 1024   # 16 * 64 or 32 * 32 or 64 * 16
HEIGHT = 720  # 16 * 48 or 32 * 24 or 64 * 12
FPS = 60
TITLE = "Tilemap Demo"
BGCOLOR = AQUA_BLUE

TILESIZE = 1
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

# Config dos projéteis
BULLET_IMG = 'stickAttack.png'
BULLET_SPEED = 500
BULLET_LIFETIME = 1000
BULLET_RATE = 400
BULLET_SIZE = 19
BULLET_COLOR = (15,15,15)
BARREL_OFFSET = vec(0, 0)   # (27,24) ; (0,0)
BULLET_DAMAGE = 15
bullets = []

GUN_SPREAD = 5

#Layers
WALL_LAYER = 1
PLAYER_LAYER = 1
BULLET_LAYER = 3
MOB_LAYER = 2
EFFECTS_LAYER = 4
ITEMS_LAYER = 1

MOUSE = pg.mouse.get_pos()
MOUSE_STATE = False


# Player settings
PLAYER_HEALTH = 200
PLAYER_SPEED = 300
PLAYER_ROT_SPEED = 250
PLAYER_IMG = 'gatoR.png'
PLAYER_IMG_INV = 'gatoL.png'
PLAYER_SIZE = 0.19
POS_PLAYER = (1, 2)
PLAYER_HIT_RECT = pg.Rect(0, 0, 35, 35)
BULLET_NUMBER = 5

# Wall settings
WALL_IMG = 'wall_mid.png'

# Mob settings
MOB_HEALTH = 100
MOB_DAMAGE = 10
MOB_KNOCKBACK = 10
MOB_IMG_R = 'theWitchR.png'
MOB_IMG_L = 'theWitchL.png'
MOB_SIZE = 3
MOB_SPEEDS = [250, 200, 175, 225, 500]
MOB_HIT_RECT = pg.Rect(0, 0, 30, 30)
AVOID_RADIUS = 50
SPLAT = 'witch_dead6.png'

#Item settings
ITEM_IMAGES = {'health': 'milk.png'}
HEALTH_PACK_AMOUNT = 20
P_RANGE = 20
P_SPEED = 0.6