import pygame as pg
import math
from settings import *
from random import uniform, choice, randint
from tilemap import Camera
from tilemap import collide_hit_rect
import pytweening as tween
vec = pg.math.Vector2

# Colisãodas paredes
def collide_with_walls(sprite, group, dir):
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y
# Classe jogador
class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y, screen):
        self.screen = screen
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_img
        self.size = self.image.get_size()
        self.image = pg.transform.scale(self.image, (int(self.size[0] * PLAYER_SIZE), int(self.size[1] * PLAYER_SIZE)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.imageL = game.player_img_inv
        self.imageL = pg.transform.scale(self.imageL,
                                         (int(self.size[0] * PLAYER_SIZE), int(self.size[1] * PLAYER_SIZE)))
        self.imageR = self.image
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.x = x
        self.y = y
        self.last_shot = 0
        self.rot = 0
        self.health = PLAYER_HEALTH
        self.bullet_number = BULLET_NUMBER
    
    # Mapeamento das teclas
    def get_keys(self):
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.image = self.imageL
            self.vel.x = -PLAYER_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.vel.x = PLAYER_SPEED
            self.image = self.imageR
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vel.y = -PLAYER_SPEED
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel.y = PLAYER_SPEED
        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.7071
        if keys[pg.K_j]:
            if self.image == self.imageR:
                self.image = self.imageL
            self.rot = 180
            now = pg.time.get_ticks()
            if now - self.last_shot > BULLET_RATE:
                    self.last_shot = now
                    dir = vec(1,0).rotate(-self.rot)
                    pos = self.pos + BARREL_OFFSET
                    Bullet(self.game, pos, dir, self.rot)
        if keys[pg.K_l]:
            if self.image == self.imageL:
                self.image = self.imageR
            self.rot = 0
            now = pg.time.get_ticks()
            if now - self.last_shot > BULLET_RATE:
                self.last_shot = now
                dir = vec(1,0).rotate(-self.rot)
                pos = self.pos + BARREL_OFFSET
                Bullet(self.game, pos, dir, self.rot)
        if keys[pg.K_k]:
            self.rot = 270
            now = pg.time.get_ticks()
            if now - self.last_shot > BULLET_RATE:
                self.last_shot = now
                dir = vec(1,0).rotate(-self.rot)
                pos = self.pos + BARREL_OFFSET
                Bullet(self.game, pos, dir, self.rot)
        if keys[pg.K_i]:
            self.rot = 90
            now = pg.time.get_ticks()
            if now - self.last_shot > BULLET_RATE:
                self.last_shot = now
                dir = vec(1,0).rotate(-self.rot)
                pos = self.pos + BARREL_OFFSET
                Bullet(self.game, pos, dir, self.rot)

    def update(self):
        self.get_keys()
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls,'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center
    
    def add_health(self, amount):
        self.health += amount
        if self.health > PLAYER_HEALTH:
            self.health = PLAYER_HEALTH
#Classe projétil
class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, dir, rotation):
        super().__init__()
        self._layer = BULLET_LAYER
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rot = rotation
        self.size = (1,1)
        spread_gun = uniform(-GUN_SPREAD, GUN_SPREAD)
        spread_pos = uniform(10, 360)
        self.image = game.bullet_img
        self.image = pg.transform.scale(self.image, (int(self.size[0] * BULLET_SIZE-10), int(self.size[1] * BULLET_SIZE+10)))
        self.image = pg.transform.rotate(self.image, self.rot + spread_pos)
        self.rect = self.image.get_rect()
        self.pos = vec(pos)
        self.rect.center = pos
        self.vel = dir.rotate(spread_gun) * BULLET_SPEED
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        if pg.time.get_ticks() - self.spawn_time > BULLET_LIFETIME:
            self.kill()
#Classe monstro
class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.imageR = game.mob_img
        self.imageL = game.mob_img_inv
        self.image = game.mob_img
        self.size = self.image.get_size()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = MOB_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        self.pos = vec(x,y) * TILESIZE
        self.vel = vec(0,0)
        self.acc = vec(0,0)
        self.health = MOB_HEALTH
        self.speed = choice(MOB_SPEEDS)

        self.rect.center = self.pos
        self.rot = 0

        width = int(self.rect.width * self.health / MOB_HEALTH)
        self.health_bar = pg.Rect(0,0, width, 7)
        if self.health < MOB_HEALTH:
            pg.draw.rect(self.image, col, self.health_bar)
    # Melhoria de movimentação dos monstros
    def avoid_mobs(self):
        for mob in self.game.mobs:
            if mob != self:
                distance = self.pos - mob.pos
                if 0 < distance.length() < AVOID_RADIUS:
                    self.acc += distance.normalize()


    def update(self):
        self.rot = (self.game.player.pos - self.pos).angle_to(vec(1,0))
        self.image = pg.transform.scale(self.image, (int(self.size[0] * MOB_SIZE), int(self.size[1] * MOB_SIZE)))
        if self.rot < 90 and self.rot > -90:
            self.image = self.imageR
            self.image = pg.transform.scale(self.image, (int(self.size[0] * MOB_SIZE), int(self.size[1] * MOB_SIZE)))
        else:
            self.image = self.imageL
            self.image = pg.transform.scale(self.image, (int(self.size[0] * MOB_SIZE), int(self.size[1] * MOB_SIZE)))
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.acc = vec(1, 0).rotate(-self.rot)
        self.avoid_mobs()
        self.acc.scale_to_length(self.speed)
        self.acc += self.vel * -1
        self.vel += self.acc * self.game.dt
        self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt **2
        self.rect.center = self.pos

        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')

        self.rect.center = self.hit_rect.center

        if self.health <= 0:
            self.kill()
            self.game.map_img.blit(self.game.splat, self.pos - vec(32,32))

    def draw_health(self):
        if self.health > 60:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED
        width = int(self.rect.width * self.health / MOB_HEALTH)
        self.health_bar = pg.Rect(0, 0, width, 7)
        if self.health < 100:
            pg.draw.rect(self.image, col, self.health_bar)
#Classe obstáculos
class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y 
    
    def update(self):
        if pg.time.get_ticks() - self.spawn_time > FLASH_DURATION:
            self.kill()
# Classe item
class Item(pg.sprite.Sprite):
    def __init__(self, game, pos, type):
        self._layer = ITEMS_LAYER
        self.groups = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.item_images[type]
        self.rect = self.image.get_rect()
        self.type = type
        self.pos = pos
        self.rect.center = pos
        self.tween = tween.easeInOutSine
        self.step = 0
        self.dir = 1
    
    def update(self):
        offset = P_RANGE * (self.tween(self.step / P_RANGE) - 0.5)
        self.rect.centery = self.pos.y + offset * self.dir
        self.step += P_SPEED
        if self.step > P_RANGE:
            self.step = 0
            self.dir *=-1