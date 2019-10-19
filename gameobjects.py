import pygame
from pygame.math import Vector2


def Rect_From_Center(pos, size):
        tx1 = pos[0] - size[0]/2
        ty1 = pos[1] - size[1]/2
        return pygame.rect.Rect(tx1, ty1, size[0], size[1])


class Sprite(pygame.sprite.Sprite):
    def __init__(self, img):
        super(Sprite, self).__init__()
        self.image = img

    def draw(self, targ_surface, pos):
        # Converting topleft to center
        rect = Rect_From_Center(pos, self.image.get_size())
        targ_surface.blit(self.image, rect)

    def update(self, delta_time):
        pass


class ASprite(Sprite):
    def __init__(self, img, steps_count=1):
        self.frame = 0
        self._internal_frame = 0.0  # For animation
        self.frames_count = steps_count
        self.animate = False
        self.animation_fps = 0
        self._sub_images(img, steps_count)
        super(ASprite, self).__init__(self._imgs[0])

    def _sub_images(self, img, steps_count):
        # Divides the sheet into sub frames
        self._framw_width = img.get_width() / steps_count
        self._frame_height = img.get_height()
        self._imgs = []

        for i in range(0, steps_count):
            sub_surface = pygame.surface.Surface((self._framw_width,
                                                 self._frame_height))
            x1 = i * self._framw_width
            x2 = self._framw_width  # Area rectangle
            source = pygame.rect.Rect(x1, 0, x2, self._frame_height)

            sub_surface.blit(img, (0, 0), source)
            self._imgs.append(sub_surface)

    def draw(self, target_surface, pos):
        self.image = self._imgs[self.frame]
        Sprite.draw(self, target_surface, pos)

    def update(self, delta_time):
        if self.animate:
            self._internal_frame += delta_time * (self.animation_fps)
            # Rounding will make us lose frames over time

            while self._internal_frame >= self.frames_count:
                self._internal_frame -= self.frames_count

            self.frame = int(self._internal_frame)  # Floor


class GameObject:
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
    def __init__(self,
                 sprite,
                 pos=Vector2(0, 0),
                 size=Vector2(32, 32)):
        GameObject.__init__(self, pos, size)
        self.sprite = sprite
        self.size = sprite.image.get_size()

    def draw(self, target_surf):
        self.sprite.draw(target_surf, self.pos)

    def update(self, delta_time):
        GameObject.update(self, delta_time)
        self.sprite.update(delta_time)
