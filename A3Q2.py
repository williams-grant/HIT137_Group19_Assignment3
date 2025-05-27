import pygame
import random
import math 

from pygame.locals import (
    K_SPACE,
    K_LEFT,
    K_RIGHT,
    K_UP,
    KEYDOWN,
    K_ESCAPE, 
    QUIT,
    RLEACCEL,
    K_r,
    K_KP_ENTER,
    K_RETURN, 
)

# Initialise game and setup screen
pygame.init()
font = pygame.font.SysFont("Arial", 30, bold=True)
screen_width = 1200
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Game") #Change name
clock = pygame.time.Clock()

# Backgrounds for levels           
bg_image1 = pygame.transform.scale(pygame.image.load("images/Background1.png").convert(), (screen_width, screen_height)
                                )
bg_image2 = pygame.transform.scale(pygame.image.load("images/Background2.png").convert(), (screen_width, screen_height)
                                ) 
bg_image3 = pygame.transform.scale(pygame.image.load("images/Background3.jpeg").convert(), (screen_width, screen_height)
                                )
scroll_level1 = 0
scroll_level2 = 0
scroll_level3 = 0
bg_width = bg_image1.get_width()
tiles = math.ceil(screen_width / bg_width) + 1

# Colours 
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
BROWN = (150, 75, 0)

# Game variables
main_menu = True
current_level = 1
max_level = 3
boss_fight = False
level_complete = False
MULTISHOT_DURATION = 5000

# Game objects
platforms = pygame.sprite.Group()
platforms_spawned = False
ADDENEMY = pygame.USEREVENT + 1

# Classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        original_image = pygame.image.load("images/soldier.png").convert()
        scaled_image = pygame.transform.scale(original_image, (240, 150))  
        self.image = scaled_image
        self.image.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.image.get_rect(center=(100, screen_height // 2)) 
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)
        self.vel_y = 0
        self.jumping = False
        self.jumpCount = 0
        self.gravity = 0.5
        self.fallcount = 0
        self.health = 100
        self.lives = 3  
        self.max_jumps = 2
        self.last_shot_time = 0                  
        self.shot_cooldown = 400

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

    def update(self, pressed_keys):
        speed = 5
        if pressed_keys[K_LEFT]:
            self.pos_x -= speed
        if pressed_keys[K_RIGHT]:
            self.pos_x += speed   
        
        self.pos_x = max(0, min(self.pos_x, screen_width - self.rect.width))
        
        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)

    # Gravity and vertical movement
        self.vel_y += self.gravity
        self.pos_y += self.vel_y

    # Floor collision
        if self.pos_y + self.rect.height >= screen_height - 20:
            self.pos_y = screen_height - 20 - self.rect.height
            self.vel_y = 0
            self.jumpCount = 0
            self.jumping = False

        if self.vel_y >= 0:
            hits = pygame.sprite.spritecollide(self, platforms, False)
        else:
            hits = [ ]
        if hits:
            lowest_platform = hits[0]
            for platform in hits:
                if platform.rect.top < lowest_platform.rect.top:
                    lowest_platform = platform

            if self.rect.bottom > lowest_platform.rect.top:
                self.pos_y = lowest_platform.rect.top - self.rect.height
                self.vel_y = 0
                self.jumpCount = 0
                self.jumping = False

        self.pos_y = max(0, min(self.pos_y, screen_height - self.rect.height)) 
        
        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)


class Enemy(pygame.sprite.Sprite): #add different types of enemies, speeds etc
    def __init__(self, level):
        super().__init__()
        original_image = pygame.image.load("images/tank.png").convert()
        scaled_image = pygame.transform.scale(original_image, (200, 110))  
        self.image = scaled_image
        self.image.set_colorkey((0, 0, 0), RLEACCEL)

        spawn_x = random.randint(screen_width + 20, screen_width + 200)

        if level == 1:
            spawn_y = screen_height - 20  
            self.rect = self.image.get_rect(midbottom=(spawn_x, spawn_y))
        else:
            spawn_y = random.randint(0, screen_height - self.image.get_height())
            self.rect = self.image.get_rect(topleft=(spawn_x, spawn_y))

        base_speed = random.randint(5, 20)
        self.speed = base_speed + level * 5
        base_hp = 1
        self.health = base_hp + level * 2 - 2
         
    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()

class Bullet(pygame.sprite.Sprite): 
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10

    def update(self):
        self.rect.move_ip(self.speed, 0)
        if self.rect.left > screen_width:
            self.kill()

class PowerUp(pygame.sprite.Sprite): 
    def __init__(self, x, y):
        super(PowerUp, self).__init__()
        self.type = random.choice(['health', 'bonus','multishot'])  # this is how we add more powerups
        self.image = pygame.Surface((20, 20))
        if self.type == 'health':
            self.image.fill((GREEN)) 
        elif self.type == 'bonus':
            self.image.fill((MAGENTA))
        elif self.type == 'multishot':
            self.image.fill((CYAN))  
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 3

    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()    

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width=100, height=20):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((BROWN))  
        self.rect = self.image.get_rect(topleft=(x, y))

class HealthBar():
    def __init__(self, x, y, width, height, max_hp):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_hp = max_hp
        self.hp = max_hp

    def draw(self, surface):
        pygame.draw.rect(surface, (RED), (self.x, self.y, self.width, self.height))
        ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, (GREEN), (self.x, self.y, self.width * ratio, self.height))

class Ground(pygame.sprite.Sprite): 
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN) 
        self.rect = self.image.get_rect(topleft=(x, y))

class Boss(pygame.sprite.Sprite): #ADD image instead of rectangle
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((120, 100))
        self.image.fill((180, 0, 180))
        self.rect = self.image.get_rect(midbottom=(screen_width - 50, screen_height - 20))
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

def reset_game():
    global player, enemies, bullets, health_bar, score, game_over, powerups
    global multishot_active, multishot_timer, level, score_to_next_level, enemy_spawn_interval
    global all_sprites, boss_group, boss_bullets, objects, platforms, main_menu
    global platforms_spawned, current_level, boss_fight, level_complete, player_group

    player = Player()
    player_group = pygame.sprite.Group(player)
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    health_bar = HealthBar(20, 20, 200, 25, 100)
    score = 0
    game_over = False
    multishot_active = False
    multishot_timer = 0
    level = 1
    score_to_next_level = 10
    enemy_spawn_interval = 550
    pygame.time.set_timer(ADDENEMY, enemy_spawn_interval)

    all_sprites = pygame.sprite.Group(player)
    boss_group = pygame.sprite.Group()
    boss_bullets = pygame.sprite.Group()

    objects = pygame.sprite.Group()
    ground = Ground(0, screen_height - 20, screen_width, 20)
    objects.add(ground)

    platforms = pygame.sprite.Group()
    platforms_spawned = False
    current_level = 1
    boss_fight = False
    level_complete = False
    main_menu = True

reset_game()

def draw_main_menu():
    screen.fill((0, 0, 0))
    title = font.render("you stink", True, WHITE) #game menu title
    start_msg = font.render("Press Any Key To Start", True, WHITE)
    quit_msg = font.render("Press ESC to Quit", True, WHITE)
    screen.blit(title, (screen_width // 2 - title.get_width() // 2, 300))
    screen.blit(start_msg, (screen_width // 2 - start_msg.get_width() // 2, 400))
    screen.blit(quit_msg, (screen_width // 2 - quit_msg.get_width() // 2, 450))
    pygame.display.flip()

def draw_health_bar(surface, x, y, health, max_health):
    pygame.draw.rect(surface, RED, (x, y, 200, 20))
    pygame.draw.rect(surface, GREEN, (x, y, 200 * (health / max_health), 20))

def draw_boss_health_bar(surface, x, y, health, max_health):
    pygame.draw.rect(surface, RED, (x, y, 300, 20))
    pygame.draw.rect(surface, CYAN, (x, y, 300 * (health / max_health), 20))
 
 #Edited up to here


# Timers #Add more enemies, waves of enemies, different speeds
enemy_spawn_event = pygame.USEREVENT + 1
pygame.time.set_timer(enemy_spawn_event, 1500)
platforms_spawned = False 
multishot_active = False
multishot_timer = 0

# Main Loop
running = True
while running:
    current_time = pygame.time.get_ticks()
    pressed_keys = pygame.key.get_pressed()

    if current_level == 1:
        for i in range(tiles):
            screen.blit(bg_image1, (i * bg_width + scroll_level1, 0)) 
        scroll_level1 -= 2
        if abs(scroll_level1) > bg_width:
            scroll_level1 = 0

    elif current_level == 2:
        for i in range(tiles):
           screen.blit(bg_image2, (i * bg_width + scroll_level2, 0)) 
        scroll_level2 -= 2
        if abs(scroll_level2) > bg_width:
            scroll_level2 = 0

    elif current_level == 3:
        for i in range(tiles):
           screen.blit(bg_image3, (i * bg_width + scroll_level3, 0)) 
        scroll_level3 -= 2
        if abs(scroll_level3) > bg_width:
            scroll_level3 = 0

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        elif event.type == KEYDOWN:
            if main_menu:
                main_menu = False
            elif event.key == K_ESCAPE:
                running = False
            elif event.key == K_SPACE and not main_menu:
                if multishot_active:
                    bullets.add(Bullet(player.rect.right, player.rect.centery - 10))
                    bullets.add(Bullet(player.rect.right, player.rect.centery))
                    bullets.add(Bullet(player.rect.right, player.rect.centery + 10))
                else:
                    bullets.add(Bullet(player.rect.right, player.rect.centery))
                player.last_shot_time = current_time
            elif event.key == K_UP:  
                player.jump()
            elif event.key == K_r and level_complete:
                reset_game()

        
        elif event.type == ADDENEMY and not level_complete and not boss_fight and not main_menu:
            if current_level < 3:
                enemies.add(Enemy(current_level)) 

    if current_level == 2 and not platforms_spawned:
        platforms.add(Platform(200, screen_height - 150))
        platforms.add(Platform(400, screen_height - 250))
        platforms.add(Platform(600, screen_height - 350))
        platforms_spawned = True  

    if main_menu:
        draw_main_menu()
        pygame.display.flip()
        clock.tick(60)
        continue        

    collected_powerups = pygame.sprite.spritecollide(player, powerups, True)
    for powerup in collected_powerups: 
                if powerup.type == 'health':
                    player.health =  min(100, player.health + 5)
                elif powerup.type == 'bonus': 
                    score += 5  
                elif powerup.type == 'multishot':
                    multishot_active = True
                    multishot_timer = current_time
    if multishot_active and current_time - multishot_timer > MULTISHOT_DURATION:
        multishot_active = False

    
    # Update
    player.update(pressed_keys)
    bullets.update()
    enemies.update()
    boss_group.update()
    boss_bullets.update()
    powerups.update()
    platforms.update()

# Collisions
    # Bullet hits enemy
    for bullet in bullets:
        hits = pygame.sprite.spritecollide(bullet, enemies, False)
        for enemy in hits:
            bullet.kill()
            enemy.health -= 1
            if enemy.health <= 0:
                enemy.kill()
                score += 1
                if random.random() < 1 and current_level == 2:
                    powerups.add(PowerUp(enemy.rect.centerx, enemy.rect.centery))

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
                        if random.random() < 0.5:  #CHANCE OF DROP 
                            powerup = PowerUp(boss.rect.centerx, boss.rect.centery)
                            powerups.add(powerup)

    # Boss bullet hits player
    if pygame.sprite.spritecollideany(player, boss_bullets):
        player.health -= 2

    # Enemy hits player
    if pygame.sprite.spritecollideany(player, enemies):
        player.health -= 1

    # Check player death
    if player.health <= 0 and not level_complete:
        player.take_damage(0)
        if player.lives == 0:
            level_complete = True


    # Level transitions
    if score >= 10 and current_level == 1:
        current_level = 2
        enemies.empty()
        bullets.empty()
        player.health = 100

    elif score >= 20 and current_level == 2 and not boss_fight:
        current_level = 3
        enemies.empty()
        bullets.empty()
        player.health = 100
        boss = Boss()
        boss_group.add(boss)
        boss_fight = True

    # Draw
    player_group.draw(screen)
    objects.draw(screen)
    bullets.draw(screen)
    enemies.draw(screen)
    boss_group.draw(screen)
    boss_bullets.draw(screen)
    platforms.draw(screen)
    powerups.draw(screen) 

    draw_health_bar(screen, 20, 20, player.health, 100)
    screen.blit(font.render(f"Score: {score}", True, WHITE), (20, 50))
    screen.blit(font.render(f"Lives: {player.lives}", True, WHITE), (20, 80))
    screen.blit(font.render(f"Level: {current_level}", True, WHITE), (20, 110))

    if boss_fight:
        for boss in boss_group:
            draw_boss_health_bar(screen, screen_width - 340, 20, boss.health, 30)

    # Win or lose screen
    if level_complete:
        if player.lives == 0:
            msg = "Game Over"
        elif current_level == 3 and boss_fight and not boss_group:
            msg = "Victory!"
        else:
            msg = "You Win!"

        screen.blit(font.render(msg, True, RED),
                    (screen_width // 2 - 100, screen_height // 2))
        screen.blit(font.render("Press R to Restart", True, WHITE),
                    (screen_width // 2 - 130, screen_height // 2 + 40))
        screen.blit(font.render("Press ESC to exit the game", True, WHITE),
                    (screen_width // 2 - 188, screen_height // 2 + 80))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
