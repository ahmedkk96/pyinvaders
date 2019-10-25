import pygame
from pygame.math import Vector2


class ResourcesLoader():
    GAME_SPRITES = {'explosion':    {'path': 'sprites/explosion.png',
                                     'tx': 8, 'ty': 8},
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
                    'powerup':      {'path': 'sprites/powerup.png',
                                     'tx': 1, 'ty': 1},
                    'shield_1':     {'path': 'sprites/shield_1.png',
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


class GameObject:
    OBJECT_TYPE = ''

    def __init__(self):
        self._pos = Vector2(0, 0)
        self._size = Vector2(1, 1)
        self.speed = Vector2(0, 0)
        self.world_add_object = None
        self.world_remove_object = None
        self.parent = None

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

    def world_add_child(self, child):
        self.world_add_object(self, child)

    def on_remove_child(self, child):
        pass


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
        self.world_add_child(b)

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
        # Should check the type of powerup
        # and initiate the right upgrade
        # but let's just go easy
        self.upgrade_shoot()

    def create_shield(self, shield):
        sh = shield()
        sh.set_player(self)
        self._shield = sh
        self.world_add_child(sh)


class bullet_1(SpriteGameObject):
    SPRITE_NAME = 'bullet_1'
    OBJECT_TYPE = 'bullet'
    DAMAGE = 25

    def __init__(self):
        super(bullet_1, self).__init__()
        self.speed.y = -1000


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
        self.world_add_child(bullet)


class Explosion(SpriteGameObject):
    SPRITE_NAME = 'explosion'
    OBJECT_TYPE = 'explosion'


class DropItem(SpriteGameObject):
    SPEED = 0

    def __init__(self, *args, **kwargs):
        super(DropItem, self).__init__(*args, **kwargs)
        self.speed = Vector2(0, self.SPEED)


class Powerup(DropItem):
    SPRITE_NAME = 'powerup'
    OBJECT_TYPE = 'powerup'
    SPEED = 300


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


class enemy_group_rect(GameObject):
    OBJECT_TYPE = 'enemy_group'

    def __init__(self):
        super(enemy_group_rect, self).__init__()
        self.enemies = []

    def create_enemies(self, width, height, pos, type):
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

    def on_remove_child(self, child):
        self.enemies.remove(child)
