import os
import sys

import pygame

pygame.init()
size = width, height = 640, 320
screen = pygame.display.set_mode(size)


def load_image(name, colorkey=None):
    fullname = os.path.join('Sprites', name)
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


all_sprites = pygame.sprite.Group()


for j in range(height // 32):
    for k in range(width // 32):
        tiles_image = load_image("Tiles.png")
        tiles = pygame.sprite.Sprite(all_sprites)
        tiles.image = tiles_image
        tiles.rect = tiles.image.get_rect()
        tiles.rect.x = k * 32
        tiles.rect.y = j * 32

running = True
fps = 50
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((0, 0, 0))
    all_sprites.draw(screen)
    pygame.display.flip()
pygame.quit()
