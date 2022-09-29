import pygame
import os

pygame.init()
screen = pygame.display.Info()
WIDTH = screen.current_w
HEIGHT = screen.current_h

#load all textures.
default_path = 'Assets/Tiles/'
texture_names = []
textures = []
base_textures = []

base_mitrhil_extraction = 4 #Amount of ore(base) per turn

mitrhil_extraction_dict = {
    "no_mine" : -75,
    "level_1" : -25,
    "level_2" : 0,
    "level_3" : 150
}

base_flerovium_extraction = 2 #Amount of ore(base) per turn

mitrhil_flerovium_dict = {
    "no_mine" : -100,
    "level_1" : -100,
    "level_2" : -50,
    "level_3" : 0
}

for img in os.listdir(default_path):
    texture_names.append(img)
    textures.append(pygame.image.load(default_path + img))
    base_textures.append(pygame.image.load(default_path + img))

def resize_textures(size):
    #resize the original textures based on the zoom level. If we were to do this with 
    #only a vector for textures, you would resize small textures and it would look bad.
    for i in range(len(texture_names)):
        newTexture = pygame.transform.scale(base_textures[i], (size, size))
        textures[i] = newTexture

images = len(textures)

empty_image_name = "Basic1.png"

class Tile:
    def __init__(self, position, collidable, image_name, special, unit, structure):
        self.position = position            #a tuple for the position
        self.collidable = collidable        #check if a unit can be placed there (ex. a wall or water)
        self.image_name = image_name
        self.special = special              #if the tile has a special ability (ex. Mithril, Flerovium, Forest that hides your troops from enemy sight etc.)
        self.unit = unit                    #store what unit is occupying this tile
        self.structure = structure          #store what structure is placed on this tile

    def DrawImage(self, screen, size, offset_x, offset_y, pos_x, pos_y):
        screen.blit(textures[texture_names.index(self.image_name)], ((self.position[0] - pos_x) * size[0] - offset_x, (self.position[1] - pos_y) * size[1] - offset_y), (0, 0, size[0], size[1]))
        if self.structure != None:
            self.structure.DrawImage(screen, size, offset_x, offset_y, pos_x, pos_y)
        if self.unit != None:
            self.unit.DrawImage(screen, size, offset_x, offset_y, pos_x, pos_y)