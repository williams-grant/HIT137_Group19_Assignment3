import pygame
import random
from pygame.locals import (
K_SPACE,
K_LEFT,
K_RIGHT,
K_UP,
K_DOWN,
K_ESCAPE,
KEYDOWN,
QUIT,
RLEACCEL,
)

pygame.init()
screen = pygame.display.set_mode([2000, 1000])
clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
  def __init__(self):
    super(player, self).__init__()
    original_image = pygame.image.load("UFO.png").convert()
    scaled_image = pygame.transform.scale(original_image, (240, 150))
    self.surf = scaled_image
    self.surf.set_colorkey((0, 0, 0), RLEACCEL)
    self.rect = self.surf.get_rect(center=(100, 500))

