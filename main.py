#!/usr/bin/python3
import pygame
from gameobjects import Sprite, ASprite, Player, Enemy
import controller
import TextDebugger


RES_X = 1280
RES_Y = 720


pygame.init()
display = pygame.display.set_mode(size=(RES_X, RES_Y))
pygame.mouse.set_visible(False)

playerimg = pygame.image.load('sprites/player.png').convert_alpha()

player_sprite = ASprite(playerimg, 2, 1)
player_sprite.fps = 15
player_sprite.animate = True
player = Player(player_sprite)


def sprite_from_path(filename):
    img = pygame.image.load(filename).convert_alpha()
    return Sprite(img)


enemy_sprite = sprite_from_path('sprites/enemyRed2.png')
enemy = Enemy(enemy_sprite)

clock = pygame.time.Clock()

debugger = TextDebugger.Renderer()


world = controller.World()
world.append(player, 'player')
world.append(enemy, 'enemy')
game = controller.Game(world)
game.animator.add_object_loop(player)
logic = controller.Logic(game)

def callback(obj):
    world.remove(obj)
    game.animator.remove_object(player)


while True:
    if not game.pygame_events():
        break

    dt = game.update_world(display)
    logic.update()

    fps = int(1 / dt)

    

    # Fill background
    mouse_x, mouse_y = pygame.mouse.get_pos()

    debugger.clear()

    # Add text here
    debugger.add(str(fps))
    debugger.add('Mouse X = {}'.format(mouse_x))
    debugger.add('Mouse Y = {}'.format(mouse_y))
    dic = game.world.get_main_dic().items()
    for type_name, array in dic:
        debugger.add('{}: {}'.format(type_name, len(array)))

    debugger.render(display)

    pygame.display.update()

    clock.tick(60)
