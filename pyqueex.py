#!/usr/bin/python3
# coding: utf-8

import os
from sprites import *
from config import *

"""
    Pyqueex 0.7 - Clone of an ancient arcade game in Pygame - not complete yet. 

    Copyright (C) 2023 Hauke Lubenow

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



class Game:

    def __init__(self):
        os.environ['SDL_VIDEO_WINDOW_POS'] = str(WINDOWPOSITION_X) + ", " + str(WINDOWPOSITION_Y)
        pygame.init()
        self.screen = pygame.display.set_mode((SCREENSIZE_X * SCALEFACTOR + 2 * BORDER_X * SCALEFACTOR, SCREENSIZE_Y * SCALEFACTOR + 2 * BORDER_Y * SCALEFACTOR))
        pygame.display.set_caption("Pyqueex")
        self.clock = pygame.time.Clock()
        self.playfield = Playfield()
        self.waiting   = 0
        self.initSprites()
        self.running = True
        while self.running:
            self.clocktick = self.clock.tick(FPS)
            self.screen.fill(COLORS["red"])

            if self.waiting:
                self.waiting -= 1
                if self.waiting == 0:
                    self.continue_game()
            else:
                self.all_sprites.update()

            self.all_sprites.draw(self.screen)

            pygame.display.flip()
        pygame.quit()

    def initSprites(self):
        self.all_sprites     = pygame.sprite.Group()
        self.playfieldsprite = PlayfieldSprite(self, self.playfield)
        self.player          = Player(self, self.playfield)
        self.opponent        = Opponent(self, self.playfield, self.player)
        self.player.setOpponent(self.opponent)

    def playerdied(self):
        self.waiting = 180

    def continue_game(self):
        self.player.initSettings()
        self.playfield.deleteYellowInPlayfield()
        self.playfieldsprite.updatePlayfieldSprite()

Game()

