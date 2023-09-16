import sys
from Utilities.UIElements import Button
from Utilities.utils import load_image
import pygame

from Utilities.gameInfo import UI
from Utilities.gameState import ScreenManager, Game

import alexeygameframework 



class MyGame(Game):
    def __init__(self):
        super().__init__()
        UI.init(self.screen)
        
        self.objects = [
            Button(self.screen,50,50,"test"),
        ]
        
        self.screen_manager = ScreenManager(self.screen)
        
        
    def run(self) -> None:
        """initial call to get the game to run"""
        while self.running:
            self.screen_manager.draw()
            self.screen_manager.logic_checks()
            self.clock.tick(60)
                
        
        



MyGame().run()