import pygame


class Renderer():
    def __init__(self, font_size=26):
        self.font = pygame.font.Font(None, font_size)
        self._padding = font_size
        self.lines = []

    def clear(self):
        self.lines.clear()

    def add(self, text):
        self.lines.append(text)

    def render(self, surface):
        y = 0
        for text in self.lines:
            textsurf = self.font.render(
                    text, False, pygame.color.Color('white'))

            surface.blit(textsurf, (0, y))
            y += self._padding
