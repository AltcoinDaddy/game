import pygame
import random
import math
import json
import os

# Initialize Pygame
pygame.init()

# Set up the game window
width = 800
height = 600
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Advanced Futuristic Hover Car Racing")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 20, 147)
NEON_GREEN = (57, 255, 20)
NEON_YELLOW = (255, 255, 0)
NEON_ORANGE = (255, 165, 0)
DARK_PURPLE = (48, 25, 52)
DARK_BLUE = (25, 25, 112)
DARK_GREEN = (0, 100, 0)

# Player hover car
player_width = 80
player_height = 40
player_x = width // 2 - player_width // 2
player_y = height - player_height - 20
player_speed = 6
hover_offset = 0

# Game variables
clock = pygame.time.Clock()
score = 0
level = 1
stage = 1
obstacle_speed = 4
font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 64)

# Projectile constants
PROJECTILE_SPEED = 10
PROJECTILE_COLOR = NEON_BLUE
PROJECTILE_SIZE = 5
SHOOT_COOLDOWN = 20  # Frames between shots

# Boss constants
BOSS_WIDTH = 150
BOSS_HEIGHT = 100
BOSS_HEALTH = 50
BOSS_SPEED = 3
BOSS_SHOOT_COOLDOWN = 60

# Upgrade system
upgrades = {
    "speed": 0,
    "fire_rate": 0,
    "projectile_power": 0
}

# High score system
def load_high_score():
    if os.path.exists("high_score.json"):
        with open("high_score.json", "r") as f:
            return json.load(f)
    return 0

def save_high_score(score):
    with open("high_score.json", "w") as f:
        json.dump(score, f)

high_score = load_high_score()

# Obstacle types
NORMAL = 0
FAST = 1
LARGE = 2
ROTATING = 3

# Power-up types
SHIELD = 0
SPEED = 1
SHRINK = 2

def create_hover_car_image(color):
    car = pygame.Surface((player_width, player_height), pygame.SRCALPHA)
    pygame.draw.ellipse(car, color, (0, 0, player_width, player_height))
    pygame.draw.ellipse(car, NEON_BLUE, (player_width // 4, 5, player_width // 2, player_height // 2))
    pygame.draw.ellipse(car, WHITE, (5, player_height - 10, 20, 10), 2)
    pygame.draw.ellipse(car, WHITE, (player_width - 25, player_height - 10, 20, 10), 2)
    return car

# Load images
player_img = create_hover_car_image(NEON_PINK)
obstacle_imgs = [
    create_hover_car_image(NEON_GREEN),  # Normal
    create_hover_car_image(NEON_YELLOW),  # Fast
    pygame.transform.scale(create_hover_car_image(NEON_GREEN), (100, 100)),  # Large
    create_hover_car_image(NEON_ORANGE)  # Rotating
]
powerup_imgs = [
    pygame.Surface((30, 30), pygame.SRCALPHA),  # Shield
    pygame.Surface((30, 30), pygame.SRCALPHA),  # Speed
    pygame.Surface((30, 30), pygame.SRCALPHA)   # Shrink
]
pygame.draw.circle(powerup_imgs[SHIELD], NEON_BLUE, (15, 15), 15)
pygame.draw.polygon(powerup_imgs[SPEED], NEON_YELLOW, [(0, 30), (15, 0), (30, 30)])
pygame.draw.rect(powerup_imgs[SHRINK], NEON_PINK, (0, 0, 30, 30))

# New list to store projectiles and boss projectiles
projectiles = []
boss_projectiles = []

def create_projectile(x, y, is_boss=False):
    return [x + (BOSS_WIDTH // 2 if is_boss else player_width // 2), y, is_boss]

def update_and_draw_projectiles():
    global projectiles, boss_projectiles
    for projectile in projectiles + boss_projectiles:
        projectile[1] += PROJECTILE_SPEED * (-1 if projectile[2] else 1)
        color = NEON_ORANGE if projectile[2] else PROJECTILE_COLOR
        pygame.draw.circle(window, color, (int(projectile[0]), int(projectile[1])), PROJECTILE_SIZE)
    projectiles = [p for p in projectiles if 0 < p[1] < height]
    boss_projectiles = [p for p in boss_projectiles if 0 < p[1] < height]

def create_background(level, stage):
    bg = pygame.Surface((width, height))
    if stage == 1:  # City level
        bg.fill(DARK_BLUE)
        for _ in range(50):
            x = random.randint(0, width)
            building_height = random.randint(100, 300)
            pygame.draw.rect(bg, NEON_BLUE, (x, height - building_height, 40, building_height))
            for i in range(0, building_height, 20):
                pygame.draw.rect(bg, NEON_YELLOW, (x + 5, height - i, 5, 5))
    elif stage == 2:  # Space level
        bg.fill(BLACK)
        for _ in range(200):
            x = random.randint(0, width)
            y = random.randint(0, height)
            pygame.draw.circle(bg, WHITE, (x, y), random.randint(1, 3))
    else:  # Forest level
        bg.fill(DARK_GREEN)
        for _ in range(30):
            x = random.randint(0, width)
            y = random.randint(0, height)
            pygame.draw.polygon(bg, NEON_GREEN, [(x, y), (x - 30, y + 60), (x + 30, y + 60)])
    return bg

# Initialize background
bg_img = create_background(level, stage)

def draw_player(x, y, shrink=False):
    global hover_offset
    hover_offset = math.sin(pygame.time.get_ticks() * 0.01) * 3
    img = pygame.transform.scale(player_img, (player_width // 2, player_height // 2)) if shrink else player_img
    window.blit(img, (x, y + hover_offset))
    pygame.draw.ellipse(window, NEON_PINK, (x + 5, y + player_height + hover_offset, 20, 10), 2)
    pygame.draw.ellipse(window, NEON_PINK, (x + player_width - 25, y + player_height + hover_offset, 20, 10), 2)

def create_obstacle(level, stage):
    weights = [0.7, 0.2, 0.1, 0]
    if level > 3:
        weights = [0.5, 0.3, 0.1, 0.1]
    if level > 6:
        weights = [0.3, 0.3, 0.2, 0.2]
    
    obs_type = random.choices([NORMAL, FAST, LARGE, ROTATING], weights=weights)[0]
    x = random.randint(0, width - obstacle_imgs[obs_type].get_width())
    y = -obstacle_imgs[obs_type].get_height()
    speed = obstacle_speed * (1.5 if obs_type == FAST else 1)
    return [x, y, random.choice([-1, 1]), obs_type, speed, 0]  # Added rotation angle

def draw_obstacles(obstacles):
    for obstacle in obstacles:
        if obstacle[3] == ROTATING:
            rotated_img = pygame.transform.rotate(obstacle_imgs[ROTATING], obstacle[5])
            rect = rotated_img.get_rect(center=(obstacle[0] + obstacle_imgs[ROTATING].get_width()//2, 
                                                obstacle[1] + obstacle_imgs[ROTATING].get_height()//2))
            window.blit(rotated_img, rect.topleft)
        else:
            window.blit(obstacle_imgs[obstacle[3]], (obstacle[0], obstacle[1]))

def create_powerup():
    powerup_type = random.randint(0, 2)
    x = random.randint(0, width - 30)
    y = -30
    return [x, y, powerup_type]

def draw_powerups(powerups):
    for powerup in powerups:
        window.blit(powerup_imgs[powerup[2]], (powerup[0], powerup[1]))

def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    window.blit(text_surface, text_rect)

def title_screen():
    window.fill(DARK_PURPLE)
    draw_text("Futuristic Hover Car Racing", title_font, NEON_PINK, width // 2, height // 3)
    draw_text("Press SPACE to start", font, NEON_BLUE, width // 2, height // 2)
    draw_text("Use LEFT and RIGHT arrows to move", font, NEON_BLUE, width // 2, height * 2 // 3)
    draw_text("Press SPACE to shoot", font, NEON_BLUE, width // 2, height * 3 // 4)
    draw_text(f"High Score: {high_score}", font, NEON_GREEN, width // 2, height * 5 // 6)
    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False

def game_over_screen():
    global high_score
    if score > high_score:
        high_score = score
        save_high_score(high_score)
    
    window.fill(DARK_PURPLE)
    draw_text("Game Over!", title_font, NEON_PINK, width // 2, height // 3)
    draw_text(f"Final Score: {score}", font, NEON_BLUE, width // 2, height // 2)
    draw_text(f"High Score: {high_score}", font, NEON_GREEN, width // 2, height * 3 // 5)
    draw_text("Press R to restart or Q to quit", font, NEON_BLUE, width // 2, height * 2 // 3)
    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                elif event.key == pygame.K_q:
                    return False
    return False

def level_transition_screen(level, stage):
    window.fill(DARK_PURPLE)
    draw_text(f"Level {level} - Stage {stage}", title_font, NEON_PINK, width // 2, height // 3)
    
    if stage == 1:
        environment = "City"
    elif stage == 2:
        environment = "Space"
    else:
        environment = "Forest"
    
    draw_text(f"Environment: {environment}", font, NEON_BLUE, width // 2, height // 2)
    draw_text("Press SPACE to continue", font, NEON_YELLOW, width // 2, height * 2 // 3)
    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False

def create_boss():
    return {
        "x": width // 2 - BOSS_WIDTH // 2,
        "y": 50,
        "health": BOSS_HEALTH,
        "direction": 1,
        "shoot_cooldown": 0
    }

def draw_boss(boss):
    pygame.draw.rect(window, NEON_ORANGE, (boss["x"], boss["y"], BOSS_WIDTH, BOSS_HEIGHT))
    health_width = (BOSS_WIDTH * boss["health"]) // BOSS_HEALTH
    pygame.draw.rect(window, NEON_GREEN, (boss["x"], boss["y"] - 10, health_width, 5))

def update_boss(boss):
    boss["x"] += BOSS_SPEED * boss["direction"]
    if boss["x"] <= 0 or boss["x"] + BOSS_WIDTH >= width:
        boss["direction"] *= -1
    
    boss["shoot_cooldown"] -= 1
    if boss["shoot_cooldown"] <= 0:
        boss_projectiles.append(create_projectile(boss["x"], boss["y"] + BOSS_HEIGHT, True))
        boss["shoot_cooldown"] = BOSS_SHOOT_COOLDOWN

def show_upgrade_screen():
    global upgrades, score
    upgrade_cost = 100
    
    window.fill(DARK_PURPLE)
    draw_text("Upgrades", title_font, NEON_PINK, width // 2, height // 4)
    draw_text(f"Score: {score}", font, NEON_BLUE, width // 2, height // 3)
    
    upgrade_options = [
        ("Speed", "speed"),
        ("Fire Rate", "fire_rate"),
        ("Projectile Power", "projectile_power")
    ]
    
    for i, (name, key) in enumerate(upgrade_options):
        y_pos = height // 2 + i * 50
        draw_text(f"{name} (Level {upgrades[key]}): {upgrade_cost} points", font, NEON_YELLOW, width // 2, y_pos)
    
    draw_text("Press 1, 2, or 3 to upgrade, or SPACE to continue", font, NEON_GREEN, width // 2, height * 3 // 4)
    
    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    upgrade_index = event.key - pygame.K_1
                    if upgrade_index < len(upgrade_options) and score >= upgrade_cost:
                        key = upgrade_options[upgrade_index][1]
                        upgrades[key] += 1
                        score -= upgrade_cost
                        return show_upgrade_screen()  # Show the screen again after upgrading
    
    return False  # Return False to continue the game

def main_game_loop():
    global score, level, stage, player_x, player_speed, bg_img, obstacle_speed, projectiles, shoot_cooldown

    obstacles = []
    powerups = []
    powerup_active = False
    powerup_timer = 0
    powerup_type = None
    running = True
    stage_score = 0
    stage_duration = 1000  # Score points before advancing to next stage
    shoot_cooldown = 0
    boss = None
    boss_stage = False
    
    level_transition_screen(level, stage)
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and shoot_cooldown == 0:
                    projectiles.append(create_projectile(player_x, player_y))
                    shoot_cooldown = max(5, SHOOT_COOLDOWN - upgrades["fire_rate"] * 2)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed + upgrades["speed"]
        if keys[pygame.K_RIGHT] and player_x < width - player_width:
            player_x += player_speed + upgrades["speed"]

        # Update shoot cooldown
        if shoot_cooldown > 0:
            shoot_cooldown -= 1

        # Move and update obstacles or boss
        if boss_stage:
            update_boss(boss)
        else:
            for obstacle in obstacles:
                obstacle[1] += obstacle[4]
                if obstacle[3] != LARGE:  # Non-large obstacles move side to side
                    obstacle[0] += obstacle[2] * 2
                    if obstacle[0] <= 0 or obstacle[0] >= width - obstacle_imgs[obstacle[3]].get_width():
                        obstacle[2] *= -1
                if obstacle[3] == ROTATING:
                    obstacle[5] = (obstacle[5] + 5) % 360  # Rotate by 5 degrees

        # Move power-ups
        for powerup in powerups:
            powerup[1] += obstacle_speed // 2

        # Remove off-screen objects
        if not boss_stage:
            obstacles = [obs for obs in obstacles if obs[1] < height]
        powerups = [pw for pw in powerups if pw[1] < height]

        # Create new obstacles
        if not boss_stage and len(obstacles) < 3 + level:
            obstacles.append(create_obstacle(level, stage))

        # Create new power-ups
        if len(powerups) < 1 and random.random() < 0.02:
            powerups.append(create_powerup())

        # Check for collisions between projectiles and obstacles/boss
        for projectile in projectiles[:]:
            if boss_stage:
                if pygame.Rect(boss["x"], boss["y"], BOSS_WIDTH, BOSS_HEIGHT).collidepoint(projectile[0], projectile[1]):
                    projectiles.remove(projectile)
                    boss["health"] -= 1 + upgrades["projectile_power"]
                    if boss["health"] <= 0:
                        boss_stage = False
                        score += 500
                        stage_score += 500
                        show_upgrade_screen()
            else:
                for obstacle in obstacles[:]:
                    obs_rect = pygame.Rect(obstacle[0], obstacle[1], 
                                           obstacle_imgs[obstacle[3]].get_width(), 
                                           obstacle_imgs[obstacle[3]].get_height())
                    if obs_rect.collidepoint(projectile[0], projectile[1]):
                        obstacles.remove(obstacle)
                        projectiles.remove(projectile)
                        score += 20
                        stage_score += 20
                        break

        # Check for player collisions with obstacles or boss projectiles
        player_rect = pygame.Rect(player_x, player_y + hover_offset, 
                                  player_width // 2 if powerup_type == SHRINK else player_width, 
                                  player_height // 2 if powerup_type == SHRINK else player_height)
        
        for obstacle in obstacles[:]:
            obs_rect = pygame.Rect(obstacle[0], obstacle[1], 
                                   obstacle_imgs[obstacle[3]].get_width(), 
                                   obstacle_imgs[obstacle[3]].get_height())
            if player_rect.colliderect(obs_rect):
                if powerup_type != SHIELD:
                    return game_over_screen()
                else:
                    obstacles.remove(obstacle)
                    score += 10
                    stage_score += 10

        for projectile in boss_projectiles[:]:
            if player_rect.collidepoint(projectile[0], projectile[1]):
                if powerup_type != SHIELD:
                    return game_over_screen()
                else:
                    boss_projectiles.remove(projectile)

        # Check for power-up collection
        for powerup in powerups[:]:
            if player_rect.colliderect(pygame.Rect(powerup[0], powerup[1], 30, 30)):
                powerups.remove(powerup)
                powerup_active = True
                powerup_timer = 300
                powerup_type = powerup[2]
                if powerup_type == SPEED:
                    player_speed = 9 + upgrades["speed"]
                elif powerup_type == SHRINK:
                    player_x += player_width // 4  # Adjust position when shrinking

        # Update power-up timer
        if powerup_active:
            powerup_timer -= 1
            if powerup_timer <= 0:
                powerup_active = False
                powerup_type = None
                player_speed = 6 + upgrades["speed"]

        # Update score, stage, and level
        score += 1
        stage_score += 1
        
        if stage_score >= stage_duration:
            if boss_stage:
                stage += 1
                if stage > 3:
                    stage = 1
                    level += 1
                    obstacle_speed += 0.5
                boss_stage = False
                show_upgrade_screen()
            else:
                boss_stage = True
                boss = create_boss()
            
            bg_img = create_background(level, stage)
            stage_score = 0
            level_transition_screen(level, stage)

        # Draw everything
        window.blit(bg_img, (0, 0))
        draw_player(player_x, player_y, powerup_type == SHRINK)
        if boss_stage:
            draw_boss(boss)
        else:
            draw_obstacles(obstacles)
        draw_powerups(powerups)
        update_and_draw_projectiles()
        draw_text(f"Score: {score}", font, NEON_BLUE, width // 2, 30)
        draw_text(f"Level: {level} - Stage: {stage}", font, NEON_YELLOW, width // 2, 70)
        if powerup_active:
            if powerup_type == SHIELD:
                draw_text("SHIELD ACTIVE!", font, NEON_GREEN, width // 2, 110)
                pygame.draw.circle(window, NEON_BLUE, (player_x + player_width // 2, player_y + player_height // 2), 
                                   player_width // 2 + 10, 2)
            elif powerup_type == SPEED:
                draw_text("SPEED BOOST!", font, NEON_YELLOW, width // 2, 110)
            elif powerup_type == SHRINK:
                draw_text("SHRINK ACTIVE!", font, NEON_PINK, width // 2, 110)

        pygame.display.update()
        clock.tick(60)

    return False

# Main game execution
if __name__ == "__main__":
    while True:
        score = 0
        level = 1
        stage = 1
        player_x = width // 2 - player_width // 2
        player_speed = 6
        obstacle_speed = 4
        bg_img = create_background(level, stage)
        
        title_screen()
        if not main_game_loop():
            break

    pygame.quit()