import pygame
import random
from pygame.locals import (
    K_SPACE,
    K_LEFT,
    K_RIGHT,
    K_UP,
    K_ESCAPE, #Add into code somewhere
    KEYDOWN, 
    QUIT,
    RLEACCEL,
    K_r,
)

# Initialise game and setup screen
pygame.init()
font = pygame.font.SysFont("Arial", 30)
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game") #Can change name
clock = pygame.time.Clock()

# Backgrounds for levels
bg_images = {
    1: pygame.transform.scale(pygame.image.load("images/background1.jpeg").convert(), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    #2: pygame.transform.scale(pygame.image.load("images/background2.jpeg").convert(), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    #3: pygame.transform.scale(pygame.image.load("images/background2.jpeg").convert(), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    #Find an image for 2 and 3

# Colours 
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

# Game variables
tile_size = 60
score = 0
main_menu = True #Add main menu into code
current_level = 1
max_level = 3
boss_fight = False
level_complete = False


# Classes
class HealthBar(): #This isnt used, draw health bar is added later - look into    
    def __init__(self, x, y, width, height, max_hp):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_hp = max_hp
        self.hp = max_hp

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 0, 0), (self.x, self.y, self.width, self.height))
        ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, (0, 255, 0), (self.x, self.y, self.width * ratio, self.height))

class Ground(pygame.sprite.Sprite): #Not sure if this is adding anything
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(topleft=(x, y))

class Player(pygame.sprite.Sprite): #Could add different speeds
    def __init__(self):
        super().__init__()
        original_image = pygame.image.load("images/soldier.png").convert()
        scaled_image = pygame.transform.scale(original_image, (240, 150))  
        self.image = scaled_image
        self.image.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.image.get_rect(center=(100, 100)) 
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)
        self.vel_x = 0
        self.vel_y = 0
        self.jumping = False
        self.jumpCount = 0
        self.time = 0
        self.timer = False
        self.gravity = 0.5
        self.fallcount = 0
        self.health = 100
        self.lives = 3  
        self.max_jumps = 2
        
    def take_damage(self, amount):
        if self.lives <= 0:
            return
        self.health -= amount
        if self.health <= 0:
            self.lives = max(0, self.lives -1)
            if self.lives > 0:
                self.health = 100
            else:
                self.health = 0   
                
    def jump(self):
        if self.jumpCount < self.max_jumps:
            self.vel_y = -10
            self.jumpCount += 1
            self.jumping = True

    def update(self, keys):
        speed = 5

    # Horizontal movement
        if keys[K_LEFT]:
            self.pos_x -= speed
        if keys[K_RIGHT]:
            self.pos_x += speed

    # Jump
        if keys[K_UP] and not self.jumping:
            self.jump()
        if not keys[K_UP]:
            self.jumping = False

    # Apply gravity and vertical movement
        self.vel_y += self.gravity
        self.pos_y += self.vel_y

    # Floor collision
        if self.pos_y + self.rect.height >= SCREEN_HEIGHT - 20:
            self.pos_y = SCREEN_HEIGHT - 20 - self.rect.height
            self.vel_y = 0
            self.jumpCount = 0

        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)

class Bullet(pygame.sprite.Sprite): #Add firing rate/cooldown time
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y +50))
        self.speed = 10

    def update(self):
        self.rect.x += self.speed
        if self.rect.left > SCREEN_WIDTH:
            self.kill()

class Enemy(pygame.sprite.Sprite): #add different types of enemies, speeds etc
    def __init__(self, level):
        super().__init__()
        original_image = pygame.image.load("images/tank.png").convert()
        scaled_image = pygame.transform.scale(original_image, (300, 210))  
        self.image = scaled_image
        self.rect = self.image.get_rect(midbottom=(SCREEN_WIDTH + random.randint(100, 400), SCREEN_HEIGHT - 30))
        self.speed = random.randint(1 + level, 2 + level)
        self.health = 2 + level

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

class Collectible(pygame.sprite.Sprite): #add different types of collectibles eg extra life
    def __init__(self, x, y):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(CYAN)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 3

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

class Boss(pygame.sprite.Sprite): #Could make it move different ways, add an image instead of rectangle
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((120, 100))
        self.image.fill((180, 0, 180))
        self.rect = self.image.get_rect(midbottom=(SCREEN_WIDTH - 50, SCREEN_HEIGHT - 20))
        self.health = 30
        self.shoot_timer = 0

    def update(self):
        self.shoot_timer += 1
        if self.shoot_timer > 60:
            boss_bullets.add(BossBullet(self.rect.centerx, self.rect.centery))
            self.shoot_timer = 0

class BossBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 6

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

# Drawing
def draw_health_bar(surface, x, y, health, max_health):
    pygame.draw.rect(surface, RED, (x, y, 200, 20))
    pygame.draw.rect(surface, GREEN, (x, y, 200 * (health / max_health), 20))

def draw_boss_health_bar(surface, x, y, health, max_health):
    pygame.draw.rect(surface, RED, (x, y, 300, 20))
    pygame.draw.rect(surface, CYAN, (x, y, 300 * (health / max_health), 20))

# Groups
player = Player()
player_group = pygame.sprite.Group(player)
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
collectibles = pygame.sprite.Group()
boss_group = pygame.sprite.Group()
boss_bullets = pygame.sprite.Group()
objects = pygame.sprite.Group()
ground = Ground(0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20)
objects.add(ground)

# Timers #Add more enemies, waves of enemies, different speeds
enemy_spawn_event = pygame.USEREVENT + 1
pygame.time.set_timer(enemy_spawn_event, 1500)

# Main Loop
running = True
while running:
    screen.blit(bg_image, (0, 0)) if current_level == 1 else (10, 10, 60) if current_level == 2 else (20, 0, 40)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        if event.type == enemy_spawn_event and not level_complete and not boss_fight:
            if current_level < 3:
                enemies.add(Enemy(current_level))

        if event.type == KEYDOWN:
            if event.key == K_SPACE and not level_complete:
                bullet = Bullet(player.rect.right, player.rect.centery)
                bullets.add(bullet)
            if event.key == K_r and level_complete:
                # Reset game
                score = 0
                current_level = 1
                player.health = 100
                player.lives = 3
                level_complete = False
                boss_fight = False
                enemies.empty()
                bullets.empty()
                collectibles.empty()
                boss_group.empty()
                boss_bullets.empty()

    # Update
    player.update(keys)
    bullets.update()
    enemies.update()
    collectibles.update()
    boss_group.update()
    boss_bullets.update()

    # Bullet hits enemy
    for bullet in bullets:
        hits = pygame.sprite.spritecollide(bullet, enemies, False)
        for enemy in hits:
            bullet.kill()
            enemy.health -= 1
            if enemy.health <= 0:
                enemy.kill()
                score += 1
                if random.random() < 0.1 and current_level == 2:
                    collectibles.add(Collectible(enemy.rect.centerx, enemy.rect.centery))

    # Bullet hits boss
    if boss_fight:
        for bullet in bullets:
            if pygame.sprite.spritecollide(bullet, boss_group, False):
                bullet.kill()
                for boss in boss_group:
                    boss.health -= 1
                    if boss.health <= 0:
                        boss.kill()
                        level_complete = True

    # Boss bullet hits player
    if pygame.sprite.spritecollideany(player, boss_bullets):
        player.health -= 2

    # Enemy hits player
    if pygame.sprite.spritecollideany(player, enemies):
        player.health -= 1

    # Collectibles
    for item in pygame.sprite.spritecollide(player, collectibles, True):
        player.health = min(100, player.health + 20)

    # Check player death
    if player.health <= 0 and not level_complete:
        player.take_damage(0) 
        if player.lives == 0:
            level_complete = True

    # Level transitions
    if score >= 20 and current_level == 1:
        current_level = 2
        enemies.empty()
        bullets.empty()
        collectibles.empty()
        player.health = 100

    elif score >= 50 and current_level == 2 and not boss_fight:
        current_level = 3
        enemies.empty()
        bullets.empty()
        collectibles.empty()
        player.health = 100
        boss = Boss()
        boss_group.add(boss)
        boss_fight = True

    # Draw
    player_group.draw(screen)
    objects.draw(screen)
    bullets.draw(screen)
    enemies.draw(screen)
    collectibles.draw(screen)
    boss_group.draw(screen)
    boss_bullets.draw(screen)

    draw_health_bar(screen, 20, 20, player.health, 100)
    screen.blit(font.render(f"Score: {score}", True, WHITE), (20, 50))
    screen.blit(font.render(f"Lives: {player.lives}", True, WHITE), (20, 80))
    screen.blit(font.render(f"Level: {current_level}", True, WHITE), (20, 110))

    if boss_fight:
        for boss in boss_group:
            draw_boss_health_bar(screen, SCREEN_WIDTH - 340, 20, boss.health, 30)

    # Win or lose screen
    if level_complete:
        msg = "You Win!" if player.lives > 0 and not boss_group else "Game Over"
        screen.blit(font.render(msg, True, WHITE),
                    (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
        screen.blit(font.render("Press R to Restart", True, WHITE),
                    (SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 + 40))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()


#Will crash after level 1 since no level 2 and 3 bg image at this stage
#Need to change size of enemies so player can jump over them, potentially add platforms and enemies that can change heights
