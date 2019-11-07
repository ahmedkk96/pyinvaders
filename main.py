#!/usr/bin/python3
import pygame
import gameobjects
import controller
from TextDebugger import Renderer as Debugger


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
    global paused, last_mouse_pos
    if not paused:
        last_mouse_pos = pygame.mouse.get_pos()
    else:
        pygame.mouse.set_pos(last_mouse_pos)
    paused = not paused


def on_reset():
    global game
    global paused, dead
    game.reset()

    paused, dead = False, False


def debug(dt):
    global display, game, debugger
    debugger.clear()

    fps = int(1 / dt)
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Add text here
    debugger.add(str(fps))
    debugger.add('Mouse X = {}'.format(mouse_x))
    debugger.add('Mouse Y = {}'.format(mouse_y))

    dic = game.world.get_main_dic().items()
    for type_name, array in dic:
        debugger.add('{}: {}'.format(type_name, len(array)))

    debugger.render(display)


def debug_rect():
    global display, game, debugger
    objs = game.world.get_all_objects()
    for obj in objs:
        pygame.draw.rect(display, (255, 255, 255), obj.get_rect(), 1)


display = init_window()

debugger = Debugger()

game_state = GameEvents()
game_state.on_pause = on_pause
game_state.on_lost = on_lost
game_state.on_reset = on_reset

game = controller.Components(game_state)
updater = controller.Updater(game)
render = controller.Render(game, display)

while True:
    if not updater.pygame_events():
        break

    dt = updater.update_all(paused)

    if dead or not paused:
        render.draw(dt)
        debug(dt)
        # debug_rect()


print('Goodbye')
