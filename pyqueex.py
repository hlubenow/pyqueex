#!/usr/bin/python
# coding: utf-8

import pygame
from pygame.locals import *
import os

"""
    Pyqueex 0.3 - Clone of an ancient arcade game - not complete yet.

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

COLORS = {"black"  : (0, 0, 0),
          "blue"   : (0, 0, 200),
          "red"    : (200, 0, 0),
          "green"  : (0, 200, 0),
          "yellow" : (200, 200, 0),
          "white"  : (200, 200, 200),
          "transparent" : (0, 0, 0, 0) }

SCALEFACTOR = 6

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
        self.surface = pygame.Surface((self.env.s_x * SCALEFACTOR, self.env.s_y * SCALEFACTOR))
        self.surface = self.surface.convert_alpha()
        self.rect    = self.surface.get_rect()
        self.rect.topleft = (0, 0)
        self.surface.fill(COLORS["black"])

    def drawLine(self, line):
        self.surface.blit(line.surface, line.rect)

    def draw(self, screen):
        screen.blit(self.surface, self.rect)


class Playfield:

    def __init__(self, env):
        self.env = env
        self.setup()

    def setup(self):
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

    def printPlayfield(self):
        for i in self.playfield:
            s = ""
            for u in i:
                s += str(u)
            print s

    def fillArea(self, opponentposition):
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
        # Can't use a dictionary here, because the order is of importance:
        changes = (("black", "blue"),
                   ("yellow", "white"),
                   ("magenta", "black"))
        for y in range(self.env.s_y):
            for x in range(self.env.s_x):
                for i in changes:
                    if self.playfield[y][x] == COLORNRS[i[0]]:
                        self.playfield[y][x] = COLORNRS[i[1]]

    def update(self, paper):
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
                    pygame.draw.rect(paper.surface, colors[self.playfield[y][x]], rect)


class Player:

    def __init__(self, env, playfield, paper, opponent):
        self.env = env
        self.playfield = playfield
        self.paper = paper
        self.opponent = opponent
        # self.spos.x can be 0 to (self.env.s_x - 1) :
        self.spos_x = self.env.s_x // 2
        self.spos_y = self.env.s_y - 1
        self.createSurface()
        self.getPCPosition()
        self.line = Line()
        self.line.setColor("white")
        self.drawing = False
        self.moved = False
        self.collided = False

    def createSurface(self):
        self.surface = pygame.Surface((2 * SCALEFACTOR, 2 * SCALEFACTOR))
        self.surface = self.surface.convert_alpha()
        self.rect    = self.surface.get_rect()
        pygame.draw.rect(self.surface, COLORS["transparent"], self.rect)
        center = (self.rect.width // 2, self.rect.height // 2)
        radius = self.rect.width // 2
        pygame.draw.circle(self.surface, COLORS["red"], center, radius)

    def getPCPosition(self):
        self.pcpos_x = self.spos_x * SCALEFACTOR - 0.25 * self.rect.width
        self.pcpos_y = self.spos_y * SCALEFACTOR - 0.25 * self.rect.height

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

    def checkPosition(self):
        self.locationcolornr = self.playfield.playfield[self.spos_y][self.spos_x]
        # print self.locationcolornr
        if self.locationcolornr == COLORNRS["black"] and not self.drawing:
            self.drawing = True
            self.line.setColor("yellow")

        if self.drawing == True and self.locationcolornr == COLORNRS["white"]:
            self.playfield.fillArea(self.opponent.getPosition())
            self.playfield.update(self.paper)
            self.drawing = False
            self.line.setColor("white")

    def move(self, direction):

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

    def showPosition(self):
        print self.spos_x, self.spos_y

    def drawToPaper(self):
        self.playfield.playfield[self.spos_y][self.spos_x] = COLORNRS[self.line.colorname]
        self.line.setPosition(self.spos_x, self.spos_y)
        self.paper.drawLine(self.line)

    def draw(self, screen):
        self.getPCPosition()
        self.rect.topleft = (self.pcpos_x, self.pcpos_y)
        screen.blit(self.surface, self.rect)


class Line:

    def __init__(self):
        self.surface = pygame.Surface((SCALEFACTOR, SCALEFACTOR))
        self.surface = self.surface.convert_alpha()
        self.rect    = self.surface.get_rect()
        self.rect.topleft = (0, 0)

    def setColor(self, colorname):
        self.colorname = colorname
        self.surface.fill(COLORS[self.colorname])

    def setPosition(self, spos_x, spos_y):
        self.rect.topleft = (spos_x * SCALEFACTOR, spos_y * SCALEFACTOR)


class Opponent:

    def __init__(self, env, playfield, paper):
        self.env = env
        self.playfield = playfield
        self.paper = paper
        self.spos_x = self.env.s_x * 3 // 4
        self.spos_y = self.env.s_y // 4
        self.createSurface()
        self.getPCPosition()
        self.moved = False

    def createSurface(self):
        self.surface = pygame.Surface((4 * SCALEFACTOR, 4 * SCALEFACTOR))
        self.surface = self.surface.convert_alpha()
        self.rect    = self.surface.get_rect()
        pygame.draw.rect(self.surface, COLORS["green"], self.rect)

    def getPCPosition(self):
        self.pcpos_x = self.spos_x * SCALEFACTOR - 0.25 * self.rect.width
        self.pcpos_y = self.spos_y * SCALEFACTOR - 0.25 * self.rect.height

    def getPosition(self):
        return (self.spos_x, self.spos_y)

    def draw(self, screen):
        self.getPCPosition()
        self.rect.topleft = (self.pcpos_x, self.pcpos_y)
        screen.blit(self.surface, self.rect)


class Main:

    def __init__(self):
        self.env = Environment()
        pygame.init()
        os.environ['SDL_VIDEO_WINDOW_POS'] = "100, 20"
        self.screen = pygame.display.set_mode((self.env.s_x * SCALEFACTOR, self.env.s_y * SCALEFACTOR))
        pygame.display.set_caption("Pyqueex")
        self.clock = pygame.time.Clock()
        self.surface = pygame.Surface((800, 600))
        self.rect    = self.surface.get_rect()
        self.rect.topleft = (0, 0)
        self.paper = Paper(self.env)
        self.playfield = Playfield(self.env)
        self.playfield.update(self.paper)
        self.opponent = Opponent(self.env, self.playfield, self.paper) 
        self.player = Player(self.env, self.playfield, self.paper, self.opponent)
        self.running = True

        while self.running:
            self.clock.tick(60)
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
            if not self.running:
                break
            self.player.checkPosition()
            self.player.drawToPaper()
            self.screen.fill(COLORS["black"])
            self.paper.draw(self.screen)
            self.player.draw(self.screen)
            self.opponent.draw(self.screen)
            pygame.display.flip()

Main()
