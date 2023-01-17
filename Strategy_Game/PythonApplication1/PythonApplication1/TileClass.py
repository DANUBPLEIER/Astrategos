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
avalible_textures = []

base_texture_length = 16

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

image_class_familly = {}

for img in os.listdir(default_path):
    if img[-4:] == '.png':
        if img[0:8] != "A-simple":
            avalible_textures.append(img)

        texture_names.append(img)
        textures.append(pygame.image.load(default_path + img))
        base_textures.append(pygame.image.load(default_path + img))
    else:
        new_names = []
        new_textures = []
        new_base_textures = []
        for sub_img in os.listdir(default_path + img + '/'):
            new_names.append(sub_img)
            myTexture = pygame.image.load(default_path + img + '/' + sub_img)
            new_textures.append(myTexture)
            new_base_textures.append(myTexture)

        image_class_familly[img] = [new_names, new_textures, new_base_textures]

def resize_textures(size):
    #resize the original textures based on the zoom level. If we were to do this with 
    #only a vector for textures, you would resize small textures and it would look bad.
    for i in range(len(texture_names)):
        newTexture = pygame.transform.scale(base_textures[i], (size, size))
        textures[i] = newTexture

empty_image_name = avalible_textures[0]

simple_textures_enabled = True

simple_textures_dict = {
    "Land" : "A-simple-land",
    "Wall" : "A-simple-wall",
    "Ore1" : "A-simple-ore1",
    "Ore2" : "A-simple-ore2"
    }

last_index = len(avalible_textures)

class Tile:
    def __init__(self, position, collidable, image_class, image_name, special, unit, structure):
        self.position = position            #a tuple for the position
        self.collidable = collidable        #check if a unit can be placed there (ex. a wall or water)
        self.image_class = image_class
        self.image_name = image_name        #the name of the image. Used by texture_names.
        self.special = special              #if the tile has a special ability (ex. Mithril, Flerovium, Forest that hides your troops from enemy sight etc.)
        self.unit = unit                    #store what unit is occupying this tile
        self.structure = structure          #store what structure is placed on this tile

    def DrawImage(self, screen, size):
        if simple_textures_enabled == True:
            screen.blit(textures[texture_names.index(self.image_name)], (self.position[0] * size[0], self.position[1]  * size[1]))
        else:
            key = ""
            if self.collidable == True:
                key = simple_textures_dict["Wall"]
            elif self.collidable == False:
                key = simple_textures_dict["Land"]
            screen.blit(textures[texture_names.index(key + ".png")], (self.position[0] * size[0], self.position[1]  * size[1]))
            
        if self.structure != None:
            self.structure.DrawImage(screen, size)
        if self.unit != None:
            self.unit.DrawImage(screen, size)