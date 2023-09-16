
#UIElements.py: This file will hold everything regarding UI elements, such as buttons, sliders, textboxes



from typing import Callable
from Utilities.objects import Rectangle
from Utilities.gameInfo import UI
import pygame


class Button:
    #things to add
    # - Text 
    # - place button based on the center of the button not top left corner
    # - add colors
    # - Buttons spam when clicked, should call something ONCE
    
    def __init__(self, window, x: int, y: int, text: str,func_onclick: Callable = None):
        self.window = window
        self.loc = [x,y]
        self.size = [75,25] #width,height
        self.text = text
        self.func_onclick = func_onclick
        
        self.textRender = UI.font.render(self.text,True,UI.default_color)
        self.size[0] = self.textRender.get_width() + 10
        self.size[1] = self.textRender.get_height() + 10
        
        self.rect = Rectangle(self.loc[0],self.loc[1],self.size[0],self.size[1],self.window)
        self.rect.set_color(UI.default_color)
    
    def check_collidepoint(self):
        pass
    
    def logic_checks(self):
        #get mouse pos
        mouse_pos = pygame.mouse.get_pos() #mouse pos
        
        #check if clicking object
        if self.rect.collidepoint(mouse_pos):
            #if pressing
            if(pygame.mouse.get_pressed()[0]):
                print("Pressed")
                
    def draw(self):
        #render text
        self.textRender = UI.font.render(self.text,True,UI.default_color)
        
        #draw box
        self.rect.draw_box()

        #draw the text
        self.window.blit(self.textRender,(self.loc[0]+5,self.loc[1]+5))
    

class TextBox:
    def __init__(self):
        pass

class SliderBar:
    #get this working
    def __init__(self,screen, pos: tuple, size: tuple, initial_value: float, min: int, max: int) -> None:
        self.screen = screen
        self.pos = pos
        self.size = size
        
        self.slider_left_pos = self.pos[0] - (size[0]//2)
        self.slider_right_pos = self.pos[0] + (size[0] // 2)
        self.slider_top_pos = self.pos[1] - (size[1] // 2)
        
        self.min = min
        self.max = max
        self.initial_val = (self.slider_right_pos - self.slider_left_pos) *initial_value # <- percentage
        
        self.container_rect = pygame.Rect(self.slider_left_pos, self.slider_top_pos, self.size[0], self.size[1])
        self.button_rect = pygame.Rect(self.slider_left_pos + self.initial_val - 5, self.slider_top_pos, 10, self.size[1])
    
    def draw(self):
        pygame.draw.rect(self.screen, "darkgray", self.container_rect)
        pygame.draw.rect(self.screen,"blue",self.button_rect)