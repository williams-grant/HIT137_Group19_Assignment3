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

  def update(self, pressed_keys):
        #if pressed_keys[K_SPACE]: 
            #self.rect.move_ip(0, -5)
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(5, 0)
        if pressed_keys [K_UP]:
            self.rect.move_ip(0, -5)  
        if pressed_keys [K_DOWN]:
            self.rect.move_ip(0, 5)  

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > 2000:
            self.rect.right = 2000
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > 1000:
            self.rect.bottom = 1000

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self). __init__()
        original_image = pygame.image.load("Alien.png").convert()
        scaled_image = pygame.transform.scale(original_image, (120, 80))
        self.surf = scaled_image
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect(
            center=(
                random.randint(2020, 2100),
                random.randint(0, 1000),
            )
        )
        self.speed = random.randint(5, 20)
    
    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()   
               
player = Player()
enemies = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(player) 

ADDENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(ADDENEMY, 250)

running = True
while running:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
        elif event.type == QUIT:
            running = False
        elif event.type == ADDENEMY:
            new_enemy = Enemy()
            enemies.add(new_enemy)
            all_sprites.add(new_enemy)
   
    pressed_keys = pygame.key.get_pressed()
    player.update(pressed_keys)
    enemies.update()

    screen.fill((0, 0, 0))
    
    for entity in all_sprites:
        screen.blit(entity.surf, entity.rect)

    pygame.display.flip()
    clock.tick(60)    

pygame.quit()    




