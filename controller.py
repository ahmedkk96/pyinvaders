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
import TextDebugger


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

    def clear(self):
        # if 2 objects are referencing each other
        # they will never be removed
        # we gotta check that one by one
        for obj in self._all_objects:
            obj.parents.clear()
        self._all_objects.clear()
        for value in self._objects.values():
            value.clear()


class Randomizer():
    def Drop(chance=0.2):
        r = random.randint(0, 100)
        max_val = 100 * chance
        return r < max_val


class Controls:
    DEBUG1 = ord('a')
    DEBUG2 = ord('z')
    PAUSE = ord('p')
    RESET = ord('r')
    LOSE = ord('l')

    def __init__(self, player, game_state):
        self.keyboard = Input()
        self.keyboard.register(Controls.DEBUG1, self.debug1)
        self.keyboard.register(Controls.DEBUG2, self.debug2)
        self.keyboard.register(Controls.PAUSE, self._pause_event)
        self.keyboard.register(Controls.RESET, self._reset_event)
        self.keyboard.register(Controls.LOSE, self._lose_event)

        self.mouse = Input()
        self.mouse.register(1, self.shoot)

        self._player = player

        self._game_state = game_state

    def debug1(self, down):
        if down:
            self._player.upgrade_shoot()

    def debug2(self, down):
        if down:
            self._player.downgrade_shoot()

    def shoot(self, down):
        if down:
            self._player.shoot()

    def update_player_pos(self):
        mouse_pos = pygame.mouse.get_pos()
        self._player.set_pos(mouse_pos)

    def _pause_event(self, down):
        if self.on_pause is not None and down:
            self._game_state.on_pause()

    def _reset_event(self, down):
        if down:
            self._game_state.on_reset()

    def _lose_event(self, down):
        if down:
            self._game_state.on_lost()


def create_explosion(world, pos):
    exp = gameobjects.Explosion()
    world.append(exp)
    exp.set_pos(pos)


def drop_powerup(world, pos):
    if Randomizer.Drop(0.05):
        rand_type = random.randint(0, 2)
        type = [gameobjects.PowerupHealth,
                gameobjects.PowerupWeapon,
                gameobjects.PowerupShield][rand_type]
        pu = type()
        world.append(pu)
        pu.set_pos(pos)


class Collisions:
    '''
    Handles events of main gameobjects collisions
    '''
    def __init__(self, world, game_state):
        self._world = world
        self._player = world.get_by_type(gameobjects.Player)[0]
        self._bullets = world.get_by_type(gameobjects.bullet_1)
        self._enemies = world.get_by_type(gameobjects.Enemy)
        self._e_bullets = world.get_by_type(gameobjects.e_bullet_1)
        self._powerups = world.get_by_type(gameobjects.DropItem)
        self._game_state = game_state

    def check_list(self, obj, list, callback, only_one=True):
        for offender in list:
            if obj.collides(offender):
                callback(obj, offender)
                if only_one:
                    break

    def on_enemy_bullet(self, bullet, enemy):
        self._world.remove(bullet)
        if enemy.take_damage(bullet.DAMAGE):
            self._world.remove(enemy)
            self._player.score += enemy.SCORE

            create_explosion(self._world, enemy.get_pos())
            drop_powerup(self._world, enemy.get_pos())

    def on_player_bullet(self, player, bullet):
        self._world.remove(bullet)
        if player.take_damage(bullet.DAMAGE):
            create_explosion(self._world, player.get_pos())
            self._world.remove(player)
            self._game_state.on_lost()

    def on_powerup(self, player, p):
        self._player.on_powerup(p)
        self._world.remove(p)

    def update(self):
        # Check if enemy is hit
        for bullet in self._bullets:
            self.check_list(bullet, self._enemies, self.on_enemy_bullet)

        # Check if player is hit
        self.check_list(self._player, self._e_bullets,
                        self.on_player_bullet, False)

        # Check if powerup hits player
        self.check_list(self._player, self._powerups, self.on_powerup)


class EnemySpwaner:
    def __init__(self, world):
        self._difficulty = 0
        self._world = world

    def spawn(self):
        enemy_group = gameobjects.enemy_group_rect()
        enemy_group.create_enemies(10, 4, gameobjects.Enemy)
        enemy_group.move((0, 0))

        move = gameobjects.MovmentClassic(enemy_group)
        move.speed_x *= (1 + (self._difficulty * 0.2))

        rand_shooter = gameobjects.EnemyGroupShoot(enemy_group)
        # rand_shooter.max_enemies_shooting += self._difficulty * 4
        rand_shooter.max_timeout -= self._difficulty * 200

        self._world.append_child(self, enemy_group)
        self._world.append(move)
        self._world.append(rand_shooter)

        self._difficulty += 1
        self.enemy_group = enemy_group

    def on_remove_child(self, child):
        self.spawn()

    def reset(self):
        self._difficulty = 0
        self.enemy_group = None


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
                callback()

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

    def clear(self):
        self._objects_loop.clear()
        self._objects_onetime.clear()


class Updater:
    FPS_LIMIT = 60

    def __init__(self, game):
        self.game = game
        self._lastdt = datetime.datetime.now()
        self.clock = pygame.time.Clock()

    def pygame_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            elif event.type == MOUSEBUTTONDOWN:
                self.game.controls.mouse.on_key(event.button, True)
            elif event.type == MOUSEBUTTONUP:
                self.game.controls.mouse.on_key(event.button, False)
            elif event.type == KEYUP or event.type == KEYDOWN:
                self.game.controls.keyboard.on_key(
                    event.key, event.type == KEYDOWN)

        return True

    def update_world(self, delta_time):
        self.game.controls.update_player_pos()
        for gobj in self.game.world.get_all_objects():
            gobj.update(delta_time)

        self.game.collisions.update()

    def update_all(self, paused):
        tnow = datetime.datetime.now()
        dt = (tnow - self._lastdt).total_seconds()
        self._lastdt = tnow

        if not paused:
            self.update_world(dt)

        self.game.gui.update()
        pygame.display.update()

        self.clock.tick(Updater.FPS_LIMIT)
        return dt


class Render:
    def __init__(self, game, display):
        self.bg = gameobjects.ResourcesLoader.background('background')
        self.game = game
        self.display = display
        self.debugger = TextDebugger.Renderer()

    def draw(self, deltatime):
        self.game.animator.update(deltatime)
        self.bg.draw(self.display, deltatime)

        for obj in self.game.world.get_all_objects():
            obj.draw(self.display)

        self.game.gui.draw(self.display)
        self._debug(deltatime, self.display)

    def _debug(self, dt, display):
        debugger = self.debugger
        debugger.clear()

        fps = int(1 / dt)
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Add text here
        debugger.add(str(fps))
        debugger.add('Mouse X = {}'.format(mouse_x))
        debugger.add('Mouse Y = {}'.format(mouse_y))

        dic = self.game.world.get_main_dic().items()
        for type_name, array in dic:
            debugger.add('{}: {}'.format(type_name, len(array)))

        debugger.render(display)
        # self.debug_rect(display)

    def debug_rect(self, display):
        objs = self.game.world.get_all_objects()
        for obj in objs:
            pygame.draw.rect(display, (255, 255, 255), obj.get_rect(), 1)


class Components():
    def __init__(self, game_state):
        self.animator = Animator()
        gameobjects.WorldHelper.animator = self.animator

        self.world = World()
        self.player = self._create_player()
        self.world.append(self.player)

        self.gui = GUI(self.player)

        self.controls = Controls(self.player, game_state)
        self.controls.on_pause = game_state.on_pause

        self.spawner = EnemySpwaner(self.world)
        self.spawner.spawn()

        self.collisions = Collisions(self.world, game_state)

        self.game_state = game_state

    def _create_player(self):
        player = gameobjects.Player()
        player.sprite.fps = 15
        return player

    def reset(self):
        self.world.clear()
        self.player.__init__()
        self.world.append(self.player)
        self.gui.loser(False)
        self.spawner.reset()
        self.spawner.spawn()
        self.animator.clear()


class GUI:
    def __init__(self, player):
        self._health = gameobjects.ProgressBar()
        self._shield = gameobjects.ProgressBar((0, 0, 255), (0, 0, 0))
        self._score = gameobjects.TextUI('0', (255, 0, 0), 32)
        self._big_message = gameobjects.TextUI('Loser', size=100)
        self._lost = False
        self._player = player

    def draw(self, surface):
        self._health.draw(surface, (20, 20))
        self._shield.draw(surface, (20, 60))
        self._score.draw(surface, (20, 100))
        if self._lost:
            self._big_message.draw(surface, (500, 400))

    def update(self):
        self._health.set_value(self._player.health /
                               self._player.HEALTH)
        self._shield.set_value(self._player.get_shield_health() /
                               gameobjects.shield_1.HEALTH)
        self._score.set_test('Score: {}'.format(self._player.score))

    def loser(self, lost=True):
        self._lost = lost
