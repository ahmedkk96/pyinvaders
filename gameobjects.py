import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, img, steps_count=1):
        # pygame.sprite.Sprite.__init__(self)
        super(Player, self).__init__()
        self.pos = (100, 50)
        self.surface = img
        self.step_px = self.surface.get_width() / steps_count
        self.height = self.surface.get_height()

    def draw(self, step, target):
        x1 = step * self.step_px
        x2 = x1 + self.step_px
        source = pygame.rect.Rect(x1, 0, x2, self.height)

        tx1 = self.pos[0] - self.step_px/2
        ty1 = self.pos[1] - self.height/2
        tx2 = tx1 + self.step_px
        ty2 = ty1 + self.height
        trect = pygame.rect.Rect(tx1, ty1, tx2, ty2)
        target.blit(self.surface, trect, source)