import pygame

class Rectangle:
    def __init__(self,
                 x,
                 y,
                 width,
                 height,
                 window, 
                 color: pygame.Color = pygame.Color(255,255,255))-> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.__rect = pygame.Rect(x,y,width,height)
        self.window = window

    def set_color(self,color:pygame.Color):
        self.color = color
    
    def draw(self)-> None:
        """a filled rectangle"""
        pygame.draw.rect(self.window,self.color,(self.x,self.y,self.width,self.height))
    
    def draw_box(self)-> None:
        """an outline of a rectangle"""
        pygame.draw.rect(self.window,self.color,(self.x,self.y,self.width,self.height),2)

    def collidepoint(self,locations: tuple) -> bool:
        """checks if the coords passed are colliding with this box"""
        self.__rect = pygame.Rect(self.x,self.y,self.width,self.height)
        return (self.__rect.collidepoint(locations))   
