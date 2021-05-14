# Imports.
import pygame
import random
import textwrap

# Gui class.
class GUI:
    def __init__(self):
        self.Font_Object = pygame.font.SysFont("Arial", 20)
        self.Visible = False
        self.TextList = []
        self.Color = (255, 255, 255)
        self.Arrow_Timer = 0.0
        self.Arrow_Color = (255, 255, 255)
        self.Changed = False
        self.Bottom_Bounds = None
        Mouse_Position = pygame.mouse.get_pos()
        self.SetArea((0,0, 500, 50))
        self.SetText("")
        self.Scroll_Pos = 0

    def SetText(self, Dialogue):
        Wrapped_Lines = textwrap.wrap(Dialogue, 65)
        self.TextList = Wrapped_Lines# Gets our dialogue.
        #for line in Wrapped_Lines:
        #    print(len(line), line)

        # Determine the size of our off-screen text area
        height = 0
        for line in self.TextList:
            height += self.Font_Object.size(line)[1]
        self.Other_Screen = pygame.Surface((self.Area[2], height))

        # Actually build the off-screen test area
        y = 0
        for line in self.TextList:
            temps = self.Font_Object.render(line, False, self.Color)
            self.Other_Screen.blit(temps, (0, y))
            y += temps.get_height()

    def SetColor(self, Color):
        self.Color = Color # Gets our color.

    def SetVisible(self, Visible):
        self.Visible = Visible # Sets text box visible or invisible.

    def SetArea(self, Area):
        self.Area = Area
        self.Bottom_Bounds = (self.Area[0] + self.Area[2] - 20, self.Area[1] + self.Area[3] - 20, 8, 10)
        self.Top_Bounds = (self.Area[0] + self.Area[2] - 20, self.Area[1] + 10, 8, 10)
        self.XBottom_Bounds = ()
        self.XTop_Bounds = ()

    def SetTriangle(self, Tri):
        self.Tri = Tri

    def handleClick(self, Mouse_Pos):
        # Could also use space bar to select the arrow and then if space is pressed again make it scroll.
        if self.Bottom_Bounds[0] < Mouse_Pos[0] < self.Bottom_Bounds[0] + self.Bottom_Bounds[2] and self.Bottom_Bounds[1] < Mouse_Pos[1] < self.Bottom_Bounds[1] + self.Bottom_Bounds[3] and self.Visible:
            self.Scroll(20)

        if self.Top_Bounds[0] < Mouse_Pos[0] < self.Top_Bounds[0] + self.Top_Bounds[2] + 2 and self.Top_Bounds[1] < Mouse_Pos[1] < self.Top_Bounds[1] + self.Top_Bounds[3] + 2 and self.Visible:
            self.Scroll(-20)



    def Draw(self, Surface):
        #pygame.draw.polygon(Screen, (255, 0, 0), 0, 0, 100, 100) # Work on bliting the new image of dialogue.
        if self.Visible:
            # Erase the gui area
            #pygame.draw.rect(Surface, (0, 0, 0), (146, 400, 508, 100))

            # Draw the border
            pygame.draw.rect(Surface, (self.Color), (self.Area), 10)  # This draws the text box to the surface.
            pygame.draw.rect(Surface, (0, 0, 0), (150, 400, 500, 100))
            # Draw the current area of text we want to show
            Surface.blit(self.Other_Screen, (self.Area[0], self.Area[1]), (0, self.Scroll_Pos, self.Area[2], self.Area[3]))

            # Draw the scroll arrow (maybe)
            A = (self.Bottom_Bounds[0], self.Bottom_Bounds[1]) # These are what needs changed.
            B = (A[0] + self.Bottom_Bounds[2], A[1])
            C = (A[0] + self.Bottom_Bounds[2] / 2, self.Bottom_Bounds[1] + self.Bottom_Bounds[3])
            pygame.draw.polygon(Surface, (self.Arrow_Color), (A, B, C), 0)
            if self.Arrow_Color == (0, 0, 0):
                pygame.draw.polygon(Surface, (255, 255, 255), (A, B, C), 1)

            D = (self.Top_Bounds[0], self.Top_Bounds[1] + self.Top_Bounds[3])
            E = (D[0] + self.Top_Bounds[2], D[1])
            F = (D[0] + self.Top_Bounds[2] / 2, self.Top_Bounds[1])
            pygame.draw.polygon(Surface, (self.Arrow_Color), (D, E, F), 0)
            if self.Arrow_Color == (0, 0, 0):
                pygame.draw.polygon(Surface, (255, 255, 255), (D, E, F), 1)

            # x drawing
            #pygame.draw.line(Surface, (self.Arrow_Color), (self.Top_Bounds[0], self.Top_Bounds[1]), (self.Top_Bounds[0] + self.Top_Bounds[2], self.Top_Bounds[1] + self.Top_Bounds[3]), 2)
            #pygame.draw.line(Surface, (self.Arrow_Color), (self.Top_Bounds[0], self.Top_Bounds[1] + self.Top_Bounds[3]), (self.Top_Bounds[0] + self.Top_Bounds[2], self.Top_Bounds[1] + self.Top_Bounds[3]), 2)

            #pygame.draw.line(Surface, (self.Arrow_Color), (self.Top_Bounds[0], self.Top_Bounds[1]), (self.Top_Bounds[0] + self.Top_Bounds[2], self.Top_Bounds[1] + self.Top_Bounds[3]), 2)
            #pygame.draw.line(Surface, (self.Arrow_Color), (self.Top_Bounds[0], self.Top_Bounds[1] + self.Top_Bounds[3]), (self.Top_Bounds[0] + self.Top_Bounds[2], self.Top_Bounds[1] + self.Top_Bounds[3]), 2)

            #pygame.draw.line(Surface, (self.Arrow_Color), (self.Top_Bounds[0], self.Top_Bounds[1]), (self.Top_Bounds[0] + self.Top_Bounds[2], self.Top_Bounds[1] + self.Top_Bounds[3]), 2)
            #pygame.draw.line(Surface, (self.Arrow_Color), (self.Top_Bounds[0], self.Top_Bounds[1] + self.Top_Bounds[3]), (self.Top_Bounds[0] + self.Top_Bounds[2], self.Top_Bounds[1] + self.Top_Bounds[3]), 2)

            #pygame.draw.line(Surface, (self.Arrow_Color), (self.Top_Bounds[0], self.Top_Bounds[1]), (self.Top_Bounds[0] + self.Top_Bounds[2], self.Top_Bounds[1] + self.Top_Bounds[3]), 2)
            #pygame.draw.line(Surface, (self.Arrow_Color), (self.Top_Bounds[0], self.Top_Bounds[1] + self.Top_Bounds[3]), (self.Top_Bounds[0] + self.Top_Bounds[2], self.Top_Bounds[1] + self.Top_Bounds[3]), 2)

            #pygame.draw.line(Surface, (self.Arrow_Color), (self.Top_Bounds[0], self.Top_Bounds[1]), (self.Top_Bounds[0] + self.Top_Bounds[2], self.Top_Bounds[1] + self.Top_Bounds[3]), 2)
            #pygame.draw.line(Surface, (self.Arrow_Color), (self.Top_Bounds[0], self.Top_Bounds[1] + self.Top_Bounds[3]), (self.Top_Bounds[0] + self.Top_Bounds[2], self.Top_Bounds[1] + self.Top_Bounds[3]), 2)


    def Update(self, DeltaTime):
        self.X = pygame.mouse.get_pos()[0]
        self.Y = pygame.mouse.get_pos()[1]
        self.Arrow_Timer += DeltaTime
        #print(self.Arrow_Timer)
        #print(self.Changed)
        if self.Arrow_Timer > 1:
            self.Changed = True
            self.Arrow_Color = (255, 255, 255)
            self.Arrow_Timer = 0.0

        elif self.Changed == True:
            if self.Arrow_Timer > 0.9:
                self.Arrow_Color = (0, 0, 0)
                self.Arrow_Timer = 0.0
                self.Changed = False

    def Scroll(self, offset):
        self.Scroll_Pos += offset
        if self.Scroll_Pos < 0:
            self.Scroll_Pos = 0
        elif self.Scroll_Pos > self.Other_Screen.get_height() - self.Area[3]:
            self.Scroll_Pos = self.Other_Screen.get_height() - self.Area[3]