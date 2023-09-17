import pygame

class UI:
    @staticmethod
    def init(screen):
        UI.center = (screen.get_size()[0] // 2, screen.get_size()[1]//2)
        UI.font = pygame.font.Font(None,32)
        UI.default_color = pygame.Color('lightskyblue3')