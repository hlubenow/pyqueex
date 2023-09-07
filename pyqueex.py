#!/usr/bin/python
# coding: utf-8

import pygame
from pygame.locals import *
import os
import random

"""
    Pyqueex 0.6 - Clone of an ancient arcade game - not complete yet.

    Copyright (C) 2023 hlubenow

    This program is free software: you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
# ----------------------------------------------------------

# Settings:

SCALEFACTOR       = 5

SPEEDSETTING      = 20

LIVES             = 3

WINNINGPERCENTAGE = 75

# ----------------------------------------------------------

COLORS = {"black"   : (0, 0, 0),
          "blue"    : (0, 0, 197),
          "magenta" : (192, 0, 192),
          "red"     : (192, 0, 0),
          "green"   : (0, 192, 0),
          "cyan"    : (0, 192, 192),
          "yellow"  : (189, 190, 0),
          "white"   : (189, 190, 197),
          "gray"   :  (127, 127, 127),
          "transparent" : (0, 0, 0, 0) }

c = ("black", "blue", "red", "magenta", "green", "cyan", "yellow", "white")
COLORNRS = {}
for i in c:
    COLORNRS[i] = c.index(i)

class Environment:

    def __init__(self):
        self.s_x = 160
        self.s_y = 100

class Paper:

    def __init__(self, env):
        self.env = env
        self.image = pygame.Surface((self.env.s_x * SCALEFACTOR, self.env.s_y * SCALEFACTOR))
        self.image = self.image.convert_alpha()
        self.rect    = self.image.get_rect()
        self.rect.topleft = (0, 0)
        self.image.fill(COLORS["black"])

    def drawLine(self, line):
        self.image.blit(line.image, line.rect)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Playfield:

    def __init__(self, env):
        self.env = env
        self.initPlayfield()

    def initPlayfield(self):
        self.filled = 0
        self.playfield = []
        for y in range(self.env.s_y):
            row = []
            for x in range(self.env.s_x):
                if y == 0 or y == self.env.s_y - 1:
                    row.append(COLORNRS["white"])
                else:
                    if x == 0 or x == self.env.s_x - 1:
                        row.append(COLORNRS["white"])
                    else:
                        row.append(COLORNRS["black"])
            self.playfield.append(row)

    def fillArea(self, opponentposition):
        """ To fill the wanted area, we use a flood-fill on the position,
            where the opponent is, then "inverse" the playfield, that is, fill
            the opposite areas. Following a suggestion at forum64.de. """ 
        self.floodfillPlayfield(opponentposition, "black", "magenta")
        self.inversePlayfield()

    def floodfillPlayfield(self, coordinates, fromcolorname, tocolorname):
        tofill = [coordinates]
        while len(tofill) > 0:
            (x, y) = tofill.pop()
            if self.playfield[y][x] != COLORNRS[fromcolorname]:
                continue
            self.playfield[y][x] = COLORNRS[tocolorname]
            tofill.append( (x - 1, y) )
            tofill.append( (x + 1, y) )
            tofill.append( (x, y - 1) )
            tofill.append( (x, y + 1) )

    def inversePlayfield(self):

        filled = 0
        c = (COLORNRS["blue"], COLORNRS["white"])

        # Can't use a dictionary here, because the order is of importance:
        changes = (("black", "blue"),
                   ("yellow", "white"),
                   ("magenta", "black"))
        for y in range(self.env.s_y):
            for x in range(self.env.s_x):
                for i in changes:
                    if self.playfield[y][x] == COLORNRS[i[0]]:
                        self.playfield[y][x] = COLORNRS[i[1]]
                if self.playfield[y][x] in c:
                    filled += 1
        self.filled = int(filled * 100. / (self.env.s_x * self.env.s_y))

    def deleteYellowInPlayfield(self):
        for y in range(self.env.s_y):
            for x in range(self.env.s_x):
                if self.playfield[y][x] == COLORNRS["yellow"]:
                    self.playfield[y][x] = COLORNRS["black"]

    def getFilledPercentage(self):
        return self.filled

    def update(self, paper):
        paper.image.fill(COLORS["black"])
        colornames = ("blue", "white")
        # This is stupid, but it works:
        colors     = {}
        colornrs   = []
        for i in colornames:
            colornrs.append(COLORNRS[i])
            colors[COLORNRS[i]] = COLORS[i]
        rect = pygame.Rect((0, 0), (SCALEFACTOR, SCALEFACTOR))
        for y in range(self.env.s_y):
            for x in range(self.env.s_x):
                if self.playfield[y][x] in colornrs:
                    rect.topleft = (x * SCALEFACTOR, y * SCALEFACTOR)
                    pygame.draw.rect(paper.image, colors[self.playfield[y][x]], rect)


class MySprite(pygame.sprite.Sprite):

    # Base class for what I'm doing with sprites.

    def __init__(self, env, playfield, paper, delaytime):
        pygame.sprite.Sprite.__init__(self)
        self.env       = env
        self.playfield = playfield
        self.paper     = paper
        self.delaytime = delaytime
        self.timer     = pygame.time.get_ticks()

    def createImage(self, ssize_x, ssize_y, colorname):
        self.image     = pygame.Surface((ssize_x * SCALEFACTOR, ssize_y * SCALEFACTOR))
        self.image     = self.image.convert_alpha()
        self.image.fill(COLORS[colorname])
        self.rect      = self.image.get_rect()

    def setPosition(self, spos_x, spos_y):
        self.spos_x = spos_x
        self.spos_y = spos_y

    def setPCPosition(self):
        self.pcpos_x = self.spos_x * SCALEFACTOR
        self.pcpos_y = self.spos_y * SCALEFACTOR

    def getPosition(self):
        return (self.spos_x, self.spos_y)

    def draw(self, screen):
        self.setPCPosition()
        self.rect.topleft = (self.pcpos_x, self.pcpos_y)
        screen.blit(self.image, self.rect)


class Player(MySprite):

    def __init__(self, env, playfield, paper, delaytime):
        MySprite.__init__(self, env, playfield, paper, delaytime)
        self.createImage("red")
        self.line = Line()
        self.line.setColor("white")
        self.initSettings()

    def initSettings(self):
        # self.spos.x can be 0 to (self.env.s_x - 1) :
        self.setPosition(self.env.s_x // 2, self.env.s_y - 1)
        self.setPCPosition()
        self.drawing = False
        self.moved = False
        self.line.setColor("white")

    def setOpponent(self, opponent):
        self.opponent = opponent

    def createImage(self, colorname):
        self.image = pygame.Surface((2 * SCALEFACTOR, 2 * SCALEFACTOR))
        self.image = self.image.convert_alpha()
        self.rect    = self.image.get_rect()
        pygame.draw.rect(self.image, COLORS["transparent"], self.rect)
        center = (self.rect.width // 2, self.rect.height // 2)
        radius = self.rect.width // 2
        pygame.draw.circle(self.image, COLORS[colorname], center, radius)

    def checkInvalidMoves(self, direction):

        # Borders:
        if self.spos_x == 0 and direction == "left":
            return True
        if self.spos_x == self.env.s_x - 1 and direction == "right":
            return True
        if self.spos_y == 0 and direction == "up":
            return True
        if self.spos_y == self.env.s_y - 1 and direction == "down":
            return True

        # Blue and yellow positions:
        targetpos = [self.spos_x, self.spos_y]
        if direction == "left":
            targetpos[0] -= 1
        if direction == "right":
            targetpos[0] += 1
        if direction == "up":
            targetpos[1] -= 1
        if direction == "down":
            targetpos[1] += 1
        if self.playfield.playfield[targetpos[1]][targetpos[0]] in (COLORNRS["blue"], COLORNRS["yellow"]): 
            return True
        return False

    def move(self, direction):

        # Prevents multiple moves (leading to diagonal movement) in one frame:
        if self.moved:
            return

        if self.checkInvalidMoves(direction):
            return

        self.moved = True

        if direction == "left":
            if self.spos_x > 0:
                self.spos_x -= 1

        if direction == "right":
            if self.spos_x < self.env.s_x:
                self.spos_x += 1

        if direction == "up":
            if self.spos_y > 0:
                self.spos_y -= 1

        if direction == "down":
            if self.spos_y < self.env.s_y:
                self.spos_y += 1

    def setPCPosition(self):
        self.pcpos_x = self.spos_x * SCALEFACTOR - 0.25 * self.rect.width
        self.pcpos_y = self.spos_y * SCALEFACTOR - 0.25 * self.rect.height

    def drawToPaper(self):
        self.playfield.playfield[self.spos_y][self.spos_x] = COLORNRS[self.line.colorname]
        self.line.setPosition(self.spos_x, self.spos_y)
        self.paper.drawLine(self.line)


class Line:

    def __init__(self):
        self.image = pygame.Surface((SCALEFACTOR, SCALEFACTOR))
        self.image = self.image.convert_alpha()
        self.rect  = self.image.get_rect()
        self.rect.topleft = (0, 0)

    def setColor(self, colorname):
        self.colorname = colorname
        self.image.fill(COLORS[self.colorname])

    def setPosition(self, spos_x, spos_y):
        self.rect.topleft = (spos_x * SCALEFACTOR, spos_y * SCALEFACTOR)


class Opponent(MySprite):

    def __init__(self, env, playfield, paper, delaytime):
        MySprite.__init__(self, env, playfield, paper, delaytime)
        self.ssize_x = 32
        self.ssize_y = 16
        self.createImage(self.ssize_x, self.ssize_y, "green")
        self.initSettings()
        self.direction = ["left", "down"]

    def initSettings(self):
        self.setPosition(self.env.s_x * 3 // 4, self.env.s_y // 4)
        self.setPCPosition()

    def setPlayer(self, player):
        self.player = player

    def getDirection(self):
        """
        direction = ["", ""]
        playerspos = self.player.getPosition()
        if self.spos_x < playerspos[0]:
            direction[0] = "right"
        if self.spos_x > playerspos[0]:
            direction[0] = "left"
        if self.spos_y < playerspos[1]:
            direction[1] = "down"
        if self.spos_y > playerspos[1]:
            direction[1] = "up"
        # Borders:
        if self.spos_x == 0 and direction[0] == "left":
            direction[0] = ""
        if self.spos_x + self.ssize_x == self.env.s_x and direction[0] == "right":
            direction[0] = ""
        if self.spos_y == 0 and direction[1] == "up":
            direction[1] = ""
        if self.spos_y + self.ssize_y == self.env.s_y and direction[1] == "down":
            direction[1] = ""
        """
        pass

    def checkDirection(self):

        # Borders:
        if self.spos_x <= 1 and self.direction[0] == "left":
            self.spos_x = 1
            self.boing(self.direction[0])
            return
        if self.spos_x + self.ssize_x >= self.env.s_x -1 and self.direction[0] == "right":
            self.spos_x = self.env.s_x - self.ssize_x - 1
            self.boing(self.direction[0])
            return
        if self.spos_y <= 1 and self.direction[1] == "up":
            self.spos_y = 1
            self.boing(self.direction[1])
            return
        if self.spos_y + self.ssize_y == self.env.s_y and self.direction[1] == "down":
            self.spos_y = self.env.s_y - self.ssize_y - 1
            self.boing(self.direction[1])
            return

        # Collision on top:
        for x in range(self.spos_x - 1, self.spos_x + self.ssize_x + 1):
            if self.playfield.playfield[self.spos_y - 1][x] == COLORNRS["white"]:
                self.boing("up")
                return


        # Collision to left:
        for y in range(self.spos_y - 1, self.spos_y + self.ssize_y + 1):
            if self.playfield.playfield[y][self.spos_x - 1] == COLORNRS["white"]:
                self.boing("left")
                return

        # Collision to right:
        for y in range(self.spos_y - 1, self.spos_y + self.ssize_y + 1):
            if self.playfield.playfield[y][self.spos_x + self.ssize_x + 1] == COLORNRS["white"]:
                self.boing("right")
                return


        # Collision at bottom:
        for x in range(self.spos_x - 1, self.spos_x + self.ssize_x + 1):
            if self.playfield.playfield[self.spos_y + self.ssize_y + 1][x] == COLORNRS["white"]:
                self.boing("down")
                return

    def boing(self, d):
        if d == "left":
            self.direction[0] = "right"
            return
        if d == "right":
            self.direction[0] = "left"
            return
        if d == "up":
            self.direction[1] = "down"
            return
        if d == "down":
            self.direction[1] = "up"
            return

    def checkField(self, fieldpos, playerpos):
        for y in range(fieldpos[1], fieldpos[1] + self.ssize_y):
            for x in range(fieldpos[0], fieldpos[0] + self.ssize_x):
                if x == playerpos[0] and y == playerpos[1]:
                    return "player"
                if self.playfield.playfield[y][x] != COLORNRS["black"]:
                    for i in COLORNRS.keys():
                        if COLORNRS[i] == self.playfield.playfield[y][x]:
                            return i
        return None

    def findNewPosition(self, playerpos):
        for y in range(1, self.env.s_y, self.ssize_y):
            for x in range(1, self.env.s_x, self.ssize_x):
                if self.checkField((x, y), playerpos) == None:
                    self.spos_x = x
                    self.spos_y = y

    def move(self, currenttime):

        if currenttime - self.timer <= self.delaytime:
            return

        # self.direction =  self.getDirection()

        self.checkDirection()

        if self.direction[0] == "left":
            self.spos_x -= 1
        if self.direction[0] == "right":
            self.spos_x += 1
        if self.direction[1] == "up":
            self.spos_y -= 1
        if self.direction[1] == "down":
            self.spos_y += 1

        self.timer = currenttime


class SideRunner(MySprite):

    def __init__(self, env, playfield, paper, delaytime):
        MySprite.__init__(self, env, playfield, paper, delaytime)
        self.createImage(2, 2, "magenta")
        self.linecolors = (COLORNRS["white"], COLORNRS["yellow"])

    def moveTo(self, side, direction):
        self.direction = direction
        if side == "left":
            self.setPosition(0, self.env.s_y // 2)
        if side == "right":
            self.setPosition(self.env.s_x - 1, self.env.s_y // 2)
        if side == "up":
            self.setPosition(self.env.s_x // 2, 0)
        if side == "down":
            self.setPosition(self.env.s_x // 2, self.env.s_y - 1)
        self.setPCPosition()

    def getDirection(self):
        d = []
        if self.spos_x > 0 and self.playfield.playfield[self.spos_y][self.spos_x - 1] in self.linecolors and self.direction != "right":
            d.append("left")
        if self.spos_x < self.env.s_x - 1 and self.playfield.playfield[self.spos_y][self.spos_x + 1] in self.linecolors and self.direction != "left":
            d.append("right")
        if self.spos_y > 0 and self.playfield.playfield[self.spos_y - 1][self.spos_x] in self.linecolors and self.direction != "down":
            d.append("up")
        if self.spos_y < self.env.s_y - 1 and self.playfield.playfield[self.spos_y + 1][self.spos_x] in self.linecolors and self.direction != "up":
            d.append("down")
        lend = len(d)
        if lend == 0:
            return "stop"
        if lend == 1:
            return d[0]
        return d[random.randrange(lend)]

    def move(self, currenttime):

        if currenttime - self.timer <= self.delaytime:
            return
        self.direction = self.getDirection()
        if self.direction == "stop":
            return
        if self.direction == "left":
            self.spos_x -= 1
        if self.direction == "right":
            self.spos_x += 1
        if self.direction == "up":
            self.spos_y -= 1
        if self.direction == "down":
            self.spos_y += 1

        self.timer = currenttime


class SideRunnersGroup(pygame.sprite.Group):

    def __init__(self, *args):
        pygame.sprite.Group.__init__(self, *args)

    def initPositions(self):
        a = (("up", "left"), ("up", "right"), ("left", "down"), ("right", "down"))
        n = 0
        for s in self.sprites():
            s.moveTo(a[n][0], a[n][1])
            n += 1

    def move(self, currenttime):
        for s in self.sprites():
            s.move(currenttime)

    def checkPlayerCollision(self, playerpos):
        for s in self.sprites():
            if s.spos_x == playerpos[0] and s.spos_y == playerpos[1]:
                return True
        return False


class Text(pygame.sprite.Sprite):

    def __init__(self, strings, colorname, sposition, fontname, fontsize):
        pygame.sprite.Sprite.__init__(self)
        self.strings = strings
        self.sposition = sposition
        self.color  = COLORS[colorname]
        self.font = pygame.font.SysFont(fontname, fontsize)
        self.setText(self.strings)

    def setText(self, strings):
        self.strings = strings
        s = ""
        for i in range(len(self.strings)):
            s += self.strings[i]
            if i != len(self.strings) - 1:
                s += "\n"
        self.image = self.font.render(s, False, self.color)
        self.image = self.image.convert_alpha()
        self.rect  = self.image.get_rect()
        self.setPosition(self.sposition[0], self.sposition[1])

    def setPosition(self, spos_x, spos_y):
        self.rect.topleft = (spos_x * SCALEFACTOR, spos_y * SCALEFACTOR)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class SpriteGroup(pygame.sprite.Group):

    def __init__(self, *args):
        pygame.sprite.Group.__init__(self, *args)

    def draw(self, screen):
        for s in self.sprites():
            s.draw(screen)

class LevelSpritesGroup(SpriteGroup):

    def __init__(self, *args):
        SpriteGroup.__init__(self, *args)

class GameOverGroup(SpriteGroup):

    def __init__(self, *args):
        SpriteGroup.__init__(self, *args)

class GameWonGroup(SpriteGroup):

    def __init__(self, *args):
        SpriteGroup.__init__(self, *args)


class GameState:

    def __init__(self):
        pass

    def initSettings(self):
        self.state = "level_1"
        self.lives = 3


class Main:

    def __init__(self):
        self.env = Environment()
        pygame.init()
        os.environ['SDL_VIDEO_WINDOW_POS'] = "100, 20"
        self.screen = pygame.display.set_mode((self.env.s_x * SCALEFACTOR, self.env.s_y * SCALEFACTOR))
        pygame.display.set_caption("Pyqueex")
        self.gamestate = GameState()
        self.gamestate.initSettings()
        self.initSprites()
        self.clock   = pygame.time.Clock()
        self.running = True

        while self.running:
            self.clock.tick(50)
            self.timer = pygame.time.get_ticks()

            if self.gamestate.state == "level_1":
                if self.processEvents() == "quit":
                    break
                self.checkPercentage()
                self.opponent.move(currenttime = self.timer)
                self.siderunnersgroup.move(currenttime = self.timer)
                self.checkPlayer()
                self.checkCollisions()
                self.player.drawToPaper()
                self.screen.fill(COLORS["black"])
                self.paper.draw(self.screen)
                self.levelsprites.draw(self.screen)
                pygame.display.flip()
                continue

            if self.gamestate.state == "gameover":
                r = self.checkForKey()
                if r == "quit":
                    break
                if r == "pressed":
                    self.initLevel()
                self.screen.fill(COLORS["black"])
                self.gameovergroup.draw(self.screen)
                pygame.display.flip()
                continue

            if self.gamestate.state == "won":
                r = self.checkForKey()
                if r == "quit":
                    break
                if r == "pressed":
                    self.initLevel()
                self.screen.fill(COLORS["black"])
                self.gamewongroup.draw(self.screen)
                pygame.display.flip()
                continue

        # Main loop has finished
        pygame.quit()

    def initLevel(self):
        self.playfield.initPlayfield()
        self.playfield.update(self.paper)
        self.player.initSettings()
        self.opponent.initSettings()
        self.siderunnersgroup.initPositions()
        self.gamestate.initSettings()
        self.livestext.setText(("Lives: " + str(self.gamestate.lives),))
        self.percentage.setText((str(self.playfield.getFilledPercentage()) + "%",))

    def initSprites(self):
        self.paper = Paper(self.env)
        self.playfield = Playfield(self.env)
        self.playfield.update(self.paper)
        self.player = Player(self.env, self.playfield, self.paper, SPEEDSETTING)
        self.opponent = Opponent(self.env, self.playfield, self.paper, SPEEDSETTING)
        self.siderunners = []
        self.siderunnersgroup = SideRunnersGroup()
        for i in range(4):
            self.siderunners.append(SideRunner(self.env, self.playfield, self.paper, SPEEDSETTING))
        for s in self.siderunners:
            self.siderunnersgroup.add(s)
        self.siderunnersgroup.initPositions()
        self.player.setOpponent(self.opponent)
        self.opponent.setPlayer(self.player)
        self.percentage = Text(("0%",), "white", (self.env.s_x * 6 // 7, self.env.s_y // 20), "Arial", 50)
        self.livestext = Text(("Lives: " + str(self.gamestate.lives),), "white", (self.env.s_x // 15, self.env.s_y // 13), "Arial", 30)
        self.levelsprites = LevelSpritesGroup(self.player, self.opponent, self.percentage, self.livestext)
        self.levelsprites.add(self.siderunnersgroup)
        self.gameovertext = Text(("Game Over",), "white", (self.env.s_x // 4, self.env.s_y // 4), "Arial", 30)
        self.gamewontext = Text(("Level Completed!",), "cyan", (self.env.s_x // 4, self.env.s_y // 4), "Arial", 30)
        self.presstext = Text(("Press any key to play again",), "magenta", (self.env.s_x // 4, self.env.s_y // 2), "Arial", 20)
        self.gameovergroup = GameOverGroup(self.gameovertext, self.presstext)
        self.gamewongroup = GameWonGroup(self.gamewontext, self.presstext)

    def checkPlayer(self):
        # When player enters dark area, switch on line drawing:
        locationcolornr = self.playfield.playfield[self.player.spos_y][self.player.spos_x]
        if locationcolornr == COLORNRS["black"] and not self.player.drawing:
            self.player.drawing = True
            self.player.line.setColor("yellow")

        # When player hits white line while drawing his line, start area-filling:
        if self.player.drawing == True and locationcolornr == COLORNRS["white"]:
            self.playfield.fillArea(self.opponent.getPosition())
            self.playfield.update(self.paper)
            self.player.drawing = False
            self.player.line.setColor("white")
            self.percentage.setText((str(self.playfield.getFilledPercentage()) + "%",))

    def checkPercentage(self):
        if self.playfield.getFilledPercentage() >= WINNINGPERCENTAGE:
            self.gamestate.state = "won"

    def checkCollisions(self):
        hit = False
        res = self.opponent.checkField((self.opponent.spos_x, self.opponent.spos_y), (self.player.spos_x, self.player.spos_y))
        if res in ("player", "yellow"):
            hit = True
        if self.siderunnersgroup.checkPlayerCollision(self.player.getPosition()):
            hit = True
        if hit: 
            self.player.initSettings()
            self.playfield.deleteYellowInPlayfield()
            # Also clears yellow line:
            self.playfield.update(self.paper)
            self.gamestate.lives -= 1
            self.siderunnersgroup.initPositions()
            self.livestext.setText(("Lives: " + str(self.gamestate.lives),))
            if self.gamestate.lives == 0:
                self.gamestate.state = "gameover"

        if res in ("blue", "white"):
            self.opponent.findNewPosition((self.player.spos_x, self.player.spos_y))

    def processEvents(self):
        pygame.event.pump()
        self.player.moved = False
        self.pressed = pygame.key.get_pressed()
        if self.pressed[K_LEFT]:
            self.player.move("left")
        if self.pressed[K_RIGHT]:
            self.player.move("right")
        if self.pressed[K_UP]:
            self.player.move("up")
        if self.pressed[K_DOWN]:
            self.player.move("down")
        if self.pressed[K_q]:
            pygame.quit()
            self.running = False
            return "quit"

    def checkForKey(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.running = False
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    self.running = False
                    return "quit"
                elif event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                    return "direction"
                else:
                    return "pressed"

Main()
