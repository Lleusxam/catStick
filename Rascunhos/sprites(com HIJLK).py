import pygame as pg
from settings import *
from random import uniform
vec = pg.math.Vector2
class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_img
        self.size = self.image.get_size()
        self.image = pg.transform.scale(self.image, (int(self.size[0] * PLAYER_SIZE), int(self.size[1] * PLAYER_SIZE)))
        self.rect = self.image.get_rect()
        self.imageL = game.player_img_inv
        self.imageL = pg.transform.scale(self.imageL,
                                         (int(self.size[0] * PLAYER_SIZE), int(self.size[1] * PLAYER_SIZE)))
        self.imageR = self.image
        self.vel = vec(0, 0)
        self.pos = vec(x, y) * TILESIZE
        self.x = x
        self.y = y
        POS_PLAYER = self.pos
        self.last_shot = 0
        self.rot = 0

        '''
        self.rot = 0 --> Direita

        self.rot = 90 --> Cima

        self.rot = 180 --> Esquerda

        self.rot = 270 --> Baixo
        '''


    def get_keys(self):
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.vel.x = -PLAYER_SPEED
            self.image = self.imageL
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
            self.rot = 180
            now = pg.time.get_ticks()
            if now - self.last_shot > BULLET_RATE:
                self.last_shot = now
                dir = vec(1,0).rotate(-self.rot)
                pos = self.pos + BARREL_OFFSET
                Bullet(self.game, pos, dir)
        if keys[pg.K_l]:
            self.rot = 0
            now = pg.time.get_ticks()
            if now - self.last_shot > BULLET_RATE:
                self.last_shot = now
                dir = vec(1,0).rotate(-self.rot)
                pos = self.pos + BARREL_OFFSET
                Bullet(self.game, pos, dir)
        if keys[pg.K_k]:
            self.rot = 270
            now = pg.time.get_ticks()
            if now - self.last_shot > BULLET_RATE:
                self.last_shot = now
                dir = vec(1,0).rotate(-self.rot)
                pos = self.pos + BARREL_OFFSET
                Bullet(self.game, pos, dir)
        if keys[pg.K_i]:
            self.rot = 90
            now = pg.time.get_ticks()
            if now - self.last_shot > BULLET_RATE:
                self.last_shot = now
                dir = vec(1,0).rotate(-self.rot)
                pos = self.pos + BARREL_OFFSET
                Bullet(self.game, pos, dir)


    def collide_with_walls(self, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.x > 0:
                    self.pos.x = hits[0].rect.left - self.rect.width
                if self.vel.x < 0:
                    self.pos.x = hits[0].rect.right
                self.vel.x = 0
                self.rect.x = self.pos.x
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.y > 0:
                    self.pos.y = hits[0].rect.top - self.rect.height
                if self.vel.y < 0:
                    self.pos.y = hits[0].rect.bottom
                self.vel.y = 0
                self.rect.y = self.pos.y

    def update(self):
        self.get_keys()
        self.pos += self.vel * self.game.dt
        self.rect.x = self.pos.x
        self.collide_with_walls('x')
        self.rect.y = self.pos.y
        self.collide_with_walls('y')



class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, dir):
        super().__init__()
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.size = (1,1)
        self.image = game.bullet_img
        self.image = pg.transform.scale(self.image, (int(self.size[0] * BULLET_SIZE), int(self.size[1] * BULLET_SIZE)))
        self.rect = self.image.get_rect()
        self.pos = vec(pos)
        self.rect.center = pos
        spread = uniform(-GUN_SPREAD, GUN_SPREAD)
        self.vel = dir.rotate(spread) * BULLET_SPEED
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        '''
        Ativar a colisão com as paredes
        if pg.sprite.collideany(self, self.game.walls):
            self.kill()
        '''
        if pg.time.get_ticks() - self.spawn_time > BULLET_LIFETIME:
            self.kill()
        #self.posbala[1] += 3
        #self.rect.center = self.pos
        #self.pos[0] = self.vx * self.vel
        #self.pos[1] = self.vy * self.vel

class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
