import pygame as pg
import sys
from os import path
from settings import *
from sprites import *
from tilemap import *


def draw_player_health(surf, x, y, pct):
    pct = max(0, pct)
    BAR_LENGTH = 100
    BAR_HEIGHT = 20
    if pct > 0.6:
        col = GREEN
    elif pct > 0.3:
        col = YELLOW
    else:
        col = RED
    pg.draw.rect(surf, col, pg.Rect(x, y, int(pct * BAR_LENGTH), BAR_HEIGHT))
    pg.draw.rect(surf, WHITE, pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT), 2)


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.load_data()

    def load_data(self):
        game_folder = path.dirname(__file__)
        player_img_folder = path.join(game_folder, 'sprites/Player')
        self.map_img_folder = game_folder
        font_img_folder = path.join(game_folder, 'sprites/General')
        self.title_font = path.join(font_img_folder, 'CuteBlock.ttf')
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180))

        self.player_img = pg.image.load(path.join(player_img_folder, PLAYER_IMG)).convert_alpha()
        self.player_img_inv = pg.image.load(path.join(player_img_folder, PLAYER_IMG_INV)).convert_alpha()

        splat_img_folder = path.join(game_folder, 'sprites/General')
        self.splat = pg.image.load(path.join(splat_img_folder, SPLAT)).convert_alpha()
        self.splat = pg.transform.scale(self.splat, (64, 64))

        weapons_img_folder = path.join(game_folder, 'sprites/Weapons')
        self.bullet_img = pg.image.load(path.join(weapons_img_folder, BULLET_IMG)).convert_alpha()

        mobs_img_folder = path.join(game_folder, 'sprites/Mobs')
        self.mob_img = pg.image.load(path.join(mobs_img_folder, MOB_IMG_R)).convert_alpha()
        self.mob_img_inv = pg.image.load(path.join(mobs_img_folder, MOB_IMG_L)).convert_alpha()

        items_folder = path.join(game_folder, 'sprites/Itens')
        self.item_images = {}
        for item in ITEM_IMAGES:
            self.item_images[item] = pg.image.load(path.join(items_folder, ITEM_IMAGES[item])).convert_alpha()

        music_path = path.join(game_folder, 'music.mp3')
        pg.mixer_music.load(music_path)

    def draw_text(self, text, font_name, size, color, x, y, align="nw"):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        align_map = {
            "nw": "topleft", "ne": "topright", "sw": "bottomleft", "se": "bottomright",
            "n": "midtop", "s": "midbottom", "e": "midright", "w": "midleft",
            "center": "center",
        }
        setattr(text_rect, align_map.get(align, "topleft"), (x, y))
        self.screen.blit(text_surface, text_rect)

    def new(self):
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.map = TiledMap(path.join(self.map_img_folder, 'level1.tmx'))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width / 2,
                             tile_object.y + tile_object.height / 2)
            if tile_object.name == "player":
                self.player = Player(self, tile_object.x, tile_object.y)
            elif tile_object.name == "wall":
                Obstacle(self, tile_object.x, tile_object.y,
                         tile_object.width, tile_object.height)
            elif tile_object.name == "mob":
                Mob(self, tile_object.x, tile_object.y)
            elif tile_object.name == "health":
                Item(self, obj_center, tile_object.name)
        self.camera = Camera(self.map.width, self.map.height)
        self.paused = False

    def run(self):
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000.0
            self.events()
            if not self.paused:
                self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player)

        if len(self.mobs) == 0 and len(self.items) == 0:
            self.playing = False
            self.show_win_screen()

        hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        for hit in hits:
            self.player.health -= MOB_DAMAGE
            hit.vel = vec(0, 0)
            if self.player.health <= 0:
                self.playing = False
                self.show_death_screen()
        if hits:
            self.player.pos += vec(MOB_KNOCKBACK, 0).rotate(-hits[0].rot)

        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for hit in hits:
            hit.health -= BULLET_DAMAGE
            hit.vel = vec(0, 0)

        hits = pg.sprite.spritecollide(self.player, self.items, False)
        for hit in hits:
            if hit.type == 'health' and self.player.health < PLAYER_HEALTH:
                hit.kill()
                self.player.add_health(HEALTH_PACK_AMOUNT)

    def draw(self):
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        for sprite in self.all_sprites:
            screen_rect = self.camera.apply(sprite)
            self.screen.blit(sprite.image, screen_rect)
            if isinstance(sprite, Mob):
                sprite.draw_health(self.screen, screen_rect)
        draw_player_health(self.screen, 10, 10, self.player.health / PLAYER_HEALTH)
        self.draw_text('Bruxas: {}'.format(len(self.mobs)), self.title_font, 30, WHITE,
                       WIDTH - 10, 10, align="ne")
        self.draw_text('Leites: {}'.format(len(self.items)), self.title_font, 30, LIGHTGREY,
                       WIDTH - 10, 50, align="ne")
        if self.paused:
            self.screen.blit(self.dim_screen, (0, 0))
            self.draw_text("Pausa", self.title_font, 105, RED, WIDTH / 2, HEIGHT / 2, align="center")
        pg.display.flip()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_p:
                    self.paused = not self.paused

    def show_start_screen(self):
        self.screen.fill(BLACK)
        self.draw_text("Comandos", self.title_font, 50, LIGHTGREY,
                       WIDTH / 2, HEIGHT / 2 - 220, align="center")
        self.draw_text("W: cima", self.title_font, 30, LIGHTGREY,
                       WIDTH / 2, HEIGHT / 2 - 170, align="center")
        self.draw_text("S: baixo", self.title_font, 30, LIGHTGREY,
                       WIDTH / 2, HEIGHT / 2 - 120, align="center")
        self.draw_text("A: esquerda", self.title_font, 30, LIGHTGREY,
                       WIDTH / 2, HEIGHT / 2 - 70, align="center")
        self.draw_text("D: direita", self.title_font, 30, LIGHTGREY,
                       WIDTH / 2, HEIGHT / 2 - 20, align="center")
        self.draw_text("Clique esquerdo: atirar", self.title_font, 30, LIGHTGREY,
                       WIDTH / 2, HEIGHT / 2 + 30, align="center")
        self.draw_text("Pressione qualquer tecla para iniciar", self.title_font, 40, RED,
                       WIDTH / 2, HEIGHT / 2 + 240, align="center")
        pg.mixer_music.play()
        pg.display.flip()
        self.wait_for_key()

    def show_win_screen(self):
        self.screen.fill(BLACK)
        self.draw_text("Parabéns!!", self.title_font, 100, RED,
                       WIDTH / 2, HEIGHT / 2, align="center")
        self.draw_text("Tecle para reiniciar", self.title_font, 75, WHITE,
                       WIDTH / 2, HEIGHT * 3 / 4, align="center")
        pg.display.flip()
        self.wait_for_key()

    def show_death_screen(self):
        self.screen.fill(BLACK)
        self.draw_text("GAME OVER", self.title_font, 100, RED,
                       WIDTH / 2, HEIGHT / 2, align="center")
        self.draw_text("Tecle para reiniciar", self.title_font, 75, WHITE,
                       WIDTH / 2, HEIGHT * 3 / 4, align="center")
        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.quit()
                if event.type == pg.KEYUP:
                    waiting = False


g = Game()
g.show_start_screen()
while True:
    g.new()
    g.run()
