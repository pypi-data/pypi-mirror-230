import pygame
from objects import Rectangle
from entity import Entity, AnimatedEntity

NEIGHBOR_OFFSETS = [(-1,0), (-1,-1), (0,-1), (1,-1), (1,0), (0,0), (-1,1),(0,1),(1,1)]

class Tile:
    def __init__(self,screen: pygame.display, pos: tuple,tile_size: int = 16,entity: Entity or AnimatedEntity = None):
        self.entity = entity
        self.tile_size = tile_size
        self.pos = pos
        self.screen = screen
        
        if self.entity is None:
            self.rect = Rectangle(pos[0]*self.tile_size,pos[1]*self.tile_size,tile_size,tile_size,screen,pygame.Color(255,0,0,255))
        
    def draw(self,offset:tuple = (0,0)):
        if self.entity is None:
            self.rect = Rectangle((self.pos[0] + offset[0])*self.tile_size,(self.pos[1]+offset[1])*self.tile_size,self.tile_size,self.tile_size,self.screen,pygame.Color(255,0,0,255))
            self.rect.draw()
        
        else: 
            self.entity.draw()
        

class Tilemap:
    def __init__(self,screen: pygame.display, tile_size: int = 16):
        self.tile_size = tile_size
        self.tilemap ={}
        self.offgrid_tiles = {}
        self.screen = screen
        
    
    def tiles_around(self,pos: tuple) -> dict:
        tiles = {}
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        
        for offset in NEIGHBOR_OFFSETS:
            check_loc = str(int(tile_loc[0]) + int(offset[0])) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in self.tilemap:
                tiles[f"{check_loc[0]}:{check_loc[1]}"] = Tile(self.screen,(check_loc[0],check_loc[1]))
        return tiles
        
    
    
    def add_surrounding_tiles(self,pos: tuple) -> None:
        """addes tiles around a given point"""
        self.tilemap = {}
        for offset in NEIGHBOR_OFFSETS:
            get_loc = ((offset[0] + int(pos[0] // self.tile_size)), (offset[1] + int(pos[1] // self.tile_size)))
            self.tilemap[f"{get_loc[0]},{get_loc[1]}"] = Tile(self.screen,get_loc,self.tile_size)
       
    
    
    def add_10x10_grid(self) -> None:
        self.tilemap = {}
        for i in range(10):
            for j in range(10):
                get_loc = ((i), (j))
                self.tilemap[f"{get_loc[0]},{get_loc[1]}"] = Tile(self.screen,get_loc,self.tile_size)
    
    def draw_grid(self,size:tuple) -> None:
        """call this to draw a grid"""
        for i in range(size[0]):
            for j in range(size[0]):
                get_loc = (i,j)
                self.tilemap[f"{get_loc[0]},{get_loc[1]}"] = Tile(self.screen,get_loc,self.tile_size)
    
    def fill_screen(self) -> None:
        size = [self.screen.get_width(),self.screen.get_height()]
        for i in range(int(size[0] / self.tile_size)+1):
            for j in range(int(size[1] / self.tile_size)+1):
                get_loc = (i,j)
                self.tilemap[f"{get_loc[0]},{get_loc[1]}"] = Tile(self.screen,get_loc,self.tile_size)
    
    def draw(self,offset:tuple = (0,0)):
        for _, value in self.tilemap.items():
            value.draw(offset=offset)
            
    
    
    def logic(self,pos:tuple) -> None:
        """"""
        pass
    