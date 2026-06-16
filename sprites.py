import pygame as pg
from settings import *
from random import uniform, choice
from tilemap import collide_hit_rect
import pytweening as tween

vec = pg.math.Vector2


def collide_with_walls(sprite, group, dir):
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            elif hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            elif hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        w, h = game.player_img.get_size()
        scaled_size = (int(w * PLAYER_SIZE), int(h * PLAYER_SIZE))
        self.imageR = pg.transform.scale(game.player_img, scaled_size)
        self.imageL = pg.transform.scale(game.player_img_inv, scaled_size)
        self.image = self.imageR
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.last_shot = 0
        self.rot = 0
        self.health = PLAYER_HEALTH

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
        if pg.mouse.get_pressed()[0]:
            mouse_screen = vec(pg.mouse.get_pos())
            world_mouse = mouse_screen - vec(self.game.camera.camera.topleft)
            diff = world_mouse - self.pos
            if diff.length() > 0:
                dir = diff.normalize()
                self.image = self.imageL if dir.x < 0 else self.imageR
                self.rot = vec(1, 0).angle_to(dir)
                now = pg.time.get_ticks()
                if now - self.last_shot > BULLET_RATE:
                    self.last_shot = now
                    Bullet(self.game, self.pos, dir, self.rot)

    def update(self):
        self.get_keys()
        self.rect = self.image.get_rect()
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center

    def add_health(self, amount):
        self.health = min(self.health + amount, PLAYER_HEALTH)


class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, dir, rotation):
        self._layer = BULLET_LAYER
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        spread_gun = uniform(-GUN_SPREAD, GUN_SPREAD)
        spread_pos = uniform(10, 360)
        self.image = pg.transform.scale(game.bullet_img, (BULLET_SIZE - 10, BULLET_SIZE + 10))
        self.image = pg.transform.rotate(self.image, rotation + spread_pos)
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


class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        w, h = game.mob_img.get_size()
        scaled_size = (int(w * MOB_SIZE), int(h * MOB_SIZE))
        self.imageR = pg.transform.scale(game.mob_img, scaled_size)
        self.imageL = pg.transform.scale(game.mob_img_inv, scaled_size)
        self.image = self.imageR
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = MOB_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.health = MOB_HEALTH
        self.speed = choice(MOB_SPEEDS)
        self.rot = 0

    def avoid_mobs(self):
        for mob in self.game.mobs:
            if mob != self:
                distance = self.pos - mob.pos
                if 0 < distance.length() < AVOID_RADIUS:
                    self.acc += distance.normalize()

    def update(self):
        self.rot = (self.game.player.pos - self.pos).angle_to(vec(1, 0))
        self.image = self.imageR if -90 < self.rot < 90 else self.imageL
        self.rect = self.image.get_rect()
        self.acc = vec(1, 0).rotate(-self.rot)
        self.avoid_mobs()
        self.acc.scale_to_length(self.speed)
        self.acc += self.vel * -1
        self.vel += self.acc * self.game.dt
        self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center
        if self.health <= 0:
            self.kill()
            self.game.map_img.blit(self.game.splat, self.pos - vec(32, 32))

    def draw_health(self, surface, screen_rect):
        if self.health >= MOB_HEALTH:
            return
        if self.health > 60:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED
        width = int(screen_rect.width * self.health / MOB_HEALTH)
        pg.draw.rect(surface, col, pg.Rect(screen_rect.x, screen_rect.y, width, 7))


class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.rect = pg.Rect(x, y, w, h)


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
            self.dir *= -1
