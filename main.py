#!/usr/bin/python3
import pygame
from gameobjects import *
import controller
import TextDebugger


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


controller.world.append(player, 'player')
shoot = True

updater = controller.Updater()
logic = controller.Logic()

while True:
    if not updater.pygame_events():
        break

    dt = updater.update_world(display)

    fps = int(1 / dt)

    # Fill background
    mouse_x, mouse_y = pygame.mouse.get_pos()

    debugger.clear()

    # Add text here
    debugger.add(str(fps))
    debugger.add('Mouse X = {}'.format(mouse_x))
    debugger.add('Mouse Y = {}'.format(mouse_y))

    debugger.render(display)

    pygame.display.update()

    clock.tick(60)
