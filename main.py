#!/usr/bin/python3
import pygame
import gameobjects
import controller


RES_X = 1280
RES_Y = 720

game = controller.Game(RES_X, RES_Y)


game.level_test()

logic = controller.Logic(game)

game.loop()
print('Goodbye')