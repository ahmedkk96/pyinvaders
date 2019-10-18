import pygame
from pygame.math import Vector2


class Sprite(pygame.sprite.Sprite):
    def __init__(self, img):
        # pygame.sprite.Sprite.__init__(self)
        super(Sprite, self).__init__()
        self.pos = Vector2(0, 0)
        self.image = img

    def draw(self, targ_surface, source_rect=None):
        if source_rect is None:
            size_x, size_y = self.image.get_size()
        else:
            size_x = source_rect.width
            size_y = source_rect.height
            
        # Converting topleft to center
        tx1 = self.pos[0] - size_x/2
        ty1 = self.pos[1] - size_y/2
        tx2 = tx1 + size_x
        ty2 = ty1 + size_y

        trect = pygame.rect.Rect(tx1, ty1, tx2, ty2)
        targ_surface.blit(self.image, trect, source_rect)


class ASprite(Sprite):
    def __init__(self, img, steps_count=1):
        # pygame.sprite.Sprite.__init__(self)
        super(ASprite, self).__init__(img)
        self._framw_width = self.image.get_width() / steps_count
        self._frame_height = self.image.get_height()
        self.frame = 0
        self._internal_frame = 0.0  # For animation
        self.frames_count = steps_count
        self.animate = False
        self.animation_fps = 0

    def draw(self, target_surface):
        x1 = self.frame * self._framw_width
        x2 = self._framw_width  # Area rectangle
        source = pygame.rect.Rect(x1, 0, x2, self._frame_height)
        Sprite.draw(self, target_surface, source)

    def update(self, delta_time):
        if self.animate:
            self._internal_frame += delta_time * (self.animation_fps / 1000)
            # Rounding will make us lose frames over time

            while self._internal_frame >= self.frames_count:
                self._internal_frame -= self.frames_count

            self.frame = int(self._internal_frame)  # Floor
