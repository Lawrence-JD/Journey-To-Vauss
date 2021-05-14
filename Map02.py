import pygame
import math
import xml.etree.ElementTree as ET
import actor
import vector
from object import*


class Map:

    def __init__(self, map_file):
        """
        :param map_file: Takes a Flare stile map .txt file and loads it into Pygame and this function
        """
        self.map = open(map_file + ".txt", "r")
        self.mapFile = map_file
        self.tileData = []

        self.layerNumber = 0
        for line in self.map:
            line = line.strip()
            if "[layer]" in line:
                self.layerNumber += 1
        self.map.close()
        self.map = open(self.mapFile + ".txt", "r")
        self.mapWidthTile = 0
        self.mapHeightTile = 0
        self.tileWidth = 0
        self.tileHeight = 0
        self.mapWidthPixel = 0
        self.mapHeightPixel = 0
        self.Orientation = 0
        self.backgroundColor = 0
        self.tileSet = 0
        self.LastTile = []
        self.collision_tiles = [1164, 1165, 1166, 1167, 1168, 1169, 854, 855, 856, 857, 858, 859, 860, 1243, 1244, 1245,
                                1246, 1247, 1248, 1249, 1250, 1251, 1252, 1253, 1254, 1255, 1256, 1257, 1258, 881, 882,
                                 883, 884, 1047, 1048, 1049, 1050]

        self.volatile_tiles = [815]
        self.test_tiles = [883, 1236, 882, 1244, 1245, 1246, 1247, 1248, 1249, 1250, 1251, 1252]
        self.alpha_tiles = [882, 1237, 883, 1244, 1245, 1246, 1247, 1248, 1249, 1250, 1251, 1252]

        #######################################################################
        # [not done]
        # Someone figure out if this should be load_extended or not...
        # Note that the load extensions will have to be changed with assets are saved in a specific file folder.
        # self.alpha_sheet = pygame.image.load_extended("../GoodEvilRPG/good_bad_RPG_art/ProjectUtumno.png").convert()
        self.alpha_sheet10 = pygame.image.load("Assets/Tilesets/" + "ProjectUtumno.png").convert_alpha()
        #######################################################################

        self.anim_timer = 0
        self.timer = 0
        self.TileX = 0
        self.TileY = 0
        self.alphas = {}
        self.alpha_sheets = {}
        for i in range(0, 11):
            self.alpha_sheets[i] = pygame.image.load("Assets/Tilesets/" + "ProjectUtumno" + str(i * 10) + ".png").convert_alpha()

        #############################################
        # Jonathan L
        self.player = actor.Player()
        self.npcs = [actor.NPC()]
        self.enemies = []
        self.transitions = []
        self.player_spawns = []
        self.good_aggro_list = []
        self.bad_aggro_list = []
        self.generate_tiled_objects(self.mapFile + ".tmx")
        self.is_paused = 0

        #############################################

        self.create_tiledata()
        self.create_aggro_lists()
        self.create_attributes()
        self.CreateAlphaImages()

####################################################################################################################
# Jonathan L

    def generate_tiled_objects(self, xml_file):
        """docstring"""
        tree = ET.parse(xml_file)
        root = tree.getroot()

        for objectgroup in root.findall("objectgroup"):
            for object in objectgroup.findall("object"):
                filename = object.get("template")

                ####################################################################
                # Enemy spawn parsing
                if filename == "EnemySpawnPosition.tx":
                    template_data = ET.parse(filename)
                    template_root = template_data.getroot()

                    object_width = object.get("width")
                    object_height = object.get("height")
                    spawn_x = float(object.get("x"))
                    spawn_y = float(object.get("y"))
                    patrolling = 1
                    for i in range (0, len(template_root[0][0])):
                        for property in object[0]:

                            if property.get("name") == "Path":
                                path_id = property.get("value")

                                if path_id == "0":
                                    patrolling = 0
                                else:
                                    patrolling = 1
                                break

                    for i in range(0, len(template_root[0][0])):
                        alignment = None
                        direction = None
                        for property in object[0]:
                            attribute = property.get("name")

                            if attribute == "Alignment":
                                alignment = property.get("value")

                            elif attribute == "Direction":
                                direction = str_to_Vector2_list(property.get("value"))
                                direction = vector.Vector2(direction[0][0], direction[0][1])

                        if alignment is None:
                            alignment = "Neutral"
                        if direction is None:
                            direction = vector.Vector2(1, 0)

                        for property in object[0]:
                            type = ""

                            if property.get("name") == "Type":
                                type = property.get("value")

                    case = 0
                    if patrolling:
                        for pathgroup in root.findall("objectgroup"):
                            for path in pathgroup.findall("object"):

                                if path.get("id") == path_id:
                                    path_x = float(path.get("x"))
                                    path_y = float(path.get("y"))
                                    path_list = path[0].get("points")
                                    path_list = str_to_Vector2_list(path_list)

                                    if path_list[0] == path_list[-1]:
                                        case = 1
                                        path_list = path_list[:-1]

                        for point in path_list:
                            point[0] += path_x
                            point[1] += path_y

                    else:
                        path_list = [vector.Vector2(spawn_x, spawn_y)]

                    self.enemies.append(actor.Enemy((spawn_x, spawn_y), path_list, patrolling, direction, alignment, type))

                    if case:
                        self.enemies[-1].is_linear_patrol = 0
                # end enemy spawn parsing
                ####################################################################

                if object.get("name") == "Transition":
                    temp_transition = {"x": float(object.get("x")), "y": float(object.get("y")),
                                       "width": float(object.get("width")), "height" : float(object.get("height"))}
                    for properties in object:
                        for property in properties:
                            name = property.get("name")
                            value = property.get("value")

                            if name == "Player Spawn ID":
                                value = int(value)

                            temp_transition[name] = value

                    self.transitions.append(temp_transition)

                if object.get("name") == "Player Spawn":

                    self.player_spawns.append([float(object.get("x")), float(object.get("y")), float(object.get("id"))])

    def transition_check(self, player):

        for box in self.transitions:
            temp_rect = Cuboid((0, 0, 0),vector.Vector2(box["x"], box["y"]), (box["width"], box["height"]))

            if player.actor_collision(temp_rect):
                self.transition(box["Next Map"], box["Player Spawn ID"])

####################################################################################################################

    def transition(self, filename, spawn_id):

        self.map = open(filename + ".txt", "r")
        self.mapFile = filename
        self.tileData = []

        self.layerNumber = 0
        for line in self.map:
            line = line.strip()
            if "[layer]" in line:
                self.layerNumber += 1
        self.map.close()
        self.map = open(self.mapFile + ".txt", "r")
        self.mapWidthTile = 0
        self.mapHeightTile = 0
        self.tileWidth = 0
        self.tileHeight = 0
        self.mapWidthPixel = 0
        self.mapHeightPixel = 0
        self.Orientation = 0
        self.backgroundColor = 0
        self.tileSet = 0
        self.LastTile = []

        #######################################################################
        # [not done]
        # Someone figure out if this should be load_extended or not...
        # Note that the load extensions will have to be changed with assets are saved in a specific file folder.
        # self.alpha_sheet = pygame.image.load_extended("../GoodEvilRPG/good_bad_RPG_art/ProjectUtumno.png").convert()
        self.alpha_sheet10 = pygame.image.load("Assets/Tilesets/" + "ProjectUtumno.png").convert_alpha()
        #######################################################################

        self.anim_timer = 0
        self.timer = 0
        self.TileX = 0
        self.TileY = 0
        self.alphas = {}
        self.alpha_sheets = {}
        for i in range(0, 11):
            self.alpha_sheets[i] = pygame.image.load("Assets/Tilesets/" + "ProjectUtumno" + str(i * 10) + ".png")

        #############################################
        # Jonathan L
        self.enemies = []
        if filename == "Final":
            if self.player.g_player.boss_counter > self.player.b_player.boss_counter:
                if self.player.b_player.is_active:
                    self.player.swap_active()
                self.enemies.append(actor.Enemy([380, 350], [], 0, vector.Vector2(0, 1), "Evil", "Boss"))
            else:
                if self.player.g_player.is_active:
                    self.player.swap_active()
                self.enemies.append(actor.Enemy([380, 350], [], 0, vector.Vector2(0, 1), "Good", "Boss"))

        self.transitions = []
        self.player_spawns = []
        self.generate_tiled_objects(self.mapFile + ".tmx")
        self.is_paused = 0

        for spawn in self.player_spawns:

            if spawn_id == int(spawn[2]):
                self.player.current_pos = vector.Vector2(spawn[0], spawn[1])

        #############################################

        self.create_tiledata()
        self.create_attributes()
        self.CreateAlphaImages()

    def __str__(self):
            S = ""
            S += str(self.mapWidthTile)
            S += str(self.mapHeightTile)
            S += str(self.tileWidth)
            S += str(self.tileHeight)
            S += str(self.tileSet)
            S += ""
            return S

    def create_tiledata(self):
        """
        :return: Takes "self.map" and runs it through python code until it is a list, list, list
        """
        for line in self.map:
            if "[layer]" in line:
                break
        for i in range(0, self.layerNumber):
            newList = []
            for line in self.map:
                line = line.strip()
                if "[layer]" in line:
                    break
                if int(line.count(",")) >= self.mapWidthTile:
                    parts = line.split(",")
                    parts.pop(-1)
                    if len(parts) > 0 :
                        newList.append(parts)
            self.tileData.append(newList)

        self.map.close()
        self.map = open(self.mapFile + ".txt", "r")
        return self.tileData

    def create_attributes(self):
        """
        Strips the map data into lines then looks thought the lines for data to be stored in a dictionary.
        After its stored in a dictionary, the Values are restored in variables with more appropriate names
        that can be used in different places.
        :return: Creates variables that have data such as tile width & height, map width & height and the orientation of the sprites.
        """
        attributes = {}
        for line in self.map:
            line = line.strip()
            if "[layer]" in line:
                # Stops when the tileSet starts
                break
            elif "=" in line:
                name, value = line.split("=")
                attributes[name] = value
        self.mapWidthTile = int(attributes["width"])
        self.mapHeightTile = int(attributes["height"])
        self.tileWidth = int(attributes["tilewidth"])
        self.tileHeight = int(attributes["tileheight"])
        self.mapWidthPixel = self.tileWidth * self.mapWidthTile
        self.mapHeightPixel = self.tileHeight * self.mapHeightTile
        self.Orientation = attributes["orientation"]
        # self.backgroundColor = attributes["background_color"]
        tileset, a, b, c, d = attributes["tileset"].split(",")  # Pulls the tile sheets name/(file path) from tiledata.

        # ############################ - CORRECT CALL - #################################
        self.tileSet = pygame.image.load("Assets/Tilesets/" + "DungeonCrawl_ProjectUtumnoTileset.png").convert_alpha()
        #################################################################################

        self.map.close()
        self.map = open(self.mapFile + ".txt", "r")

    def create_aggro_lists(self):
        i = 0
        while i < len(self.enemies):

            if self.enemies[i].alignment == "Evil":
                self.good_aggro_list.append(self.enemies[i])

            elif self.enemies[i].alignment == "Good":
                self.bad_aggro_list.append(self.enemies[i])

            i += 1

    def remove_from_aggro_list(self, other):

        if other.alignment == "Evil":
            self.good_aggro_list.remove(other)

        else:
            self.bad_aggro_list.remove(other)

    def MapDraw(self, surf, camera):
        """
        :param surf: Takes a Pygame surface.
        :param camera: Takes the returned rect from the Camera class.
        :return: None
        """
        row_start = int(camera.cameraRect[1] / self.tileHeight)
        col_start = int(camera.cameraRect[0] / self.tileWidth)
        num_rows = int(surf.get_height() / self.tileHeight) + 2
        num_cols = int(surf.get_width() / self.tileWidth) + 2
        for layer_num, layer in enumerate(self.tileData):
            self.TileY = -int(camera.cameraRect[1] % self.tileHeight)
            for row_num in range(row_start, row_start + num_rows):
                self.TileX = -int(camera.cameraRect[0] % self.tileWidth)
                for col_num in range(col_start, col_start + num_cols):
                    try:
                        tile = int(self.tileData[layer_num][row_num][col_num])
                        self.LastTile = tile
                    except:
                        tile = self.LastTile
                    spriteSheetW = self.alpha_sheet10.get_width()
                    spriteSheetSW = int(spriteSheetW / self.tileWidth)
                    spritePosx = ((tile % spriteSheetSW) - 1) * self.tileWidth
                    spritePosy = (tile // spriteSheetSW) * self.tileHeight
                    # mapPosx = col_num * self.tileWidth
                    # mapPosy = row_num * self.tileHeight
                    # mapPos = camera.apply([mapPosx, mapPosy, self.tileWidth, self.tileHeight])
                    #######################################################################
                    # Need to clean up conditional blits [not done]
                    # Need to add a way to randomly select tiles of a certain tile code at a random time to blit another tile on top. This would be for
                    # the lava right now so that we can make fire pop up randomly. [not done]
                    #######################################################################
                    surf.blit(self.alpha_sheet10, (self.TileX, self.TileY), (spritePosx, spritePosy, self.tileWidth, self.tileHeight))    # Puts base layer down
                    if tile not in self.test_tiles:     # Asks if the current tile being blitted is in our list of tile codes to have animations
                        surf.blit(self.alpha_sheet10, (self.TileX, self.TileY), (spritePosx, spritePosy, self.tileWidth, self.tileHeight))
                    else:   # If its not then blit the tile at the animation counters current set.
                        if tile == 883:
                            surf.blit(self.alphas[str(882) + "-" + str(self.timer)], (self.TileX, self.TileY), (0, 0, self.tileWidth, self.tileHeight))
                        if tile == 1236:
                            surf.blit(self.alphas[str(1237) + "-" + str(self.timer)], (self.TileX, self.TileY), (0, 0, self.tileWidth, self.tileHeight))
                        if tile == 882:
                            surf.blit(self.alphas[str(883) + "-" + str(self.timer)], (self.TileX, self.TileY), (0, 0, self.tileWidth, self.tileHeight))
                        if tile == 1244:
                            surf.blit(self.alphas[str(1252) + "-" + str(self.timer)], (self.TileX, self.TileY), (0, 0, self.tileWidth, self.tileHeight))
                        if tile == 1245:
                            surf.blit(self.alphas[str(1251) + "-" + str(self.timer)], (self.TileX, self.TileY), (0, 0, self.tileWidth, self.tileHeight))
                        if tile == 1246:
                            surf.blit(self.alphas[str(1250) + "-" + str(self.timer)], (self.TileX, self.TileY), (0, 0, self.tileWidth, self.tileHeight))
                        if tile == 1247:
                            surf.blit(self.alphas[str(1249) + "-" + str(self.timer)], (self.TileX, self.TileY), (0, 0, self.tileWidth, self.tileHeight))
                        if tile == 1248:
                            surf.blit(self.alphas[str(1244) + "-" + str(self.timer)], (self.TileX, self.TileY), (0, 0, self.tileWidth, self.tileHeight))
                        if tile == 1249:
                            surf.blit(self.alphas[str(1245) + "-" + str(self.timer)], (self.TileX, self.TileY), (0, 0, self.tileWidth, self.tileHeight))
                        if tile == 1250:
                            surf.blit(self.alphas[str(1246) + "-" + str(self.timer)], (self.TileX, self.TileY), (0, 0, self.tileWidth, self.tileHeight))
                        if tile == 1251:
                            surf.blit(self.alphas[str(1247) + "-" + str(self.timer)], (self.TileX, self.TileY), (0, 0, self.tileWidth, self.tileHeight))
                        if tile == 1252:
                            surf.blit(self.alphas[str(1248) + "-" + str(self.timer)], (self.TileX, self.TileY), (0, 0, self.tileWidth, self.tileHeight))
                    self.TileX += self.tileWidth
                self.TileY += self.tileHeight

                ######################
                # Jonathan L
                for i in self.enemies:
                    i.draw(surf, camera)

                for n in self.npcs:
                    n.draw(surf, camera)

                self.player.draw(surf, camera)
                ######################

    def CreateAlphaImages(self):
        """
        The surface should be a tile sheet so that you can make a dictionary using it.
        :param surface: Takes a pygame surface
        :return: a dictionary of images
        """
        # L: When using this code its important to think in the terms of tiles not pixels for the most part.
        temp_list = []  # Used to store the tiles that need to be stored in our alpha dictionary
        width_in_tiles = self.alpha_sheet10.get_width() / self.tileWidth      # Tile sheets width in tiles
        height_in_tiles = self.alpha_sheet10.get_height() / self.tileHeight   # Tile sheets height in tiles
        k = 0   # used to save "k" used in the for loop
        for counter in range(len(self.alpha_tiles)):
            width = 0   # Resets width every time the counter goes up
            height = 0  # Resets height every time the counter goes up
            k = self.alpha_tiles[counter]   # k is the tile to be found. Use the print statement above this line to check tile.
            for i in range(int(width_in_tiles * height_in_tiles)):  # This is establishing the max range
                if i <= k:  # This keeps the loop in the range of the tile to be found so that there is no extra work done after its found.
                    if i % width_in_tiles == 0 and i != 0:  # This counts how many rows down we are and starts counting after 0
                        height += 1     # Adds one to height which is essentially the row number for the tile to be found on.
            # This takes our sprite sheet coord's and height and spits out how far on the X axis we need to blit at.
            width = ((k - (width_in_tiles * height)) * self.tileWidth) - self.tileWidth  # Forgot how or why this workds :)
            height *= self.tileHeight    # This just takes our height counter and multiplies it by tile height to get the blit Y position.
            temp_list.append((int(width), int(height), k))   # Stores the corresponding (x, y) values and their tile code in a list called temp_list.
        # ======================================================================================================================================================
        # This for loop creates all the image files of the individual alpha tiles and saves them in a dictionary with their corresponding tile codes
        # and a number 1-10 (to determine opacity level) as keys in the format "tile code-opacity number".
        for counter in range(0, 11):
            for i in range(len(temp_list)):
                #alpha_image = pygame.Surface((self.tileWidth, self.tileHeight), pygame.SRCALPHA)  # Makes an empty surf to blit images on.
                #alpha_image.blit(self.alpha_sheets[counter], (0, 0), (temp_list[i][0], temp_list[i][1], self.tileWidth, self.tileHeight))  # Blits images onto alpha_image
                #pygame.image.save(alpha_image, str(temp_list[i][2]) + "-" + str(counter) + ".png")  # Saves the image in this format "tile-code-alpha_percentage.png"
                alpha_image = pygame.image.load("Assets/AlphaImages/" + str(temp_list[i][2]) + "-" + str(counter) + ".png")  # populates self.alphas with alpha images in assets folder
                # Loads the image to the dictionary using the tile code of the respective image being saved as the dictionary key.
                self.alphas[str(temp_list[i][2]) + "-" + str(counter)] = alpha_image.convert_alpha()    # uses convert alpha to save the images native alpha

    def MapUpdate(self, theCamera, player, dt, game_won, mpos_vec):
        """
        ALL OF THIS IS IN TESTING FOR PRETTYMAP PROJECT ;)
        """
        #######################################################################
        # Gonna need to revamp this for more utility such as the lava fire tiles [not done]
        #######################################################################
        self.anim_timer += 0.1  # Increasing this increases the speed of an animation
        if self.anim_timer >= 40:   # There is no need to go over "p" because setting x to p makes the timer = 0
            self.anim_timer = 0
        p = 40  # This is the period (distance between one full cycle)
        a = 10  # This is the amplitude of our triangle graph (max height of the cycle)
        x = int(self.anim_timer)    # This moves our timer equation along.
        self.timer = int(abs((((2*a)/p) * (abs(x % p - (p/2))) - (p/4))))

        ########################################################################
        # Jonathan L
        if not self.is_paused:
            if self.player.g_player.is_active:
                self.player.update(self, theCamera, mpos_vec, self.good_aggro_list, dt)

            else:
                self.player.update(self, theCamera, mpos_vec, self.bad_aggro_list, dt)

            i = 0
            while i < len(self.enemies):
                aggro_list = []

                if self.enemies[i].alignment == "Good":
                    aggro_list += self.good_aggro_list

                    if self.player.b_player.is_active:
                        aggro_list.append(player)

                elif self.enemies[i].alignment == "Evil":
                    aggro_list += self.bad_aggro_list

                    if self.player.g_player.is_active:
                        aggro_list.append(player)

                self.enemies[i].update("forward", self, theCamera, aggro_list, dt)

                if self.enemies[i].is_dead():
                    self.remove_from_aggro_list(self.enemies[i])
                    self.enemies.__delitem__(i)

                i += 1

        self.transition_check(self.player)

        for n in self.npcs:
            n.update(mpos_vec, "None", self, [self.player], dt)

            if n.is_activated:
                self.is_paused = 1
                break

            else:
                self.is_paused = 0

        ########################################################################

    def tilecheck(self, Actor):
        ####################################################################################
        #                NEEDS TO CHECK ALL LAYERS OR A SPECIFIC LAYER  [not done]
        ####################################################################################
        """
        Note: Only gets called if actor is moving as of 2/25/2018 (first deliv.)
        :param sprite: Is a rect or an actor
        :return: returns the tile that the character is about to go onto
        """
        actor_position = Actor
        # Creates the column number by taking the actors x-coord in world-coord's and floor dividing by tile width
        column = int(actor_position[0] // self.tileWidth)
        row = int(actor_position[1] // self.tileWidth)      # This does a similar thing as column does
        current_tile = []                                   # Temp empty list to save the tile the player is currently standing on
        # This for-loop checks all of the tile-codes in the tile data and appends the one the actor is standing on to the temp list "current_tiles"
        for i in range(len(self.tileData)):
            current_tile.append(int(self.tileData[i][row][column]) - 1)  # Checking only where the actor is standing, -1 to compensate for "pretty map" tileset configuration

        for tile in current_tile:                   # This for-loop looks at the tiles-codes in our "current_tile" list
            for bad_tile in self.collision_tiles:   # This for-loop looks at the tile code its given and the tile-codes in the "collision_tiles" list
                if int(tile) == int(bad_tile):      # If the tile-codes match then True is returned for this method
                    return True

        return False


class Camera:
    """
    :Returns: A rect in a list that represents the cameras [x, y , sprite width, sprite height]
    """
    def __init__(self, map, width, height):
        """
        Takes map values, window width, and window height.
        """
        self.cameraRect = [0, 0, width, height]
        self.Width = map.mapWidthPixel
        self.Height = map.mapHeightPixel
        self.cameraWidth = width
        self.cameraHeight = height

    def update_camera_scale(self, xy):
        """
        Takes a list containing two numbers and updates the cameras size to match those numbers.
        :param xy: A list containing two numbers ex:[x,y]
        :return: N/A
        """
        self.cameraWidth = xy[0]
        self.cameraHeight = xy[1]

    def apply(self, object):
        """
        Used to convert "objects" coord's from world to screen.
        :param object: any entity to be drawn to the screen.
        :return: N/A
        """
        temp = object.copy()
        temp[0] -= self.cameraRect[0]
        temp[1] -= self.cameraRect[1]
        return temp

    def update(self, sprite):
        """
        Takes the parameter "sprite" (A rect) and uses the passed rect to move camera.
        """
        x = sprite[0] - int(self.cameraWidth // 2)
        y = sprite[1] - int(self.cameraHeight // 2)
        x = max(x, 0)
        y = max(y, 0)
        x = min((self.Width - self.cameraWidth), x)
        y = min((self.Height - self.cameraHeight), y)
        self.cameraRect = [x, y, self.Width, self.Height]

########################################################################################################################
# Jonathan L


def str_to_Vector2_list(string):
    temp_list = []
    temp_str_1 = ""
    temp_str_2 = ""
    build_1 = 1
    build_2 = 0

    for i in range(0, len(string)):

        if not string[i] == " " and not string[i] == ",":
            if build_1 and not string[i] == " ":
                temp_str_1 += string[i]
            elif build_2 and not string[i] == ",":
                temp_str_2 += string[i]

        elif string[i] == ",":
            build_1 = 0
            build_2 = 1

        if string[i] == " " or i == len(string) - 1:
            build_1 = 1
            build_2 = 0

            if temp_str_1[0] == "-":
                temp_str_1 = temp_str_1[1:]
                modifier_1 = -1
            else:
                modifier_1 = 1

            if temp_str_2[0] == "-":
                temp_str_2 = temp_str_2[1:]
                modifier_2 = -1
            else:
                modifier_2 = 1

            temp_list.append(vector.Vector2(float(temp_str_1) * modifier_1, float(temp_str_2) * modifier_2))
            temp_str_1 = ""
            temp_str_2 = ""

    return temp_list
    ########################################################################################################################

