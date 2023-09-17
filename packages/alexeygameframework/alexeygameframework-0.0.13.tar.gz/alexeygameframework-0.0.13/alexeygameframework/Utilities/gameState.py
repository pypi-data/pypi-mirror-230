#this file will have the game state manager and the screens that can be inherited from
import pygame
import sys


class Screen:
    def __init__(self, window):
        self.window = window
        
    def logic_checks(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
        
    def draw(self):
        self.window.fill((255,0,0))
        pygame.display.flip()
    
    def quit(self) -> None:
        """quits the game and closes the window"""
        self.running = False
        pygame.quit()
        sys.exit()
    
    
    
    
class ScreenManager:
    """this is the default implementation of the screen manager which will allow to swap between screens"""
    def __init__(self, window):
        self.window = window
        self.current_screen = "game"
        self.screen = {
            "game": GameScreen(self.window)
        }
        
    def draw(self):
        self.screen[self.current_screen].draw()
        
    def logic_checks(self):
        self.screen[self.current_screen].logic_checks()




class GameScreen(Screen):
    """this is a default implementation of a game screen that uses tiles as the map"""
    def __init__(self,window):
        super().__init__(window)
        
    def draw(self):
        self.window.fill((255,255,255))
        pygame.display.flip()
    
    def logic_checks(self):
        super().logic_checks()
        
        
class Game:
    """this is a default implementation of a game, to use this import Game then call the run function"""
    def __init__(self) -> None:
        pygame.init()
        self.screen_size = (800,600)
        self.window = pygame.display.set_mode((self.screen_size[0],self.screen_size[1]))
        self.running = True
        self.clock = pygame.time.Clock()
        
    def run(self) -> None:
        """initial call to get the game to run"""
        while self.running:
            self.logic_checks()
            self.draw()
            self.clock.tick(60)
            
    def draw(self) -> None:
        """draws everything to the screen"""
        self.window.fill((255,255,255))
        pygame.display.flip()
        
    def logic_checks(self) -> None:
        """runs all the logic for the game"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
        
    