import pygame
from pygame.math import Vector2


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

    def create_gameobject(type):
        sprite = ResourcesLoader.sprites[type.SPRITE_NAME]
        return type(sprite)


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
    OBJECT_TYPE=''

    def __init__(self,
                 pos=Vector2(0, 0),
                 size=Vector2(32, 32)):
        self.pos = pos
        self.size = size
        self.speed = Vector2(0, 0)

    def update(self, delta_time):
        # Movement
        self.pos += self.speed * delta_time

    def get_rect(self):
        return Rect_From_Center(self.pos, self.size)

    def collides(self, other):
        return self.get_rect().colliderect(other.get_rect())


class SpriteGameObject(GameObject):
    '''
    Implementation with sprite
    which gets the size from it
    '''
    SPRITE_NAME = ''

    def __init__(self,
                 sprite,
                 pos=Vector2(0, 0),
                 size=Vector2(32, 32)):
        GameObject.__init__(self, pos, size)
        self.sprite = sprite
        self.size = sprite.image.get_size()
        self.frame = 0

    def draw(self, target_surf):
        self.sprite.draw(target_surf, self.pos, self.frame)


class Player(SpriteGameObject):
    SPRITE_NAME = 'player'
    OBJECT_TYPE = 'player'

    def __init__(self, sprite):
        super(Player, self).__init__(sprite)
        self.health = 100

    def update(self, delta_time):
        SpriteGameObject.update(self, delta_time)
        self.pos = Vector2(pygame.mouse.get_pos())

    def shoot(self):
        b = ResourcesLoader.create_gameobject(Bullet)
        b.pos = self.pos
        return b


class Bullet(SpriteGameObject):
    SPRITE_NAME = 'bullet'
    OBJECT_TYPE = 'bullet'

    def __init__(self, sprite):
        super(Bullet, self).__init__(sprite)
        self.speed.y = -1000


class Enemy(SpriteGameObject):
    SPRITE_NAME = 'enemy'
    OBJECT_TYPE = 'enemy'

    def __init__(self, sprite):
        super(Enemy, self).__init__(sprite, (512, 32))
        self.health = 100


class Explosion(SpriteGameObject):
    SPRITE_NAME = 'explosion'
    OBJECT_NAME = 'explosion'
