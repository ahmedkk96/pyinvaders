import pygame
from pygame.math import Vector2
import random


class ResourcesLoader():
    def __init__():
        file = open('sprites/sprites_list.csv')
        file.readline()

        ResourcesLoader.sprites = {}

        while True:
            line = file.readline()
            if line == '':
                break

            line = line.strip()
            data = line.split(',')

            name, path, tx, ty, fps = data
            tx = int(tx)
            ty = int(ty)
            fps = int(fps)

            if name == 'background':
                sprite = ResourcesLoader.background(path)
            else:
                sprite = ResourcesLoader.sprite_from_path(path, tx, ty)

            ResourcesLoader.sprites[name] = sprite

    def sprite_from_path(filename, tx, ty):
        img = pygame.image.load(filename).convert_alpha()
        return Sprite(img, tx, ty)

    def background(path):
        img = pygame.image.load(path).convert_alpha()
        return Background(img)


class WorldHelper:
    '''
    Global static class that works as an interface
    between gameobject instances and world
    (world global variable)
    '''
    append = None
    remove = None
    animator = None
    screen_rect = None


def Rect_From_Center(pos, size):
        tx1 = pos[0] - size[0]/2
        ty1 = pos[1] - size[1]/2
        return pygame.rect.Rect(tx1, ty1, size[0], size[1])


def velocity_dir(start, end, velocity):
    dir = (end - start).normalize()
    return dir * velocity


class Sprite(pygame.sprite.Sprite):
    def __init__(self, img, tiles_x, tiles_y=1):
        super(Sprite, self).__init__()
        self.frames_count = tiles_x * tiles_y
        self.fps = 30
        self._sub_images(img, tiles_x, tiles_y)
        self.image = self._imgs[0]

    def _sub_images(self, img, tiles_x, tiles_y):
        # non animated check:
        if self.frames_count == 1:
            self._imgs = [img]
            return

        # Divides the sheet into sub frames
        self._framw_width = img.get_width() / tiles_x
        self._frame_height = img.get_height() / tiles_y
        self._imgs = []

        for y in range(0, tiles_y):
            y1 = y * self._frame_height
            for x in range(0, tiles_x):
                sub_surface = pygame.surface.Surface(
                    (self._framw_width, self._frame_height),
                    pygame.SRCALPHA, 32)

                x1 = x * self._framw_width

                source = pygame.rect.Rect(
                                x1, y1,
                                self._framw_width, self._frame_height)

                sub_surface.blit(img, (0, 0), source)
                self._imgs.append(sub_surface)

    def draw(self, target_surface, pos, frame):
        img = self._imgs[frame]
        rect = Rect_From_Center(pos, img.get_size())
        target_surface.blit(img, rect)


class Background(Sprite):
    def __init__(self, img):
        self.image = img
        self._size = img.get_rect()
        self.scroll_speed = 100
        self._y = 0

    def draw(self, display, delta_time):
        # Fill size with background.
        # Always rendering more than one additional tile
        screen_rect = display.get_rect()

        x, y = 0, self._y - self._size.height
        self._y += delta_time * self.scroll_speed
        self._y %= self._size.height

        while y < screen_rect.height:
            while x < screen_rect.width:
                targ = self._size.move(x, y)
                display.blit(self.image, targ)
                x += targ.width
            x = 0
            y += targ.height


class GameObject:
    OBJECT_TYPE = ''

    def __init__(self):
        self._pos = Vector2(0, 0)
        self._size = Vector2(1, 1)
        self.speed = Vector2(0, 0)
        self.on_removed_event = []

    def update(self, delta_time):
        # Movement
        self._pos += self.speed * delta_time

    def draw(self, display):
        pass

    def get_rect(self):
        return Rect_From_Center(self._pos, self._size)

    def collides(self, other):
        return self.get_rect().colliderect(other.get_rect())

    def inside_screen(self, screen_rect):
        self_rect = self.get_rect()
        return self_rect.colliderect(screen_rect)

    def get_pos(self):
        return Vector2(self._pos)  # a copy

    def set_pos(self, pos):
        self._pos = Vector2(pos)  # a copy

    def move(self, offset):
        self.set_pos(self._pos + offset)

    def remove_outside_screen(self):
        if not self.get_rect().colliderect(WorldHelper.screen_rect):
            WorldHelper.remove(self)

    def on_world_remove(self):
        # notify listeners for remove event
        for event in self.on_removed_event:
            event(self)


class SpriteGameObject(GameObject):
    '''
    Implementation with sprite
    which gets the size from it
    '''
    SPRITE_NAME = ''

    def __init__(self):
        GameObject.__init__(self)
        sprite = self._load_sprite()
        self.sprite = sprite
        self._size = sprite.image.get_size()
        self.frame = 0

    def _load_sprite(self):
        sprite = ResourcesLoader.sprites[self.SPRITE_NAME]
        return sprite

    def draw(self, target_surf):
        self.sprite.draw(target_surf, self._pos, self.frame)


class HealthGameObject(SpriteGameObject):
    HEALTH = 0

    def __init__(self, *args, **kw):
        super(HealthGameObject, self).__init__(*args, **kw)
        self.health = self.HEALTH

    def take_damage(self, damage):
        '''
        Returns True when health is depleted
        '''
        self.health -= damage
        if self.health <= 0:
            return True
        return False


class Player(HealthGameObject):
    SPRITE_NAME = 'player'
    OBJECT_TYPE = 'player'
    HEALTH = 100

    def __init__(self, *args, **kw):
        super(Player, self).__init__(*args, **kw)
        self._shooting_modes = [self._shoot_0,
                                self._shoot_1,
                                self._shoot_2,
                                self._shoot_3]
        self._shooting_mode = 0
        self._shield = None
        self.score = 0

        self.sprite.fps = 15
        WorldHelper.animator.add_object_loop(self)

    def take_damage(self, damage):
        if self._shield is not None:
            if self._shield.take_damage(damage):
                WorldHelper.remove(self._shield)
                self._shield = None
        else:
            return super(Player, self).take_damage(damage)

    def _shoot_0(self):
        self._create_bullet(0, 0, Bullet)

    def _shoot_1(self):
        self._create_bullet(25, 0, Bullet)
        self._create_bullet(-25, 0, Bullet)

    def _shoot_2(self):
        self._create_bullet(0, -25, Bullet)
        self._shoot_1()

    def _shoot_3(self):
        self._create_bullet(25, 0, Bullet2)
        self._create_bullet(-25, 0, Bullet2)

    def shoot(self):
        self._shooting_modes[self._shooting_mode]()

    def _create_bullet(self, offset_x, offset_y, type):
        b = type()
        b.set_pos(self._pos + Vector2(offset_x, offset_y))
        WorldHelper.append(b)

    def upgrade_shoot(self):
        if self._shooting_mode < len(self._shooting_modes) - 1:
            self._shooting_mode += 1

    def remove_shoot_upgrades(self):
        self._shooting_mode = 0

    def downgrade_shoot(self):
        if self._shooting_mode > 0:
            self._shooting_mode -= 1

    def on_powerup(self, powerup):
        if powerup.PU_TYPE == 'weapon':
            self.upgrade_shoot()
        elif powerup.PU_TYPE == 'health':
            self.health = 100
        elif powerup.PU_TYPE == 'shield':
            self.create_shield(shield_1)

    def create_shield(self, shield):
        if self._shield is None:
            sh = shield()
            sh.set_player(self)
            self._shield = sh
            WorldHelper.append(sh)
        else:
            self._shield.health = self._shield.HEALTH

    def get_shield_health(self):
        if self._shield is not None:
            return self._shield.health
        else:
            return 0


class Bullet(SpriteGameObject):
    SPRITE_NAME = 'bullet_1'
    OBJECT_TYPE = 'bullet'
    DAMAGE = 25
    SPEED = -1000

    def __init__(self):
        super(Bullet, self).__init__()
        self.speed.y = self.SPEED

    def update(self, dt):
        super(Bullet, self).update(dt)
        self.remove_outside_screen()


class Bullet2(Bullet):
    SPRITE_NAME = 'bullet_2'
    OBJECT_TYPE = 'bullet'
    DAMAGE = 50


class EBullet(Bullet):
    SPRITE_NAME = 'e_bullet_1'
    OBJECT_TYPE = 'enemy_bullet'
    DAMAGE = 25
    SPEED = 300


class EBulletTargeted(EBullet):
    def __init__(self, pos, target):
        super(EBulletTargeted, self).__init__()
        self.set_pos(pos)
        self.speed = velocity_dir(pos,
                                  target,
                                  self.SPEED)


class Enemy(HealthGameObject):
    SPRITE_NAME = 'enemy'
    OBJECT_TYPE = 'enemy'
    ENEMY_TYPE = 'simple'
    HEALTH = 75
    SCORE = 100

    def shoot(self):
        bullet = EBullet()
        bullet.set_pos(self._pos)
        WorldHelper.append(bullet)


class Enemy2(Enemy):
    SPRITE_NAME = 'enemy_blue2'
    HEALTH = 125
    SCORE = 300


class EnemyDiver(Enemy):
    DIVE_SPEED = 500
    ACCEL_TIME = 1
    ENEMY_TYPE = 'diver'
    HEALTH = 100
    SCORE = 200

    def dive(self):
        move = MovementAccelDown(self.ACCEL_TIME, self.DIVE_SPEED)
        move.set_child(self)
        WorldHelper.append(move)


class EnemyTargtedBullet(Enemy):
    SPRITE_NAME = 'enemy_red4'
    HEALTH = 150
    SCORE = 500
    ENEMY_TYPE = 'targeted_bullet'

    def __init__(self, player):
        super(EnemyTargtedBullet, self).__init__()
        self.player = player

    def shoot(self):
        bullet = EBulletTargeted(self.get_pos(),
                                 self.player.get_pos())

        WorldHelper.append(bullet)


class Explosion(SpriteGameObject):
    SPRITE_NAME = 'explosion'
    OBJECT_TYPE = 'explosion'

    def __init__(self):
        super(Explosion, self).__init__()
        self.sprite.fps = 15
        WorldHelper.animator.add_object_onetime(self, self.on_finish)

    def on_finish(self):
        WorldHelper.remove(self)


class DropItem(SpriteGameObject):
    OBJECT_TYPE = 'dropitem'
    SPEED = 150

    def __init__(self, *args, **kwargs):
        super(DropItem, self).__init__(*args, **kwargs)
        self.speed = Vector2(0, self.SPEED)

    def update(self, dt):
        super(DropItem, self).update(dt)
        self.remove_outside_screen()


class PowerupWeapon(DropItem):
    SPRITE_NAME = 'pu_weapon'
    PU_TYPE = 'weapon'


class PowerupShield(DropItem):
    SPRITE_NAME = 'pu_shield'
    PU_TYPE = 'shield'


class PowerupHealth(DropItem):
    SPRITE_NAME = 'pu_health'
    PU_TYPE = 'health'


class Shield(HealthGameObject):
    OBJECT_TYPE = 'shield'
    HEALTH = 0
    OFF_Y = 0

    def set_player(self, player):
        self._player = player

    def update(self, delta_time):
        self._pos = self._player.get_pos()
        self._pos.y += self.OFF_Y


class shield_1(Shield):
    SPRITE_NAME = 'shield_1'
    HEALTH = 100
    OFF_Y = -30


class EnemyGroup(GameObject):
    OBJECT_TYPE = 'enemy_group'

    def __init__(self):
        super(EnemyGroup, self).__init__()
        self.enemies = {}
        self.all_enemies = []

    def append(self, enemy):
        if enemy.ENEMY_TYPE in self.enemies:
            self.enemies[enemy.ENEMY_TYPE].append(enemy)
            self.all_enemies.append(enemy)
            enemy.on_removed_event.append(self.on_child_removed)
            WorldHelper.append(enemy)
        else:
            self.enemies[enemy.ENEMY_TYPE] = []
            self.append(enemy)

    def dive(self):
        divers = self.enemies_by_type(EnemyDiver)
        if divers is not None and len(divers) > 0:
            rand = random.randrange(len(divers))
            divers[rand].dive()

            # It's not actually removed,
            # but it just separated
            # unsub from (onremoved) event
            divers[rand].on_removed_event.remove(self.on_child_removed)
            self.on_child_removed(divers[rand])
            return True
        return False

    def shoot(self):
        enemies = self.all_enemies
        enemies_count = len(enemies) - 1
        enemy = enemies[random.randint(0, enemies_count)]
        enemy.shoot()

    def on_child_removed(self, child):
        self.enemies[child.ENEMY_TYPE].remove(child)
        self.all_enemies.remove(child)
        if len(self.all_enemies) == 0:
            WorldHelper.remove(self)

    def update(self, delta_time):
        pass

    def _update_pos(self, diff):
        for e in self.all_enemies:
            e.move(diff)

    def get_rect(self):
        rect = self.all_enemies[0].get_rect()
        for e in self.all_enemies:
            rect.union_ip(e.get_rect())

        return rect

    def set_pos(self, new_pos):
        self._update_pos(new_pos-self._pos)
        self._pos = new_pos

    def enemies_by_type(self, type):
        if type.ENEMY_TYPE in self.enemies:
            return self.enemies[type.ENEMY_TYPE]
        else:
            return None

    def clear(self):
        for enemy in self.all_enemies:
            enemy.on_removed_event.remove(self.on_child_removed)
            WorldHelper.remove(enemy)

        self.enemies.clear()
        self.all_enemies.clear()

    def on_world_remove(self):
        super(EnemyGroup, self).on_world_remove()
        self.clear()


class EnemyRect(EnemyGroup):
    def _create_enemy(self, type, offset):
        p = Vector2(self._pos)
        e = type()
        p.x += offset[0]
        p.y += offset[1]
        e.set_pos(p)
        self.append(e)

    def uniform_rectangle(self, width, height, type,
                          padding_x=100, padding_y=60):
        for y in range(0, height):
            for x in range(0, width):
                self._create_enemy(type,
                                   (x*padding_x, y*padding_y))

    def mixed_rows(self, width, types,
                   padding_x=100, padding_y=60):
        for y in range(0, len(types)):
            for x in range(0, width):
                self._create_enemy(types[y],
                                   (x*padding_x, y*padding_y))

    def random_rectangle(self, width, height, weighted,
                         padding_x=100, padding_y=60):
        count = height
        for y in range(0, count):
            for x in range(0, width):
                self._create_enemy(weighted.roll(),
                                   (x*padding_x, y*padding_y))


class Parent(GameObject):
    '''
    This class is a parent for one object,
    removes itself when child is removed from world
    '''

    def __init__(self):
        super(Parent, self).__init__()
        self.child = None

    def set_child(self, child):
        if self.child is not None:
            self.child.on_removed_event.remove(self.on_child_removed)
        self.child = child
        self.child.on_removed_event.append(self.on_child_removed)

    def on_child_removed(self, child):
        self.child = None
        WorldHelper.remove(self)

    def remove_self(self):
        self.child.on_removed_event.remove(self.on_child_removed)
        WorldHelper.remove(self)


class Movement(Parent):
    OBJECT_TYPE = 'movement'


class MovementPath(Movement):
    '''
    Interpolater between 0 and 1
    0.0 is the start of animation
    1.0 is the end
    '''
    def __init__(self, time):
        super(MovementPath, self).__init__()
        self._time = time
        self.t = 0
        self.loop = False
        self._dir = 1  # 1 or -1

    def clamp(self):
        if self.t > 1:
            self.t = 1
            if self.loop:
                self._dir *= -1
                return False
            else:
                return True
        elif self.t < 0:
            self.t = 0
            if self.loop:
                self._dir *= -1
                return False
            else:
                return True

    def seek(self, dt):
        self.t += (dt / self._time) * self._dir
        result = self.clamp()
        if result:
            self.on_finished()
        return result

    def on_finished(self):
        self.remove_self()

    def update(self, dt):
        self.seek(dt)
        self.child.set_pos(self.get_current())

    def get_total_time(self):
        return self._time

    def set_abs_time(self, time):
        self.t = time / self._time


class MovementLinear(MovementPath):
    def __init__(self, time, p1, p2):
        super(MovementLinear, self).__init__(time)
        self._p1 = Vector2(p1)
        self._p2 = Vector2(p2)

    def get_current(self):
        return self._p1.lerp(self._p2, self.t)


class MovementLinearVel(MovementLinear):
    def __init__(self, p1, p2, velocity):
        p1 = Vector2(p1)
        p2 = Vector2(p2)
        distance = (p2-p1).magnitude()
        time = distance / velocity
        super(MovementLinearVel, self).__init__(time, p1, p2)


class MovementBezier(MovementPath):
    def __init__(self, time, p0, p1, p2):
        super(MovementBezier, self).__init__(time)
        self._p0 = Vector2(p0)
        self._p1 = Vector2(p1)
        self._p2 = Vector2(p2)

    def get_current(self):
        x1 = self._p0.lerp(self._p1, self.t)
        x2 = self._p1.lerp(self._p2, self.t)
        return x1.lerp(x2, self.t)


class MovementCompound(MovementPath):
    def __init__(self, movements):
        time = 0
        for move in movements:
            time += move.get_total_time()
        super(MovementCompound, self).__init__(time)
        self._moves = movements

    def get_current(self):
        cum_time = 0  # Add each animation total time
        t = self.t * self._time  # convert normalized time
        for move in self._moves:
            last_time = cum_time  # starting time of this move
            cum_time += move.get_total_time()  # ending time
            if t <= cum_time:  # if t is in between start and end
                # set move.t to (current time) - (starting time)
                # which means convert global time to local
                move.t = (t - last_time) / move.get_total_time()
                return move.get_current()


class MovementAccelDown(Parent):
    def __init__(self, time, max_vel):
        super(MovementAccelDown, self).__init__()
        self.accel = max_vel / time
        self.max_vel = max_vel
        self.cur_vel = 0

    def update(self, dt):
        if self.cur_vel < self.max_vel:
            self.cur_vel += dt * self.accel
        else:
            self.cur_vel = self.max_vel
        self.child.speed.y = self.cur_vel
        self.child.remove_outside_screen()


class MovementGroupSpawn(MovementPath):
    STARTING_POS = (-50, 400)
    DELAY = 0.2
    ONE_CURVE_TIME = 1

    def __init__(self):
        super(MovementGroupSpawn, self).__init__(-1)
        self._after_movement = None

    def set_child(self, child):
        super(MovementGroupSpawn, self).set_child(child)
        self.reset()

    def set_movement_after(self, movement):
        self._after_movement = movement

    def reset(self):
        '''
        Moves enemies out of screen and spawn them one by one

        call it after filling enemy group
        '''
        self.number = len(self.child.all_enemies)
        self.index = 0
        delay_time = (self.number-1) * self.DELAY
        self._time = delay_time + self.ONE_CURVE_TIME

        index = 0
        for e in self.child.all_enemies:
            end_pos = e.get_pos()

            delay = index * self.DELAY
            index += 1

            bezier = MovementBezier(self.ONE_CURVE_TIME,
                                    self.STARTING_POS,
                                    (end_pos[0], self.STARTING_POS[1]),
                                    end_pos)
            bezier.delay = delay

            e.group_curve = bezier
            e.set_pos(self.STARTING_POS)

    def update(self, dt):
        self.seek(dt)
        for e in self.child.all_enemies:
            bezier = e.group_curve
            delay = bezier.delay
            end_time = delay + bezier.get_total_time()

            abs_time = self.t * self._time
            t = 0
            if abs_time > end_time:
                t = bezier.get_total_time()
            elif abs_time < delay:
                t = 0
            else:
                t = abs_time - delay

            bezier.set_abs_time(t)
            e.set_pos(bezier.get_current())

    def on_finished(self):
        super(MovementGroupSpawn, self).on_finished()
        if self._after_movement is not None:
            WorldHelper.append(self._after_movement)
            self._after_movement.set_child(self.child)


class MovmentClassic(Parent):
    OBJECT_TYPE = 'movement'
    SPEED_X = 100
    STEP_Y = 60
    PADDING_X = 30
    LOWER_LIMIT = 720

    def __init__(self):
        super(MovmentClassic, self).__init__()
        self.speed_x = MovmentClassic.SPEED_X
        self.step_y = MovmentClassic.STEP_Y
        self.dir = True
        self._residual = 0
        self.on_under_screen = None
        self.lower_limit = self.LOWER_LIMIT

    def set_child(self, child):
        super(MovmentClassic, self).set_child(child)
        self._rect = child.get_rect()
        self._left = self._rect.left
        self._right = self._rect.right
        self._bottom = self._rect.bottom

    def update(self, delta_time):
        offset_x = delta_time * self.speed_x
        if not self.dir:
            offset_x *= -1
        offset_y = 0
        sc = WorldHelper.screen_rect

        if self._right + offset_x > sc.width:
            offset_x = sc.width - self._right
            offset_y = self.step_y
            self.check_under_screen(offset_y)
            self.dir = False

        if self._left + offset_x < 0:
            offset_x = -self._left
            offset_y = self.step_y
            self.check_under_screen(offset_y)
            self.dir = True

        self._right += offset_x
        self._left += offset_x

        self.child.move(Vector2(offset_x, offset_y))

    def check_under_screen(self, offset_y):
        self._bottom += offset_y
        if self._bottom > self.lower_limit and\
           self.on_under_screen is not None:
            self.on_under_screen()


class ShooterPeriodic(Parent):
    OBJECT_TYPE = 'shooter_pattern'
    INTERVAL = 1.0

    def __init__(self):
        super(ShooterPeriodic, self).__init__()
        self.set_interval(self.INTERVAL)

    def set_interval(self, interval):
        self.interval = interval
        self._time = interval

    def reset_clock(self):
        self._time = self.interval

    def update(self, dt):
        self._time -= dt
        if self._time <= 0:
            self.reset_clock()
            self.shoot()

    def shoot(self):
        self.child.shoot()


class ShooterPeriodicVary(ShooterPeriodic):
    def __init__(self):
        super(ShooterPeriodicVary, self).__init__()
        self.min_timeout = 0.1
        self.max_timeout = 2
        self.variance = 1
        self.reset_clock()

    def reset_clock(self):
        tmin = int(self.min_timeout * 1000)
        tmax = int(self.max_timeout * 1000)
        val = tmin
        for i in range(0, self.variance):
            val = max(val, random.randint(tmin, tmax))
        self.set_interval(val / 1000.0)


class ShooterGroup(ShooterPeriodicVary):
    def __init__(self):
        super(ShooterGroup, self).__init__()
        self.max_enemies_shooting = 1

    def shoot(self):
        num_of_enemies = random.randint(1, self.max_enemies_shooting)
        for i in range(0, num_of_enemies):
            self.child.shoot()


class ShooterGroupDiver(ShooterGroup):
    OBJECT_TYPE = 'shooter_pattern_diver'

    def shoot(self):
        if not self.child.dive():
            self.remove_self()


class Meteor(SpriteGameObject):
    OBJECT_TYPE = 'meteor'
    SPEED = 1000

    def __init__(self):
        super(Meteor, self).__init__()
        self._inside_screen = False
        self.speed.x = self.SPEED
        self.speed.rotate_ip(30)

    def update(self, dt):
        super(Meteor, self).update(dt)
        if self.inside_screen(WorldHelper.screen_rect):
            self._inside_screen = True
        # Waits until it get's on screen (spawn)
        # then check if it became out to remove
        if self._inside_screen:
            self.remove_outside_screen()


class MeteorBig(Meteor):
    SPRITE_NAME = 'meteor_big'


class MeteorGenerator(ShooterPeriodic):
    OBJECT_TYPE = 'meteor_spawner'
    INTERVAL = 1
    UPPER_LIMIT = -300
    LOWER_LIMIT = 500

    def __init__(self, life_time):
        super(MeteorGenerator, self).__init__()
        self.speed = Meteor.SPEED
        self.life_time = life_time

    def update(self, dt):
        super(MeteorGenerator, self).update(dt)
        self.life_time -= dt
        if self.life_time <= 0:
            WorldHelper.remove(self)

    def spawn(self):
        meteor = MeteorBig()
        meteor.set_pos((-100, random.randint(self.UPPER_LIMIT,
                                             self.LOWER_LIMIT)))
        WorldHelper.append(meteor)

    def shoot(self):
        self.spawn()


class ProgressBar:
    WIDTH = 400
    HEIGHT = 20
    PADDING = 3
    BORDER_COLOR = (255, 255, 255)

    def __init__(self, color_fore=(0, 255, 0), color_back=(255, 0, 0)):
        self.color1 = color_fore
        self.color2 = color_back
        self._surf = pygame.surface.Surface((self.WIDTH, self.HEIGHT))
        self._rect = self._surf.get_rect()
        self._last_val = -1
        self.set_value(0)

    def set_value(self, val):
        if val != self._last_val:
            self._rect.right = self.WIDTH * val
            self._surf.fill(self.color2)
            pygame.draw.rect(self._surf, self.color1, self._rect)
            pygame.draw.rect(self._surf, self.BORDER_COLOR,
                             self._surf.get_rect(), self.PADDING)
            self.last_val = val

    def draw(self, surface, pos):
        surface.blit(self._surf, pos)


class TextUI:
    def __init__(self, init_val='Testing', color=(255, 255, 255), size=24):
        self._font = pygame.font.Font(None, size)
        self.color = color
        self._last_text = ''
        self.set_test(init_val)

    def draw(self, surface, pos):
        surface.blit(self._surf, pos)

    def set_test(self, text):
        if self._last_text != text:
            self._surf = self._font.render(text, False, self.color)
            self._last_text = text

    def top_left_to_center(self, top_left):
        rect = self._surf.get_rect()
        return (top_left[0] - rect.width/2,
                top_left[1] - rect.height/2)
