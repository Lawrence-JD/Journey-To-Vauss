# Main file

import pygame
import Map02 as m
import vector
from object import *

pygame.init()
screen = pygame.display.set_mode((800, 600))
screensize = (800, 600)
is_fullscreen = 0

MainImg = pygame.image.load("Assets/MainBackground.jpg")
Death_Music = pygame.mixer.Sound("Assets/Sounds/DeathMusic.wav")
Main_Menu_Music = pygame.mixer.Sound("Assets/Sounds/MainMusic.wav")
Start_Button = pygame.mixer.Sound("Assets/Sounds/Main_Menu_Effect_1.wav")
Menu_Sound = pygame.mixer.Sound("Assets/Sounds/Menu_Sounds.wav")
Good_Image = pygame.image.load("Assets/Good_Image.png")
Evil_Image = pygame.image.load("Assets/Evil_Image.png")
Title = pygame.font.SysFont("Arial", 70)
Start = pygame.font.SysFont("Arial", 45)
Quit = pygame.font.SysFont("Arial", 45)
Select = pygame.font.SysFont("Arial", 55)

Text = Title.render("Journey To Vauss", True, (255, 215, 0))
Start_Object = Start.render("Start", True, (255, 215, 0))
Quit_Object = Quit.render("Quit", True, (255, 215, 0))
Select = Select.render("Select your destiny  ...it's your choice.", True, (255, 215, 0))
Start_Bounds = Cuboid(vector.Vector3(0, 0, 0), vector.Vector2(485, 465), vector.Vector2(90, 40))
Quit_Bounds = Cuboid(vector.Vector3(255, 255, 255), vector.Vector2(485, 515), vector.Vector2(90, 40))
Good_Bounds = Cuboid(vector.Vector3(255, 255, 255), vector.Vector2(200, 300), vector.Vector2(390, 590))
Evil_Bounds = Cuboid(vector.Vector3(0, 0, 0), vector.Vector2(600, 300), vector.Vector2(390, 590))

Sword_Image = pygame.image.load('Assets/Sword_Image.png').convert_alpha()

theMap = m.Map("Test_map")

done = 0
game_won = 0
In_Menu = 1
In_Character_Selection = 0
Currently_Selected = None # 1 is good and bad is 0.
Main_Menu_Music.play(-1)
Main_Menu_Music.set_volume(1)
In_Bounds_Lastframe = 0

while In_Menu:
    Mouse_Position = pygame.mouse.get_pos()
    Mouse_Button = pygame.mouse.get_pressed()
    Mouse_Position_Vector = vector.Vector2(Mouse_Position[0], Mouse_Position[1])

    Event = pygame.event.poll()
    Keys = pygame.key.get_pressed()

    screen.fill((255, 255, 255))

    if not In_Character_Selection:
        screen.blit(MainImg, (0, 0))
        screen.blit(Text, (180, 80))
        screen.blit(Start_Object, (450, 440))
        screen.blit(Quit_Object, (450, 490))

    else:
        pygame.draw.rect(screen, (55, 148, 110), [(0, 0), (400, 600)], 0)
        pygame.draw.rect(screen, (41, 10, 28), [(400, 0), (800, 600)], 0)
        screen.blit(Evil_Image, (600, 300))
        screen.blit(Good_Image, (100, 300))
        screen.blit(Select, (13, 0))
        if Good_Bounds.pointInShape(Mouse_Position_Vector):
            if Currently_Selected != 1:
                Menu_Sound.play(0)
            Currently_Selected = 1
            pygame.draw.rect(screen, (95, 188, 150), [(0, 0), (400, 600)], 0)
            pygame.draw.rect(screen, (255, 255, 255), [(0, 0), (400, 600)], 10)
            screen.blit(Good_Image, (100, 300))
            if Event.type == pygame.MOUSEBUTTONDOWN and Event.button == 1:
                In_Menu = 0
        elif Evil_Bounds.pointInShape(Mouse_Position_Vector):
            if Currently_Selected != 0:
                Menu_Sound.play(0)
            Currently_Selected = 0
            pygame.draw.rect(screen, (81, 50, 68), [(400, 0), (800, 600)], 0)
            pygame.draw.rect(screen, (255, 255, 255), [(400, 0), (400, 600)], 10)
            screen.blit(Evil_Image, (600, 300))
            if Event.type == pygame.MOUSEBUTTONDOWN and Event.button == 1:
                In_Menu = 0
                theMap.player.curr_map = "Bad Hub"
                theMap.player.swap_active()

    if Event.type == pygame.KEYDOWN:
        if Keys[pygame.K_ESCAPE]:
            pygame.quit()
            exit(0)

    if Start_Bounds.pointInShape(Mouse_Position_Vector) and not In_Character_Selection:
        Start_Object = Start.render("Start", True, (255, 255, 255))
        if not In_Bounds_Lastframe:
            Menu_Sound.play(0)
            In_Bounds_Lastframe = 1

    elif Quit_Bounds.pointInShape(Mouse_Position_Vector) and not In_Character_Selection:
        Quit_Object = Quit.render("Quit", True, (255, 255, 255))
        # Bugged currently.
        if not In_Bounds_Lastframe:
            Menu_Sound.play(0)
            In_Bounds_Lastframe = 1

    else:
        In_Bounds_Lastframe = 0
        Start_Object = Start.render("Start", True, (255, 215, 0))
        Quit_Object = Quit.render("Quit", True, (255, 215, 0))

    if Start_Bounds.pointInShape(Mouse_Position_Vector) and Event.type == pygame.MOUSEBUTTONDOWN and Event.button == 1 and not In_Character_Selection:
        In_Character_Selection = 1

    elif Quit_Bounds.pointInShape(Mouse_Position_Vector) and Mouse_Button[0] and not In_Character_Selection:
        exit(0)

    screen.blit(Sword_Image, (Mouse_Position))
    pygame.mouse.set_visible(False)
    pygame.display.flip()

Start_Button.play(0)

Main_Menu_Music.stop()
theMap.player.Cur_Background_Music.play(-1)

theCamera = m.Camera(theMap, 800, 600)

pointerImg = pygame.image.load('Assets/GoodEvilReticuleC.png').convert_alpha()
MainImg = pygame.image.load("Assets/MainBackground.jpg")

# FONTS
defaultfont = pygame.font.SysFont("Courier", 20)

clock = pygame.time.Clock()
Menu_Sound.stop()
Start_Button.stop()

while not done:
    dt = clock.tick(60) / 1000 # updating delta time at the start of every frame

    # FPS
    fps = str(round(clock.get_fps(), 2))
    fps = defaultfont.render(fps, False, (255, 255, 255))

    # handle inputs
    evt = pygame.event.poll()
    keys = pygame.key.get_pressed()
    m_button = pygame.mouse.get_pressed()
    mpos = pygame.mouse.get_pos()
    mpos_vec = vector.Vector2(mpos[0], mpos[1])

    if evt.type == pygame.QUIT:
        done = 1

    if evt.type == pygame.MOUSEBUTTONDOWN:
        if m_button[0]:
            if theMap.is_paused:

                for person in theMap.npcs:

                    if person.is_activated:
                        person.gui_runner.handleClick(mpos)
                        break

            else:
                if theMap.player.g_player.is_active:
                    theMap.player.attack(theMap.good_aggro_list)
                else:
                    theMap.player.attack(theMap.bad_aggro_list)

    if not theMap.player.is_knocked_back and not theMap.player.current_weapon.is_swinging and not theMap.is_paused:
        if keys[pygame.K_w]:
            theMap.player.move("forward", theMap, dt)
        if keys[pygame.K_s]:
            theMap.player.move("backward", theMap, dt)
        if keys[pygame.K_d]:
            theMap.player.move("left", theMap, dt)
        if keys[pygame.K_a]:
            theMap.player.move("right", theMap, dt)

    if evt.type == pygame.KEYDOWN:
        if keys[pygame.K_ESCAPE]:
            done = 1

        if keys[pygame.K_F5]:
            if is_fullscreen:
                screen = pygame.display.set_mode((800, 600))

                theCamera.update_camera_scale((800, 600))

                is_fullscreen = 0

            else:

                screen = pygame.display.set_mode(screensize, pygame.FULLSCREEN)

                theCamera.update_camera_scale(screensize)

                is_fullscreen = 1

        if keys[pygame.K_F1] and not theMap.is_paused:
            theMap.player.swap_active()

        if keys[pygame.K_e]:
            theMap.player.activate_other(theMap.npcs)

        if keys[pygame.K_q]:
            theMap.player.current_weapon.Equip()

        if keys[pygame.K_f]:
            theMap.player.current_weapon.swap_weapon()

        for person in theMap.npcs:

            if person.is_activated and theMap.player.b_player.is_active:
                game_won = 1

    # update
    if mpos[0] > 0 and mpos[0] < screen.get_width() and mpos[1] > 0 and mpos[1] < screen.get_height():
        pygame.mouse.set_visible(0)
    else:
        pygame.mouse.set_visible(1)

    theCamera.update(theMap.player)
    if theMap.player.is_dead():
        game_won = 1

    theMap.MapUpdate(theCamera, theMap.player, dt, game_won, mpos_vec)

    if game_won:
        done = 1

    # draw
    screen.fill((0, 0, 0))
    theMap.MapDraw(screen, theCamera)
    screen.blit(pointerImg, (mpos[0] - (pointerImg.get_width() // 2), mpos[1] - (pointerImg.get_height() // 2)))
    screen.blit(fps, (800 - fps.get_width(), 0))

    # clean up
    theMap.player.is_moving = 0
    pygame.display.flip()

if game_won:
    done = 0
    Death_Music.play(-1)
    while not done:

        evt = pygame.event.poll()
        keys = pygame.key.get_pressed()
        m_button = pygame.mouse.get_pressed()
        mpos = pygame.mouse.get_pos()
        mpos_vec = vector.Vector2(mpos[0], mpos[1])

        if evt.type == pygame.QUIT:
            done = 1

        if evt.type == pygame.KEYDOWN:
            if keys[pygame.K_ESCAPE]:
                done = 1

        screen.fill((0, 0, 0))

        message = defaultfont.render("GAME OVER", 0, (255, 255, 255))
        screen.blit(message, (screen.get_width()//2 - message.get_width()//2, screen.get_height()//2 - message.get_height()//2))

        pygame.display.flip()

pygame.mixer.quit()
pygame.quit()