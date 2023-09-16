import pygame
import os
import time
import math


def load_image(path: str = "",colorkey: tuple = (0,0,0)) -> pygame.Surface:
    img = pygame.image.load(path)
    img.set_colorkey(colorkey)
    return img

def load_images(path: str = "", colorkey: tuple = (0,0,0)) -> list:
    images = []
    
    for img_name in os.listdir(path):
        images.append(load_image(path + img_name,colorkey))
    return images

class Animation:
    def __init__(self, images: list, img_dur: int = 5, loop:bool = True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0
        
    def update(self) -> None:
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True
    
    def img(self) -> pygame.Surface:
        return self.images[int(self.frame / self.img_duration)]
    
    
class FpsCounter:
    """This class is designed only to show the current FPS, it does not allow to limit the framerate of the game"""
    def __init__(self,window: pygame.display,font_size: int = 12,background_color: tuple = (0,0,0,0))-> None:
        pygame.font.init()
        
        self.cSec = 0
        self.cFrame = 0
        self.FPS= 0
        self.deltatime = 0
        self.font_fps = pygame.font.Font(None,font_size)
        self.color_fps = pygame.Color(0,255,0)
        self.area = window.get_rect()
        self.window = window
        self.tickrate = 100
    
    def count_fps(self)-> None:
        """run this inside the game loop"""
        if self.cSec == time.strftime("%S"):
            self.cFrame +=1
        else:
            self.FPS = self.cFrame
            self.cFrame = 0
            self.cSec = time.strftime("%S")
            if self.FPS > 0:
                self.deltatime = 1 / self.FPS
                
                
    def draw(self)-> None:
        """call this to draw the frame counter"""
        #background rectangle
        
        
        #text
        self.FPS_counter_surface = self.font_fps.render(str(math.floor(self.FPS))+"FPS",True,self.color_fps)
        self.window.blit(self.FPS_counter_surface,(self.area.width-self.FPS_counter_surface.get_width(),0))