#!/usr/bin/python3
import pygame
import datetime
from gameobjects import *
import TextDebugger

from pygame.locals import (
    QUIT,
)


RES_X = 512
RES_Y = 512


pygame.init()
display = pygame.display.set_mode(size=(RES_X, RES_Y))

playerimg = pygame.image.load('sprites/coin_copper.png').convert()

player_sprite = ASprite(playerimg, 8)
player_sprite.animation_fps = 15
player_sprite.animate = True
player = GameObject()
player.sprite = player_sprite
player.set_size_from_sprite()

bullet = GameObject()
bullet.pos.x = 200
bullet.speed = pygame.math.Vector2(20, 50)
bullet.sprite = player_sprite

clock = pygame.time.Clock()

debugger = TextDebugger.Renderer()

fps = 0
running = True
lastdt = datetime.datetime.now()

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
            print('Goodbyte')

    dt = datetime.datetime.now()
    delta_time = (dt - lastdt).total_seconds()

    fps = int(1 / delta_time)
    lastdt = dt

    # Fill background
    display.fill((0, 0, 0))

    mouse_x, mouse_y = pygame.mouse.get_pos()
    player.pos = pygame.math.Vector2(mouse_x, mouse_y)

    player.update(delta_time)
    player.draw(display)

    bullet.update(delta_time)
    bullet.draw(display)

    collision = pygame.sprite.collide_rect(player.sprite, bullet.sprite)

    debugger.clear()

    # Add text here
    debugger.add(str(fps))
    debugger.add('Mouse X = {}'.format(mouse_x))
    debugger.add('Mouse Y = {}'.format(mouse_y))
    debugger.add('Frame: {}'.format(player.sprite.frame))
    debugger.add('Collision {}'.format(collision))
    debugger.add('Rect1 {}'.format(bullet.sprite.rect))

    debugger.render(display)

    pygame.display.update()

    clock.tick(60)
