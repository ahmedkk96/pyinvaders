import pygame
from pygame.math import Vector2
import random


class ResourcesLoader():
    GAME_SPRITES = {'explosion':    {'path': 'sprites/exp.png',
                                     'tx': 6, 'ty': 1},
                    'player':       {'path': 'sprites/player.png',
                                     'tx': 2, 'ty': 1},
                    'enemy':        {'path': 'sprites/enemyRed2.png',
                                     'tx': 1, 'ty': 1},
                    'bullet_1':     {'path': 'sprites/laserRed01.png',
                                     'tx': 1, 'ty': 1},
                    'bullet_2':     {'path': 'sprites/bullet_2.png',
                                     'tx': 1, 'ty': 1},
                    'e_bullet_1':   {'path': 'sprites/e_bullet_1.png',
                                     'tx': 1, 'ty': 1},
                    'pu_weapon':    {'path': 'sprites/pu_weapon.png',
                                     'tx': 1, 'ty': 1},
                    'pu_health':    {'path': 'sprites/pill_green.png',
                                     'tx': 1, 'ty': 1},
                    'pu_shield':    {'path': 'sprites/shield_bronze.png',
                                     'tx': 1, 'ty': 1},
                    'shield_1':     {'path': 'sprites/shield_1.png',
                                     'tx': 1, 'ty': 1},
                    'background':   {'path': 'sprites/background.png',
                                     'tx': 1, 'ty': 1}
                    }

    def __init__():
        ResourcesLoader.sprites = {}
        for name in ResourcesLoader.GAME_SPRITES.keys():
            sprite = ResourcesLoader.load_sprite(name)
            ResourcesLoader.sprites[name] = sprite

    def load_sprite(name):
        data = ResourcesLoader.GAME_SPRITES[name]
        return ResourcesLoader.sprite_from_path(
                data['path'], data['tx'], data['ty'])

    def sprite_from_path(filename, tx, ty):
        img = pygame.image.load(filename).convert_alpha()
        return Sprite(img, tx, ty)

    def background(name):
        data = ResourcesLoader.GAME_SPRITES[name]
        img = pygame.image.load(data['path']).convert_alpha()
        return Background(img)


class WorldHelper:
    '''
    Global static class that works as an interface
    between gameobject instances and world
    (world global variable)
    '''
    def init(append_object, remove_object):
        WorldHelper.append = append_object
        WorldHelper.remove = remove_object


def Rect_From_Center(pos, size):
        tx1 = pos[0] - size[0]/2
        ty1 = pos[1] - size[1]/2
        return pygame.rect.Rect(tx1, ty1, size[0], size[1])


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

    def draw(self, display, screen_rect, delta_time):
        # Fill size with background.
        # Always rendering more than one additional tile
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
        self.parents = []

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

    def world_add_object(self, object):
        WorldHelper.append(None, object)

    def world_add_child(self, child):
        WorldHelper.append(self, child)

    def world_remove_object(self, object):
        WorldHelper.remove(object)

    def remove_outside_screen(self):
        if not self.get_rect().colliderect(WorldHelper.screen_rect):
            self.world_remove_object(self)


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
        self.shoot = self._shoot_0
        self._shooting_modes = [self._shoot_0,
                                self._shoot_1,
                                self._shoot_2,
                                self._shoot_3]
        self._shooting_mode = 0
        self._shield = None

    def take_damage(self, damage):
        if self._shield is not None:
            if self._shield.take_damage(damage):
                self.world_remove_object(self._shield)
                self._shield = None
        else:
            return super(Player, self).take_damage(damage)

    def _shoot_0(self):
        self._create_bullet(0, 0, bullet_1)

    def _shoot_1(self):
        self._create_bullet(25, 0, bullet_1)
        self._create_bullet(-25, 0, bullet_1)

    def _shoot_2(self):
        self._create_bullet(0, -25, bullet_1)
        self._shoot_1()

    def _shoot_3(self):
        self._create_bullet(25, 0, bullet_2)
        self._create_bullet(-25, 0, bullet_2)

    def _create_bullet(self, offset_x, offset_y, type):
        b = type()
        b.set_pos(self._pos + Vector2(offset_x, offset_y))
        self.world_add_object(b)

    def _set_shoot_mode(self):
        self.shoot = self._shooting_modes[self._shooting_mode]

    def upgrade_shoot(self):
        if self._shooting_mode < len(self._shooting_modes) - 1:
            self._shooting_mode += 1
            self._set_shoot_mode()

    def remove_shoot_upgrades(self):
        self._shooting_mode = 0
        self._set_shoot_mode()

    def downgrade_shoot(self):
        if self._shooting_mode > 0:
            self._shooting_mode -= 1
            self._set_shoot_mode()

    def on_powerup(self, powerup):
        if powerup.PU_TYPE == 'weapon':
            self.upgrade_shoot()
        elif powerup.PU_TYPE == 'health':
            self.health = 100
        elif powerup.PU_TYPE == 'shield' and self._shield is None:
            self.create_shield(shield_1)

    def create_shield(self, shield):
        sh = shield()
        sh.set_player(self)
        self._shield = sh
        self.world_add_object(sh)


class bullet_1(SpriteGameObject):
    SPRITE_NAME = 'bullet_1'
    OBJECT_TYPE = 'bullet'
    DAMAGE = 25

    def __init__(self):
        super(bullet_1, self).__init__()
        self.speed.y = -1000

    def update(self, dt):
        super(bullet_1, self).update(dt)
        self.remove_outside_screen()


class bullet_2(bullet_1):
    SPRITE_NAME = 'bullet_2'
    OBJECT_TYPE = 'bullet'
    DAMAGE = 50

    def __init__(self):
        super(bullet_1, self).__init__()
        self.speed.y = -1000


class e_bullet_1(bullet_1):
    SPRITE_NAME = 'e_bullet_1'
    OBJECT_TYPE = 'enemy_bullet'
    DAMAGE = 25

    def __init__(self, *args, **kw):
        super(e_bullet_1, self).__init__(*args, **kw)
        self.speed.y = 300


class Enemy(HealthGameObject):
    SPRITE_NAME = 'enemy'
    OBJECT_TYPE = 'enemy'
    SCORE = 10
    HEALTH = 50

    def shoot(self):
        bullet = e_bullet_1()
        bullet.set_pos(self._pos)
        self.world_add_object(bullet)


class Explosion(SpriteGameObject):
    SPRITE_NAME = 'explosion'
    OBJECT_TYPE = 'explosion'

    def __init__(self):
        super(Explosion, self).__init__()
        self.sprite.fps = 15


class DropItem(SpriteGameObject):
    OBJECT_TYPE = 'dropitem'
    SPEED = 300

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
        self.enemies = []

    def on_remove_child(self, child):
        if len(self.enemies) == 1:
            WorldHelper.remove(self)
        self.enemies.remove(child)

    def update(self, delta_time):
        pass

    def _update_pos(self, diff):
        for e in self.enemies:
            e.move(diff)

    def get_rect(self):
        rect = self.enemies[0].get_rect()
        for e in self.enemies:
            rect.union_ip(e.get_rect())

        return rect

    def set_pos(self, new_pos):
        self._update_pos(new_pos-self._pos)


class enemy_group_rect(EnemyGroup):
    def create_enemies(self, width, height, type):
        pos = self._pos
        padding = 30
        for y in range(0, height):
            for x in range(0, width):
                e = type()
                rect = e.get_rect()
                p = Vector2(pos)
                p.x += rect.width*x + padding
                p.y += rect.width*y + padding
                e.set_pos(p)
                self.enemies.append(e)
                self.world_add_child(e)


class MovmentClassic(GameObject):
    OBJECT_TYPE = 'movement'
    SPEED_X = 300
    STEP_Y = 60
    PADDING_X = 30

    def __init__(self, child):
        super(MovmentClassic, self).__init__()
        self._child = child
        self.world_add_child(child)
        self._rect = child.get_rect()
        self._left = self._rect.left
        self._right = self._rect.right
        self.speed_x = MovmentClassic.SPEED_X
        self.step_y = MovmentClassic.STEP_Y
        self.dir = True
        self._residual = 0

    def update(self, delta_time):
        offset_x = delta_time * self.speed_x
        if not self.dir:
            offset_x *= -1
        offset_y = 0
        sc = WorldHelper.screen_rect

        if self._right + offset_x > sc.width:
            offset_x = sc.width - self._right
            offset_y = self.step_y
            self.dir = False

        if self._left + offset_x < 0:
            offset_x = -self._left
            offset_y = self.step_y
            self.dir = True

        self._right += offset_x
        self._left += offset_x

        self._child.move(Vector2(offset_x, offset_y))

    def on_remove_child(self, child):
        self._child = None
        self.world_remove_object(self)


class EnemyGroupShoot(GameObject):
    OBJECT_TYPE = 'random_shooter'

    def __init__(self, enemygroup):
        super(EnemyGroupShoot, self).__init__()
        self._child = enemygroup
        self.world_add_child(enemygroup)
        self.max_timeout = 1
        self.max_enemies_shooting = 4
        self._e_shoot_timeout = self.max_timeout

    def update(self, delta_time):
        self._e_shoot_timeout -= delta_time
        enemies = self._child.enemies
        if self._e_shoot_timeout <= 0:
            num_of_enemies = random.randint(0, self.max_enemies_shooting)
            enemies_count = len(enemies) - 1
            for i in range(0, num_of_enemies):
                enemy = enemies[random.randint(0, enemies_count)]
                enemy.shoot()
            self._e_shoot_timeout = self.max_timeout

    def on_remove_child(self, child):
        self._child = None
        self.world_remove_object(self)


class ProgressBar:
    WIDTH = 400
    HEIGHT = 20
    PADDING = 3
    BORDER_COLOR = (255, 255, 255)

    def __init__(self):
        self._surf = pygame.surface.Surface((self.WIDTH, self.HEIGHT))
        self._rect = self._surf.get_rect()
        self.set_value(1)

    def set_value(self, val):
        self._rect.right = self.WIDTH * val
        self._surf.fill((255, 0, 0, 0))
        pygame.draw.rect(self._surf, (0, 255, 0), self._rect)
        pygame.draw.rect(self._surf, self.BORDER_COLOR,
                         self._surf.get_rect(), self.PADDING)

    def draw(self, surface, pos):
        surface.blit(self._surf, pos)


class TextUI:
    def __init__(self, init_val='Testing', color=(255, 255, 255), size=24):
        self._font = pygame.font.Font(None, size)
        self.color = color
        self.set_test(init_val)

    def draw(self, surface, pos):
        surface.blit(self._surf, pos)

    def set_test(self, text):
        self._surf = self._font.render(text, False, self.color)
