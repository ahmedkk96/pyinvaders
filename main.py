#!/usr/bin/python3
import pygame
import gameobjects
import controller

RES_X = 1280
RES_Y = 720

paused = False


def init_window():
    pygame.init()
    display = pygame.display.set_mode(size=(RES_X, RES_Y))
    pygame.mouse.set_visible(False)
    pygame.mouse.set_pos((RES_X / 2, RES_Y * 0.9))

    # init sprites
    gameobjects.ResourcesLoader.__init__()
    gameobjects.WorldHelper.screen_rect = display.get_rect()
    return display


display = init_window()
game = controller.Components()
updater = controller.Updater(game)
render = controller.Render(game, display)

while True:
    if not updater.pygame_events():
        break

    dt = updater.update_all(paused)
    render.draw(dt)


print('Goodbye')
