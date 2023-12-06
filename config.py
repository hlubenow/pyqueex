#!/usr/bin/python3
# coding: utf-8

SCREENSIZE_X     = 99
SCREENSIZE_Y     = 99
BORDER_X         = 10
BORDER_Y         = 5
SCALEFACTOR      = 5

WINDOWPOSITION_X = 185
WINDOWPOSITION_Y = 30

FPS              = 60

PLAYERSPEED      = 0.05
OPPONENTSPEED    = 0.05

OPPONENTSIZE_X   = 18
OPPONENTSIZE_Y   = 8
OPPONENTCOLOR    = "green"

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

COLORNAMES = ("black", "blue", "red", "magenta", "green", "cyan", "yellow", "white")
COLORNRS = {}
for i in COLORNAMES:
    COLORNRS[i] = COLORNAMES.index(i)
