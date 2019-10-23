import pygame
import gameobjects
from pygame.locals import (
    QUIT,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
    KEYDOWN,
    KEYUP
)
import datetime


class ResourcesLoader():
    GAME_SPRITES = {'explosion':    {'path': 'sprites/explosion.png',
                                     'tx': 8, 'ty': 8},
                    'player':       {'path': 'sprites/player.png',
                                     'tx': 2, 'ty': 1},
                    'enemy':        {'path': 'sprites/enemyRed2.png',
                                     'tx': 1, 'ty': 1},
                    'bullet':       {'path': 'sprites/laserRed01.png',
                                     'tx': 1, 'ty': 1}
                    }

    def __init__(self):
        self.sprites = {}
        for name in ResourcesLoader.GAME_SPRITES.keys():
            sprite = ResourcesLoader.load_sprite(name)
            self.sprites[name] = sprite

    def load_sprite(name):
        data = ResourcesLoader.GAME_SPRITES[name]
        if data['tx'] + data['ty'] > 2:
            return ResourcesLoader.asprite_from_path(
                        data['path'], data['tx'], data['ty'])
        else:
            return ResourcesLoader.sprite_from_path(data['path'])

    def sprite_from_path(filename):
        img = pygame.image.load(filename).convert_alpha()
        return gameobjects.Sprite(img)

    def asprite_from_path(filename, tx, ty):
        img = pygame.image.load(filename).convert_alpha()
        return gameobjects.ASprite(img, tx, ty)


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
    def __init__(self, game_manager):
        self._can_shoot = True
        self._game_manager = game_manager
        world = game_manager.world
        mouse = game_manager.mouse
        self._player = world.get_by_type('player')[0]
        self._bullets = world.get_by_type('bullet')
        self._enemies = world.get_by_type('enemy')
        self._world = world
        self._res = game_manager.res_load

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
            else:
                for enemy in self._enemies:
                    if bullet.collides(enemy):
                        enemy.health -= 10
                        self._world.remove(bullet)
                        if enemy.health <= 0:
                            self._world.remove(enemy)
                            self._create_explosion(enemy.pos)

    def _create_explosion(self, pos):
        exp_sprite = self._res.sprites['explosion']
        exp = gameobjects.SpriteGameObject(exp_sprite,
                                           pos)
        self._game_manager.world.append(exp, 'explosion')
        self._game_manager.animator.add_object_onetime(exp, self._world.remove)
              

class Animator():
    def __init__(self):
        self._objects_loop = []  # Keep animating
        self._objects_onetime = {}  # {object, callback}

    def update(self, delta_time):
        for obj in self._objects_loop:
            self._update_obj(obj, delta_time)

        to_remove = []
        for obj, callback in self._objects_onetime.items():
            if self._update_obj(obj, delta_time):
                to_remove.append(obj)
                callback(obj)

        for r in to_remove:
            del self._objects_onetime[r]

    def _update_obj(self, obj, delta_time):
        '''
        Returns True when replaying.
        '''
        asprite = obj.sprite
        fps = asprite.fps
        asprite.internal_frame += delta_time * fps
        if asprite.internal_frame >= 1:
            delta_frames = int(asprite.internal_frame)
            asprite.internal_frame -= delta_frames
            asprite.frame += delta_frames
            if asprite.frame >= asprite.frames_count:
                asprite.frame %= asprite.frames_count
                return True
        return False

    def add_object_loop(self, object):
        if object not in self._objects_loop:
            object.sprite.internal_frame = 0
            self._objects_loop.append(object)

    def remove_object(self, object):
        if object in self._objects_loop:
            self._objects_loop.remove(object)

    def add_object_onetime(self, object, callback):
        if object not in self._objects_onetime:
            object.sprite.internal_frame = 0
            self._objects_onetime[object] = callback


class Game():
    def __init__(self, world):
        self.keyboard = Input()
        self.mouse = Input()
        self.world = world
        self.animator = Animator()
        self.res_load = ResourcesLoader()
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

        display.fill((0, 30, 30))

        self.animator.update(delta_time)

        for gobj in self.world.get_all_objects():
            gobj.update(delta_time)
            gobj.draw(display)

        self._lastdt = dt
        return delta_time
