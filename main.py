#!/usr/bin/python3
import pygame
import gameobjects
import controller

RES_X = 1280
RES_Y = 720

paused = False
dead = False


class GameEvents:
    def __init__(self):
        self.on_lost = None
        self.on_pause = None


def init_window():
    pygame.init()
    display = pygame.display.set_mode(size=(RES_X, RES_Y))
    pygame.mouse.set_visible(False)
    pygame.mouse.set_pos((RES_X / 2, RES_Y * 0.9))

    # init sprites
    gameobjects.ResourcesLoader.__init__()
    gameobjects.WorldHelper.screen_rect = display.get_rect()
    return display


def on_lost():
    global paused, dead
    paused = True
    dead = True
    game.gui.loser()


def on_pause():
    global paused
    paused = not paused


game_state = GameEvents()
game_state.on_pause = on_pause
game_state.on_lost = on_lost

display = init_window()
game = controller.Components(game_state)
updater = controller.Updater(game)
render = controller.Render(game, display)

while True:
    if not updater.pygame_events():
        break

    dt = updater.update_all(paused)

    if dead or not paused:
        render.draw(dt)


print('Goodbye')
