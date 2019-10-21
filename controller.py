import pygame
from pygame.locals import (
    QUIT,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
    KEYDOWN,
    KEYUP
)
import datetime


class Input():
    def __init__(self):
        self._events = {}

    def register(self, key_code, command):
        self._events[key_code] = command

    def on_key(self, key_code, down=True):
        if key_code in self._events:
            self._events[key_code](down)


class World():
    def __init__(self):
        # Key: Object type string
        # Value: Object
        self._objects = {}

        # Key = gameobject
        # Value = array of containing groups
        # helps in deleting objects
        self._obj_parents = {}

        # Contains all objects
        self._all_objects = []

    def append(self, object, type_name):
        self._append_dic(type_name, object, self._objects)
        self._append_list(object, self._all_objects)
        self._append_dic(object, self._objects[type_name], self._obj_parents)

    def _append_dic(self, key, value, dic):
        if key in dic:
            self._append_list(value, dic[key])
        else:
            dic[key] = []
            self._append_list(value, dic[key])

    def _append_list(self, value, list):
        if value not in list:
            list.append(value)

    def get_all_objects(self):
        return self._all_objects

    def remove(self, object):
        groups = self._obj_parents[object]
        for g in groups:
            g.remove(object)
        self._all_objects.remove(object)
        del self._obj_parents[object]

    def get_by_type(self, type_name):
        if type_name not in self._objects:
            # Create the requested type_name and
            # return it as an empty array
            self._objects[type_name] = []
            return self._objects[type_name]
        return self._objects[type_name]

    def get_main_dic(self):
        return self._objects


class Logic():
    def __init__(self, keyboard, mouse, world):
        self._can_shoot = True
        self._player = world.get_by_type('player')[0]
        self._bullets = world.get_by_type('bullet')
        self._world = world

        mouse.register(1, self.shoot)

    def shoot(self, down):
        if down:
            if self._can_shoot:
                self._world.append(self._player.shoot(), 'bullet')
                self._can_shoot = False
        else:
            self._can_shoot = True

    def update(self):
        for bullet in self._bullets:
            if bullet.pos.y < 0:
                self._world.remove(bullet)


class Game():
    def __init__(self, world):
        self.keyboard = Input()
        self.mouse = Input()
        self.world = world
        self.logic = Logic(self.keyboard, self.mouse, self.world)
        self._lastdt = datetime.datetime.now()

    def pygame_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            elif event.type == MOUSEBUTTONDOWN:
                self.mouse.on_key(event.button, True)
            elif event.type == MOUSEBUTTONUP:
                self.mouse.on_key(event.button, False)
            elif event.type == KEYUP or event.type == KEYDOWN:
                self.keyboard.on_key(event.key, event.type == KEYDOWN)

        return True

    def update_world(self, display):
        dt = datetime.datetime.now()
        delta_time = (dt - self._lastdt).total_seconds()

        display.fill((0, 0, 0))

        global world
        for gobj in self.world.get_all_objects():
            gobj.update(delta_time)
            gobj.draw(display)

        self.logic.update()

        self._lastdt = dt
        return delta_time
