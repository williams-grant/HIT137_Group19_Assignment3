import pygame
import random
import math 
import os

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
    K_p,
)

# Initialise game and setup screen
pygame.init()
font = pygame.font.SysFont("Arial", 30, bold=True)
screen_width = 1200
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("2D Game") 
clock = pygame.time.Clock()

# Backgrounds for levels           
bg_image1 = pygame.transform.scale(pygame.image.load(os.path.dirname(__file__) + "/images/Background1.png").convert(), (screen_width, screen_height))
bg_image2 = pygame.transform.scale(pygame.image.load(os.path.dirname(__file__) + "/images/Background2.jpeg").convert(), (screen_width, screen_height)) 
bg_image3 = pygame.transform.scale(pygame.image.load(os.path.dirname(__file__) + "/images/Background3.jpeg").convert(), (screen_width, screen_height))

scroll_level1 = 0
scroll_level2 = 0
scroll_level3 = 0
bg_width = bg_image1.get_width()
tiles = math.ceil(screen_width / bg_width) + 1

# Background for main menu
main_menu_bg = pygame.transform.scale(pygame.image.load(os.path.dirname(__file__) + "/images/mainmenu.jpg").convert(), (screen_width, screen_height))

# Pause
paused = False

# Colours 
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
BROWN = (150, 75, 0)
BLACK = (0,0,0)

# Game variables
current_level = 1
max_level = 3
boss_fight = False
level_complete = False
MULTISHOT_DURATION = 5000

# Level transtion message
level_transition = False
level_transition_time = 0
transition_display_duration = 2000

# Game objects
platforms = pygame.sprite.Group()
platforms_spawned = False
ADDENEMY = pygame.USEREVENT + 1

# Load animation frames
def load_animation_frames(sheet_path, frame_width, frame_height, row, num_frames, colorkey=(0, 0, 0)):
    sheet = pygame.image.load(sheet_path).convert_alpha()
    sheet.set_colorkey((48, 73, 65))
    frames = []
    for i in range(num_frames):
        x = i * frame_width
        y = row * frame_height
        frame = sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
        frames.append(frame)
    return frames

# -- Classes --
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Set sprite sheet path and calculate frame dimensions
        sprite_sheet_path = os.path.dirname(__file__) + "/images/soldier.png"
        frame_width = pygame.image.load(sprite_sheet_path).get_width() // 4
        frame_height = pygame.image.load(sprite_sheet_path).get_height() // 4

        # Load animations
        self.animations = {
            "idle": load_animation_frames(sprite_sheet_path, frame_width, frame_height, 0, 1),
            "walk": load_animation_frames(sprite_sheet_path, frame_width, frame_height, 2, 1),
            "run":  load_animation_frames(sprite_sheet_path, frame_width, frame_height, 2, 1),
            "shoot":load_animation_frames(sprite_sheet_path, frame_width, frame_height, 3, 1)
        }

        # Animation settings
        self.state = "idle"
        self.frame_index = 0
        self.animation_speed = 0.3
        self.frame_timer = 0
        self.facing_right = True
        self.shooting = False
        self.shoot_anim_duration = 450  
        self.shoot_anim_timer = 0

        self.image = self.animations[self.state][self.frame_index]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)
        
        self.rect = self.image.get_rect()
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)

        self.vel_y = 0
        self.jumping = False
        self.jumpCount = 0
        self.gravity = 0.5

        # Health and lives
        self.health = 100
        self.lives = 3
        self.max_jumps = 2

        # Shooting
        self.last_shot_time = 0
        self.shot_cooldown = 400

    def update(self, pressed_keys):
        # Determine state
        if self.shooting and pygame.time.get_ticks() - self.shoot_anim_timer > self.shoot_anim_duration:
            self.shooting = False
        if self.shooting:
            self.state = "shoot"
        elif pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_RIGHT]:
            self.state = "walk"
        else:
            self.state = "idle"

        # Animation frame control
        self.frame_timer += self.animation_speed
        if self.frame_timer >= 1:
            self.frame_index = (self.frame_index + 1) % len(self.animations[self.state])
            self.frame_timer = 0

        # Update image
        current_bottomleft = self.rect.bottomleft
        self.image = self.animations[self.state][self.frame_index]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        self.rect.bottomleft = current_bottomleft
        frame = self.animations[self.state][self.frame_index]
        
        # Movement
        speed = 5
        if pressed_keys[pygame.K_LEFT]:
            self.pos_x -= speed
            self.facing_right = False
        if pressed_keys[pygame.K_RIGHT]:
            self.pos_x += speed
            self.facing_right = True
        self.pos_x = max(0, min(self.pos_x, screen_width - self.rect.width))

        # Gravity and jumping
        self.vel_y += self.gravity
        self.pos_y += self.vel_y

        if self.pos_y + self.rect.height >= screen_height - 10:
            self.pos_y = screen_height - 10 - self.rect.height
            self.vel_y = 0
            self.jumpCount = 0
            self.jumping = False

        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)
        
        # Platform collision
        on_platform = False
        for platform in platforms:
            if (
                self.vel_y >= 0 and
                self.rect.bottom <= platform.rect.top + 5 and
                self.rect.bottom + self.vel_y >= platform.rect.top and
                self.rect.centerx > platform.rect.left and
                self.rect.centerx < platform.rect.right
            ):
                self.pos_y = platform.rect.top - self.rect.height
                self.vel_y = 0
                self.jumpCount = 0
                self.jumping = True
                on_platform = True
                break
                
        if not on_platform and self.pos_y + self.rect.height < screen_height - 20:
            self.jumping = True
   
    def take_damage(self, amount):
        if self.lives <= 0:
            return
        self.health -= amount
        if self.health <= 0:
            self.lives = max(0, self.lives - 1)
            self.health = 100 if self.lives > 0 else 0
            

    def jump(self):
        if self.jumpCount < self.max_jumps:
            self.vel_y = -10
            self.jumpCount += 1
            self.jumping = True

class Enemy(pygame.sprite.Sprite): 
    def __init__(self, level):
        super().__init__()
        original_image = pygame.image.load(os.path.dirname(__file__) + "/images/tank.png").convert_alpha()
        scaled_image = pygame.transform.scale(original_image, (200, 110))  
        self.image = scaled_image
        self.image.set_colorkey((0, 0, 0), RLEACCEL)

        spawn_x = random.randint(screen_width + 20, screen_width + 200)

        if level == 1:
            spawn_y = screen_height - 20  
            self.rect = self.image.get_rect(midbottom=(spawn_x, spawn_y))
        else:
            original_image = pygame.image.load(os.path.dirname(__file__) + "/images/plane.png").convert_alpha()
            scaled_image = pygame.transform.scale(original_image, (200, 110))  
            self.image = scaled_image
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

# Spikes on platforms
class Sittingenemy(Enemy):
    def __init__(self, x, y, level):
        super().__init__(level)
        original_image = pygame.image.load(os.path.dirname(__file__) + "/images/sittingenemy.png").convert()
        self.image = pygame.transform.scale(original_image, (20, 50))  
        self.image.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.health = 3  
        self.level = level
        self.rect = self.image.get_rect()
        self.rect.x = 500
        self.rect.y = screen_height - 400

    def update(self):
        pass 
        if self.rect.right < 0:
            self.kill()

# Flying enemy
class SineEnemy(Enemy):
    def __init__(self, level):
        super().__init__(level)
        original_image = pygame.image.load(os.path.dirname(__file__) + "/images/sineenemy.png").convert_alpha()
        self.image = pygame.transform.scale(original_image, (200, 110))  
        self.start_x = self.rect.x
        self.start_y = self.rect.y
        self.wave_amplitude = 250  # vertical swing
        self.wave_frequency = 0.05  # controls speed of sine wave
        self.frame = 0
        
        if level == 2:
            self.speed = 4
            self.health = 2
        else:
            self.speed = 6
            self.health = 1

    def update(self):
        self.rect.x -= self.speed
        self.rect.y = self.start_y + self.wave_amplitude * math.sin(self.frame * self.wave_frequency)
        self.frame += 1
        if self.rect.right < 0:
            self.kill()

class Bullet(pygame.sprite.Sprite): 
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10 * direction

    def update(self):
        self.rect.move_ip(self.speed, 0)
        if self.rect.left > screen_width:
            self.kill()

class PowerUp(pygame.sprite.Sprite): 
    def __init__(self, x, y):
        super(PowerUp, self).__init__()
        self.type = random.choice(["health", "bonus", "multishot"])  # this is how we add more powerups
        self.image = pygame.Surface((20, 20))
        if self.type == "health":
            self.image.fill((GREEN)) 
        elif self.type == "bonus":
            self.image.fill((MAGENTA))
        elif self.type == "multishot":
            self.image.fill((CYAN))  
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 3

    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()    

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width = 200, height = 20):
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
        self.last_laser_time = 0
        self.lasers = pygame.sprite.Group()
        original_image = pygame.image.load(os.path.dirname(__file__) + "/images/boss.png").convert_alpha()
        self.image = pygame.transform.scale(original_image, (200, 110))  
        self.rect = self.image.get_rect(midbottom=(screen_width - 50, screen_height - 20))
        self.health = 35
        self.shoot_timer = 0
        self.laser_active = False
        self.laser_duration = 1000
        self.laser_cooldown = 0
        self.vertical_speed = 2
        self.vertical_direction = random.choice([-1, 1])
        self.change_direction_timer = pygame.time.get_ticks()
        self.direction_change_interval = 5000 
    def update(self):
        self.shoot_timer += 1
        current_time = pygame.time.get_ticks()
    
        if self.shoot_timer > 60:
            boss_bullets.add(BossBullet(self.rect.centerx, self.rect.centery))
            self.shoot_timer = 0

        # Cooldown countdown
        if self.laser_cooldown > 0:
            self.laser_cooldown -= 1

        # Fire laser
        if not self.laser_active and self.health < 50 and self.laser_cooldown == 0:
            self.lasers.add(Laser(self))
            self.last_laser_time = pygame.time.get_ticks()
            self.laser_active = True
            print("laser shot")
        # Turn off laser after duration
        if self.laser_active and pygame.time.get_ticks() - self.last_laser_time > self.laser_duration * 10:
            self.laser_active = False
            self.laser_cooldown = 300
            self.lasers.empty()
            print("laser go ")

        if current_time - self.change_direction_timer > self.direction_change_interval:
            self.vertical_direction = random.choice([-1, 1])
            self.change_direction_timer = current_time

        self.rect.y += self.vertical_speed * self.vertical_direction
        
        if self.rect.top < 0: # just keeps boss on screen
            self.rect.top = 0
            self.vertical_direction = 1
        elif self.rect.bottom > screen_height - 20:
            self.rect.bottom = screen_height - 20
            self.vertical_direction = -1

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

class Laser(pygame.sprite.Sprite):
    def __init__(self, boss):
        super().__init__()
        self.boss = boss 
        self.width = boss.rect.left
        self.height = 20
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(midleft=(0, boss.rect.centery))
        self.spawn_time = pygame.time.get_ticks()
      
    def update(self):
        self.width = self.boss.rect.left
        self.image = pygame.Surface((self.width, self.height)) #this code is for if boss moves side to side but may not be used if we do not add that
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(midright=(self.boss.rect.left, self.boss.rect.centery))

        if pygame.time.get_ticks() - self.boss.last_laser_time > self.boss.laser_duration:
            self.kill()

# Game setup
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
    enemy_spawn_interval = 1500

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
    title = font.render("MAIN MENU", True, BLACK) #game menu title
    start_msg = font.render("Press Any Key To Start", True, BLACK)
    quit_msg = font.render("Press ESC to Quit", True, BLACK)
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
 


# Timers 
enemy_spawn_event = pygame.USEREVENT + 1
pygame.time.set_timer(enemy_spawn_event, enemy_spawn_interval)
platforms_spawned = False 
multishot_active = False
multishot_timer = 0


# Main Loop
running = True
while running:
    current_time = pygame.time.get_ticks()
    pressed_keys = pygame.key.get_pressed()

    # Scrolling backgrounds
    if current_level == 1:
        scroll_level1 = (scroll_level1 - 2) % bg_width
        for i in range(tiles):
            screen.blit(bg_image1, (i * bg_width - scroll_level1, 0))
    elif current_level == 2:
        scroll_level2 = (scroll_level2 - 2) % bg_width
        for i in range(tiles):
            screen.blit(bg_image2, (i * bg_width - scroll_level2, 0))
    elif current_level == 3:
        scroll_level3 = (scroll_level3 - 2) % bg_width
        for i in range(tiles):
            screen.blit(bg_image3, (i * bg_width - scroll_level3, 0))

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        elif event.type == KEYDOWN:
            if main_menu:
                main_menu = False
            elif event.key == K_ESCAPE:
                running = False
            elif event.key == K_SPACE and not main_menu:
                if current_time - player.last_shot_time > player.shot_cooldown:

                    if player.facing_right:
                        direction = 1
                        bullet_shape = player.rect.right
                    else:
                        direction = -1
                        bullet_shape = player.rect.left

                    if multishot_active:
                        bullets.add(Bullet(bullet_shape, player.rect.centery - 10, direction))
                        bullets.add(Bullet(bullet_shape, player.rect.centery, direction))
                        bullets.add(Bullet(bullet_shape, player.rect.centery + 10, direction))
                    else:
                        bullets.add(Bullet(bullet_shape, player.rect.centery, direction))
                    player.last_shot_time = current_time
                    player.shooting = True
                    player.shoot_anim_timer = pygame.time.get_ticks()
            elif event.key == K_UP:  
                player.jump()
            elif event.key == K_r and level_complete:
                reset_game()
            elif event.key == pygame.K_p:
                paused = not paused
                if paused:
                    while paused:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                                paused = False
            
                        screen.blit(font.render("Paused - Press 'P' to resume", True, (255, 255, 255)), (250, 300))
                        pygame.display.flip()
                        clock.tick(5)  

        elif event.type == ADDENEMY and not level_complete and not boss_fight and not main_menu:
            if current_level == 2:
                if random.random() < 0.5:
                    enemies.add(Enemy(current_level))
                else:
                    enemies.add(SineEnemy(current_level))
            elif current_level == 1:
                enemies.add(Enemy(current_level))

    if current_level == 2 and not platforms_spawned:
        platform_positions = [
            (200, screen_height - 150),
            (400, screen_height - 250),
            (600, screen_height - 350)
        ]
        for x, y in platform_positions:
            platform = Platform(x, y, 200, 20)
            platforms.add(platform)

            sit_enemy = Sittingenemy(platform.rect.centerx, platform.rect.top, level)
            sit_enemy.rect.midbottom = (platform.rect.centerx, platform.rect.top)
            enemies.add(sit_enemy)

        platforms_spawned = True

    if main_menu:  
        screen.blit(main_menu_bg,(0,0))
        draw_main_menu()
        pygame.display.flip()
        clock.tick(60)
        continue        

    collected_powerups = pygame.sprite.spritecollide(player, powerups, True)
    for powerup in collected_powerups: 
                if powerup.type == "health":
                    player.health =  min(100, player.health + 5)
                elif powerup.type == "bonus": 
                    score += 5  
                elif powerup.type == "multishot":
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
    for boss in boss_group:
        boss.lasers.update()

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
                    boss.lasers.update()
                    if boss.health <= 0:
                        boss.kill()
                        level_complete = True
                        if random.random() < 0.5:  #CHANCE OF DROP 
                            powerup = PowerUp(boss.rect.centerx, boss.rect.centery)
                            powerups.add(powerup)

    # Boss bullet hits player
    if pygame.sprite.spritecollideany(player, boss_bullets):
        player.health -= 2
        for boss in boss_group:
            for laser in boss.lasers:
                if player.rect.colliderect(laser.rect):
                    player.health -= 50
    # Enemy hits player
    if pygame.sprite.spritecollideany(player, enemies):
        collided_enemies = pygame.sprite.spritecollide(player, enemies, False)
        for enemy in collided_enemies:
            if isinstance(enemy, Sittingenemy):
            # Check if player is landing on top of the enemy
                if player.rect.bottom <= enemy.rect.top + 10 and player.vel_y > 0:
                    #enemy.kill()  # or reduce health
                    player.health -= 10
            else:
            # Other enemy types (optional)
                player.health -= 1

    # Check player death
    if player.health <= 0 and not level_complete:
        player.take_damage(0)
        if player.lives == 0:
            level_complete = True

    # Level transitions
    if score >= score_to_next_level * current_level and current_level == 1:
        current_level = 2
        enemies.empty()
        bullets.empty()
        player.health = 100
        level_transition = True
        level_transition_time = pygame.time.get_ticks()

    elif score >= score_to_next_level * current_level and current_level == 2 and not boss_fight:
        current_level = 3
        enemies.empty()
        bullets.empty()
        player.health = 100
        boss = Boss()
        boss_group.add(boss)
        boss_fight = True
        level_transition = True
        level_transition_time = pygame.time.get_ticks()

    # Draw
    player_group.draw(screen)
    objects.draw(screen)
    bullets.draw(screen)
    enemies.draw(screen)
    boss_group.draw(screen)
    boss_bullets.draw(screen)
    platforms.draw(screen)
    powerups.draw(screen) 
    if current_level == 3:
        for boss in boss_group:
            boss.lasers.draw(screen)

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
    if level_transition:
        if pygame.time.get_ticks() - level_transition_time < transition_display_duration:
            transition_text = font.render(f"LEVEL {current_level}", True, YELLOW)
            screen.blit(transition_text, (
                screen_width // 2 - transition_text.get_width() // 2,
                screen_height // 2 - transition_text.get_height() // 2
            ))
        else:
            level_transition = False
    pygame.display.flip()
    clock.tick(60)

pygame.quit()

