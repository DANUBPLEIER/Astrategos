import TileClass
import Structures
import Units

import pygame

pygame.init()
screen = pygame.display.Info()
WIDTH = screen.current_w
HEIGHT = screen.current_h

WIN = pygame.display.set_mode((WIDTH, HEIGHT))

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

    def render_tiles_in_camera(self, tiles):   #Render all the tiles that the camera can "see".
        counter = 0
        i = self.x // current_tile_length
        first_i = i
        while i <= (self.x + WIDTH) // current_tile_length and i < tiles_per_row:
            j = self.y // current_tile_length
            first_j = j
            while j <= (self.y + HEIGHT) // current_tile_length and j < rows:
                tiles[i][j].DrawImage(WIN, (current_tile_length, current_tile_length), self.x % current_tile_length, self.y % current_tile_length, first_i, first_j)
                j += 1
                counter += 1
            i += 1

        print(counter)

CurrentCamera = Camera((0,0), 1, 1.3, 0.6)

normal_tile_length = TileClass.base_texture_length * WIDTH // HEIGHT     #the length of a tile when the zoom is 1
current_tile_length = normal_tile_length * CurrentCamera.zoom

TileClass.resize_textures(current_tile_length)
Structures.resize_textures(current_tile_length)
Units.resize_textures(current_tile_length)

rows = 80
tiles_per_row = 80

tiles = []

for x in range(rows):       #Create the map with empty tiles
    newLine = []
    for y in range(tiles_per_row):
        newLine.append(TileClass.Tile((x, y), False, TileClass.empty_image_name, None, None, None))
    tiles.append(newLine)

#For testing purposes, 2 tiles have been modified.
tiles[2][2].structure = Structures.Core((2, 2), None)
tiles[3][3].unit = Units.Marine((3, 3), None)

FPS = 60

clock = pygame.time.Clock()

Running = True

WIN.fill((0,0,0))

while Running:
    clock.tick(FPS)
    #print(clock.get_fps())
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Running = False
        if event.type == pygame.MOUSEBUTTONDOWN:    #Check if mouse was scrolled
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

            TileClass.resize_textures(current_tile_length)
            Structures.resize_textures(current_tile_length)
            Units.resize_textures(current_tile_length)

            CurrentCamera.Check_Camera_Boundaries()
            CurrentCamera.Calculate_After_Zoom_Position(last_map_size_x, map_size_x, last_map_size_y, map_size_y)

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
    WIN.fill((0,0,0))
    CurrentCamera.render_tiles_in_camera(tiles)
      
    pygame.display.update()

#END
pygame.quit()