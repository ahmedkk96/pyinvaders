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
import random


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

        # Contains all objects
        self._all_objects = []

        gameobjects.WorldHelper.init(self.append_child,
                                     self.remove)

    def append(self, object):
        type_name = object.OBJECT_TYPE
        self._append_dic(type_name, object, self._objects)
        self._append_list(object, self._all_objects)

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
        for parent in object.parents:
            parent.on_remove_child(object)

        g = self._objects[object.OBJECT_TYPE]
        g.remove(object)
        self._all_objects.remove(object)

    def get_by_type(self, type):
        type_name = type.OBJECT_TYPE
        if type_name not in self._objects:
            # Create the requested type_name and
            # return it as an empty array
            self._objects[type_name] = []
            return self._objects[type_name]
        return self._objects[type_name]

    def get_main_dic(self):
        return self._objects

    def append_child(self, parent, child):
        if parent is not None:
            child.parents.append(parent)
        self.append(child)


class Randomizer():
    def Drop(chance=0.2):
        r = random.randint(0, 100)
        max_val = 100 * chance
        return r < max_val


class Logic():
    def __init__(self, game_manager):
        self._can_shoot = True
        self._game = game_manager
        world = game_manager.world
        mouse = game_manager.mouse
        self._player = world.get_by_type(gameobjects.Player)[0]
        self._bullets = world.get_by_type(gameobjects.bullet_1)
        self._enemies = world.get_by_type(gameobjects.Enemy)
        self._e_bullets = world.get_by_type(gameobjects.e_bullet_1)
        self._world = world
        self._res = gameobjects.ResourcesLoader
        self.score = 0
        self._spawner = EnemySpwaner(self._world)
        self._wave = self._spawner.spawn()
        self._gui = game_manager.gui

        self._e_shoot_timeout = 1

        mouse.register(1, self.shoot)
        self._game.keyboard.register(97, self.upgrade_shoot)
        self._game.keyboard.register(122, self.downgrade_shoot)

    def shoot(self, down):
        if down:
            if self._can_shoot:
                self._player.shoot()
                self._can_shoot = False
        else:
            self._can_shoot = True

    def upgrade_shoot(self, down):
        if down:
            self._player.upgrade_shoot()

    def downgrade_shoot(self, down):
        if down:
            self._player.downgrade_shoot()

    def update(self, delta_time):
        self._update_player_pos()
        self._check_player_bullets()
        self._check_enemy_bullets()
        self._check_powerups()
        self.update_gui()

    def _create_explosion(self, pos):
        exp = self._game.create_add_go(gameobjects.Explosion)
        exp.set_pos(pos)
        self._game.animator.add_object_onetime(exp, self._world.remove)

    def _check_player_bullets(self):
        for bullet in self._bullets:
            for enemy in self._enemies:
                if bullet.collides(enemy):
                    self._world.remove(bullet)
                    if enemy.take_damage(bullet.DAMAGE):
                        self._world.remove(enemy)
                        self._create_explosion(enemy.get_pos())
                        self.score += enemy.SCORE
                        self._drop_powerup(enemy.get_pos())
                        if len(self._wave.enemies) == 0:
                            self._wave = self._spawner.spawn()
                    break  # Don't go to next enemy

    def _check_enemy_bullets(self):
        for bullet in self._e_bullets:
            if bullet.collides(self._player):
                self._world.remove(bullet)
                if self._player.take_damage(bullet.DAMAGE):
                    print('You\'ve lost')

    def _update_player_pos(self):
        mouse_pos = pygame.mouse.get_pos()
        self._player.set_pos(mouse_pos)

    def _drop_powerup(self, pos):
        if Randomizer.Drop(0.1):
            rand_type = random.randint(0, 2)
            type = [gameobjects.PowerupHealth,
                    gameobjects.PowerupWeapon,
                    gameobjects.PowerupShield][rand_type]
            pu = self._game.create_add_go(type)
            pu.set_pos(pos)

    def _check_powerups(self):
        powerups = self._world.get_by_type(gameobjects.DropItem)
        for p in powerups:
            if p.collides(self._player):
                self._player.on_powerup(p)
                self._world.remove(p)

    def update_gui(self):
        self._gui.set_health(self._player.health/gameobjects.Player.HEALTH)
        self._gui.set_score(self.score)


class EnemySpwaner:
    def __init__(self, world):
        self._difficulty = 0
        self._world = world

    def spawn(self):
        enemy_group = gameobjects.enemy_group_rect()
        enemy_group.create_enemies(10, 4, gameobjects.Enemy)
        enemy_group.move((0, 0))

        move = gameobjects.MovmentClassic(enemy_group)
        move.speed_x *= (1 + (self._difficulty * 0.5))

        rand_shooter = gameobjects.EnemyGroupShoot(enemy_group)
        rand_shooter.max_enemies_shooting += self._difficulty * 4
        rand_shooter.max_timeout -= self._difficulty * 0.1

        self._world.append(enemy_group)
        self._world.append(move)
        self._world.append(rand_shooter)

        self._difficulty += 1
        return enemy_group


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
        obj.internal_frame += delta_time * fps
        if obj.internal_frame >= 1:
            delta_frames = int(obj.internal_frame)
            obj.internal_frame -= delta_frames
            obj.frame += delta_frames
            if obj.frame >= asprite.frames_count:
                obj.frame %= asprite.frames_count
                return True
        return False

    def add_object_loop(self, object):
        if object not in self._objects_loop:
            object.internal_frame = 0
            self._objects_loop.append(object)

    def remove_object(self, object):
        if object in self._objects_loop:
            self._objects_loop.remove(object)

    def add_object_onetime(self, object, callback):
        if object not in self._objects_onetime:
            object.internal_frame = 0
            self._objects_onetime[object] = callback


class Game():
    def __init__(self, screen_width, screen_height):
        self.keyboard = Input()
        self.mouse = Input()
        self.world = World()
        self.animator = Animator()
        gameobjects.ResourcesLoader.__init__()
        self._lastdt = datetime.datetime.now()
        self.screen_rect = pygame.rect.Rect(0, 0,
                                            screen_width,
                                            screen_height)
        gameobjects.WorldHelper.screen_rect = self.screen_rect
        self.bg = gameobjects.ResourcesLoader.background('background')
        self.gui = GUI()

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

        self.bg.draw(display, self.screen_rect, delta_time)

        self.animator.update(delta_time)

        for gobj in self.world.get_all_objects():
            gobj.update(delta_time)
            gobj.draw(display)

        self.gui.draw(display)

        self._lastdt = dt
        return delta_time

    def create_add_go(self, type):
        go = type()
        self.add_go(go)
        return go

    def add_go(self, go):
        self.world.append(go)


class GUI:
    def __init__(self):
        self._health = gameobjects.ProgressBar()
        self._score = gameobjects.TextUI('0', (255, 0, 0), 32)

    def draw(self, surface):
        self._health.draw(surface, (20, 20))
        self._score.draw(surface, (20, 60))

    def set_health(self, health):
        self._health.set_value(health)

    def set_score(self, score):
        self._score.set_test('Score: {}'.format(score))
