#!/usr/bin/python
# coding: utf-8

import pygame
from pygame.locals import *
import os

# Pyqueex 0.1
# License: GNU GPL 3.

BLACK = (0, 0, 0)
RED   = (200, 0, 0)
WHITE = (200, 200, 200)
TRANSPARENT = (0, 0, 0, 0)

SCALEFACTOR = 6

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
        self.surface.fill(BLACK)
        self.line = Line()

    def drawLine(self, spos_x, spos_y):
        self.line.setPosition(spos_x, spos_y)
        self.surface.blit(self.line.surface, self.line.rect)

    def draw(self, screen):
        screen.blit(self.surface, self.rect)

class Line:

    def __init__(self):
        self.surface = pygame.Surface((SCALEFACTOR, SCALEFACTOR))
        self.surface = self.surface.convert_alpha()
        self.rect    = self.surface.get_rect()
        self.rect.topleft = (0, 0)
        pygame.draw.rect(self.surface, WHITE, self.rect)

    def setPosition(self, spos_x, spos_y):
        self.rect.topleft = (spos_x * SCALEFACTOR, spos_y * SCALEFACTOR)

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
                    row.append(1)
                else:
                    if x == 0 or x == self.env.s_x - 1:
                        row.append(1)
                    else:
                        row.append(0)
            self.playfield.append(row)

    def update(self, paper):
        rect = pygame.Rect((0, 0), (SCALEFACTOR, SCALEFACTOR))
        for y in range(self.env.s_y):
            for x in range(self.env.s_x):
                if self.playfield[y][x] == 1:
                    rect.topleft = (x * SCALEFACTOR, y * SCALEFACTOR)
                    pygame.draw.rect(paper.surface, WHITE, rect)


class Player:

    def __init__(self, env, playfield, paper):
        self.env = env
        self.playfield = playfield
        self.paper = paper
        self.spos_x = self.env.s_x // 2
        self.spos_y = self.env.s_y // 2
        self.createSurface()
        self.getPCPosition()
        self.moved = False

    def createSurface(self):
        self.surface = pygame.Surface((2 * SCALEFACTOR, 2 * SCALEFACTOR))
        self.surface = self.surface.convert_alpha()
        self.rect    = self.surface.get_rect()
        pygame.draw.rect(self.surface, TRANSPARENT, self.rect)
        center = (self.rect.width // 2, self.rect.height // 2)
        radius = self.rect.width // 2
        pygame.draw.circle(self.surface, RED, center, radius)

    def getPCPosition(self):
        self.pcpos_x = self.spos_x * SCALEFACTOR - 0.25 * self.rect.width
        self.pcpos_y = self.spos_y * SCALEFACTOR - 0.25 * self.rect.height

    def checkCollision(self, direction):
        targetpos = [self.spos_x, self.spos_y]
        if direction == "left":
            targetpos[0] -= 1
        if direction == "right":
            targetpos[0] += 1
        if direction == "up":
            targetpos[1] -= 1
        if direction == "down":
            targetpos[1] += 1
        if self.playfield.playfield[targetpos[1]][targetpos[0]] == 1:
            return True
        return False

    def move(self, direction):
        if self.moved:
            return

        if self.checkCollision(direction):
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
        self.playfield.playfield[self.spos_y][self.spos_x] = 1
        self.paper.drawLine(self.spos_x, self.spos_y)

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
        self.player = Player(self.env, self.playfield, self.paper)
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
            if self.running:
                self.screen.fill(BLACK)
                # self.player.showPosition()
                # self.playfield.update(self.paper)
                self.player.drawToPaper()
                self.paper.draw(self.screen)
                self.player.draw(self.screen)
                pygame.display.flip()

Main()
