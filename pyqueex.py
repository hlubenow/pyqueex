#!/usr/bin/python3
# coding: utf-8

import pygame
import random
import os

"""
    PyQueex 1.1 - Clone of an ancient arcade game.

    Python-script Copyright (C) 2023 hlubenow

    Except font-data (see class "VGAFont").

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

#####################################
# Config:

SCREENSIZE_X      = 160
SCREENSIZE_Y      = 100
BORDER_X          = 10
BORDER_Y          = 5
SCALEFACTOR       = 5

SOUND             = True

WINDOWPOSITION_X  = 185
WINDOWPOSITION_Y  = 30

# Can be 0 (= no joystick), joystick number 1  or number 2:
JOYSTICKNUMBER    = 1

FPS               = 60

WINNINGPERCENTAGE = 80

GETREADYTIME      = 180
COMPLETEDTIME     = 360

PLAYERLIVES       = 3

PLAYERSPEED       = 0.05
OPPONENTSPEED     = 0.03
LINERUNNERSSPEED  = 0.05

OPPONENTSIZE_X    = 28
OPPONENTSIZE_Y    = 13
OPPONENTCOLOR     = "green"

# Up to 8:
LINERUNNERSMAX    = 6

EXTRALIFELEVEL    = 3

COLORS = {"black"         : (0, 0, 0),
          "blue"          : (0, 0, 197),
          "magenta"       : (192, 0, 192),
          "red"           : (192, 0, 0),
          "green"         : (0, 192, 0),
          "cyan"          : (0, 192, 192),
          "yellow"        : (189, 190, 0),
          "white"         : (189, 190, 197),
          "grey"          : (127, 127, 127),
          "bright_white"  : (255, 255, 255),
          "bright_yellow" : (255, 255, 0),
          "transparent"   : (0, 0, 0, 0) }

COLORNAMES = ("black", "blue", "red", "magenta", "green", "cyan", "yellow", "white", "grey")
COLORNRS = {}
for i in COLORNAMES:
    COLORNRS[i] = COLORNAMES.index(i)

#####################################
# Playfield:

class Playfield:

    def __init__(self):
        self.initPlayfield()

    def initPlayfield(self):
        self.filled = 0
        # Build empty playfield with a white frame:
        self.playfield = []
        for y in range(SCREENSIZE_Y):
            row = []
            for x in range(SCREENSIZE_X):
                if y == 0 or y == SCREENSIZE_Y - 1:
                    row.append(COLORNRS["white"])
                else:
                    if x == 0 or x == SCREENSIZE_X - 1:
                        row.append(COLORNRS["white"])
                    else:
                        row.append(COLORNRS["black"])
            self.playfield.append(row)

    def insertIntoPlayfield(self, line):
        self.playfield[line.spos_y][line.spos_x] = COLORNRS[line.colorname]

    def fillArea(self, opponentposition):
        """ To fill the wanted area, we use a flood-fill on the position,
            where the opponent is, then "inverse" the playfield, that is, fill
            the opposite areas. Following a suggestion at forum64.de. """
        self.floodfillPlayfield(opponentposition, "black", "grey")
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
                   ("magenta", "white"),
                   ("grey", "black"))
        for y in range(SCREENSIZE_Y):
            for x in range(SCREENSIZE_X):
                for i in changes:
                    if self.playfield[y][x] == COLORNRS[i[0]]:
                        self.playfield[y][x] = COLORNRS[i[1]]
                if self.playfield[y][x] in c:
                    filled += 1
        self.filled = int(filled * 100. / (SCREENSIZE_X * SCREENSIZE_Y))

    def deleteMagentaInPlayfield(self):
        for y in range(SCREENSIZE_Y):
            for x in range(SCREENSIZE_X):
                if self.playfield[y][x] == COLORNRS["magenta"]:
                    self.playfield[y][x] = COLORNRS["black"]

    def getFilledPercentage(self):
        return self.filled


#####################################
# Sprites:

class MySprite(pygame.sprite.Sprite):

    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.game   = game
        self.image  = None
        self.rect   = None
        self.floatcounter = 0

    def getChange(self, speed):
        self.floatcounter += speed * self.game.clocktick
        if self.floatcounter < 1:
            return 0
        if self.floatcounter >= 2:
            self.floatcounter = 0
            return 1
        # Between 1 and 2 by now:
        self.floatcounter -= 1
        return 1

    def setPosition(self):
        self.rect.x = (self.spos_x + BORDER_X) * SCALEFACTOR
        self.rect.y = (self.spos_y + BORDER_Y) * SCALEFACTOR

    def getPosition(self):
        return (self.spos_x, self.spos_y)

class Player(MySprite):

    def __init__(self, game, playfield):
        MySprite.__init__(self, game)
        self.playfield   = playfield
        self.shimmermode = 1
        self.lives       = PLAYERLIVES
        self.colorlist   = list(COLORS["red"])
        self.createImage()
        self.collisioncolornrs = []
        for i in ("magenta", "blue"):
            self.collisioncolornrs.append(COLORNRS[i])
        self.line = Line()
        self.initSettings()

    def initSettings(self):
        self.spos_x = int(SCREENSIZE_X / 2)
        self.spos_y = SCREENSIZE_Y - 1
        self.setPosition()
        self.colorlist = list(COLORS["red"])
        self.shimmermode = 1
        self.drawCircle()
        self.drawing = False
        self.line.setColor("white")

    def setOpponent(self, opponent):
        self.opponent = opponent

    def createImage(self):
        self.image = pygame.Surface((2 * SCALEFACTOR, 2 * SCALEFACTOR))
        self.image = self.image.convert()
        self.rect  = self.image.get_rect()
        self.center = (self.rect.width // 2, self.rect.height // 2)
        self.radius = self.rect.width // 2
        self.drawCircle()

    def update(self):
        if self.game.state == "level":
            self.walldetected = False
            self.getNewPos()
            self.collisions_playfield()
            if self.walldetected:
                return
            if self.collisions_linerunners():
                return
            self.checkPlayfield()
            self.drawToPlayfield()
            self.move()
        if self.game.state in ("playerexplosion", "getready"):
            self.shimmer()

    def drawCircle(self):
        self.image.fill(COLORS["black"])
        pygame.draw.circle(self.image, self.colorlist, self.center, self.radius)
        self.image.set_colorkey(COLORS["black"])

    def setPosition(self):
        self.rect.x = (self.spos_x + BORDER_X) * SCALEFACTOR - 0.25 * self.rect.width
        self.rect.y = (self.spos_y + BORDER_Y) * SCALEFACTOR - 0.25 * self.rect.height

    def shimmer(self):
        step = 4
        if self.shimmermode == 1 and self.colorlist[0] < 255 - step:
            self.colorlist[0] += step
            self.drawCircle()
            return
        if self.shimmermode == 1 and self.colorlist[1] < 255 - step:
            self.colorlist[1] += step
            self.drawCircle()
            return
        if self.shimmermode == 1 and self.colorlist[2] < 255 - step:
            self.colorlist[2] += step
            self.drawCircle()
            return
        self.shimmermode = 0
        step = 2
        if self.shimmermode == 0 and self.colorlist[2] > step:
            self.colorlist[2] -= step
            self.drawCircle()
        if self.shimmermode == 0 and self.colorlist[1] > step:
            self.colorlist[1] -= step
            self.drawCircle()
        if self.shimmermode == 0 and self.colorlist[0] > step:
            self.colorlist[0] -= step
            self.drawCircle()
            return
        self.shimmermode = 1

        if self.game.state == "playerexplosion":
            self.game.setState("getready", "counter")

    def getNewPos(self):
        self.newpos = [self.spos_x, self.spos_y]
        change = self.getChange(PLAYERSPEED)
        if self.game.keyaction["left"]:
            self.newpos[0] -= change
            return
        if self.game.keyaction["right"]:
            self.newpos[0] += change
            return
        if self.game.keyaction["up"]:
            self.newpos[1] -= change
            return
        if self.game.keyaction["down"]:
            self.newpos[1] += change
            return

    def move(self):
        self.spos_x = self.newpos[0]
        self.spos_y = self.newpos[1]
        self.setPosition()

    def collisions_playfield(self):
        if self.newpos[0] < 0 or self.newpos[0] > SCREENSIZE_X - 1:
            self.walldetected = True
            return
        if self.newpos[1] < 0 or self.newpos[1] > SCREENSIZE_Y - 1:
            self.walldetected = True
            return
        if self.playfield.playfield[self.newpos[1]][self.newpos[0]] in self.collisioncolornrs:
            self.walldetected = True

    def collisions_linerunners(self):
        if pygame.sprite.spritecollide(self, self.game.linerunners, False):
            self.game.setState("playerexplosion", "player")
            return True
        return False

    def checkPlayfield(self):

        # When player enters dark area, switch on line drawing:
        locationcolornr = self.playfield.playfield[self.spos_y][self.spos_x]
        if locationcolornr == COLORNRS["black"] and not self.drawing:
            self.drawing = True
            self.line.setColor("magenta")

        # When player hits white line while drawing his line, start area-filling:
        if self.drawing and locationcolornr == COLORNRS["white"]:
            self.game.playSound("fill")
            self.playfield.fillArea(self.opponent.getPosition())
            self.drawing = False
            self.line.setColor("white")
            self.game.playfieldsprite.updatePlayfieldSprite()
            p = self.playfield.getFilledPercentage()
            s = ""
            if p < 10:
                s += " "
            s += str(p) + "%"
            self.game.texts["percentage"].setText(s)
 
    def drawToPlayfield(self):
        self.line.setPosition(self.spos_x, self.spos_y)
        self.playfield.insertIntoPlayfield(self.line)
        self.game.playfieldsprite.drawLine(self.line)

    def onWhiteLine(self):
        if self.playfield.playfield[self.spos_y][self.spos_x] == COLORNRS["white"]:
            return True
        else:
            return False

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Line:

    def __init__(self):
        self.spos_x = 0
        self.spos_y = 0
        self.drawImage()

    def drawImage(self):
        self.image = pygame.Surface((SCALEFACTOR, SCALEFACTOR))
        self.image = self.image.convert()
        self.rect  = self.image.get_rect()
        self.rect.topleft = (0, 0)

    def setColor(self, colorname):
        self.colorname = colorname
        self.image.fill(COLORS[self.colorname])

    def setPosition(self, spos_x, spos_y):
        self.spos_x = spos_x
        self.spos_y = spos_y
        self.rect.topleft = (spos_x * SCALEFACTOR, spos_y * SCALEFACTOR)


class PlayfieldSprite(MySprite):

    def __init__(self, game, playfield):
        MySprite.__init__(self, game)
        self.playfield = playfield 
        self.createImage()
        self.dsrect = pygame.Rect((0, 0), (SCALEFACTOR, SCALEFACTOR))
        self.updatePlayfieldSprite()

    def createImage(self):
        self.image = pygame.Surface((SCREENSIZE_X * SCALEFACTOR, SCREENSIZE_Y * SCALEFACTOR))
        self.image = self.image.convert()
        self.image.fill(COLORS["black"])
        self.rect  = self.image.get_rect()
        self.rect.topleft = (BORDER_X * SCALEFACTOR, BORDER_Y * SCALEFACTOR)

    def updatePlayfieldSprite(self):
        self.image.fill(COLORS["black"])
        colornames = ("blue", "white", "magenta")
        # This is stupid, but it works:
        colors     = {}
        colornrs   = []
        for i in colornames:
            colornrs.append(COLORNRS[i])
            colors[COLORNRS[i]] = COLORS[i]
        for y in range(len(self.playfield.playfield)):
            for x in range(len(self.playfield.playfield[y])):
                if self.playfield.playfield[y][x] in colornrs:
                    self.dsrect.topleft = (x * SCALEFACTOR, y * SCALEFACTOR)
                    pygame.draw.rect(self.image, colors[self.playfield.playfield[y][x]], self.dsrect)

    def drawLine(self, line):
        self.image.blit(line.image, line.rect)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Opponent(MySprite):

    def __init__(self, game, playfield, player):
        MySprite.__init__(self, game)
        self.playfield = playfield 
        self.player    = player
        self.direction = ["right", "up"]
        self.walls = (COLORNRS["white"], COLORNRS["blue"])
        self.walldetected = False
        self.boings = {"left" : "right", "right" : "left",
                       "up"   : "down",  "down"  :  "up"}
        self.createImage()
        self.initSettings()

    def initSettings(self):
        self.spos_x = SCREENSIZE_X * 3 // 4
        self.spos_y = SCREENSIZE_Y // 4
        self.setPosition()

    def update(self):
        if self.game.state == "level":
            self.walldetected = False
            self.collision_player()
            self.collision_playfield()
            if self.walldetected:
                # pygame.time.wait(300)
                return
            self.move()

    def move(self):
        change = self.getChange(OPPONENTSPEED)
        if self.direction[0] == "left":
            self.spos_x -= change
        if self.direction[0] == "right":
            self.spos_x += change
        if self.direction[1] == "up":
            self.spos_y -= change
        if self.direction[1] == "down":
            self.spos_y += change
        self.setPosition()

    def collision_playfield(self):

        if self.direction[0] == "left":
            for y in range(OPPONENTSIZE_Y):
                if self.playfield.playfield[self.spos_y + y][self.spos_x - 1] in self.walls:
                    self.walldetected = True
                    self.boing("left")
                    return

        if self.direction[0] == "right":
            for y in range(OPPONENTSIZE_Y):
                if self.playfield.playfield[self.spos_y + y][self.spos_x + OPPONENTSIZE_X] in self.walls:
                    self.walldetected = True
                    self.boing("right")
                    return

        if self.direction[1] == "up":
            for x in range(OPPONENTSIZE_X):
                if self.playfield.playfield[self.spos_y - 1][self.spos_x + x] in self.walls:
                    self.walldetected = True
                    self.boing("up")
                    return

        if self.direction[1] == "down":
            for x in range(OPPONENTSIZE_X):
                if self.playfield.playfield[self.spos_y + OPPONENTSIZE_Y][self.spos_x + x] in self.walls:
                    self.walldetected = True
                    self.boing("down")
                    return

    def boing(self, tochange):
        if self.direction[0] == tochange:
            self.direction[0] = self.boings[tochange]
        if self.direction[1] == tochange:
            self.direction[1] = self.boings[tochange]
        self.game.playSound("wall")

    def collision_player(self):
        # Collision with Player itself:
        if self.rect.colliderect(self.player.rect):
            # Don't kill the Player, while he's on a white line:
            if not self.player.onWhiteLine():
                self.game.setState("playerexplosion", "opponent")
                return
        # Collision with Player's magenta line.
        # "return", in order not to drain more than one life from the Player:
        for y in range(OPPONENTSIZE_Y):
            for x in range(OPPONENTSIZE_X):
                # Collision with Player's magenta line:
                if self.playfield.playfield[self.spos_y + y][self.spos_x + x] == COLORNRS["magenta"]:
                    self.game.setState("playerexplosion", "opponent")
                    return

    def createImage(self):
        self.image     = pygame.Surface((OPPONENTSIZE_X * SCALEFACTOR, OPPONENTSIZE_Y * SCALEFACTOR))
        self.image     = self.image.convert()
        self.image.fill(COLORS[OPPONENTCOLOR])
        self.rect      = self.image.get_rect()


class LineRunner(MySprite):

    def __init__(self, game, initside, initdirection):
        MySprite.__init__(self, game)
        self.playfield     = self.game.playfield
        self.player        = self.game.player
        self.initside      = initside
        self.initdirection = initdirection
        self.linecolors = (COLORNRS["white"], COLORNRS["magenta"])
        self.createImage()

    def createImage(self):
        self.image = pygame.Surface((3 * SCALEFACTOR, 3 * SCALEFACTOR))
        self.image = self.image.convert()
        self.rect  = self.image.get_rect()
        center = (int(self.rect.width / 2), int(self.rect.height / 2))
        radius = int(self.rect.width / 2)
        self.image.fill(COLORS["black"])
        # pygame.draw.circle(self.image, COLORS["magenta"], center, radius)
        pygame.draw.circle(self.image, COLORS["bright_yellow"], center, radius)
        self.image.set_colorkey(COLORS["black"])

    def initSettings(self):
        self.direction = self.initdirection
        if self.initside == "left":
            self.spos_x = 0
            self.spos_y = int(SCREENSIZE_Y / 2)
        if self.initside == "right":
            self.spos_x = SCREENSIZE_X - 1
            self.spos_y = int(SCREENSIZE_Y / 2)
        if self.initside == "up":
            self.spos_x = int(SCREENSIZE_X / 2)
            self.spos_y = 0
        if self.initside == "down":
            self.spos_x = int(SCREENSIZE_X / 2)
            self.spos_y = SCREENSIZE_Y - 1
        self.setPosition()

    def setPosition(self):
        self.rect.x = (self.spos_x + BORDER_X) * SCALEFACTOR - 0.25 * self.rect.width
        self.rect.y = (self.spos_y + BORDER_Y) * SCALEFACTOR - 0.25 * self.rect.height

    def getDirection(self):
        # Look to every direction and see, what way the siderunner can walk:
        d = []
        if self.spos_x > 0 and self.playfield.playfield[self.spos_y][self.spos_x - 1] in self.linecolors and self.direction != "right":
            d.append("left")
        if self.spos_x < SCREENSIZE_X - 1 and self.playfield.playfield[self.spos_y][self.spos_x + 1] in self.linecolors and self.direction != "left":
            d.append("right")
        if self.spos_y > 0 and self.playfield.playfield[self.spos_y - 1][self.spos_x] in self.linecolors and self.direction != "down":
            d.append("up")
        if self.spos_y < SCREENSIZE_Y - 1 and self.playfield.playfield[self.spos_y + 1][self.spos_x] in self.linecolors and self.direction != "up":
            d.append("down")
        lend = len(d)
        if lend == 0:
            return "stop"
        if lend == 1:
            return d[0]
        return d[random.randrange(lend)]

    def update(self):
        if self.game.state == "level":
            self.move()

    def move(self):
        change = self.getChange(LINERUNNERSSPEED)
        # Don't change the direction in frames, in which the siderunner isn't moving:
        if change == 0:
            return
        self.direction = self.getDirection()
        if self.direction == "stop":
            return
        if self.direction == "left":
            self.spos_x -= change
        if self.direction == "right":
            self.spos_x += change
        if self.direction == "up":
            self.spos_y -= change
        if self.direction == "down":
            self.spos_y += change
        self.setPosition()


#####################################
# Sprite Groups:

class GetReadyGroup(pygame.sprite.Group):

    def __init__(self):
        pygame.sprite.Group.__init__(self)

class LevelGroup(pygame.sprite.Group):

    def __init__(self):
        pygame.sprite.Group.__init__(self)

class PlayerExplosionGroup(pygame.sprite.Group):

    def __init__(self):
        pygame.sprite.Group.__init__(self)

class CompletedGroup(pygame.sprite.Group):

    def __init__(self):
        pygame.sprite.Group.__init__(self)

class LostGroup(pygame.sprite.Group):

    def __init__(self):
        pygame.sprite.Group.__init__(self)

class InfoTextsGroup(pygame.sprite.Group):

    def __init__(self):
        pygame.sprite.Group.__init__(self)


class LineRunnersGroup(pygame.sprite.Group):

    def __init__(self):
        pygame.sprite.Group.__init__(self)
        self.lrdata = []
        a = (("up", "left"), ("up", "right"),
             ("left", "down"), ("right", "down"))
        for i in range(2):
            for u in a:
                self.lrdata.append(u)

    def initPositions(self):
        for s in self.sprites():
            s.initSettings()


#####################################
# Text Class:

class Text(pygame.sprite.Sprite):

    def __init__(self, text, colorname, spos_x, spos_y, scalefactor):
        pygame.sprite.Sprite.__init__(self)
        # self.game      = game
        self.text        = text
        self.colorname   = colorname
        self.scalefactor = scalefactor
        self.fontdata    = VGAFont()
        self.pointrect = pygame.Rect((0, 0), (self.scalefactor, self.scalefactor))
        self.createImage()
        self.initSettings(spos_x, spos_y)

    def setText(self, text):
        self.text = text
        self.drawLetters()

    def createImage(self):
        self.image = pygame.Surface((len(self.text) * 8 * self.scalefactor, 8 * self.scalefactor))
        self.image = self.image.convert()
        self.rect  = self.image.get_rect()
        self.drawLetters()

    def drawLetters(self):
        self.image.fill(COLORS["black"])
        indent = 0
        for s in self.text:
            for y in range(8):
                b = "{0:08b}".format(self.fontdata.vgafont[s][y])
                for x in range(8):
                    if b[x] == "1":
                        self.pointrect.topleft = ((indent + x) * self.scalefactor, y * self.scalefactor)
                        pygame.draw.rect(self.image, COLORS[self.colorname], self.pointrect)
            indent += 8
        self.image.set_colorkey(COLORS["black"])

    def initSettings(self, spos_x, spos_y):
        self.spos_x = spos_x
        self.spos_y = spos_y
        self.rect.x = (self.spos_x + BORDER_X) * SCALEFACTOR
        self.rect.y = (self.spos_y + BORDER_Y) * SCALEFACTOR

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class MultilineText(pygame.sprite.Sprite):

    def __init__(self, textlist, paragraph, colorname, spos_x, spos_y, scalefactor):
        pygame.sprite.Sprite.__init__(self)
        self.textlist = textlist
        self.paragraph = paragraph
        self.colorname   = colorname
        self.scalefactor = scalefactor
        self.fontdata    = VGAFont()
        self.pointrect = pygame.Rect((0, 0), (self.scalefactor, self.scalefactor))
        self.createImage()
        self.initSettings(spos_x, spos_y)

    def initSettings(self, spos_x, spos_y):
        self.spos_x = spos_x
        self.spos_y = spos_y
        self.rect.x = (self.spos_x + BORDER_X) * SCALEFACTOR
        self.rect.y = (self.spos_y + BORDER_Y) * SCALEFACTOR

    def getDimensions(self):
        max = 0
        for i in self.textlist:
            if len(i) > max:
                max = len(i)
        return (max, len(self.textlist))

    def createImage(self):
        dimensions = self.getDimensions()
        self.image = pygame.Surface((dimensions[0] * 8 * self.scalefactor, dimensions[1] * self.scalefactor * (8 + self.paragraph)))
        self.image = self.image.convert()
        self.rect  = self.image.get_rect()
        self.drawStrings()

    def drawStrings(self):
        self.image.fill(COLORS["black"])
        newline = 0
        for t in self.textlist:
            indent  = 0
            for s in t:
                for y in range(8):
                    b = "{0:08b}".format(self.fontdata.vgafont[s][y])
                    for x in range(8):
                        if b[x] == "1":
                            self.pointrect.topleft = ((indent + x) * self.scalefactor, (newline + y) * self.scalefactor)
                            pygame.draw.rect(self.image, COLORS[self.colorname], self.pointrect)
                indent += 8
            newline += self.paragraph
        self.image.set_colorkey(COLORS["black"])


class VGAFont:

    def __init__(self):
        """
        vgafont
    
        Data from: https://github.com/lgblgblgb/xemu/blob/master/xemu/vgafonts.c
        Which has this message:
    
           Taken From the SeaBIOS open source project, HOWEVER SeaBIOS states the followings
           for this file (unmodified comment following):
           ----------------------------------------------------------------------------------
           These fonts come from ftp://ftp.simtel.net/pub/simtelnet/msdos/screen/fntcol16.zip
           The package is (c) by Joseph Gil
           The individual fonts are public domain
           ----------------------------------------------------------------------------------
        This seems to refer to these resources (as of 2023-12-08):
        https://github.com/qemu/seabios/blob/master/vgasrc/vgafonts.c
        https://ftp.sunet.se/mirror/archive/ftp.sunet.se/pub/simtelnet/msdos/screen/fntcol16.zip
        """

        self.vgafont = {" " : (0, 0, 0, 0, 0, 0, 0, 0),
                        "!" : (48, 120, 120, 48, 48, 0, 48, 0),
                        "\"" : (108, 108, 108, 0, 0, 0, 0, 0),
                        "#" : (108, 108, 254, 108, 254, 108, 108, 0),
                        "$" : (48, 124, 192, 120, 12, 248, 48, 0),
                        "%" : (0, 198, 204, 24, 48, 102, 198, 0),
                        "&" : (56, 108, 56, 118, 220, 204, 118, 0),
                        "'" : (96, 96, 192, 0, 0, 0, 0, 0),
                        "(" : (24, 48, 96, 96, 96, 48, 24, 0),
                        ")" : (96, 48, 24, 24, 24, 48, 96, 0),
                        "*" : (0, 102, 60, 255, 60, 102, 0, 0),
                        "+" : (0, 48, 48, 252, 48, 48, 0, 0),
                        "," : (0, 0, 0, 0, 0, 48, 48, 96),
                        "-" : (0, 0, 0, 252, 0, 0, 0, 0),
                        "." : (0, 0, 0, 0, 0, 48, 48, 0),
                        "/" : (6, 12, 24, 48, 96, 192, 128, 0),
                        "0" : (124, 198, 206, 222, 246, 230, 124, 0),
                        "1" : (48, 112, 48, 48, 48, 48, 252, 0),
                        "2" : (120, 204, 12, 56, 96, 204, 252, 0),
                        "3" : (120, 204, 12, 56, 12, 204, 120, 0),
                        "4" : (28, 60, 108, 204, 254, 12, 30, 0),
                        "5" : (252, 192, 248, 12, 12, 204, 120, 0),
                        "6" : (56, 96, 192, 248, 204, 204, 120, 0),
                        "7" : (252, 204, 12, 24, 48, 48, 48, 0),
                        "8" : (120, 204, 204, 120, 204, 204, 120, 0),
                        "9" : (120, 204, 204, 124, 12, 24, 112, 0),
                        ":" : (0, 48, 48, 0, 0, 48, 48, 0),
                        ";" : (0, 48, 48, 0, 0, 48, 48, 96),
                        "<" : (24, 48, 96, 192, 96, 48, 24, 0),
                        "=" : (0, 0, 252, 0, 0, 252, 0, 0),
                        ">" : (96, 48, 24, 12, 24, 48, 96, 0),
                        "?" : (120, 204, 12, 24, 48, 0, 48, 0),
                        "@" : (124, 198, 222, 222, 222, 192, 120, 0),
                        "A" : (48, 120, 204, 204, 252, 204, 204, 0),
                        "B" : (252, 102, 102, 124, 102, 102, 252, 0),
                        "C" : (60, 102, 192, 192, 192, 102, 60, 0),
                        "D" : (248, 108, 102, 102, 102, 108, 248, 0),
                        "E" : (254, 98, 104, 120, 104, 98, 254, 0),
                        "F" : (254, 98, 104, 120, 104, 96, 240, 0),
                        "G" : (60, 102, 192, 192, 206, 102, 62, 0),
                        "H" : (204, 204, 204, 252, 204, 204, 204, 0),
                        "I" : (120, 48, 48, 48, 48, 48, 120, 0),
                        "J" : (30, 12, 12, 12, 204, 204, 120, 0),
                        "K" : (230, 102, 108, 120, 108, 102, 230, 0),
                        "L" : (240, 96, 96, 96, 98, 102, 254, 0),
                        "M" : (198, 238, 254, 254, 214, 198, 198, 0),
                        "N" : (198, 230, 246, 222, 206, 198, 198, 0),
                        "O" : (56, 108, 198, 198, 198, 108, 56, 0),
                        "P" : (252, 102, 102, 124, 96, 96, 240, 0),
                        "Q" : (120, 204, 204, 204, 220, 120, 28, 0),
                        "R" : (252, 102, 102, 124, 108, 102, 230, 0),
                        "S" : (120, 204, 224, 112, 28, 204, 120, 0),
                        "T" : (252, 180, 48, 48, 48, 48, 120, 0),
                        "U" : (204, 204, 204, 204, 204, 204, 252, 0),
                        "V" : (204, 204, 204, 204, 204, 120, 48, 0),
                        "W" : (198, 198, 198, 214, 254, 238, 198, 0),
                        "X" : (198, 198, 108, 56, 56, 108, 198, 0),
                        "Y" : (204, 204, 204, 120, 48, 48, 120, 0),
                        "Z" : (254, 198, 140, 24, 50, 102, 254, 0),
                        "[" : (120, 96, 96, 96, 96, 96, 120, 0),
                        "]" : (120, 24, 24, 24, 24, 24, 120, 0),
                        "a" : (0, 0, 120, 12, 124, 204, 118, 0),
                        "b" : (224, 96, 96, 124, 102, 102, 220, 0),
                        "c" : (0, 0, 120, 204, 192, 204, 120, 0),
                        "d" : (28, 12, 12, 124, 204, 204, 118, 0),
                        "e" : (0, 0, 120, 204, 252, 192, 120, 0),
                        "f" : (56, 108, 96, 240, 96, 96, 240, 0),
                        "g" : (0, 0, 118, 204, 204, 124, 12, 248),
                        "h" : (224, 96, 108, 118, 102, 102, 230, 0),
                        "i" : (48, 0, 112, 48, 48, 48, 120, 0),
                        "j" : (12, 0, 12, 12, 12, 204, 204, 120),
                        "k" : (224, 96, 102, 108, 120, 108, 230, 0),
                        "l" : (112, 48, 48, 48, 48, 48, 120, 0),
                        "m" : (0, 0, 204, 254, 254, 214, 198, 0),
                        "n" : (0, 0, 248, 204, 204, 204, 204, 0),
                        "o" : (0, 0, 120, 204, 204, 204, 120, 0),
                        "p" : (0, 0, 220, 102, 102, 124, 96, 240),
                        "q" : (0, 0, 118, 204, 204, 124, 12, 30),
                        "r" : (0, 0, 220, 118, 102, 96, 240, 0),
                        "s" : (0, 0, 124, 192, 120, 12, 248, 0),
                        "t" : (16, 48, 124, 48, 48, 52, 24, 0),
                        "u" : (0, 0, 204, 204, 204, 204, 118, 0),
                        "v" : (0, 0, 204, 204, 204, 120, 48, 0),
                        "w" : (0, 0, 198, 214, 254, 254, 108, 0),
                        "x" : (0, 0, 198, 108, 56, 108, 198, 0),
                        "y" : (0, 0, 204, 204, 204, 124, 12, 248),
                        "z" : (0, 0, 252, 152, 48, 100, 252, 0)}

#####################################
# InputHandler:

class InputHandler:

    def __init__(self):

        self.data = { pygame.K_LEFT  : "left", pygame.K_RIGHT   : "right",
                      pygame.K_UP    : "up",   pygame.K_DOWN    : "down",
                      pygame.K_LCTRL : "fire", pygame.K_RCTRL   : "fire",
                      pygame.K_q     : "quit", pygame.K_ESCAPE : "quit",
                      pygame.K_RETURN : "return" }

        self.datakeys = self.data.keys()
        self.datavalues = self.data.values()

        self.joystick = {}
        if JOYSTICKNUMBER > 0:
            self.initJoystick()
        self.initKeys()

    def initJoystick(self):
        if pygame.joystick.get_count() == 0:
            print("No joysticks found.")
            return
        self.js = pygame.joystick.Joystick(JOYSTICKNUMBER - 1)
        self.js.init()
        for i in self.datavalues:
            if i == "quit":
                continue
            self.joystick[i] = False

    def initKeys(self):
        self.keypresses = {}
        for i in self.datakeys:
            self.keypresses[i] = False

    def getKeyboardAndJoystickAction(self):
        action = {"left" : False, "right" : False, "up" : False, "down" : False,
                  "fire" : False, "quit" : False, "return" : False}
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                action["quit"] = True
                continue
            if event.type == pygame.KEYDOWN:
                for i in self.keypresses:
                    if event.key == i:
                        self.keypresses[i] = True
            if event.type == pygame.KEYUP:
                for i in self.keypresses:
                    if event.key == i:
                        self.keypresses[i] = False
            if JOYSTICKNUMBER > 0:
                if event.type == pygame.JOYBUTTONDOWN:
                    self.joystick["fire"] = True
                if event.type == pygame.JOYBUTTONUP:
                    self.joystick["fire"] = False
                if event.type == pygame.JOYAXISMOTION:
                    # Joystick pushed:
                    if event.axis == 0 and int(event.value) == -1:
                        self.joystick["left"] = True
                    if event.axis == 0 and int(event.value) == 1:
                        self.joystick["right"] = True
                    if event.axis == 1 and int(event.value) == -1:
                        self.joystick["up"] = True
                    if event.axis == 1 and int(event.value) == 1:
                        self.joystick["down"] = True
                    # Joystick released:
                    if event.axis == 0 and int(event.value) == 0:
                        self.joystick["left"] = False
                        self.joystick["right"] = False
                    if event.axis == 1 and int(event.value) == 0:
                        self.joystick["up"] = False
                        self.joystick["down"] = False

        # Same indentation level as "for event in pygame.event.get()":
        for i in self.datakeys:
            if self.keypresses[i]:
                action[self.data[i]] = True

        if JOYSTICKNUMBER > 0:
            for i in self.datavalues:
                if i == "quit":
                    continue
                if self.joystick[i]:
                    action[i] = True
        return action


#####################################
# Game / Main Class:

class Game:

    def __init__(self):
        os.environ['SDL_VIDEO_WINDOW_POS'] = str(WINDOWPOSITION_X) + ", " + str(WINDOWPOSITION_Y)
        if SOUND:
            pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        self.screen = pygame.display.set_mode((SCREENSIZE_X * SCALEFACTOR + 2 * BORDER_X * SCALEFACTOR, SCREENSIZE_Y * SCALEFACTOR + 2 * BORDER_Y * SCALEFACTOR))
        pygame.display.set_caption("PyQueex")
        self.clock = pygame.time.Clock()
        self.ih = InputHandler()
        self.keyaction = {}
        self.counters = {"getready"  : GETREADYTIME,
                         "completed" : COMPLETEDTIME}
        self.level          = 1
        self.state          = "intro"
        self.extralifeshown = False
        self.leveltwoplayed = 0
        self.playfield = Playfield()
        self.initSprites()
        if SOUND:
            self.initSounds()
        self.running = True
        while self.running:
            self.clocktick = self.clock.tick(FPS)
            self.checkKeys()
            self.screen.fill(COLORS["grey"])
            self.checkGameState()

            self.spritegroups[self.state].update()
            self.spritegroups[self.state].draw(self.screen)

            pygame.display.flip()
        pygame.quit()

    def initSprites(self):
        # Create sprites:
        self.playfieldsprite      = PlayfieldSprite(self, self.playfield)
        self.player               = Player(self, self.playfield)
        self.opponent             = Opponent(self, self.playfield, self.player)
        self.player.setOpponent(self.opponent)
        self.texts                = {}
        self.texts["intro"]       = Text("PyQueex",
                                         "bright_white",
                                         60, 15,
                                         3)
        self.texts["intro_story"] = MultilineText(("The evil green-rectangle-mutant",
                                                   "wants to kill you, his creator!",
                                                   "Try to wall it in, before it gets you,",
                                                   "or you'll be chicken feed!"),
                                                   16,
                                                   "green",
                                                   25, 30,
                                                   2)
        self.texts["intro_return"] = Text("Press \"Return\" to play.",
                                          "bright_white",
                                          40, 60,
                                          2)
        self.texts["intro_author"] = Text("Written by H. Lubenow, (C) 2023, GNU GPL.",
                                          "white",
                                          15, 80,
                                          2)
        self.texts["gr_level"]     = Text("Level 999",
                                          "cyan",
                                          65, 10,
                                          3)
        self.texts["getready"]     = Text("GET READY",
                                          "bright_white",
                                          60, 20,
                                          3)
        self.texts["completed"]    = Text("Level 900 Completed",
                                          "bright_white",
                                          40, 20,
                                          3)
        self.texts["lost"]         = Text("GAME OVER",
                                          "bright_white",
                                          60, 35,
                                          3)
        self.texts["press_return"] = Text("Press \"Return\" to play again.",
                                          "bright_white",
                                          36, 50,
                                          2)
        self.texts["livestext"]    = Text("Lives: ",
                                          "bright_white",
                                          3, 3,
                                          2)
        self.texts["lives"]        = Text(str(self.player.lives),
                                         "bright_white",
                                         self.texts["livestext"].spos_x + 20,
                                         self.texts["livestext"].spos_y,
                                         self.texts["livestext"].scalefactor)
        self.texts["percentage"]   = Text(" 0%",
                                          "bright_white",
                                          SCREENSIZE_X - 12, 3,
                                          2)
        self.texts["extra_life"]   = Text("Extra Life!",
                                          "cyan",
                                          65, 40,
                                          2)
        # Create groups:
        self.spritegroups = {}
        for i in ("intro", "getready", "level", "playerexplosion", "completed", "lost", "infotexts"):
            self.spritegroups[i] = pygame.sprite.Group()
        self.linerunners = LineRunnersGroup()

        # Put sprites in groups:
        self.spritegroups["infotexts"].add(self.texts["livestext"], self.texts["lives"], self.texts["percentage"])
        self.spritegroups["intro"].add(self.playfieldsprite, self.texts["intro"], self.texts["intro_story"], self.texts["intro_return"], self.texts["intro_author"])
        self.spritegroups["getready"].add(self.playfieldsprite, self.player, self.opponent, self.texts["gr_level"], self.texts["getready"], self.spritegroups["infotexts"])
        self.spritegroups["level"].add(self.playfieldsprite, self.player, self.opponent, self.spritegroups["infotexts"])
        self.spritegroups["playerexplosion"].add(self.playfieldsprite, self.player, self.spritegroups["infotexts"])
        self.spritegroups["completed"].add(self.playfieldsprite, self.texts["completed"], self.spritegroups["infotexts"])
        self.spritegroups["lost"].add(self.playfieldsprite, self.texts["lost"],  self.texts["press_return"])

    def initLevel(self):
        self.counters["completed"] = COMPLETEDTIME
        self.counters["getready"]  = GETREADYTIME
        self.playfield.initPlayfield()
        self.playfieldsprite.updatePlayfieldSprite()
        self.texts["gr_level"].setText("Level " + str(self.level))
        self.texts["percentage"].setText(" 0%")
        self.player.initSettings()
        self.opponent.initSettings()
        # Increasing number of Siderunners from level 1 to 4:
        if self.level >= 1 and self.level <= LINERUNNERSMAX:
            self.addLineRunner()
        self.linerunners.initPositions()
        self.state = "getready"

    def initSounds(self):
        self.sounds = {}
        sounddir = os.path.join(os.getcwd(), "sounds")
        soundfilenames = ("start", "wall", "fill", "levelcompleted", "level2", "explosion", "end")
        for i in soundfilenames:
            self.sounds[i] = pygame.mixer.Sound(os.path.join(sounddir, i + ".mp3"))

    def playSound(self, name):
        if not SOUND:
            return
        self.sounds[name].play()

    def addLineRunner(self):
        l = LineRunner(self, self.linerunners.lrdata[self.level - 1][0], self.linerunners.lrdata[self.level - 1][1])
        self.linerunners.add(l)
        self.spritegroups["level"].add(l)
        self.spritegroups["getready"].add(l)
        self.spritegroups["playerexplosion"].add(l)

    def removeLinerunnersFromGroups(self):
        for l in self.linerunners.sprites():
            self.spritegroups["level"].remove(l)
            self.spritegroups["getready"].remove(l)
            self.spritegroups["playerexplosion"].remove(l)
            self.linerunners.remove(l)

    def checkKeys(self):
        self.keyaction = self.ih.getKeyboardAndJoystickAction()
        if self.keyaction["quit"]:
            self.running = False

        # Start the game after the intro-screen:
        if self.state == "intro" and self.keyaction["return"]:
            self.initLevel()
            self.playSound("start")

        # Restart the game after having lost the previous one:
        if self.state == "lost" and self.keyaction["return"]:
            self.level        = 1
            self.player.lives = PLAYERLIVES
            self.texts["lives"].setText(str(self.player.lives))
            self.removeLinerunnersFromGroups()
            self.leveltwoplayed = 0
            self.initLevel()
            self.playSound("start")

    def setState(self, state, caller):
        self.state = state

        # Is called after the Player-"explosion":
        if self.state == "getready":
            self.player.initSettings()
            self.linerunners.initPositions()
            self.playfield.deleteMagentaInPlayfield()
            self.playfieldsprite.updatePlayfieldSprite()

        # Is called by the Player or the Opponent due to collision:
        if self.state == "playerexplosion":
            self.player.lives -= 1
            if self.player.lives > 0:
                self.playSound("explosion")
            # Game lost:
            if self.player.lives == 0:
                self.state = "lost"
                self.linerunners.initPositions()
                self.playfield.initPlayfield()
                self.playfieldsprite.updatePlayfieldSprite()
                self.playSound("end")
                return
            self.linerunners.initPositions()
            self.texts["lives"].setText(str(self.player.lives))
            self.playfield.deleteMagentaInPlayfield()
            self.playfieldsprite.updatePlayfieldSprite()

    def checkGameState(self):

        if self.state == "level":
            # Level completed:
            if self.playfield.getFilledPercentage() >= WINNINGPERCENTAGE:
                self.texts["completed"].setText("Level " + str(self.level) + " Completed")
                self.state = "completed"
                self.playSound("levelcompleted")
                return

        if self.state == "completed":
            self.counters["completed"] -= 1
            if self.counters["completed"] <= 0:
                self.level += 1
                if self.level % EXTRALIFELEVEL == 0:
                    self.player.lives += 1
                    self.texts["lives"].setText(str(self.player.lives))
                    self.spritegroups["getready"].add(self.texts["extra_life"])
                    self.extralifeshown = True
                    self.playSound("start")
                self.initLevel()
                return

        # Happens either before the level starts, or after the Player-"explosion":
        if self.state == "getready":
            self.counters["getready"] -= 1
            # Play "Level Two" once at start of, well, level two:
            if self.level == 2 and self.counters["getready"] == int(GETREADYTIME * 2 / 3):
                if self.leveltwoplayed == 0:
                    self.playSound("level2")
                    self.leveltwoplayed += 1
                elif self.leveltwoplayed == 1:
                    if random.randrange(10) < 3:
                        self.playSound("level2")
                        self.leveltwoplayed += 1

            if self.counters["getready"] <= 0:
                self.state = "level"
                self.player.initSettings()
                self.texts["lives"].setText(str(self.player.lives))
                if self.extralifeshown:
                    self.spritegroups["getready"].remove(self.texts["extra_life"])
                    self.extralifeshown = False
                self.counters["getready"] = GETREADYTIME

Game()
