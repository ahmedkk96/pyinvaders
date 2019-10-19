import pygame
from pygame.math import Vector2


class Sprite(pygame.sprite.Sprite):
    def __init__(self, img):
        super(Sprite, self).__init__()
        self.pos = Vector2(0, 0)
        self.image = img

    def draw(self, targ_surface):
        # Converting topleft to center
        size_x, size_y = self.image.get_size()

        tx1 = self.pos[0] - size_x/2
        ty1 = self.pos[1] - size_y/2
        tx2 = tx1 + size_x
        ty2 = ty1 + size_y

        trect = pygame.rect.Rect(tx1, ty1, tx2, ty2)
        targ_surface.blit(self.image, trect)


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

    def draw(self, target_surface):
        self.image = self._imgs[self.frame]
        Sprite.draw(self, target_surface)

    def update(self, delta_time):
        if self.animate:
            self._internal_frame += delta_time * (self.animation_fps)
            # Rounding will make us lose frames over time

            while self._internal_frame >= self.frames_count:
                self._internal_frame -= self.frames_count

            self.frame = int(self._internal_frame)  # Floor


class GameObject:
    def __init__(self):
        self.pos = pygame.math.Vector2(0, 0)
        self.size = pygame.math.Vector2(0, 0)
        self.sprite = None

        self.speed = pygame.math.Vector2(0, 0)

    def draw(self, surface):
        self.sprite.pos = self.pos
        self.sprite.draw(surface)

    def update(self, delta_time):
        self.sprite.update(delta_time)

        # Movement
        self.pos += self.speed * delta_time

    def set_size_from_sprite(self):
        self.size = self.sprite.image.get_size()