import pygame
import os

default_path = 'Assets/Units/'
texture_names = []
textures = []
base_textures = []

for img in os.listdir(default_path):    #Load all images
    texture_names.append(img)
    image = pygame.image.load(default_path + img)
    textures.append(image)
    base_textures.append(image)

def resize_textures(size):
    #resize the original textures based on the zoom level. If we were to do this with 
    #only a vector for textures, you would resize small textures and it would look bad.
    for i in range(len(texture_names)):
        newTexture = pygame.transform.scale(base_textures[i], (size, size))
        textures[i] = newTexture  

last_index = len(texture_names)

predefined_Units = {   #HP, MaxHp, attack, defence, Range, fog_range, Price
    "Marine" : [5, 5, 2, 3, 1, (1,1), (6,0)],
    "Phantom" : [5, 5, 2, 3, 1, (1,1), (10,0)],
    }

class Unit():
    def __init__(self, name, position, owner):
        self.position = position    #The position of the tile it's sitted.
        self.owner = owner          #The owner of the unit.
        self.name = name            #The unit

        vec = predefined_Units[name]

        self.texture = name + ".png"
        self.HP = vec[0]
        self.MaxHP = vec[1]
        self.attack = vec[2]
        self.defence = vec[3]
        self.Range = vec[4]
        self.fog_range = vec[5]      #How much can the unit see

        self.price = vec[6]

    def DrawImage(self, screen, size, colorTable, special_blit = False):
        image = textures[texture_names.index(self.texture)].copy()
        for i in range(image.get_width()):
            for j in range(image.get_height()):
                if image.get_at((i,j)) == (1,1,1):
                    image.set_at((i,j), colorTable[self.owner])
        if special_blit == False:
            screen.blit(image, (self.position[0] * size[0], self.position[1]  * size[1]))
        else:
            image = pygame.transform.scale(image, size)
            screen.blit(image, (self.position[0] * size[0], self.position[1]  * size[1]))