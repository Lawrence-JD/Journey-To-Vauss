# Actor class declarations
# For Journey to Vauss

import math
import pygame
import vector
import GUI
from object import *
from weapon import *

# normalized vector values representing cartesian facings
east = (1, 0)
n_east = (0.7071067811865476, -0.7071067811865476)
north = (0, -1)
n_west = (-0.7071067811865476, -0.7071067811865476)
west = (-1, 0)
s_west = (-0.7071067811865476, 0.7071067811865476)
south = (0, 1)
s_east = (0.7071067811865476, 0.7071067811865476)

e_n_east = (0.92387, -0.38268)
n_n_east = (0.38268, -0.92387)

e_s_east = (0.92387, 0.38268)
s_s_east = (0.38268, 0.92387)

n_n_west = (-0.38268, -0.92387)
w_n_west = (-0.92387, -0.38268)

s_s_west = (-0.38268, 0.92387)
w_s_west = (-0.92387, 0.38268)


########################################################################################################################
class Actor(object):
    """Parent Actor class containing attributes and methods needed by both Enemies and the Player, later NPCs"""

    def __init__(self):
        """
        Actor Constructor, should only be called by the super, takes no arguments, yet.
        """

        self.current_direction = vector.Vector2(1, 0)  # in rads, resets if it goes beyond -2pi or +2pi

        self.current_pos = vector.Vector2(64, 64)  # in pixels per second
        self.current_vel = vector.Vector2(0, 0)  # starts at rest
        self.acceleration = vector.Vector2(200, 0)  # based on the angle we are looking
        self.max_speed = vector.Vector2(100, 0)  # gotta go fast
        self.knock_vel = vector.Vector2(0, 0)  # for use when being knocked back
        self.move_buffer = vector.Vector2 (18, 0)  # pixel buffer to apply when doing collision detection, updated with the vectors
        self.strafe_buffer = vector.Vector2(0, 18)
        self.strafe_vel = vector.Vector2(0, 0)

        self.max_health = 100
        self.health = self.max_health  # default
        self.damage = 0
        self.is_attacking = 0  # boolean value for controlling attack animations, particularly "thrusting" ones
        self.is_swinging = 0  # another boolean value for controlling attack animations, particularly withdraw ones
        self.is_moving = 0  # boolean value for controlling movement and rest animations
        self.attack_anim_timer = 0.0  # timer used to smooth out attack animations
        self.move_anim_timer = 0.0  # timer used to smooth out movement animations
        self.attack_anim_counter = 0  # counter for controlling the "frame" of animation
        self.attack_cd_timer = 0  # cool down timer for attacks
        self.in_range = 0  # boolean used by enemy and npc to see if a target is in range to attack
        self.is_knocked_back = 0  # boolean value to determine the actor state of being knocked back
        self.knock_timer = 0  # timer for knockback animation
        self.actor_collide = 0
        self.is_patrolling = 1
        self.is_linear_patrol = 1
        self.alignment = "Neutral"

        self.sprite_size = 32  # dimension of the temporary sprites
        self.sprite_offset = (288, 128)  # offset of the temporary sprite within the temporary sheet
        self.sprite_sheet = pygame.image.load_extended("Assets/tile"
                                                       "s from rpgmaker/people4.png").convert_alpha()  # temporary sprite sheet
        self.sprite_column = 1  # column number of the default sprite within its relative grid
        self.sprite_row = 2  # row number of the default sprite within its relative grid

        self.hit_box = Cuboid((255, 0, 0), self.current_pos, vector.Vector2(16, 32))

        self.collision_tiles = [1200]

        self.patrol_path = []
        self.patrol_stage = 0
        self.patrol_stage_cap = 0
        self.patrol_modifier = 1
        self.destination = None

        self.Sword_Hit = pygame.mixer.Sound("Assets/Sounds/SwordHit.wav")
        self.current_weapon = Thrusting(self)

    def __getitem__(self, item):
        """
        overload of the [] operator, 0 returns x of current_pos and 1 returns the y
        :param item: index number
        :return: x or y value of current_pos
        """

        if item == 0:

            return self.current_pos[0]

        elif item == 1:

            return self.current_pos[1]

        elif item == 2:

            return self.hit_box[2]

        elif item == 3:

            return self.hit_box[3]

        else:
            raise ValueError("Index out of range: Actor get item")

    def __setitem__(self, key, value):
        """
        overloads the [] item to set a value to the give index where 0 is the x value and 1 is the y
        :param key: index to be changed
        :param value: new value to assign
        :return: nothing
        """

        if key == 0:

            self.current_pos[0] = value

        elif key == 1:

            self.current_pos[1] = value

        else:
            raise ValueError("Index out of range: Actor set item")

    def actor_collision(self, Rect):
        """
        Takes two pygame style rectangles and determines if they overlap
        :param Rect: Rectangle
        :return: True if they overlap, False otherwise
        """

        if collides(self.hit_box, Rect):
             return 1

        else:
            return 0

    def update(self, direction, map, actors, dt):
        """
        update function for the actor class, updates timers and actor states, and automatically moves the actor
        :param direction: string dictating which direction to move
        :param map: map object to run tile collision for the movement
        :param actors: list of actors for running actor collision for the move
        :param dt: change in time
        :return: nothing
        """

        self.attack_anim_timer += dt  # advance the attack animation timer

        self.move_anim_timer += dt  # advance the movement animation timer

        if self.attack_cd_timer > 0:  # checks to see if the weapon attack is still on cooldown, and lowers it if so
            self.attack_cd_timer -= dt

        else:  # resets the attack cooldown timer
            self.attack_cd_timer = 0

        if self.knock_timer > 0:  # checks to see if the actor is still being knocked back and reduces the timer

            self.knock_timer -= dt # updates timer

            self.knock_move(map, dt)  # uses appropriate movement function

        else:  # resets the timer and actor state

            self.knock_timer = 0
            self.is_knocked_back = 0

        if not self.is_knocked_back and isinstance(self, Enemy):  # checks if the actor can move properly
            self.move(direction, map, actors, dt)  # moves the actor, does movement collision for tiles and other actors

        if not self.is_moving:
            self.current_vel -= self.current_vel * dt # lowers velocity

        self.hit_box_update()  # updates hitbox to new location

    def update_sprite_facing(self):
        """
        Determines the direction the actor is looking and sets the appropriate sprite to active based on unit length
        direction vector and preset vector values (at the top of file)
        :return: nothing
        """
        # right
        if self.current_direction.x >= 0 and (self.current_direction.y > e_n_east[1] and self.current_direction.y < e_s_east[1]):
            self.sprite_row = 6

        # up
        elif (self.current_direction.x < n_n_east[0] and self.current_direction.x >= n_n_west[0]) and self.current_direction.y <= 0:
            self.sprite_row = 4

        # left
        elif self.current_direction.x <= 0 and (self.current_direction.y > w_n_west[1] and self.current_direction.y < w_s_west[1]):
            self.sprite_row = 2

        # down
        elif (self.current_direction.x < s_s_east[0] and self.current_direction.x >= s_s_west[0]) and self.current_direction.y >= 0:
            self.sprite_row = 0

        #up-right
        elif (self.current_direction.x < e_n_east[0] and self.current_direction.x >= n_n_east[0]) and self.current_direction.y < 0:
            self.sprite_row = 5

        #down-right
        elif (self.current_direction.y >= e_s_east[1] and self.current_direction.y < s_s_east[1]) and self.current_direction.x > 0:
            self.sprite_row = 7

        #up-left
        elif (self.current_direction.x < n_n_west[0] and self.current_direction.x >= w_n_west[0]) and self.current_direction.y < 0:

            self.sprite_row = 3

        #down-left
        elif (self.current_direction.y >= w_s_west[1] and self.current_direction.y < s_s_west[1]) and self.current_direction.x < 0:
            self.sprite_row = 1

    def draw(self, surf, camera):
        """
        draw function for actors, currently animates basic temporary sprites
        :param surf: pygame style Surface
        :param camera: camera object for world coordinate conversion
        :return: nothing
        """
        if self.is_dead(): # dead men tell no tales
            return

        temp_rect = camera.apply(self.current_pos)  # create temporary list to protect the current position
          # converts from world coord to screen coords

        temp_cube = Cuboid(vector.Vector3(0, 0, 0), self.current_weapon.Hitbox.mPos.copy(),
                           vector.Vector2(48, 4))

        temp_cube.mAngle = self.current_weapon.Hitbox.mAngle
        temp_vec = camera.apply(temp_cube.mPos)
        temp_cube.mPos = temp_vec

        if isinstance(self, Enemy) and self.is_chasing:

            if self.sprite_row == 4 or self.sprite_row == 1 or self.sprite_row == 2 or self.sprite_row == 3 or self.sprite_row == 0:
                x = temp_cube.mPos.x - self.current_weapon.rotated_weap_img.get_width() // 2
                y = temp_cube.mPos.y - self.current_weapon.rotated_weap_img.get_height() // 2

                surf.blit(self.current_weapon.rotated_weap_img, (x, y))

        # Drawing the actor from the sprite sheet using known attributes, and offsets the sprite so current_pos is the
        #... center of the sprite
        surf.blit(self.sprite_sheet, (temp_rect[0] - (self.sprite_size // 2),
                   temp_rect[1] - (self.sprite_size // 2)),
                  (self.sprite_column * self.sprite_size + self.sprite_offset[0],
                   self.sprite_row * self.sprite_size + self.sprite_offset[1],
                   self.sprite_size, self.sprite_size))

        if isinstance(self, Enemy) and self.is_chasing:
            if self.sprite_row == 5 or self.sprite_row == 6 or self.sprite_row == 7:
                x = temp_cube.mPos.x - self.current_weapon.rotated_weap_img.get_width()//2
                y = temp_cube.mPos.y - self.current_weapon.rotated_weap_img.get_height()//2
                surf.blit(self.current_weapon.rotated_weap_img, (x, y))

            pygame.draw.rect(surf, (0, 0, 0), (temp_rect[0] - 20, temp_rect[1] - 20, 40, 3), 0)
            pygame.draw.rect(surf, (255, 0, 0), (temp_rect[0] - 20, temp_rect[1] - 20, 40 * (self.health/self.max_health), 3), 0)

        elif isinstance(self, NPC) and self.gui_runner.Visible:
            self.gui_runner.Draw(surf)

    def move(self, direction, map, actors, delta_t):
        """
        default move function for actors, does tile/actor collision, in case of tile collision, rotates 180 degrees
        and keeps moving. also caps velocity based on maximum move speed.
        :param direction: string containing the desired direction, forwards or backwards
        :param map: map object to run tile collision
        :param actors: list of actors to run actor collision
        :param delta_t: change in time
        :return: nothing
        """

        # advance our position with vectors based on desired direction
        if direction == "forward":
            delta_pos = self.current_pos + self.current_vel * delta_t

        if direction == "backward":
            delta_pos = self.current_pos - self.current_vel * delta_t

        if direction == "None":
            return

        delta_vel = self.current_vel + self.acceleration * delta_t

        # runs actor collision check, sets actor state to reflect whether there was a collision
        for i in actors:
            if not self.actor_collision(i.hit_box):
                self.actor_collide = 0

            else:  # breaks out of the loop and stops movement
                self.is_moving = 0
                self.reset_velocity()
                self.actor_collide = 1
                break

        # checks if the actor didn't hit a bad tile or another actor, then moves the actor
        if not map.tilecheck(delta_pos + self.move_buffer) and not self.actor_collide:
            self.is_moving = 1  # updating player state
            self.current_pos = delta_pos
            self.current_vel = delta_vel

        # checks if the actor hit a bad tile, then rotates them to keep walking
        elif not self.actor_collide:
            self.current_direction = -self.current_direction
            self.update_vectors()

        # checks to see if the velocity has gone beyond the max speed of the actor and if so caps it.
        if self.current_vel.magnitude > self.max_speed.magnitude:
            self.current_vel = self.max_speed

    def knock_move(self, map, dt):
        """
        special move function for actors to be applied when a knock back effect is desired. moves the actor based
        on its knock velocity which is applied when hit by such an effect
        :param map: map object for tile collision check
        :param dt: change in time
        :return: nothing
        """

        delta_pos = self.current_pos + self.knock_vel * dt  # calculates how many pixels to move

        # runs tile collision check and moves if no collision occurs, accounts for sprite/tile overlap
        if not map.tilecheck(delta_pos + (16 * self.knock_vel.normalized)):
            self.is_moving = 1  # updating player state
            self.current_pos = delta_pos

        else:  # stops movement
            self.is_moving = 0

        # caps move speed
        if self.current_vel.magnitude > self.max_speed.magnitude:
            self.current_vel = self.max_speed

    def look_at_screen_point(self, point, camera):
        """
        sets the direction to look at the given point, only works if the point is in screen coords
        :param point: a set of coords depicting a position in screen coords
        :param camera: the camera for converting into screen coords
        :return: nothing
        """
        # converting to screen coords and protecting against list mutability
        temp_pos = camera.apply(self.current_pos)

        self.current_direction = (point - temp_pos).normalized

        self.update_vectors()  # updates acceleration, velocity, sprite facing, and max speed to all match the new direction

    def look_at_world_point(self, point, camera):
        """
        sets current direction to look at the player, where both the players position and self are in world coords
        :param point: position of the player in world coords, a vector2
        :param camera: camera object for world coordinate conversion
        :return: nothing
        """

        # converting to screen coords and protecting against list mutability
        temp_pos_1 = self.current_pos.copy()
        camera.apply(temp_pos_1)

        temp_pos_2 = point.copy()
        camera.apply(temp_pos_2)

        self.current_direction = (temp_pos_2 - temp_pos_1).normalized

        self.update_vectors()  # updates acceleration, velocity, sprite facing, and max speed to all match the new direction

    def look_at_nearest_actor(self, actor_list, camera):
        """
        sets current direction to look at the player, where both the players position and self are in world coords
        :param point: position of the player in world coords, a vector2
        :param camera: camera object for world coordinate conversion
        :return: nothing
        """

        closest_actor = None
        shortest_distance = 10000
        for actor in actor_list:
            # converting to screen coords and protecting against list mutability
            temp_pos_1 = self.current_pos.copy()
            camera.apply(temp_pos_1)

            temp_pos_2 = actor.current_pos.copy()
            camera.apply(temp_pos_2)

            test_distance = (temp_pos_2 - temp_pos_1).magnitude

            if test_distance < shortest_distance:
                shortest_distance = test_distance
                closest_actor = actor

        temp_pos_1 = self.current_pos.copy()
        camera.apply(temp_pos_1)

        temp_pos_2 = closest_actor.current_pos.copy()
        camera.apply(temp_pos_2)

        self.current_direction = (temp_pos_2 - temp_pos_1).normalized

        self.update_vectors()  # updates acceleration, velocity, sprite facing, and max speed to all match the new direction

    def is_dead(self):
        """
        checks to see if the actor has died
        :return: boolean based on the health level of the actor
        """
        if self.health <= 0:
            return 1
        else:
            return 0

    def knock_back(self):
        """
        sets the actor state to being knocked back, as well as starting the timer
        :return: nothing
        """
        self.is_knocked_back = 1
        self.knock_timer = 0.75

    def hit_box_update(self):
        """
        updates hitbox based on the current position
        :return: noting
        """
        self.hit_box.mPos = self.current_pos
        self.hit_box.mAngle = self.current_direction.radians

    def reset_velocity(self):
        """
        resets the velocity to 0 to stop movement
        :return: nothing
        """
        self.current_vel[0] = 0
        self.current_vel[1] = 0

    def update_vectors(self):
        """
        updates acceleration, velocity, strafe velocity, sprite pixel buffers, and max speed to all match the new
         direction, automatically updates sprite facing
        :return: nothing
        """
        self.acceleration = self.acceleration.magnitude * self.current_direction

        # prevents a drifting effect
        self.current_vel = self.current_vel.magnitude * self.current_direction

        self.strafe_buffer = self.strafe_buffer.magnitude * self.current_direction.perpendicular

        self.strafe_vel = self.current_vel.magnitude * self.current_direction.perpendicular

        self.move_buffer = self.move_buffer.magnitude * self.current_direction

        self.max_speed = self.max_speed.magnitude * self.current_direction

        self.update_sprite_facing()

    def patrol_stage_check(self):

        if len(self.patrol_path) > 1:
            if (self.patrol_path[self.patrol_stage] - self.current_pos).magnitude < 10:
                if self.is_linear_patrol:
                    if self.patrol_stage >= self.patrol_stage_cap:
                        self.patrol_modifier = -1
                    elif self.patrol_stage == 0:
                        self.patrol_modifier = 1

                    self.patrol_stage += 1 * self.patrol_modifier
                else:
                    if self.patrol_stage >= self.patrol_stage_cap:
                        self.patrol_stage = -1
                    self.patrol_stage += 1
        else:
            self.patrol_stage = 0


########################################################################################################################
class Player(Actor):
    """
    Class for handling the player, inherits from the Actor class. Needs more support for Good and Evil player
    """

    class Good(object):
        """
        Nested inside of player, holds its own stats, inventory, position, direction and so on. To Be Developed
        """
        def __init__(self):

            self.is_active = 1  # boolean to determine if this is the currently selected player

            # self.level = 0
            # self.inventory = {}  # to be replaced with inventory class
            # self.experience = 0
            # self.weapons = {}  # to be replaced with weapon class
            # self.armor = {}  # to be replaced with armor class
            # self.trinkets = {}  # to be replaced with trinket class
            self.sprite_sheet = pygame.image.load_extended("Assets/tiles from rpgmaker/barb_good_walk.png").convert_alpha()  # temporary sprite sheet
            self.sprite_offset = (0, 0)
            self.is_active = 1
            self.pos = vector.Vector2(880, 2450)  # players position in world coords
            self.direction = vector.Vector2(1, 0)  # radians value showing the direction the player is facing
            self.max_health = 100
            self.health = self.max_health
            self.boss_counter = 0

    class Evil(object):
        """
        Nested inside of player, holds its own stats, inventory, position, direction and so on. To Be Developed
        """
        def __init__(self):

            self.is_active = 0  # boolean to determine if this is the currently selected player

            # self.level = 0
            # self.inventory = {}  # to be replaced with inventory class
            # self.experience = 0
            # self.weapons = {}  # to be replaced with weapon class
            # self.armor = {}  # to be replaced with armor class
            # self.trinkets = {}  # to be replaced with trinket class
            self.sprite_sheet = pygame.image.load_extended("Assets/tiles from rpgmaker/spell_bad_walk.png").convert_alpha()  # temporary sprite sheet
            self.sprite_offset = (0, 0)
            self.is_active = 0
            self.pos = vector.Vector2(2650, 3060)  # players position in world coords
            self.direction = vector.Vector2(1, 0)  # radians value showing the direction the player is facing
            self.max_health = 100
            self.health = self.max_health
            self.boss_counter = 0

    def __init__(self):
        """
        Player constructor, takes no arguments as of yet
        """

        super().__init__()  # calling parents constructor

        self.g_player = self.Good()  # good player object
        self.b_player = self.Evil()  # bad player object
        self.current_pos = self.g_player.pos
        self.rotate_speed = 10  # speed at which the player rotates in pixels /s
        # self.sprite_size = 32  # dimension of the players temporary sprites
        self.sprite_sheet = self.g_player.sprite_sheet
        self.sprite_offset = self.g_player.sprite_offset  # offset of the players temporary sprite within the temporary sheet
        # self.sprite_sheet = pygame.image.load_extended("good_bad_RPG_art/tiles from rpgmaker/people4.png")  # players temporary sprite sheet
        self.sprite_column = 1  # column number of the default sprite within the grid of the players sprite
        self.sprite_row = 2  # row number of the default sprite within the grid of the players sprite
        self.reach = 75  # reach of players weapon
        self.damage = 15
        self.max_speed = vector.Vector2(125, 0)
        self.Cur_Background_Music = pygame.mixer.Sound("Assets/Sounds/GoodPeopleTravelingMusic.wav")
        self.Bad_Theme = pygame.mixer.Sound("Assets/Sounds/EvilTravelingMusic.wav")
        self.Good_Theme = self.Cur_Background_Music
        self.Cur_Background_Music.set_volume(0.5)
        self.curr_map = "Good Hub"

        self.current_weapon = Weapon(self)
        self.current_weapon.current_weapon = "Spear"

    def update(self, map, camera, mpos, aggro_list, dt):
        """
        updates player timers and resets player states if needed, also moves the player in case of a knock back
        according to the players knock velocity, also updates direction based on mouse postion
        :param map: map object for running tile collision when knocked back
        :param camera: camera object for use when updating direction
        :param mpos: mouse position used when updating direction
        :param dt: change in time, keep it smooth folks
        :return: nothing
        """

        self.look_at_screen_point(mpos, camera)  # updates to look at the mouse

        self.current_weapon.Update(self, dt, camera)

        self.attack_anim_timer += dt  # advance the attack animation timer

        self.move_anim_timer += dt  # advance the movement animation timer

        if self.move_anim_timer > 0.1 and self.is_moving:
            self.sprite_column += 1  # advancing the sprite to the next animation frame

            if self.sprite_column > 2:  # wrapping the sprite back around to the start of the walk animation if it
                                        #...  goes out of range.
                self.sprite_column = 0

            self.move_anim_timer = 0  # resetting the animation timer

        elif not self.is_moving:  # checking if the idle animations need to be played (currently just a still sprite)
            self.sprite_column = 1

        if self.attack_cd_timer > 0:  # checks to see if the weapon attack is still on cooldown, and lowers it if so
            self.attack_cd_timer -= dt

        else:  # resets the attack cooldown timer
            self.attack_cd_timer = 0

        if self.knock_timer > 0:  # checks to see if the actor is still being knocked back and reduces the timer

            self.knock_timer -= dt

            self.knock_move(map, dt)

        else:  # resets the timer and actor state

            self.knock_timer = 0
            self.is_knocked_back = 0

        if self.current_weapon.is_swinging:
            self.attack(aggro_list)

        if not self.is_moving:  # prevents conservation of momentum after stopping
            self.reset_velocity()

        if self.health < self.max_health:
            self.health += 1 * dt

        if self.health > self.max_health:
            self.health = self.max_health

        self.hit_box_update()

    def move(self, direction, map, delta_t):
        """
        overloaded move function for the player, overloaded to handle user inputs and to not rotate on tile collision,
         moves only forwards or backwards, and knocks back when colliding with an actor (will be updated to protect
         against npc collision
        :param direction: the direction string used to determine forward or backward movement
        :param map: map object used to check tile collision
        :param actors: actor object used to check actor collision
        :param delta_t: change in time of the program
        :return: nothing
        """

        # processing movement based on direction, generating hypothetical new position (delta_pos)
        #... for collision detection, and generation a buffer vector for sprite offset
        if direction == "forward":
            delta_pos = self.current_pos + self.current_vel * delta_t
            buffer = self.move_buffer
        elif direction == "backward":
            delta_pos = self.current_pos - self.current_vel * delta_t
            buffer = -self.move_buffer
        elif direction == "right":
            delta_pos = self.current_pos - self.strafe_vel * delta_t
            buffer = -self.strafe_buffer
            buffer[0] = self.strafe_buffer[0]
        elif direction == "left":
            delta_pos = self.current_pos + self.strafe_vel * delta_t
            buffer = -self.strafe_buffer
            buffer[1] = -buffer[1]

        delta_vel = self.current_vel + self.acceleration * delta_t

        # checks for actor collision
        for i in map.enemies:
            if not self.actor_collision(i.hit_box):
                self.actor_collide = 0

            else:  # knocks player back and reduces health if the npc is an enemy
                self.actor_collide = 1
                if i.alignment == "Evil" and self.g_player.is_active:
                    self.knock_vel = 50 * -self.acceleration.normalized  # magnitude times direction
                    self.knock_back()
                    self.health -= 5
                    self.knock_move(map, delta_t)
                elif i.alignment == "Good" and self.b_player.is_active:
                    self.knock_vel = 50 * -self.acceleration.normalized  # magnitude times direction
                    self.knock_back()
                    self.health -= 5
                    self.knock_move(map, delta_t)

                self.current_pos -= (delta_pos - self.current_pos)
                self.current_vel -= (delta_vel - self.current_vel)
                break

            for i in map.npcs:
                if not self.actor_collision(i.hit_box):
                    self.actor_collide = 0
                else:
                    self.actor_collide = 1
                    self.current_pos -= self.current_direction / 2
                    self.current_vel -= self.current_direction / 2

        # checks to see if there was a tile or actor collision, and moves if not
        if not map.tilecheck(delta_pos + buffer) and not self.actor_collide:
            self.is_moving = 1  # updating player state
            self.current_pos = delta_pos
            self.current_vel = delta_vel
            self.current_vel -= self.current_vel * 0.01

        else:  # stops moving
            self.is_moving = 0

        if self.current_vel.magnitude > self.max_speed.magnitude:  # caps move speed
            self.current_vel = self.max_speed

        self.hit_box_update()

    def attack(self, other):
        """
        attack function for the player class, dealing damage to all enemies hit after running the hit_detect() method
        :param other: map object containing a list of enemies on screen
        :return: nothing
        """
        if self.attack_cd_timer == 0:  # checking the attack cool down
            self.current_weapon.is_swinging = 1  # updating player state for animations
            self.is_attacking = 1  # more player state updating for animations
            self.attack_cd_timer = 0.1  # triggering the cool down
            for i in other:  # rolling through all enemies on screen to see if the player hits them
                if self.current_weapon.hit_detect(i):  # calling parent hit_detect method
                    if (self.g_player.is_active and i.alignment == "Evil") or (self.b_player.is_active and i.alignment == "Good"):
                        i.health -= self.damage  # dealing damage to the hit enemy
                        if i.is_dead():
                            if self.g_player.is_active:
                                self.g_player.boss_counter += 1
                            else:
                                self.b_player.boss_counter += 1
                        i.knock_back()  # applies knockback effect to enemies
                        i.knock_vel = 50 * self.acceleration.normalized  # applies force to the opponent

    def draw(self, surf, camera):
        """
        draw function for actors, currently animates basic temporary sprites
        :param surf: pygame style Surface
        :param camera: camera object for world coordinate conversion
        :return: nothing
        """
        if self.is_dead():  # dead men tell no tales
            return
        # print(self.current_weapon)
        # print(self.Spear.Hitbox)
        temp_cube = Cuboid(vector.Vector3(0, 0, 0), self.current_weapon.Hitbox.mPos.copy(), vector.Vector2(48, 4))

        # temp_cube = Cuboid(vector.Vector3(0, 0, 0), self.current_weapon.Hitbox.mPos.copy(), vector.Vector2(self.current_weapon.Hitbox.mExtents[0] * 2, self.current_weapon.Hitbox.mExtents[1] * 2))
        temp_cube.mAngle = self.current_weapon.Hitbox.mAngle
        temp_vec = camera.apply(temp_cube.mPos)
        temp_cube.mPos = temp_vec
        # ##--Lane(Weapon_drawing)--##
        if self.current_weapon.weapon_drawn is True:   # if weapon_drawn is True then draw weapon hit box
            if self.sprite_row == 4 or self.sprite_row == 1 or self.sprite_row == 2 or self.sprite_row == 3 or self.sprite_row == 0:
                x = temp_cube.mPos.x - self.current_weapon.rotated_weap_img.get_width()//2
                y = temp_cube.mPos.y - self.current_weapon.rotated_weap_img.get_height()//2

                surf.blit(self.current_weapon.rotated_weap_img, (x, y))
                #temp_cube.drawPygame(surf)

        temp_rect = camera.apply(self.current_pos)  # create temporary list to protect the current position
        # converts from world coord to screen coords

        # Drawing the actor from the sprite sheet using known attributes, and offsets the sprite so current_pos is the
        # ... center of the sprite
        surf.blit(self.sprite_sheet, (temp_rect[0] - (self.sprite_size // 2),
                   temp_rect[1] - (self.sprite_size // 2)),
                  (self.sprite_column * self.sprite_size + self.sprite_offset[0],
                   self.sprite_row * self.sprite_size + self.sprite_offset[1],
                   self.sprite_size, self.sprite_size))

        # ##--Lane(Weapon_drawing)--##
        if self.current_weapon.weapon_drawn is True:  # if weapon_drawn is True then draw weapon hit box
            if self.sprite_row == 5 or self.sprite_row == 6 or self.sprite_row == 7:
                x = temp_cube.mPos.x - self.current_weapon.rotated_weap_img.get_width()//2
                y = temp_cube.mPos.y - self.current_weapon.rotated_weap_img.get_height()//2
                surf.blit(self.current_weapon.rotated_weap_img, (x, y))

        pygame.draw.rect(surf, (0, 0, 0), (temp_rect[0] - 20, temp_rect[1] - 20, 40, 3), 0)
        pygame.draw.rect(surf, (255, 255, 0), (temp_rect[0] - 20, temp_rect[1] - 20, 40 * (self.health/self.max_health), 3), 0)

    def activate_other(self, npc_list):

        for npc in npc_list:

            hit_vector = npc.current_pos - self.current_pos
            hit_direction = hit_vector.normalized

            if (hit_direction.x < self.current_direction.x + 0.3 and hit_direction.y < self.current_direction.y + 0.3
                and hit_direction.x > self.current_direction.x - 0.3 and hit_direction.y > self.current_direction.y - 0.3) \
                    and hit_vector.magnitude <= 75:

                if npc.is_activated:
                    npc.is_activated = 0
                else:
                    npc.is_activated = 1

                return

        return

    def is_dead(self):
        """
        checks to see if the actor has died
        :return: boolean based on the health level of the actor
        """
        if self.health <= 0:
            self.Cur_Background_Music.stop()
            return 1
        else:
            return 0

    def swap_active(self):
        """
        swap active player method, used to store the current position, inventory etc. into the relevant good or bad
        player objects, and to make the inactive good or bad player active, setting its relevant data to the current
        :return: nothing
        """

        if self.g_player.is_active and self.curr_map == "Bad Hub":
            self.g_player.is_active = 0  # deactivate good player
            self.b_player.is_active = 1  # activate bad player

            # update the separately stored good player values with the current values
            self.g_player.direction = self.current_direction
            self.g_player.pos = self.current_pos
            self.g_player.max_health = self.max_health
            self.g_player.health = self.health

            # set the current variables to the previously stored bad player values
            self.current_direction = self.b_player.direction
            self.current_pos = self.b_player.pos
            self.sprite_sheet = self.b_player.sprite_sheet
            self.sprite_offset = self.b_player.sprite_offset
            self.health = self.b_player.health
            self.max_health = self.b_player.max_health
            self.Cur_Background_Music.stop()
            self.Cur_Background_Music = self.Bad_Theme

        elif self.b_player.is_active and self.curr_map == "Good Hub":
            self.b_player.is_active = 0  # deactivate the bad player
            self.g_player.is_active = 1  # activate the good player

            # update the separately stored bad player values with the current values
            self.b_player.direction = self.current_direction
            self.b_player.pos = self.current_pos
            self.b_player.max_health = self.max_health
            self.b_player.health = self.health

            # set the current variables to the previousl stored good player values
            self.current_direction = self.g_player.direction
            self.current_pos = self.g_player.pos
            self.sprite_sheet = self.g_player.sprite_sheet
            self.sprite_offset = self.g_player.sprite_offset
            self.health = self.g_player.health
            self.max_health = self.g_player.max_health
            self.Cur_Background_Music.stop()
            self.Cur_Background_Music = self.Good_Theme

        else:
            return

        self.update_sprite_facing()

        self.Cur_Background_Music.set_volume(0.5)
        self.Cur_Background_Music.play(1)

    # End Player Class

########################################################################################################################


class Enemy(Actor):
    """
    Class for handling enemies, inherits from the Actor class.
    """

    def __init__(self, spawn, path_list, patrolling, direction, alignment, type):

        super().__init__()  # parent constructor

        self.current_pos = vector.Vector2(int(spawn[0]), int(spawn[1]))  # customized spawn point for enemy
        self.acceleration = vector.Vector2(50, 0)

        self.rest_direction = direction
        if not patrolling:
            self.current_direction = self.rest_direction
        self.aggro_range = 125  # range in pixels the enemy will check for an opponent to chase
        self.chase_range = 150  # range the enemy must pass in order to trigger a loss in aggro from the enemy
        self.is_chasing = 0  # boolean actor state to control player chasing
        self.chase_timer = 0  # timer that controls how long the enemy chases the player after the player leaves chase range
        self.is_losing_aggro = 0  # boolean actor state to control the use of the chase timer
        self.is_moving = 1  # boolean actor state to control movement animations
        self.attack_cd_timer = 0.5
        self.move_cd_timer = 0
        self.is_patrolling = patrolling
        self.patrol_path = path_list
        self.patrol_stage = 0
        self.patrol_stage_cap = len(self.patrol_path) - 1
        self.max_speed = vector.Vector2(50, 0)
        self.update_vectors()
        self.type = type

        if type == "Guard":
            self.sprite_sheet = pygame.image.load_extended("Assets/tiles from rpgmaker/badnpc_walk_final.png").convert_alpha()  # temporary sprite sheet
            self.sprite_offset = (0, 0)
            self.max_health = 100
            self.health = self.max_health
            self.damage = 5

        elif type == "Knight":
            self.sprite_sheet = pygame.image.load_extended("Assets/tiles from rpgmaker/goodnpc_walk_final.png").convert_alpha()  # temporary sprite sheet
            self.sprite_offset = (0, 0)
            self.max_health = 200
            self.health = self.max_health
            self.damage = 15

        elif type == "Boss":
            if alignment == "Good":
                self.sprite_sheet = pygame.image.load_extended(
                    "Assets/tiles from rpgmaker/spell_bad_walk.png").convert_alpha()  # temporary sprite sheet
            else:
                self.sprite_sheet = pygame.image.load_extended(
                    "Assets/tiles from rpgmaker/barb_good_walk.png").convert_alpha()  # temporary sprite sheet
                self.sprite_sheet = pygame.image.load_extended("Assets/tiles from rpgmaker/people4.png").convert_alpha()

            self.sprite_offset = (0, 0)
            self.max_health = 300
            self.health = self.max_health

        self.alignment = alignment

        self.current_weapon = Weapon(self)
        self.current_weapon.current_weapon = "Spear"

    def aggro_check(self, actors):
        """
        Function to aggro the enemy onto the player if the player is within the aggro range of the enemy
        :param player: player object
        :return: nothing
        """
        temp_list = []

        for actor in actors:

            # calculate the distance from the player in pixels using vectors
            hyp = actor.current_pos - self.current_pos

            if hyp.magnitude <= self.aggro_range:
                self.is_chasing = 1  # the hunt begins
                self.max_speed = 75 * self.acceleration.normalized  # speeds up to chase the player
                self.destination = self.patrol_path[self.patrol_stage]
                temp_list.append(actor)
                return temp_list

            if hyp.magnitude > self.chase_range and self.is_chasing and not self.is_losing_aggro:  # triggers loss of aggro
                self.is_losing_aggro = 1
                self.chase_timer = 5

        return temp_list

    def update(self, direction, map, camera, actors, dt):
        """
        Updates the enemy's timers, checks to aggro the player, attacks the player if possible, chases the player if
        aggroed, and moves the enemy while also doing tile and actor collision
        :param direction: typically always forward, a string
        :param map: map object for tile collision checks
        :param camera: camera object for world coord conversions
        :param player: player object for aggro checks and hit detection
        :param dt: change in time
        :return: nothing
        """

        self.attack_anim_timer += dt  # advance the attack animation timer

        self.move_anim_timer += dt  # advance the movement animation timer

        if self.move_anim_timer > 0.1 and self.is_moving:
            self.sprite_column += 1  # advancing the sprite to the next animation frame

            if self.sprite_column > 2:  # wrapping the sprite back around to the start of the walk animation if it
                                        #...  goes out of range.
                self.sprite_column = 0

            self.move_anim_timer = 0  # resetting the animation timer

        elif not self.is_moving:  # checking if the idle animations need to be played (currently just a still sprite)
            self.sprite_column = 1

        if self.attack_cd_timer > 0:  # checks to see if the weapon attack is still on cooldown, and lowers it if so
            self.attack_cd_timer -= dt

        else:  # resets the attack cooldown timer
            self.attack_cd_timer = 0

        aggroed_actors = self.aggro_check(actors)  # checks to see if the enemy should chase the player

        if self.is_chasing:  # chases player
            self.is_patrolling = 0
            self.look_at_nearest_actor(actors, camera)  # update direction in order to chase player
            self.attack(aggroed_actors)  # hits the player if they are in reach

        if self.is_losing_aggro and self.is_chasing:  # lowers aggro timer and when it runs out resets the appropriate
                                                      #... actor values
            self.chase_timer -= dt

            if self.chase_timer < 0:

                self.chase_timer = 0
                self.is_chasing = 0
                self.is_losing_aggro = 0
                self.max_speed = 50 * self.acceleration.normalized  # magnitude times direction
                self.destination = self.patrol_path[self.patrol_stage]

                if len(self.patrol_path) > 1:
                    self.is_patrolling = 1
                else:
                    self.is_patrolling = 0

        if self.is_patrolling:
            self.patrol_stage_check()
            self.look_at_world_point(self.patrol_path[self.patrol_stage], camera)

        if self.actor_collide:  # prevents the enemy from stun locking player movement by constantly running into and
            self.reset_velocity()  # causes the enemy to have to accelerate again after colliding with the player

        if self.knock_timer > 0:  # decreases the knock back timer and then calls the knock movement function

            self.knock_timer -= dt
            self.knock_move(map, dt)

        else:  # resets knock back actor values

            self.knock_timer = 0
            self.is_knocked_back = 0

        if not self.is_knocked_back and not self.in_range and not self.current_weapon.is_swinging:  # moves the enemy if possible
            if self.is_patrolling or self.is_chasing:
                self.move(direction, map, actors, dt)
                self.is_moving = 1

            elif not self.destination is None:
                distance = (self.destination - self.current_pos).magnitude
                if distance > 1:
                    self.look_at_world_point(self.destination, camera)
                    self.move(direction, map, actors, dt)

                else:
                    self.destination = None
                    self.current_direction = self.rest_direction
                    self.update_vectors()

            else:
                self.is_moving = 0

        self.hit_box_update()
        self.current_weapon.Update(self, dt, camera)

    def attack(self, other):
        """
        attack function for the enemy class, dealing damage to the player after running the hit_detect() method
        :param other: the player or neutral npcs
        :return: nothing
        """
        for i in other:
            if self.attack_cd_timer <= 0:  # checking the attack cool down
                if (i.current_pos - self.current_pos).magnitude < self.current_weapon.reach:
                    self.is_attacking = 1  # more enemy state updating for animations
                    self.current_weapon.is_swinging = 1  # updating enemy state for animations

                    if self.current_weapon.hit_detect(i):
                        self.attack_cd_timer = 1  # triggering the cool down
                        i.health -= self.damage  # deals damage to the player
                        i.knock_back()  # knocks the player back
                        i.knock_vel = 50 * self.current_direction  # makes the opponent move straight back independent of where they are facing
                        break


class NPC(Actor):

    def __init__(self):

        super().__init__()

        self.sprite_offset = (0, 0)
        self.sprite_sheet = pygame.image.load_extended("Assets/tiles from rpgmaker/shop_walk.png").convert_alpha()
        self.current_pos = vector.Vector2(600, 2550)
        self.current_direction = vector.Vector2(1, 0)
        self.update_sprite_facing()
        self.health = 50
        self.max_health = 50
        self.is_activated = 0

        self.gui_runner = GUI.GUI()
        self.gui_runner.SetText("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc pretium lorem vel ligula vulputate ultrices non vel leo. Nunc elementum ipsum vitae tellus faucibus scelerisque. Vivamus consequat, nisl ut porta rhoncus, justo mauris ornare nisl, varius ornare nunc neque vel nisi. Sed aliquet magna eu dui iaculis bibendum. Pellentesque sed tellus dapibus, ultricies ex vel, gravida tellus. Nulla convallis elit nec felis dapibus, et vehicula odio euismod. Vestibulum et eros eu velit mollis laoreet fermentum vitae ligula. Praesent quis est non mauris luctus pharetra. Aenean tincidunt vulputate neque, nec blandit arcu placerat sed. Integer vel elit maximus, aliquam tortor ac.")
        self.gui_runner.SetColor((255, 255, 255))
        self.gui_runner.SetArea((150, 400, 500, 100))
        self.gui_runner.SetTriangle(([530, 130], [538, 130], [534, 140]))

    def update(self, mpos, direction, map, actors, dt):

        if self.is_activated:
            self.gui_runner.SetVisible(1)

        else:
            self.gui_runner.SetVisible(0)

        if self.gui_runner.Visible:
            self.gui_runner.Update(dt)

        self.move_anim_timer += dt  # advance the movement animation timer

        if self.move_anim_timer > 0.1 and self.is_moving:
            self.sprite_column += 1  # advancing the sprite to the next animation frame

            if self.sprite_column > 2:  # wrapping the sprite back around to the start of the walk animation if it
                                        #...  goes out of range.
                self.sprite_column = 0

            self.move_anim_timer = 0  # resetting the animation timer

        elif not self.is_moving:  # checking if the idle animations need to be played (currently just a still sprite)
            self.sprite_column = 1

        self.move(direction, map, actors, dt)  # moves the actor, does movement collision for tiles and other actors

        if not self.is_moving:
            self.current_vel -= self.current_vel * dt # lowers velocity

        self.hit_box_update()  # updates hitbox to new location