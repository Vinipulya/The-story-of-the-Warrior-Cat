import os
import sys
from fileinput import close
import time
from random import randint

import pygame

pygame.init()
pygame.key.set_repeat(200, 70)
size = width, height = 1200, 800
screen = pygame.display.set_mode(size)
FPS = 50
clock = pygame.time.Clock()


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def start_screen():

    fon = pygame.transform.scale(load_image('fon.png'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 70

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


tile_images = {
    'wall_fr': pygame.transform.scale(load_image('Wall_front.png'), (100, 100)),
    'wall_fr_1': pygame.transform.scale(load_image('Wall_front_1.png'), (100, 100)),
    'tent': pygame.transform.scale(load_image('Tentacle.png'), (100, 100)),
    'empty': pygame.transform.scale(load_image('Tiles.png'), (100, 100)),
    'pobeda': pygame.transform.scale(load_image("pobeda.jpg"), (100, 100)),
}
player_image = pygame.transform.scale(load_image('Cat_Warrior.png'), (90, 90))
enemy_image = pygame.transform.scale(load_image("Ishak.png"), (100, 100))

tile_width = tile_height = 100

# основной персонаж
player = None

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
wall_fr_group = pygame.sprite.Group()
wall_fr_1_group = pygame.sprite.Group()
tent_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
pobeda_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()


def generate_level(level):
    global player
    tiles_group.empty()
    player_group.empty()
    enemy_group.empty()
    new_player, x, y = None, None, None
    new_enemy, xE, yE = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall_fr', x, y)
            elif level[y][x] == 'H':
                Tile('wall_fr_1', x, y)
            elif level[y][x] == 'F':
                Tile('tent', x, y)
            elif level[y][x] == 'E':
                Tile('empty', x, y)
                xE, yE = x, y
                new_enemy = Enemy(x, y)
            elif level[y][x] == 'p':
                Tile('pobeda', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y, new_enemy, xE, yE


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        if tile_type == 'wall_fr':
            super().__init__(tiles_group, all_sprites, wall_fr_group)
        elif tile_type == 'wall_fr_1':
            super().__init__(tiles_group, all_sprites, wall_fr_1_group)
        elif tile_type == 'tent':
            super().__init__(tiles_group, all_sprites, tent_group)
        elif tile_type == 'pobeda':
            super().__init__(tiles_group, all_sprites, pobeda_group)
        elif tile_type == 'enemy':
            super().__init__(tiles_group, all_sprites, enemy_group)

        else:
            super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.tile_type = tile_type
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.tile_type = "player"
        self.health = 5
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 60, tile_height * pos_y + 15)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(enemy_group, all_sprites)
        self.image = enemy_image
        self.tile_type = "enemy"
        self.health = 1
        self.health = 5
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        hit_list = pygame.sprite.spritecollide(self, enemy_group, False)
        for enemy in hit_list:
            self.health -= 1
            print(self.health)


def end_screen():
    outro_text = ["Ты победил!", ""
                                 "Поздравляю!", ""
                                                "Нажми любую кнопку, чтобы выйти."]

    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 70
    for line in outro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                time.sleep(3)
                terminate()
        pygame.display.flip()
        clock.tick(FPS)


def loading_screen():
    outro_text = ["Загрузка уровня..."]

    fon = pygame.transform.scale(load_image('loading_level.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 70
    for line in outro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                time.sleep(3)
                second_level()
        pygame.display.flip()
        clock.tick(FPS)


def loose_screen():
    outro_text = ["Ты проиграл.", ""
                                  "", ""
                                      "Нажми любую кнопку, чтобы выйти."]

    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 70
    for line in outro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return first_level()

        pygame.display.flip()
        clock.tick(FPS)


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


currect_scene = None


def switch_level(scene):
    global currect_scene
    currect_scene = scene


def first_level():
    player, level_x, level_y, enemy, xE, yE = generate_level(load_level('map1.txt'))
    running = True
    STEP = 10
    health = 5
    gameplay = True
    camera = Camera()
    while running:
        if gameplay:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif player.rect.x >= width:
                    end_screen()
                elif event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_LEFT or event.key == ord('a'):
                        player.rect.x -= STEP
                        if pygame.sprite.groupcollide(player_group, wall_fr_1_group, False, False) or \
                                pygame.sprite.groupcollide(player_group, wall_fr_group, False, False):
                            player.rect.x += STEP

                        if pygame.sprite.groupcollide(player_group, tent_group, False, False):
                            health -= 1
                            player.rect.x += 2 * STEP

                        if pygame.sprite.groupcollide(player_group, pobeda_group, False, False):
                            loading_screen()
                            switch_level(second_level())
                            gameplay = False

                    if event.key == pygame.K_RIGHT or event.key == ord('d'):
                        player.rect.x += STEP
                        if pygame.sprite.groupcollide(player_group, wall_fr_1_group, False, False) or \
                                pygame.sprite.groupcollide(player_group, wall_fr_group, False, False):
                            player.rect.x -= STEP

                        if pygame.sprite.groupcollide(player_group, tent_group, False, False):
                            health -= 1
                            player.rect.x -= 2 * STEP

                        if pygame.sprite.groupcollide(player_group, pobeda_group, False, False):
                            loading_screen()
                            switch_level(second_level())
                            gameplay = False

                    if event.key == pygame.K_UP or event.key == ord('w'):
                        player.rect.y -= STEP
                        if pygame.sprite.groupcollide(player_group, wall_fr_1_group, False, False) or \
                                pygame.sprite.groupcollide(player_group, wall_fr_group, False, False):
                            player.rect.y += STEP

                        if pygame.sprite.groupcollide(player_group, tent_group, False, False):
                            health -= 1
                            player.rect.y += 2 * STEP

                        if pygame.sprite.groupcollide(player_group, pobeda_group, False, False):
                            loading_screen()
                            switch_level(second_level())
                            gameplay = False

                    if event.key == pygame.K_DOWN or event.key == ord('s'):
                        player.rect.y += STEP
                        if pygame.sprite.groupcollide(player_group, wall_fr_1_group, False, False) or \
                                pygame.sprite.groupcollide(player_group, wall_fr_group, False, False):
                            player.rect.y -= STEP

                        if pygame.sprite.groupcollide(player_group, tent_group, False, False):
                            health -= 1
                            player.rect.y -= 2 * STEP

                        if pygame.sprite.groupcollide(player_group, pobeda_group, False, False):
                            loading_screen()
                            switch_level(second_level())
                            gameplay = False

            if health == 0:
                loose_screen()

            screen.fill(pygame.Color(0, 0, 0))
            camera.update(player)
            for sprite in all_sprites:
                camera.apply(sprite)
            tiles_group.draw(screen)
            player_group.draw(screen)
            enemy_group.draw(screen)
            pygame.display.flip()

            clock.tick(FPS)


def second_level():
    global player
    player, level_x, level_y, enemy, xE, yE = generate_level(load_level('map2.txt'))
    running = True
    STEP = 10
    camera = Camera()
    while running:
        print(player.pos_x, player.pos_y)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == ord('a'):
                    player.rect.x -= STEP
                    player.pos_x -= STEP

                if event.key == pygame.K_RIGHT or event.key == ord('d'):
                    player.rect.x += STEP
                    player.pos_x += STEP

                if event.key == pygame.K_UP or event.key == ord('w'):
                    player.rect.y -= STEP
                    player.pos_y -= STEP

                if event.key == pygame.K_DOWN or event.key == ord('s'):
                    player.rect.y += STEP
                    player.pos_y += STEP

                if enemy.pos_x > player.pos_x:
                    enemy.rect.x -= STEP
                    enemy.pos_x -= STEP
                elif enemy.pos_x < player.pos_x:
                    enemy.rect.x += STEP
                    enemy.pos_x += STEP
                if enemy.pos_y < player.pos_y:
                    enemy.rect.y += STEP
                    enemy.pos_y += STEP
                elif enemy.pos_y > player.pos_y:
                    enemy.rect.y -= STEP
                    enemy.pos_y -= STEP

        screen.fill(pygame.Color(0, 0, 0))
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)
        tiles_group.draw(screen)
        player_group.draw(screen)
        enemy_group.draw(screen)
        pygame.display.flip()

        clock.tick(FPS)


start_screen()
second_level()
while currect_scene is not None:
    currect_scene()
terminate()
