#!/usr/bin/python3
import pygame
import datetime
from gameobjects import *
import TextDebugger

from pygame.locals import (
    QUIT,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP
)


RES_X = 1280
RES_Y = 720


pygame.init()
display = pygame.display.set_mode(size=(RES_X, RES_Y))
pygame.mouse.set_visible(False)

playerimg = pygame.image.load('sprites/player.png').convert()

player_sprite = ASprite(playerimg, 2)
player_sprite.animation_fps = 15
player_sprite.animate = True
player = Player(player_sprite)

clock = pygame.time.Clock()

debugger = TextDebugger.Renderer()

fps = 0
running = True
lastdt = datetime.datetime.now()

# array containing all gameobjects
world = []
world.append(player)
shoot = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
            print('Goodbyte')
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            if shoot:
                world.append(player.shoot())
                shoot = False
        elif event.type == MOUSEBUTTONUP and event.button == 1:
            shoot = True

    dt = datetime.datetime.now()
    delta_time = (dt - lastdt).total_seconds()

    fps = int(1 / delta_time)
    lastdt = dt

    # Fill background
    display.fill((0, 0, 0))

    mouse_x, mouse_y = pygame.mouse.get_pos()

    for gobj in world:
        gobj.update(delta_time)
        gobj.draw(display)

    debugger.clear()

    # Add text here
    debugger.add(str(fps))
    debugger.add('Mouse X = {}'.format(mouse_x))
    debugger.add('Mouse Y = {}'.format(mouse_y))

    debugger.render(display)

    pygame.display.update()

    clock.tick(60)
