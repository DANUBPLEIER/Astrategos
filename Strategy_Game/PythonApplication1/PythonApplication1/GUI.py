import pygame
import TileClass
import os

font = pygame.font.Font('freesansbold.ttf', 1024)

pygame.init()
screen = pygame.display.Info()
WIDTH = screen.current_w
HEIGHT = screen.current_h

GUIs_enabled = True

Tools_icon_size = 64

default_path = 'Assets/EditorToolIcons/'
icons = []
icon_names = []
brush_icons = []
brush_names = []

for img in os.listdir('Assets/EditorToolBrushIcons/'):
    image = pygame.image.load('Assets/EditorToolBrushIcons/' + img)
    image = pygame.transform.scale(image, (Tools_icon_size, Tools_icon_size))
    brush_icons.append(image)
    brush_names.append(img)

for img in os.listdir(default_path):    #Load all icons
    icons.append(pygame.image.load(default_path + img))
    icon_names.append(img)

for i in range(len(icons)):
    newTexture = pygame.transform.scale(icons[i], (Tools_icon_size, Tools_icon_size))
    icons[i] = newTexture

last_icons_index = len(icons)

texture_size = 64
texture_distance = 10
max_x_pos = 2
max_y_pos = TileClass.last_index // max_x_pos

Tools_icon_distance = 10
Tools_max_x_pos = 2
Tools_max_y_pos = last_icons_index // Tools_max_x_pos

Texture_x_size = (texture_size + texture_distance) * (max_x_pos + 1) + texture_distance
Tool_x_size = (Tools_icon_size + Tools_icon_distance) * (Tools_max_x_pos + 1) + Tools_icon_distance
print(Texture_x_size)

#Surfaces for Editor GUI
TextureSurface = pygame.Surface((Texture_x_size, texture_size * 2 * max_y_pos * texture_distance), pygame.SRCALPHA)
ToolsSurface = pygame.Surface((Tool_x_size, HEIGHT), pygame.SRCALPHA)

def Initialize_Editor_GUIs():
    TextureSurface.convert_alpha()
    ToolsSurface.convert_alpha()
            
def Draw_Textures_GUI(position):
    TextureSurface.fill((0, 0, 0, 150))

    current_x = 0
    current_y = 0

    for image_name in TileClass.avalible_textures:
        cloned_image = pygame.transform.scale(TileClass.base_textures[TileClass.texture_names.index(image_name)], (texture_size, texture_size))
        if position != None:
            pygame.draw.rect(TextureSurface, (255, 255, 0), (position[0] * (texture_size + texture_distance) + texture_distance - 5, position[1] * (texture_size + texture_distance) + texture_distance - 5, texture_size + 10, texture_size + 10), 5)
        TextureSurface.blit(cloned_image, (current_x * (texture_size + texture_distance) + texture_distance, current_y * (texture_size + texture_distance) + texture_distance))
        if current_x >= max_x_pos:
            current_x = 0
            current_y += 1
        else:
            current_x += 1

def Draw_Tools_GUI(positions, brush_size):
    #Draw Tools
    ToolsSurface.fill((0, 0, 0, 150))

    current_x = 0
    current_y = 0

    for i in range(len(icons)):
        if positions != None:
            for position in positions:
               pygame.draw.rect(ToolsSurface, (255, 255, 0), (position[0] * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance - 5, position[1] * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance - 5, texture_size + 10, texture_size + 10), 5)
        
        ToolsSurface.blit(icons[i], (current_x * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance, current_y * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance))
        if current_x >= max_x_pos:
            current_x = 0
            current_y += 1
        else:
            current_x += 1

    #Draw Brush Tools
    current_y += 2
    current_x = 0

    ToolsSurface.blit(brush_icons[0], (current_x * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance, current_y * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance))
    
    current_x += 1 
    if brush_size != None:
        text = font.render(str(brush_size), True, (188,188,188))
        text = pygame.transform.smoothscale(text, (Tools_icon_size, Tools_icon_size))
        print(brush_size)
        textRect = text.get_rect()
        textRect.x = current_x * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance
        textRect.y = current_y * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance
        ToolsSurface.blit(text, textRect)

    current_x += 1
    ToolsSurface.blit(brush_icons[1], (current_x * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance, current_y * (Tools_icon_size + Tools_icon_distance) + Tools_icon_distance))