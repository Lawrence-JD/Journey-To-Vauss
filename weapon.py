import pygame
from actor import *
from object import *
from vector import *


class Weapon(object):

    def __init__(self, actor):
        self.Damage = 0
        self.Attack_Speed = 0
        self.Reach = 0
        self.Is_Active = False
        self.Position = [0, 0]
        self.Hitbox = Cuboid(Vector3(1, 0, 0), Vector2(0, 0), Vector2(48, 4))
        self.HitNoise = pygame.mixer.Sound("Assets/Sounds/SwordHit.wav")
        self.is_swinging = 0
        self.attack_anim_counter = 0
        self.attack_anim_timer = 0
        self.reach = 50
        self.weapon_drawn = False
        self.current_weapon = None
        self.scaled_weap_img = None
        self.rotated_weap_img = None
        self.spear_img = pygame.image.load("Spear.png").convert_alpha()
        self.sword_img = pygame.image.load("Sword.png").convert_alpha()
        self.actor = actor
        self.__class__ = Thrusting


    def Equip(self):
        if self.weapon_drawn:
            self.weapon_drawn = False
        else:
            self.weapon_drawn = True

    def swap_weapon(self):
        """
        Checks for current weapon type and switches classes to the other weapon type
        :return:
        """
        self.__class__ = Thrusting
        self.Hitbox = Cuboid(Vector3(1, 0, 0), self.actor.current_pos.copy(), Vector2(48, 4))

    def hit_detect(self, other):
        """
        detects if an attack by the self hit the other
        :param other: an actor object
        :return: true if hits, false if not
        """
        if collides(self.Hitbox, other.hit_box):
            self.in_range = 1  # lets the AI know it can make an attack
            self.HitNoise.play(0)
            return 1  # True

        else:
            self.in_range = 0
            return 0

    def passive_animate(self, actor):
        if not self.is_swinging:
            self.Hitbox.mPos = actor.current_pos.copy()
            if actor.sprite_row == 0:
                self.Hitbox.mPos.x -= 7
                self.Hitbox.mPos.y += 3

                if actor.sprite_column == 0:
                    self.Hitbox.mPos.y += 4

                elif actor.sprite_column == 2:
                    self.Hitbox.mPos.y -= 2

            if actor.sprite_row == 1:
                self.Hitbox.mPos.x -= 4
                self.Hitbox.mPos.y += 3

                if actor.sprite_column == 0:
                    self.Hitbox.mPos.x -= 3
                    self.Hitbox.mPos.y -= 2

                elif actor.sprite_column == 2:
                    self.Hitbox.mPos.y -= 3
                    self.Hitbox.mPos.x += 3

            if actor.sprite_row == 2:
                self.Hitbox.mPos.y += 4

                if actor.sprite_column == 0:
                    self.Hitbox.mPos.x -= 4

                elif actor.sprite_column == 2:
                    self.Hitbox.mPos.x += 4

            if actor.sprite_row == 6:
                self.Hitbox.mPos.y += 4

                if actor.sprite_column == 0:
                    self.Hitbox.mPos.x -= 4

                elif actor.sprite_column == 2:
                    self.Hitbox.mPos.x += 4

            if actor.sprite_row == 3:
                self.Hitbox.mPos.x += 1
                self.Hitbox.mPos.y += 1

                if actor.sprite_column == 0:
                    self.Hitbox.mPos.x -= 3
                    self.Hitbox.mPos.y -= 3

                elif actor.sprite_column == 2:
                    self.Hitbox.mPos.y += 3
                    self.Hitbox.mPos.x += 3

            if actor.sprite_row == 4:
                self.Hitbox.mPos.x += 6

                if actor.sprite_column == 0:
                    self.Hitbox.mPos.y -= 3

                elif actor.sprite_column == 2:
                    self.Hitbox.mPos.y += 3

            if actor.sprite_row == 5:
                self.Hitbox.mPos.x += 6
                self.Hitbox.mPos.y += 3

                if actor.sprite_column == 0:
                    self.Hitbox.mPos.x += 3
                    self.Hitbox.mPos.y += 2

                elif actor.sprite_column == 2:
                    self.Hitbox.mPos.y += 3
                    self.Hitbox.mPos.x -= 3

            if actor.sprite_row == 7:
                self.Hitbox.mPos.x -= 4
                self.Hitbox.mPos.y += 4

                if actor.sprite_column == 0:
                    self.Hitbox.mPos.x += 3
                    self.Hitbox.mPos.y += 3

                elif actor.sprite_column == 2:
                    self.Hitbox.mPos.y -= 3
                    self.Hitbox.mPos.x -= 3

    def Primaries(self):
        pass
    # Animation related things here.

    def Secondaries(self):
        pass

    def Tertiary(self):
        pass

    def Update(self, player, dt, camera):
        pass

    def Draw(self, Screen):

        self.Hitbox.drawPygame(Screen)

    # Get temporary sprite, one for each weapon and point it towards where the player is facing.
    # Move hit detection into the weapon class
    # Open Actor module open hit detect function. Start with that. It needs to be specific to the weapon. Move hit detection function to the actor class.
    # Make every weapon a rectangle.
    # Going to have three animations: Thrust: Make it only do damage when it's thrusting out, and whenever the animation is retracting it won't do damage.
    # Going to have a swiping animation for a sword which will only do damage when the blade comes into contact with another object.
    # Going to have a crush animation for the mace. Make it face towards where the player is facing.
    # Player will always face the mouse so make the weapons face in the same direction as the player.
    # Think about the different types of weapons that this could possiby contain. The more functionality in the long run the better.


class Thrusting(Weapon):

    def __init__(self, actor):
        super().__init__(actor)
        self.Hitbox = Cuboid(Vector3(1, 0, 0), actor.current_pos.copy(), Vector2(48, 4))
        self.reach = 48

    def Update(self, actor, dt, camera):
        # print("THRUST UPDATE")
        self.passive_animate(actor)
        self.Hitbox.mAngle = actor.current_direction.radians
        self.swing_anim_stage = 0

        # ##--Lane(Weapon_image_update)--##
        rad = math.degrees(self.Hitbox.mAngle)  # use same angle as weapon hit box
        temp = 0
        # These if statements are to negate the effects of how our current direction system works and
        # turns it into a more traditional 0-360 degree system for the weapon image rotation.
        if rad < 0:
            temp = math.fabs(rad)
        if rad > 0:
            temp = 180 + (180-rad)
        self.scaled_weap_img = pygame.transform.scale(self.spear_img, (48, 4))
        self.rotated_weap_img = pygame.transform.rotate(self.scaled_weap_img, temp)
        # ##--Lane(Weapon_drawing_update)--##

        if actor.is_attacking:
            self.attack_anim_timer += dt  # advance the attack animation timer

            if self.attack_anim_timer > 0.01 and self.is_swinging:  # checks if we should advance the frame in a "thrust"
                self.attack_anim_counter += 1
                self.attack_anim_timer = 0  # resetting the animation timer

                if self.attack_anim_counter > 4:  # check to see if we have completed the "thrust" animation
                    self.is_swinging = 0

            if self.attack_anim_timer > 0.01 and not self.is_swinging:  # checks if we should advance the "retract"
                self.attack_anim_counter -= 1

            if self.attack_anim_counter == 0:  # checks if we have finished the animation
                actor.is_attacking = 0  # resetting the animation state
                self.attack_anim_timer = 0  # resetting the animation timer
            self.Hitbox.mPos = actor.current_pos + (3 * self.attack_anim_counter * actor.current_direction)


class Sweeping(Weapon):

    def __init__(self, actor):
        super().__init__(actor)
        self.Hitbox = mCuboid(Vector3(1, 0, 0), actor.current_pos.copy(), Vector2(20, 4))
        self.reach = 20

    def Update(self, actor, dt, camera):
        # print("SWING UPDATE")
        self.passive_animate(actor)

        self.Hitbox.mAngle = actor.current_direction.radians
        self.swing_anim_stage = 0

        # ##--Lane(Weapon_image_update)--##
        rad = math.degrees(self.Hitbox.mAngle)  # use same angle as weapon hit box
        temp = 0
        # These if statements are to negate the effects of how our current direction system works and
        # turns it into a more traditional 0-360 degree system for the weapon image rotation.
        if rad < 0:
            temp = math.fabs(rad)
        if rad > 0:
            temp = 180 + (180-rad)
        self.scaled_weap_img = pygame.transform.scale(self.sword_img, (20, 4))
        self.rotated_weap_img = pygame.transform.rotate(self.scaled_weap_img, temp)
        # ##--Lane(Weapon_drawing_update)--##

        if actor.is_attacking:
            self.attack_anim_timer += dt  # advance the attack animation timer

            if self.attack_anim_timer > 0.05 and self.is_swinging:  # checks if we should advance the frame in a "thrust"
                self.attack_anim_counter += 1
                self.attack_anim_timer = 0  # resetting the animation timer

            if self.attack_anim_counter > 4:  # checks if we have finished the animation
                self.is_swinging = 0
                self.attack_anim_counter = 0
                actor.is_attacking = 0  # resetting the animation state
                self.attack_anim_timer = 0  # resetting the animation timer
            self.Hitbox.mAngle = actor.current_direction.radians - (0.5 * self.attack_anim_counter) + (math.pi / 3)
            self.rotated_weap_img = pygame.transform.rotate(self.scaled_weap_img, math.degrees(-self.Hitbox.mAngle))


class Crushing(Weapon):

    def __init__(self):
        super().__init__()