#!/usr/bin/python3
import pygame
from gameobjects import Player, Enemy, ResourcesLoader, shield_1, enemy_group_rect
import controller
import TextDebugger


RES_X = 1280
RES_Y = 720


pygame.init()
display = pygame.display.set_mode(size=(RES_X, RES_Y))
pygame.mouse.set_visible(False)


def level_test(game_manager):
    world = game_manager.world

    player = Player()
    player.sprite.fps = 15
    world.append(player)
    game_manager.animator.add_object_loop(player)
    player.create_shield(shield_1)

    enemy_group = enemy_group_rect()
    world.append(enemy_group)
    enemy_group.create_enemies(10, 4, (300, 200), Enemy)


clock = pygame.time.Clock()

debugger = TextDebugger.Renderer()

game = controller.Game(RES_X, RES_Y)
level_test(game)
logic = controller.Logic(game)

while True:
    if not game.pygame_events():
        break

    dt = game.update_world(display)
    logic.update(dt)

    fps = int(1 / dt)

    # Fill background
    mouse_x, mouse_y = pygame.mouse.get_pos()

    debugger.clear()

    # Add text here
    debugger.add(str(fps))
    debugger.add('Mouse X = {}'.format(mouse_x))
    debugger.add('Mouse Y = {}'.format(mouse_y))
    debugger.add('Score = {}'.format(logic.score))
    dic = game.world.get_main_dic().items()
    for type_name, array in dic:
        debugger.add('{}: {}'.format(type_name, len(array)))

    debugger.render(display)

    pygame.display.update()

    clock.tick(60)
