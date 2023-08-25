import pygame as pg
import sys
from os import path
from settings import *
from sprites import *
from tilemap import *
from settings import *
import pyglet
# Configurações do HUD
# Desenhar barra de vida na tela
def draw_player_health(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 20
    fill = pct * BAR_LENGTH
    col = GREEN
    outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
    if pct > 0.6 and pct < 1.0:
        col = GREEN
    if pct < 0.6 and pct > 0.3:
        col = YELLOW
    if pct < 0.3:
        col = RED

    pg.draw.rect(surf, col, fill_rect)
    pg.draw.rect(surf, WHITE, outline_rect, 2)
# Classe principal do jogo
class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100)
        self.load_data()
    # Carregamento de dados (sprites, videos...)
    def load_data(self):
        game_folder = path.dirname(__file__)
        "''' SPRITES DO PLAYER '''"
        player_img_folder = path.join(game_folder, 'sprites/Player')
        self.map_img_folder = game_folder
        font_img_folder = path.join(game_folder, 'sprites/General')
        self.title_font = path.join(font_img_folder, 'CuteBlock.ttf')
        self.hud_font = path.join(font_img_folder, 'Impact.ttf')
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0,0,0,180))
        

        self.player_img = pg.image.load(path.join(player_img_folder, PLAYER_IMG)).convert_alpha()
        self.player_img_inv = pg.image.load(path.join(player_img_folder, PLAYER_IMG_INV)).convert_alpha()
        "''' PAUSE '''"
        splat_img_folder = path.join(game_folder, 'sprites/General')
        self.splat = pg.image.load(path.join(splat_img_folder, SPLAT)).convert_alpha()
        self.splat = pg.transform.scale(self.splat, (64,64))
        "''' SPRITES DAS ARMAS/BALAS '''"
        weapons_img_folder = path.join(game_folder, 'sprites/Weapons')
        self.bullet_img = pg.image.load(path.join(weapons_img_folder, BULLET_IMG)).convert_alpha()
        "''' SPRITES DOS MOBS''' "
        mobs_img_folder = path.join(game_folder, 'sprites/Mobs')
        self.mob_img = pg.image.load(path.join(mobs_img_folder, MOB_IMG_R)).convert_alpha()
        self.mob_img_inv = pg.image.load(path.join(mobs_img_folder, MOB_IMG_L)).convert_alpha()

        "''' ITENS '''"
        items_folder = path.join(game_folder, 'sprites/Itens')
        self.item_images = {}
        for item in ITEM_IMAGES:
            self.item_images[item] = pg.image.load(path.join(items_folder, ITEM_IMAGES[item])).convert_alpha()
    # Base para desenhar textos na tela
    def draw_text(self, text, font_name, size, color, x, y, align="nw"):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "nw":
            text_rect.topleft = (x, y)
        if align == "ne":
            text_rect.topright = (x, y)
        if align == "sw":
            text_rect.bottomleft = (x, y)
        if align == "se":
            text_rect.bottomright = (x, y)
        if align == "n":
            text_rect.midtop = (x, y)
        if align == "s":
            text_rect.midbottom = (x, y)
        if align == "e":
            text_rect.midright = (x, y)
        if align == "w":
            text_rect.midleft = (x, y)
        if align == "center":
            text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def new(self):
        #Inicialização de todas as variáveis do jogo
        screen = self.screen
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.map = TiledMap(path.join(self.map_img_folder, 'level1.tmx'))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        ''' Definição dos objetos '''
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width /2, 
                        tile_object.y + tile_object.height/2)
            if tile_object.name == "player":
                self.player = Player(self, tile_object.x, tile_object.y, screen)
            if tile_object.name == "wall":
                Obstacle(self, tile_object.x, tile_object.y,
                        tile_object.width, tile_object.height)
            if tile_object.name == "mob":
                Mob(self, tile_object.x, tile_object.y)
            if tile_object.name in ['health']:
                Item(self, obj_center, tile_object.name)
            

        self.camera = Camera(self.map.width, self.map.height)
        self.paused = False

    def run(self):
        # gameLoop - o jogo rodará enquanto o loop estiver com valor True
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
        # Update do gameLoop
        self.all_sprites.update()
        self.camera.update(self.player)
        
        #Fim de jogo
        if len(self.mobs) == 0 and len(self.items) == 0:
            self.playing = False
            g.show_win_screen()

        

        # Colisão monstros com o player
        hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        for hit in hits:
            self.player.health -= MOB_DAMAGE
            hit.vel = vec(0, 0)
            if self.player.health <= 0:
                self.playing = False
                g.show_death_screen()
        if hits:
            self.player.pos += vec(MOB_KNOCKBACK, 0).rotate(-hits[0].rot)
        # Colisão projéteis com os monstros
        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for hit in hits:
            hit.health -= BULLET_DAMAGE
            hit.vel = vec(0, 0)
        # Colisão do player com os itens
        hits = pg.sprite.spritecollide(self.player, self.items, False)
        for hit in hits:
            if hit.type == 'health' and self.player.health <= PLAYER_HEALTH:
                hit.kill()
                self.player.add_health(HEALTH_PACK_AMOUNT) 

    def draw(self):
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob):
                sprite.draw_health()
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        draw_player_health(self.screen, 10, 10, self.player.health / PLAYER_HEALTH )
        self.draw_text('Bruxas: {}'.format(len(self.mobs)), self.title_font, 30, WHITE,
                       WIDTH - 10, 10, align="ne")
        self.draw_text('Leites: {}'.format(len(self.items)), self.title_font, 30, LIGHTGREY,
                       WIDTH - 10, 50, align="ne")
        if self.paused:
            self.screen.blit(self.dim_screen, (0, 0))
            self.draw_text("Pausa",self.title_font, 105, RED, WIDTH/2, HEIGHT/2, align="center" )
        pg.display.flip()

    def events(self):
        # Para todos os eventos do teclado/mouse
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_p:
                    self.paused = not self.paused
    # Método que chama a primeira tela do jogo
    def show_start_screen(self):
        pass


    def show_start_screen(self):

        self.screen.fill(BLACK)
        self.draw_text("Comandos", self.title_font, 50, LIGHTGREY, 
                        WIDTH /2, HEIGHT /2 -220, align="center")
        self.draw_text("W: cima", self.title_font, 30, LIGHTGREY, 
                        WIDTH /2, HEIGHT /2 -170, align="center")
        self.draw_text("S: baixo", self.title_font, 30, LIGHTGREY, 
                        WIDTH /2, HEIGHT /2 -120, align="center")
        self.draw_text("A: esquerda", self.title_font, 30, LIGHTGREY, 
                        WIDTH /2, HEIGHT /2 -70, align="center")
        self.draw_text("D: direita", self.title_font, 30, LIGHTGREY, 
                        WIDTH /2, HEIGHT /2 -20, align="center")
        
        self.draw_text("I: atirar cima", self.title_font, 30, LIGHTGREY, 
                        WIDTH /2, HEIGHT /2 + 30, align="center")
        self.draw_text("K: atirar baixo", self.title_font, 30, LIGHTGREY, 
                        WIDTH /2, HEIGHT /2 +80, align="center")
        self.draw_text("J: atirar esquerda", self.title_font, 30, LIGHTGREY, 
                        WIDTH /2, HEIGHT /2 +130, align="center")
        self.draw_text("L: atirar direita", self.title_font, 30, LIGHTGREY, 
                        WIDTH /2, HEIGHT /2 +180, align="center")

        self.draw_text("Pressione qualquer tecla para iniciar", self.title_font, 40, RED, 
                        WIDTH /2, HEIGHT /2 +240, align="center")
        self.musicPath = path.join(path.dirname(__file__), 'music.mp3')
        pg.mixer_music.load(self.musicPath)
        
        print(self.musicPath)
        pg.mixer_music.play()
        pg.display.flip()
        self.wait_for_key()


    # Método mostrar textos na tela
    def show_win_screen(self):
        self.screen.fill(BLACK)
        self.draw_text("Parabéns!!", self.title_font, 100, RED, 
                        WIDTH /2, HEIGHT /2, align="center")
        self.draw_text("Tecle para reiniciar", self.title_font, 75, WHITE,
                         WIDTH/2, HEIGHT*3/4, align="center" )
        pg.display.flip()
        self.wait_for_key()

    def show_death_screen(self):
        self.draw_text("GAME OVER", self.title_font, 100, RED, 
                        WIDTH /2, HEIGHT /2, align="center")
        self.draw_text("Tecle para reiniciar", self.title_font, 75, WHITE,
                         WIDTH/2, HEIGHT*3/4, align="center" )
        pg.display.flip()
        self.wait_for_key()
    
    # Game Over
    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYUP:
                    waiting = False

# Início do código
g = Game()
g.show_start_screen()
while True:
    g.new()
    g.run()