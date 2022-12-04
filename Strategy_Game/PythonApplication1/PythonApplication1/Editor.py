import TileClass
import Structures
import Units
import GUI
import math
import os
import pickle
import numpy

import pygame

pygame.init()
screen = pygame.display.Info()
WIDTH = screen.current_w
HEIGHT = screen.current_h

WIN = pygame.display.set_mode((WIDTH, HEIGHT))

GUI.Initialize_Editor_GUIs()
GUI.Draw_Textures_GUI((0,0))

class Camera:
    def __init__(self, position, zoom, max_zoom, min_zoom):
        self.x = position[0]
        self.y = position[1]
        self.zoom = zoom
        self.max_zoom = max_zoom
        self.min_zoom = min_zoom
        
        self.camera_movement = 15

        #make sure the zoom is insde [min_zoom, max_zoom]
        if min_zoom > zoom:
            self.zoom = self.min_zoom

        if zoom > max_zoom:
            self.zoom = self.max_zoom

    def Update_Camera_Zoom_Level(self):     #Make sure the camera zoom is within [min_zoom, max_zoom]
        if self.min_zoom > self.zoom:
            self.zoom = self.min_zoom

        if self.zoom > self.max_zoom:
            self.zoom = self.max_zoom

    def Check_Camera_Boundaries(self):     #Check if camera is within the boundaries of the map. If not, bring it there
        if self.x - self.camera_movement < - WIDTH // 2:
            self.x  = 0 - WIDTH // 2
        if self.y - self.camera_movement < - HEIGHT // 2:
            self.y = 0 - HEIGHT // 2
        if self.x + self.camera_movement + WIDTH // 2 > tiles_per_row * current_tile_length:
            self.x = tiles_per_row * current_tile_length - WIDTH // 2
        if self.y + self.camera_movement + HEIGHT // 2 > rows * current_tile_length:
            self.y = rows * current_tile_length - HEIGHT // 2

    def Calculate_After_Zoom_Position(self, last_map_size_x, map_size_x, last_map_size_y, map_size_y):  #Make the camera stay in the middle when zooming in/out
        self.x = int((self.x + WIDTH // 2) / last_map_size_x * map_size_x) - WIDTH // 2
        self.y = int((self.y + HEIGHT // 2) / last_map_size_y * map_size_y) - HEIGHT // 2

CurrentCamera = Camera((0,0), 1, 3, 0.4)

normal_tile_length = int(TileClass.base_texture_length * (WIDTH / HEIGHT))     #the length of a tile when the zoom is 1
current_tile_length = normal_tile_length * CurrentCamera.zoom

TileClass.resize_textures(current_tile_length)
Structures.resize_textures(current_tile_length)
Units.resize_textures(current_tile_length)

rows = 100
tiles_per_row = 100

tiles = []

#The base surface of the map. Zooming in/out will use this surface.
mapSurfaceNormal = pygame.Surface((int(tiles_per_row * normal_tile_length), int(rows * normal_tile_length)))

for x in range(rows):  #Create the map with empty tiles
    newLine = []
    for y in range(tiles_per_row):
        newTile = TileClass.Tile((y, x), False, None, TileClass.empty_image_name, None, None, None)
        newLine.append(newTile)
        newTile.DrawImage(mapSurfaceNormal, (normal_tile_length, normal_tile_length))
    tiles.append(newLine)
    del newTile

#For testing purposes, 2 tiles have been modified. Each modification has to be updated.
tiles[1][2].structure = Structures.Structure("Core", (2, 1), None)
tiles[1][2].DrawImage(mapSurfaceNormal, (normal_tile_length, normal_tile_length))

tiles[3][3].unit = Units.Unit("Marine", (3, 3), None)
tiles[3][3].DrawImage(mapSurfaceNormal, (normal_tile_length, normal_tile_length))

mapSurface = pygame.transform.scale(mapSurfaceNormal, (int(tiles_per_row * current_tile_length), int(rows * current_tile_length)))

ToolsSelectedPositions = []

#Editor specific variables:
Brush_size = 1
Brush_min = 1
Brush_max = 35

GUI.Draw_Tools_GUI(None, Brush_size)

Collision = False
Eraser = False
Fill = False
FillAll = False
FillSame = False

Editor_var_dict = {
    "ZCollision" : Collision,
    "Eraser" : Eraser,
    "Fill" : Fill,
    "FillAll" : FillAll,
    "FillSame" : FillSame
}

def image_modifier(x,y):
    if GUI.current_texture_screen == "Tiles":
        tiles[y][x].image_name = TileClass.avalible_textures[current_index]
    elif GUI.current_texture_screen == "Structures":
        struct = Structures.Structure(Structures.texture_names[current_index][:-4], (x,y), None)
        tiles[y][x].structure = struct
    elif GUI.current_texture_screen == "Units":
        unit = Units.Unit(Units.texture_names[current_index][:-4], (x,y), None)
        tiles[y][x].structure = unit

    if Editor_var_dict["Eraser"] == True:
        tiles[y][x].structure = None
        tiles[y][x].special = None
        tiles[y][x].unit = None
    tiles[y][x].collidable = Editor_var_dict["ZCollision"]
    tiles[y][x].DrawImage(mapSurfaceNormal, (normal_tile_length, normal_tile_length))

def place_tile(target_img = None):     #Function to determine what to place and how
    if Editor_var_dict["Fill"] == True:
        mouse_pos = pygame.mouse.get_pos()

        x_layer = (mouse_pos[0] + CurrentCamera.x) // current_tile_length 
        y_layer = (mouse_pos[1] + CurrentCamera.y) // current_tile_length

        visited_vec = []
        queued_tiles = [(x_layer, y_layer)]

        directions = [
            (-1,0),
            (1,0),
            (0,1),
            (0,-1)
        ]

        checks = 0
        tries = 0

        isDone = False

        while not isDone:

            new_tiles = []

            for myTile in queued_tiles:

                tries += 1

                x = myTile[0]
                y = myTile[1]

                if (x, y) not in visited_vec:
                    if x >= 0 and y >= 0 and x < rows and y < tiles_per_row and tiles[y][x].image_name[:-4] == target_img:
                        checks += 1
                        visited_vec.append((x, y))
                        image_modifier(x, y)

                        for direction in directions:
                            in_x = direction[0]
                            in_y = direction[1]
                            if (x + in_x, y + in_y) not in visited_vec:
                                new_tiles.append((x + in_x, y + in_y))

            queued_tiles.clear()

            if len(new_tiles) == 0: isDone = True

            queued_tiles += new_tiles

        visited_vec.clear()
        queued_tiles.clear()

    elif Editor_var_dict["FillAll"] == True:
        for x in range(rows):
            for y in range(tiles_per_row):
                image_modifier(x,y)

    elif Editor_var_dict["FillSame"] == True:
        for x in range(rows):
            for y in range(tiles_per_row):
                if tiles[y][x].image_name[:-4] == target_img:
                    image_modifier(x,y)

    else:
        mouse_pos = pygame.mouse.get_pos()

        x_layer = (mouse_pos[0] + CurrentCamera.x) // current_tile_length 
        y_layer = (mouse_pos[1] + CurrentCamera.y) // current_tile_length

        x = x_layer
        y = y_layer

        if Brush_size == 1:
            if x_layer >= 0 and x_layer < tiles_per_row:
                if y_layer >= 0 and y_layer < rows:
                    image_modifier(x,y)

        else:
            for Y in range(y - math.ceil(Brush_size / 2), y + math.ceil(Brush_size / 2) + 1):
                for X in range(x - math.ceil(Brush_size / 2), x + math.ceil(Brush_size / 2) + 1):
                    if X >= 0 and X < tiles_per_row:
                        if Y >= 0 and Y < rows:
                            image_modifier(X,Y)

                     
current_index = 0
max_index = TileClass.last_index

FPS = 60

clock = pygame.time.Clock()

Running = True

hasLeftClickPressed = False    #Determine if left mouse is pressed down.

WIN.fill((0,0,0))

def clearMap():
    print("1")

while Running:
    clock.tick(FPS)
    #print(clock.get_fps())
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Running = False
        if event.type == pygame.KEYDOWN:
            if event.unicode.lower() == 'p':    #Enable/Disable simple textures
                TileClass.simple_textures_enabled = not TileClass.simple_textures_enabled

                for x in range(rows):  #Redraw the whole map
                    for y in range(tiles_per_row):
                        tiles[x][y].DrawImage(mapSurfaceNormal, (normal_tile_length, normal_tile_length))
                    #tiles.append(newLine)

                mapSurface = pygame.transform.scale(mapSurfaceNormal, (int(tiles_per_row * current_tile_length), int(rows * current_tile_length)))

            elif event.unicode.lower() == 'l':  #Enable/Disable GUIs
                GUI.GUIs_enabled = not GUI.GUIs_enabled

            if event.unicode.lower() == 'q':    #Something simple to save the map. WILL CHANGE
                pygame.image.save(mapSurfaceNormal, "Maps/images/test.jpg")
                used_textures = []
                with open("Maps/info/test.txt", "wb") as outfile:   #Saves the map into the file.
                    for x in range(rows):
                        for y in range(tiles_per_row):
                            rawUnitData = {}
                            rawStructureData = {}
                            if tiles[x][y].structure != None:
                                rawStructureData = {
                                    "Position" : tiles[x][y].structure.position,
                                    "Owner" : tiles[x][y].structure.owner,
                                    "Name" : tiles[x][y].structure.name,
                                    }

                            if tiles[x][y].unit != None:
                                rawUnitData = {
                                    "Position" : tiles[x][y].unit.position,
                                    "Owner" : tiles[x][y].unit.owner,
                                    "Name" : tiles[x][y].unit.name,
                                    }

                            rawTileData = {
                                "Position" : tiles[x][y].position,
                                "Collidable" : tiles[x][y].collidable,
                                "Image_name" : tiles[x][y].image_name,
                                "Unit" : rawUnitData,
                                "Structure" : rawStructureData,
                                }

                            pickle.dump(rawTileData, outfile)
                            used_textures.append(tiles[x][y].image_name)
                    pickle.dump(used_textures, outfile)
                outfile.close()

            if event.unicode.lower() == 'w':    #Load maps. WILL CHANGE
                with open("Maps/info/test.txt", "rb") as infile:
                    tiles.clear()
                    for x in range(rows):
                        new_vec = []
                        for y in range(tiles_per_row):        
                            loaded_object = pickle.load(infile)
                            new_unit, new_structure = None, None
                            if loaded_object["Unit"]:  
                                new_unit = Units.Unit(loaded_object["Unit"]["Name"],
                                                      loaded_object["Unit"]["Position"],
                                                      loaded_object["Unit"]["Owner"]
                                                        )

                            if loaded_object["Structure"]:
                                new_structure = Structures.Structure(loaded_object["Structure"]["Name"],
                                                      loaded_object["Structure"]["Position"],
                                                      loaded_object["Structure"]["Owner"]
                                                        )

                            new_tile = TileClass.Tile(loaded_object["Position"],
                                                      loaded_object["Collidable"],
                                                      None,     #Image Class
                                                      loaded_object["Image_name"],
                                                      None,     #Special
                                                      new_unit,
                                                      new_structure
                                                        )

                            new_vec.append(new_tile)
                        tiles.append(new_vec)

                    for x in range(rows):  #Redraw the whole map
                        for y in range(tiles_per_row):
                            tiles[x][y].DrawImage(mapSurfaceNormal, (normal_tile_length, normal_tile_length))
                        #tiles.append(newLine)

                    mapSurface = pygame.transform.scale(mapSurfaceNormal, (int(tiles_per_row * current_tile_length), int(rows * current_tile_length)))


        if event.type == pygame.MOUSEBUTTONDOWN:    #Check if mouse was scrolled or pressed
            if event.button == 1:   #Left-click. Editor specific
                mouse_pos = pygame.mouse.get_pos()
                hasLeftClickPressed = True
                if GUI.GUIs_enabled == True and mouse_pos[0] >= WIDTH - GUI.Texture_x_size:  
                    #Check if the mouse is inside the TextureGUI
                    #and check which texture is selected.

                    x_layer = (mouse_pos[0] - (WIDTH - GUI.Texture_x_size)) // (GUI.texture_size + GUI.texture_distance)
                    y_layer = mouse_pos[1] // (GUI.texture_size + GUI.texture_distance)
                    
                    index_to_use = None
                    if GUI.current_texture_screen == "Tiles":
                        index_to_use = TileClass.last_index
                    elif GUI.current_texture_screen == "Structures":
                        index_to_use = Structures.last_index
                    elif GUI.current_texture_screen == "Units":
                        index_to_use = Units.last_index

                    if (mouse_pos[0] - (WIDTH - GUI.Texture_x_size)) % (GUI.texture_size + GUI.texture_distance) < GUI.texture_distance:
                        break
                    elif mouse_pos[1] % (GUI.texture_size + GUI.texture_distance) < GUI.texture_distance:
                        break
                    else:
                        index = GUI.max_x_pos * y_layer + x_layer
                        if GUI.max_x_pos * y_layer > 0: index += y_layer
                        if index < index_to_use:
                            current_index = index
                            GUI.Draw_Textures_GUI((x_layer, y_layer))

                elif GUI.GUIs_enabled == True and mouse_pos[0] >= WIDTH - GUI.Texture_x_size - GUI.Tool_x_size:
                    #Check if the mouse is inside the ToolsGUI
                    #and check which texture is selected.
                    x_layer = (mouse_pos[0] - (WIDTH - GUI.Texture_x_size - GUI.Tool_x_size)) // (GUI.texture_size + GUI.texture_distance)
                    y_layer = mouse_pos[1] // (GUI.texture_size + GUI.texture_distance)

                    if (mouse_pos[0] - (WIDTH - GUI.Texture_x_size - GUI.Tool_x_size)) % (GUI.Tools_icon_size + GUI.Tools_icon_distance) < GUI.Tools_icon_distance:
                        break
                    elif mouse_pos[1] % (GUI.Tools_icon_size + GUI.Tools_icon_distance) < GUI.Tools_icon_distance:
                        break
                    else:
                        index = GUI.max_x_pos * y_layer + x_layer
                        if GUI.max_x_pos * y_layer > 0: index += y_layer
                        if index < GUI.last_icons_index:
                            name = GUI.icon_names[index][:-4]

                            if ToolsSelectedPositions.count((x_layer, y_layer)) > 0:
                                ToolsSelectedPositions.remove((x_layer, y_layer))
                                Editor_var_dict[name] = False
                            else:
                                ToolsSelectedPositions.append((x_layer, y_layer))
                                Editor_var_dict[name] = True

                            def find_img(image):    #Find and image to deselect
                                new_x = 0
                                new_y = 0
                                newIndex = GUI.Tools_max_x_pos * new_y + new_x
                                while newIndex < GUI.last_icons_index:
                                    if GUI.icon_names[newIndex][:-4] == image and ToolsSelectedPositions.count((new_x, new_y)) > 0:
                                        ToolsSelectedPositions.remove((new_x, new_y))
                                        break
                                    if new_x >= GUI.Tools_max_x_pos:
                                        new_x = 0
                                        new_y += 1
                                    else:
                                        new_x += 1
                                    newIndex = GUI.max_x_pos * new_y + new_x
                                    if GUI.Tools_max_x_pos * new_y > 0: newIndex += new_y

                            if name == "Fill":
                                Editor_var_dict["FillAll"] = False
                                Editor_var_dict["FillSame"] = False
                                find_img("FillAll")
                                find_img("FillSame")
                            elif name == "FillAll":
                                Editor_var_dict["Fill"] = False
                                Editor_var_dict["FillSame"] = False
                                find_img("Fill")
                                find_img("FillSame")
                            elif name == "FillSame":
                                Editor_var_dict["Fill"] = False
                                Editor_var_dict["FillAll"] = False
                                find_img("Fill")
                                find_img("FillAll")

                        else:
                            #Check if plus/minus sign for the brush is pressed.
                            minus_index = GUI.max_x_pos * GUI.minus_brush[1] + GUI.minus_brush[0]
                            if GUI.max_x_pos * GUI.minus_brush[1] > 0: minus_index += GUI.minus_brush[1]
                            plus_index = GUI.max_x_pos * GUI.plus_brush[1] + GUI.plus_brush[0]
                            if GUI.max_x_pos * GUI.plus_brush[1] > 0: plus_index += GUI.plus_brush[1]

                            if index == minus_index:
                                if Brush_size - 1 < Brush_min:
                                    Brush_size = Brush_min
                                else: Brush_size -= 1;

                            elif index == plus_index:
                                if Brush_size + 1 > Brush_max:
                                    Brush_size = Brush_max
                                else: Brush_size += 1;
                                
                        GUI.Draw_Tools_GUI(ToolsSelectedPositions, Brush_size)

                else:  #Mouse is on the map, so check which tile is selected
                    x_layer = (mouse_pos[0] + CurrentCamera.x) // current_tile_length 
                    y_layer = (mouse_pos[1] + CurrentCamera.y) // current_tile_length

                    if x_layer >= 0 and x_layer < tiles_per_row:
                        if y_layer >= 0 and y_layer < rows:
                            place_tile(tiles[y_layer][x_layer].image_name[:-4])
                            mapSurface = pygame.transform.scale(mapSurfaceNormal, (int(tiles_per_row * current_tile_length), int(rows * current_tile_length)))

            modifier = 0
            if event.button == 4:
                modifier = 1
            elif event.button == 5:
                modifier = -1
            else: continue
               
            last_map_size_x = current_tile_length * tiles_per_row
            last_map_size_y = current_tile_length * rows

            #Update the zoom and tile length
            CurrentCamera.zoom += 0.1 * modifier
            CurrentCamera.Update_Camera_Zoom_Level()
            current_tile_length = int(normal_tile_length * CurrentCamera.zoom)

            map_size_x = current_tile_length * tiles_per_row
            map_size_y = current_tile_length * rows

            CurrentCamera.Check_Camera_Boundaries()
            CurrentCamera.Calculate_After_Zoom_Position(last_map_size_x, map_size_x, last_map_size_y, map_size_y)
            #TODO: Make a way to zoom in/out with minimal lag. This method is very bad but for now it works... kinda.
            #Apparently it works well with low texture sizes.
            try:
                mapSurface = pygame.transform.scale(mapSurfaceNormal, (int(tiles_per_row * current_tile_length), int(rows * current_tile_length)))
            except:     #if that failed, the surface is too big.
                print("Can't zoom in further")

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:   #Left-click. Editor specific
                hasLeftClickPressed = False

        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            if not (GUI.GUIs_enabled == True and mouse_pos[0] >= WIDTH - GUI.Texture_x_size) and not (mouse_pos[0] >= WIDTH - GUI.Texture_x_size - GUI.Tool_x_size): 
                if hasLeftClickPressed == True:
                    x_layer = (mouse_pos[0] + CurrentCamera.x) // current_tile_length 
                    y_layer = (mouse_pos[1] + CurrentCamera.y) // current_tile_length

                    if x_layer >= 0 and x_layer < tiles_per_row:
                        if y_layer >= 0 and y_layer < rows:
                            place_tile(tiles[y_layer][x_layer].image_name[:-4])
                            mapSurface = pygame.transform.scale(mapSurfaceNormal, (int(tiles_per_row * current_tile_length), int(rows * current_tile_length)))

    #Check if user wants to change the camera's position
    x_pos = pygame.mouse.get_pos()[0]
    y_pos = pygame.mouse.get_pos()[1]

    if x_pos == 0:
        CurrentCamera.x -= CurrentCamera.camera_movement
    if y_pos == 0:
        CurrentCamera.y -= CurrentCamera.camera_movement
    if x_pos == WIDTH - 1:
        CurrentCamera.x += CurrentCamera.camera_movement
    if y_pos == HEIGHT - 1:
        CurrentCamera.y += CurrentCamera.camera_movement

    CurrentCamera.Check_Camera_Boundaries()

    #Render everything
    tempSurface = pygame.Surface((WIDTH, HEIGHT))
    tempSurface.blit(mapSurface, (0, 0), (CurrentCamera.x, CurrentCamera.y, WIDTH, HEIGHT))

    WIN.blit(tempSurface, (0, 0))
    if GUI.GUIs_enabled == True: 
        WIN.blit(GUI.TextureSurface, (WIDTH - GUI.Texture_x_size, 0))
        WIN.blit(GUI.ToolsSurface, (WIDTH - GUI.Texture_x_size - GUI.Tool_x_size, 0))
    pygame.display.update()

#END
pygame.quit()