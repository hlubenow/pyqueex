#!/usr/bin/python3
# coding: utf-8

import pygame
from inputhandler import *
from config import *

class Playfield:

    def __init__(self):
        self.initPlayfield()

    def initPlayfield(self):
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
        for y in range(SCREENSIZE_Y):
            for x in range(SCREENSIZE_X):
                for i in changes:
                    if self.playfield[y][x] == COLORNRS[i[0]]:
                        self.playfield[y][x] = COLORNRS[i[1]]
                if self.playfield[y][x] in c:
                    filled += 1
        self.filled = int(filled * 100. / (SCREENSIZE_X * SCREENSIZE_Y))

    def deleteYellowInPlayfield(self):
        for y in range(SCREENSIZE_Y):
            for x in range(SCREENSIZE_X):
                if self.playfield[y][x] == COLORNRS["yellow"]:
                    self.playfield[y][x] = COLORNRS["black"]


class MySprite(pygame.sprite.Sprite):

    def __init__(self, game):
        self.game   = game
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
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
        self.game      = game
        self.playfield = playfield
        MySprite.__init__(self, game)
        self.createImage("red")
        self.collisioncolornrs = []
        for i in ("yellow", "blue"):
            self.collisioncolornrs.append(COLORNRS[i])
        self.ih = InputHandler(False)
        self.line = Line()
        self.initSettings()

    def initSettings(self):
        # self.spos.x can be 0 to (SCREENSIZE_X - 1) :
        self.spos_x = SCREENSIZE_X // 2
        self.spos_y = SCREENSIZE_Y - 1
        self.setPosition()
        self.drawing = False
        self.line.setColor("white")

    def setOpponent(self, opponent):
        self.opponent = opponent

    def createImage(self, colorname):
        self.image = pygame.Surface((2 * SCALEFACTOR, 2 * SCALEFACTOR))
        self.image = self.image.convert()
        self.rect  = self.image.get_rect()
        center = (self.rect.width // 2, self.rect.height // 2)
        radius = self.rect.width // 2
        self.image.fill(COLORS["black"])
        pygame.draw.circle(self.image, COLORS[colorname], center, radius)
        self.image.set_colorkey(COLORS["black"])

    def update(self):
        self.walldetected = False
        self.getNewPos()
        self.collisions_playfield()
        if self.walldetected:
            return
        self.checkPlayfield()
        self.drawToPlayfield()
        self.move()

    def getNewPos(self):
        action = self.ih.getKeyboardAndJoystickAction()
        if action["quit"]:
            self.game.running = False
            return
        self.newpos = [self.spos_x, self.spos_y]
        change = self.getChange(PLAYERSPEED)
        if action["left"]:
            self.newpos[0] -= change
            return
        if action["right"]:
            self.newpos[0] += change
            return
        if action["up"]:
            self.newpos[1] -= change
            return
        if action["down"]:
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

    def checkPlayfield(self):

        # When player enters dark area, switch on line drawing:
        locationcolornr = self.playfield.playfield[self.spos_y][self.spos_x]
        if locationcolornr == COLORNRS["black"] and not self.drawing:
            self.drawing = True
            self.line.setColor("yellow")

        # When player hits white line while drawing his line, start area-filling:
        if self.drawing and locationcolornr == COLORNRS["white"]:
            self.playfield.fillArea(self.opponent.getPosition())
            self.drawing = False
            self.line.setColor("white")
            self.game.playfieldsprite.updatePlayfieldSprite()
            # self.percentage.setText((str(self.playfield.getFilledPercentage()) + "%",))
 
    def drawToPlayfield(self):
        self.line.setPosition(self.spos_x, self.spos_y)
        self.playfield.insertIntoPlayfield(self.line)
        self.game.playfieldsprite.drawLine(self.line)


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
        colornames = ("blue", "white", "yellow")
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


class Opponent(MySprite):

    def __init__(self, game, playfield, player):
        MySprite.__init__(self, game)
        self.playfield = playfield 
        self.player    = player
        self.ih = InputHandler(True)
        self.direction = ["right", "up"]
        # self.direction = ["left", "up"]
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
        self.walldetected = False
        self.collision_playfield()
        self.collision_player()
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
                    # print("left")
                    self.walldetected = True
                    self.boing("left")
                    return

        if self.direction[0] == "right":
            for y in range(OPPONENTSIZE_Y):
                if self.playfield.playfield[self.spos_y + y][self.spos_x + OPPONENTSIZE_X] in self.walls:
                    # print("right")
                    self.walldetected = True
                    self.boing("right")
                    return

        if self.direction[1] == "up":
            for x in range(OPPONENTSIZE_X):
                if self.playfield.playfield[self.spos_y - 1][self.spos_x + x] in self.walls:
                    # print("top")
                    self.walldetected = True
                    self.boing("up")
                    return

        if self.direction[1] == "down":
            for x in range(OPPONENTSIZE_X):
                if self.playfield.playfield[self.spos_y + OPPONENTSIZE_Y][self.spos_x + x] in self.walls:
                    # print("bottom")
                    self.walldetected = True
                    self.boing("down")
                    return

    def boing(self, tochange):
        if self.direction[0] == tochange:
            self.direction[0] = self.boings[tochange]
        if self.direction[1] == tochange:
            self.direction[1] = self.boings[tochange]

    def collision_player(self):
        for y in range(OPPONENTSIZE_Y):
            for x in range(OPPONENTSIZE_X):
                # Collision with Player itself:
                if self.spos_x + x == self.player.spos_x and self.spos_y + y == self.player.spos_y:
                    self.game.playerdied()
                # Collision with Player's yellow line:
                if self.playfield.playfield[self.spos_y + y][self.spos_x + x] == COLORNRS["yellow"]:
                    self.game.playerdied()
 
    def createImage(self):
        self.image     = pygame.Surface((OPPONENTSIZE_X * SCALEFACTOR, OPPONENTSIZE_Y * SCALEFACTOR))
        self.image     = self.image.convert()
        self.image.fill(COLORS[OPPONENTCOLOR])
        self.rect      = self.image.get_rect()


