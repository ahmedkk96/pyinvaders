#!/usr/bin/python3
import pygame
import gameobjects
import controller


RES_X = 1280
RES_Y = 720
controller.EnemySpwaner.LOWER_LIMIT = RES_Y

paused = False
dead = False


class GameEvents:
    def __init__(self):
        self.on_lost = None
        self.on_pause = None
        self.on_reset = None


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

    game.world.remove(game.player)
    controller.create_explosion(game.world, game.player.get_pos())
    game.gui.loser()


def on_pause():
    global paused
    paused = not paused


def on_reset():
    global game
    global paused, dead
    game.reset()

    paused, dead = False, False


game_state = GameEvents()
game_state.on_pause = on_pause
game_state.on_lost = on_lost
game_state.on_reset = on_reset

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
