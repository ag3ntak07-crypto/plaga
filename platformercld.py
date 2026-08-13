import pygame
import sys
import os
import random

# ── Constants ────────────────────────────────────────────────────────────────
NATIVE_W, NATIVE_H = 1920, 1080   # internal render resolution (matches bg art)
TILE_SIZE           = 90           
FPS                 = 60
GRAVITY             = 0.7
JUMP_FORCE          = -22
MOVE_SPEED          = 9
CAMERA_LERP         = 0.08         # lower = more lag bwteen input and camera movement

# Colours these are placeholders
SKY_COLOR       = (30, 30, 46)
WALL_COLOR      = (80, 80, 110)
WALL_EDGE_COLOR = (110, 110, 150)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def asset(name):
    return os.path.join(BASE_DIR, name)
def crop_transparent(image):

    rect = image.get_bounding_rect()

    if rect.width == 0 or rect.height == 0:
        return image

    return image.subsurface(rect).copy()

# ── Level grid  (0 = empty, 1 = wall) 
# 12 rows × 106 columns  →  world = 9600 × 1080 px
# Each row = 90 px tall, each col = 90 px wide.
# Add/remove columns but every row must stay the same length.
GRID = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1.1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,0,0,0,0,1,1,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,2,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,0,0,0,0,0,1,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,1,1,1,1,1,1,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,1,1,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,1,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,1,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,1,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,1,1,1,0,0,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

GRID_ROWS = len(GRID)
GRID_COLS = max(len(row) for row in GRID)
WORLD_W   = GRID_COLS * TILE_SIZE   # 9600
WORLD_H   = GRID_ROWS * TILE_SIZE   # 1080

# ── Background zones 
# Each zone covers a horizontal slice of the world.
# Zones are checked left-to-right; first match wins.
# For now they all fall back to a solid colour placeholder
ZONES = [
    {"x_start": 0,    "x_end": 3840,  "bg": "bg_1.jpg",  "fallback": (20,  40,  20)},
    {"x_start": 3840, "x_end": 6720,  "bg": "bg_2.jpg",    "fallback": (20,  20,  40)},
    {"x_start": 6720, "x_end": 9600,  "bg": "bg_3.jpg",  "fallback": (40,  20,  20)},
]

def load_bg_images():

    global background
    global stone_tiles
    global grass_tiles

    background = pygame.image.load(
        asset("assets/pragassets/bgplagaa.jpg")
    ).convert()

    stone_tiles = []
    grass_tiles = []

    for i in range(1, 5):

        img = pygame.image.load(
            asset(f"assets/pragassets/tilees1.png")
        ).convert_alpha()

        stone_tiles.append(crop_transparent(img))
        img = pygame.image.load(
            asset(f"assets/pragassets/tiles_gameeeee1.png")
        ).convert_alpha()

        grass_tiles.append(crop_transparent(img))
def build_wall_rects():

    global tile_map

    rects = []
    tile_map = {}

    for r, row in enumerate(GRID):

        for c, cell in enumerate(row):

            if cell != 1:
                continue

            rects.append(
                pygame.Rect(
                    c * TILE_SIZE,
                    r * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE
                )
            )

            surface = (
                r == 0 or
                GRID[r-1][c] == 0
            )

            if surface:

                tile_map[(r, c)] = random.choice(grass_tiles)

            else:

                tile_map[(r, c)] = random.choice(stone_tiles)

    return rects
    
def build_enemy_spawns():
    spawns = []
    for r, row in enumerate(GRID):
        for c, cell in enumerate(row):
            if cell == 2:
                spawns.append((c * TILE_SIZE, r * TILE_SIZE))
    return spawns
def lerp(a, b, t):
    return a + (b - a) * t


# Camera 
class Camera:
    #Renders to a NATIVE_W *NATIVE_H surface; that surface is then scaled to the actual monitor resolution so the game always looks correct

    def __init__(self):
        self.x = 0.0
        self.y = 0.0

    def update(self, target_rect):
        tx = target_rect.centerx - NATIVE_W / 2
        ty = target_rect.centery - NATIVE_H / 2
        self.x = lerp(self.x, tx, CAMERA_LERP)
        self.y = lerp(self.y, ty, CAMERA_LERP)
        # Clamp to world edges
        self.x = max(0, min(self.x, WORLD_W - NATIVE_W))
        self.y = max(0, min(self.y, WORLD_H - NATIVE_H))

    def apply(self, rect):
        return rect.move(-int(self.x), -int(self.y))


# Player 
class Player:
    WALK_FRAME_TIME = 0.08
    ATTACK_FRAME_TIME = 0.045

    SPRITE_SCALE = 1

    def __init__(self, x, y,
                 idle,
                 walk_frames,
                 attack1,
                 attack2):

        # ---------------- Collision ----------------

        self.rect = pygame.Rect(
            x,
            y,
            TILE_SIZE - 60,
            TILE_SIZE + 25
        )

        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False

        # ---------------- Direction ----------------

        self.facing = "left"      # left/right
        self.flip = False

        # ---------------- Images ----------------

        self.idle = self.scale(idle)

        self.walk = [self.scale(img) for img in walk_frames]

        self.attack_left = [self.scale(img) for img in attack1]
        self.attack_right = [self.scale(img) for img in attack2]

        self.image = self.idle

        # ---------------- Animation ----------------

        self.walk_frame = 0
        self.walk_timer = 0

        self.attack_frame = 0
        self.attack_timer = 0

        self.attacking = False

        self.attack_combo = 0

        # Used later for drawing slash separately
        self.current_slash = None


    def scale(self, img):

        w = img.get_width()
        h = img.get_height()

        return pygame.transform.scale(
            img,
            (
                w * self.SPRITE_SCALE,
                h * self.SPRITE_SCALE
            )
        )


    def attack(self):

        if self.attacking:
            return

        self.attacking = True

        self.attack_frame = 0
        self.attack_timer = 0

        self.attack_combo = 1 - self.attack_combo


    def handle_input(self):

        keys = pygame.key.get_pressed()

        self.vel_x = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -MOVE_SPEED
            self.flip = True          # or False depending on your final flip logic
            self.facing = "left"

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = MOVE_SPEED
            self.flip = False         # or True depending on your final flip logic
            self.facing = "right"

        if (keys[pygame.K_SPACE]
            or keys[pygame.K_UP]
            or keys[pygame.K_w]) and self.on_ground:

            self.vel_y = JUMP_FORCE
            self.on_ground = False


    def apply_gravity(self):

        self.vel_y = min(self.vel_y + GRAVITY, 22)


    def move_and_collide(self, walls):

        self.rect.x += int(self.vel_x)

        for w in walls:

            if self.rect.colliderect(w):

                if self.vel_x > 0:

                    self.rect.right = w.left

                elif self.vel_x < 0:

                    self.rect.left = w.right


        self.rect.y += int(self.vel_y)

        self.on_ground = False

        for w in walls:

            if self.rect.colliderect(w):

                if self.vel_y > 0:

                    self.rect.bottom = w.top
                    self.vel_y = 0
                    self.on_ground = True

                else:

                    self.rect.top = w.bottom
                    self.vel_y = 0


        self.rect.clamp_ip(
            pygame.Rect(
                0,
                0,
                WORLD_W,
                WORLD_H
            )
        )


    def animate(self):

        dt = 1 / FPS

        # ---------------- Attack ----------------

        if self.attacking:

            self.attack_timer += dt

            if self.attack_timer >= self.ATTACK_FRAME_TIME:

                self.attack_timer = 0

                self.attack_frame += 1

                if self.attack_frame >= 4:

                    self.attacking = False

                    self.attack_frame = 0

           # ---------- Slash Animation ----------

            if self.attack_combo == 0:
                attack_frames = self.attack_left      # left-hand slash
            else:
                attack_frames = self.attack_right     # right-hand slash
            SLASH_SCALE = 1.3  # Increase this to make it bigger

            slash = attack_frames[self.attack_frame]

            w = slash.get_width()
            h = slash.get_height()

            self.current_slash = pygame.transform.scale(
                slash,
                (int(w * SLASH_SCALE), int(h * SLASH_SCALE))
            )

            return


        # ---------------- Walking ----------------

        self.current_slash = None

        if self.vel_x != 0:

            self.walk_timer += dt

            if self.walk_timer >= self.WALK_FRAME_TIME:

                self.walk_timer = 0

                self.walk_frame += 1

                self.walk_frame %= 7

            self.image = self.walk[self.walk_frame]

        else:

            self.walk_frame = 0
            self.walk_timer = 0

            self.image = self.idle


    def update(self, walls):

        self.handle_input()

        self.apply_gravity()

        self.move_and_collide(walls)

        self.animate()


    def draw(self, surface, camera):

        # ---------- Draw Ghost ----------

        sprite = self.image

        if self.flip:
            sprite = pygame.transform.flip(sprite, True, False)

        draw_rect = sprite.get_rect(
            midbottom=(
                self.rect.centerx,
                self.rect.bottom + 50      # Adjust if you want the ghost higher/lower
            )
        )

        surface.blit(
            sprite,
            camera.apply(draw_rect)
        )

        # ---------- Draw Slash ----------

        if self.current_slash:

            slash = self.current_slash

            if self.facing == "left":

                slash = pygame.transform.flip(slash, True, False)

                slash_rect = slash.get_rect(
                    midright=(
                        draw_rect.left +230,
                        draw_rect.centery
                    )
                )

            else:  # facing right

                slash_rect = slash.get_rect(
                    midleft=(
                        draw_rect.right -230,
                        draw_rect.centery
                    )
                )

            surface.blit(
                slash,
                camera.apply(slash_rect)
            )

        # ---------- Collision Box (Debug) ----------

        pygame.draw.rect(
            surface,
            (255, 0, 0),
            camera.apply(self.rect),
            2
        )
# Enemy
class Enemy:
    def __init__(self, x, y, image, speed=2):
        w, h = TILE_SIZE - 10, TILE_SIZE - 6
        # y passed in is the TOP of the spawn tile; snap rect bottom to the
        # bottom of that tile (= top of the platform tile below it)
        self.rect      = pygame.Rect(x, y + (TILE_SIZE - h), w, h)
        self.speed     = speed
        self.direction = 1   # 1 = right, -1 = left
        self.image     = pygame.transform.scale(image, (w, h))

    def update(self, walls):
        move_x = self.speed * self.direction
        next_rect = self.rect.move(move_x, 0)

        hit_wall = any(next_rect.colliderect(w) for w in walls)

        foot_x = next_rect.right - 1 if self.direction > 0 else next_rect.left
        probe = pygame.Rect(foot_x, self.rect.bottom + 2, 2, 4)
        ground_ahead = any(probe.colliderect(w) for w in walls)

        if hit_wall or not ground_ahead:
            self.direction *= -1
        else:
            self.rect.x += move_x

    def draw(self, surface, camera):
        img = pygame.transform.flip(self.image, self.direction < 0, False)
        surface.blit(img, camera.apply(self.rect))
def draw_background(surface, camera):

    bw = background.get_width()
    bh = background.get_height()

    start_x = -(camera.x % bw)
    start_y = -(camera.y % bh)

    for x in range(int(start_x) - bw, NATIVE_W + bw, bw):
        for y in range(int(start_y) - bh, NATIVE_H + bh, bh):
            surface.blit(background, (x, y))

def draw_world(surface, camera):

    visible = pygame.Rect(
        camera.x,
        camera.y,
        NATIVE_W,
        NATIVE_H
    )

    for (r, c), img in tile_map.items():

        world_rect = pygame.Rect(
            c * TILE_SIZE,
            r * TILE_SIZE,
            TILE_SIZE,
            TILE_SIZE
        )

        if not visible.colliderect(world_rect):
            continue

        img = pygame.transform.scale(
            img,
            (TILE_SIZE, TILE_SIZE)
        )

        surface.blit(
            img,
            camera.apply(world_rect)
        )

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    pygame.init()

    # Fullscreen at native monitor resolution
    screen      = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    info        = pygame.display.Info()
    MONITOR_W   = info.current_w
    MONITOR_H   = info.current_h
    pygame.display.set_caption("Platformer")

    # All game rendering happens on this fixed surface, then scaled to screen
    canvas = pygame.Surface((NATIVE_W, NATIVE_H))

    clock = pygame.time.Clock()

    # Load assets
    load_bg_images()
    try:

        idle = pygame.image.load(
            asset("assets/pragassets/plaga_standing.png")
        ).convert_alpha()

        walk_frames = []

        for i in range(1, 8):

            walk_frames.append(

                pygame.image.load(
                    asset(f"assets/pragassets/praga_moving_{i}.png")
                ).convert_alpha()

            )

        attack1 = []

        for i in range(1, 5):

            attack1.append(

                pygame.image.load(
                    asset(f"assets/pragassets/praga_attack_{i}.png")
                ).convert_alpha()

            )

        attack2 = []

        for i in range(1, 5):

            attack2.append(

                pygame.image.load(
                    asset(f"assets/pragassets/praga_attackr_{i}.png")
                ).convert_alpha()

            )

    except FileNotFoundError as e:

        print(e)

        pygame.quit()

        sys.exit()
        idle = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        idle.fill((220, 60, 220))
        print("test.png not found using placeholder sprite.")
    wall_rects = build_wall_rects()
    enemy_spawns = build_enemy_spawns()
    enemies = [Enemy(x, y, idle) for x, y in enemy_spawns]

    spawn_col = 1
    spawn_row = GRID_ROWS - 2
    player = Player(

        spawn_col * TILE_SIZE + 4,
        spawn_row * TILE_SIZE - TILE_SIZE,

        idle,
        walk_frames,
        attack1,
        attack2

    )

    camera = Camera()
    camera.x = player.rect.centerx - NATIVE_W / 2
    camera.y = player.rect.centery - NATIVE_H / 2

    font = pygame.font.SysFont("monospace", 20)

    while True:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_x:

                    player.attack()

        player.update(wall_rects)
        for enemy in enemies:
            enemy.update(wall_rects)
        camera.update(player.rect)

        # ── Render to canvas ─────────────────────────────────────────────────
        # ── Render to canvas ─────────────────────────────────────────────────

        canvas.fill((0, 0, 0))

        draw_background(canvas, camera)

        for (r, c), img in tile_map.items():

            canvas.blit(
                pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE)),
                camera.apply(
                    pygame.Rect(
                        c * TILE_SIZE,
                        r * TILE_SIZE,
                        TILE_SIZE,
                        TILE_SIZE
                    )
                )
            )

        for enemy in enemies:
            enemy.draw(canvas, camera)

        player.draw(canvas, camera)
        # HUD
        hud = font.render(
            f"pos: ({player.rect.x}, {player.rect.y})   zone x: {int(camera.x)}",
            True, (220, 220, 220))
        canvas.blit(hud, (12, 12))

        # ── Scale canvas → fullscreen monitor
        scaled = pygame.transform.scale(canvas, (MONITOR_W, MONITOR_H))
        screen.blit(scaled, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    
    main()