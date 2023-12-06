#!/usr/bin/python3
# coding: utf-8

import pygame

"""
    inputhandler 1.0 - My Standard Input Handler for Pygame.
                       Control keys for directions, Control-keys for "fire".
                       Plus support for one joystick.

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

class InputHandler:

    def __init__(self, hasjoystick):
        self.hasjoystick = hasjoystick

        self.data = { pygame.K_LEFT  : "left", pygame.K_RIGHT   : "right",
                      pygame.K_UP    : "up",   pygame.K_DOWN    : "down",
                      pygame.K_LCTRL : "fire", pygame.K_RCTRL   : "fire",
                      pygame.K_q     : "quit", pygame.K_ESCAPE : "quit" }

        self.datakeys = self.data.keys()
        self.datavalues = self.data.values()

        self.joystick = {}
        if self.hasjoystick:
            self.initJoystick()
        self.initKeys()

    def initJoystick(self):
        if pygame.joystick.get_count() == 0:
            print("No joysticks found.")
            self.hasjoystick = False
            return
        self.js = pygame.joystick.Joystick(0)
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
                  "fire" : False, "quit" : False}
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
            if self.hasjoystick:
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
        if self.hasjoystick:
            for i in self.datavalues:
                if i == "quit":
                    continue
                if self.joystick[i]:
                    action[i] = True
        return action
