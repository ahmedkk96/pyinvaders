#!/usr/bin/python3
import pygame
import datetime
import math
from gameobjects import Player

from pygame.locals import (
    QUIT,
)


RES_X = 512
RES_Y = 512


pygame.init()
display = pygame.display.set_mode(size=(RES_X, RES_Y))
font = pygame.font.Font(None, 26)
playerimg = pygame.image.load('sprites/player.png').convert()
player = Player(playerimg, 2)
clock = pygame.time.Clock()


fps = 0
running = True
lastdt = datetime.datetime.now()
step = 0
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
            print('Goodbyte')

    dt = datetime.datetime.now()
    fps = math.floor(1000000 / (dt - lastdt).microseconds)
    lastdt = dt

    # Fill background
    display.fill((0, 0, 0))

    player.draw(step, display)
    step = (step + 1) % 2

    textsurf = font.render(str(fps), False, pygame.color.Color('white'))
    display.blit(textsurf, (0, 0))
    pygame.display.update()

    clock.tick(15)
