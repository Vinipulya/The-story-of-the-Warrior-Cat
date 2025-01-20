import os
import sys
from fileinput import close
import time

import pygame

pygame.init()
pygame.key.set_repeat(200, 70)
size = width, height = 900, 900
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
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 70
    for line in intro_text:
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
    'wall': pygame.transform.scale(load_image('Tentacle.png'), (70, 70)),
    'empty': pygame.transform.scale(load_image('Tiles.png'), (70, 70)),
    'pobeda': pygame.transform.scale(load_image("pobeda.jpg"), (70, 70)),
}
player_image = load_image('Cat_Warrior.png')
enemy_image = pygame.transform.scale(load_image("Ishak.png"), (70, 70))

tile_width = tile_height = 70

# основной персонаж
player = None

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
wall_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
pobeda_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()


def generate_level(level):
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
                Tile('wall', x, y)
            elif level[y][x] == 'E':
                Tile('empty', x, y)
                xE, yE = x, y
                new_enemy = Enemy(x,y)
            elif level[y][x] == 'p':
                Tile('pobeda', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y, new_enemy, xE, yE


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        if tile_type == 'wall':
            super().__init__(tiles_group, all_sprites, wall_group)
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
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        hit_list = pygame.sprite.spritecollide(self, enemy_group, False)
        for enemy in hit_list:
            self.health -= 1
            print(self.health)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(enemy_group, all_sprites)
        self.image = enemy_image
        self.tile_type = "enemy"
        self.health = 1
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)


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
                        if pygame.sprite.groupcollide(player_group, wall_group, False, False):
                            loose_screen()

                        if pygame.sprite.groupcollide(player_group, pobeda_group, False, False):
                            loading_screen()
                            switch_level(second_level())
                            gameplay = False
                    if event.key == pygame.K_RIGHT or event.key == ord('d'):
                        player.rect.x += STEP
                        if pygame.sprite.groupcollide(player_group, wall_group, False, False):
                            loose_screen()
                        if pygame.sprite.groupcollide(player_group, pobeda_group, False, False):
                            loading_screen()
                            switch_level(second_level())
                            gameplay = False
                    if event.key == pygame.K_UP or event.key == ord('w'):
                        player.rect.y -= STEP
                        if pygame.sprite.groupcollide(player_group, wall_group, False, False):
                            loose_screen()
                        if pygame.sprite.groupcollide(player_group, pobeda_group, False, False):
                            loading_screen()
                            switch_level(second_level())
                            gameplay = False
                    if event.key == pygame.K_DOWN or event.key == ord('s'):
                        player.rect.y += STEP
                        if pygame.sprite.groupcollide(player_group, wall_group, False, False):
                            loose_screen()
                        if pygame.sprite.groupcollide(player_group, pobeda_group, False, False):
                            loading_screen()
                            switch_level(second_level())
                            gameplay = False

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
    player, level_x, level_y, enemy, xE, yE = generate_level(load_level('map2.txt'))
    running = True
    STEP = 10
    camera = Camera()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif player.rect.x >= width:
                end_screen()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == ord('a'):
                    player.rect.x -= STEP
                    enemy.rect.x -= STEP
                if event.key == pygame.K_RIGHT or event.key == ord('d'):
                    player.rect.x += STEP
                if event.key == pygame.K_UP or event.key == ord('w'):
                    player.rect.y -= STEP
                if event.key == pygame.K_DOWN or event.key == ord('s'):
                    player.rect.y += STEP
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
first_level()
while currect_scene is not None:
    currect_scene()
terminate()
