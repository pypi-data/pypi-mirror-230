import pygame
from pygame.locals import *
import sys
from sys import *

def start():
    pygame.init()

def window(x, y):
    pygame.display.set_mode((x, y))

def background(screen ,color):
    screen.fill(color)

def r(screen, color, size):
    pygame.draw.rect(screen, color, size)

def c(screen, color, position, radius):
    pygame.draw.circle(screen, color, position, radius)

def key_pressed(key):
    pygame.key.get_pressed()[key]

def colission(obj1, obj2):
    obj1.colliderect(obj2)

def on_stop():
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

def window_name(name):
    pygame.display.set_caption(name)

def key_press(key, code):
    for event in pygame.event.get():
        if event.type == KEYDOWN and event.key and key:
            exec(code)