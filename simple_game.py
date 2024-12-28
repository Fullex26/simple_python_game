import pygame
import sys
import random
import os
import time

# ------------------------
# GAME STATES
# ------------------------
STATE_MENU = 0
STATE_PLAY = 1
STATE_PAUSE = 2
STATE_GAME_OVER = 3

pygame.init()

# ------------------------
# SCREEN SETUP
# ------------------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Advanced Game with Adjusted Level/Enemy Logic")

clock = pygame.time.Clock()

# ------------------------
# COLORS & FONTS
# ------------------------
WHITE       = (255, 255, 255)
BLACK       = (  0,   0,   0)
GRAY        = (128, 128, 128)
LIGHTGRAY   = (220, 220, 220)
RED         = (255,   0,   0)
GREEN       = (  0, 255,   0)
BLUE        = (  0,   0, 255)
YELLOW      = (255, 255,   0)

font = pygame.font.SysFont(None, 40)
big_font = pygame.font.SysFont(None, 80)

# ------------------------
# SOUND SETUP (OPTIONAL)
# ------------------------
try:
    coin_sound = pygame.mixer.Sound("coin_sound.wav")  # coin pickup
except pygame.error:
    coin_sound = None

# ------------------------
# GAME VARIABLES
# ------------------------
# Enemies will be 40×40; player is half that = 20×20
enemy_size = 40
player_size = 20

player_speed = 5
player_x = SCREEN_WIDTH // 2 - player_size // 2
player_y = SCREEN_HEIGHT // 2 - player_size // 2

# Score
score = 0

# High Score persistence
high_score = 0
high_score_file = "highscore.txt"
if os.path.exists(high_score_file):
    with open(high_score_file, "r") as f:
        try:
            high_score = int(f.read().strip())
        except ValueError:
            high_score = 0

# Lists to hold multiple coins and enemies
coins = []
enemies = []
powerup = None  # Will hold a dict for the power-up

# We always have 5 coins to collect per level (or customize)
num_coins = 5    

# Min/Max enemy speed
ENEMY_MIN_SPEED = 2
ENEMY_MAX_SPEED = 5

# Player invincibility
invincible = False
invincible_end_time = 0.0

# Leveling rules
level = 1
coins_collected_this_level = 0
COINS_PER_LEVEL = 10  # after collecting 10 coins, move to next level
MAX_ENEMIES = 5       # do not exceed 5 enemies on screen

# Current game state
game_state = STATE_MENU

# ------------------------
# HELPER FUNCTIONS
# ------------------------
def draw_centered_text(text, y, font_obj, color=BLACK):
    """
    Render 'text' centered horizontally at vertical position 'y'.
    """
    text_surface = font_obj.render(text, True, color)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y))
    screen.blit(text_surface, text_rect)

def reset_player():
    """
    Reset the player's position, score, level, and relevant counters.
    """
    global player_x, player_y
    global score, level, coins_collected_this_level
    global invincible, invincible_end_time, enemies

    player_x = SCREEN_WIDTH // 2 - player_size // 2
    player_y = SCREEN_HEIGHT // 2 - player_size // 2
    score = 0
    level = 1
    coins_collected_this_level = 0
    invincible = False
    invincible_end_time = 0.0

    # Clear out old enemies so we can spawn exactly 1 for level 1
    enemies = []

def spawn_coins(num):
    """
    Create a list of coin dictionaries with random positions,
    ensuring coins don't overlap each other.
    """
    global coins
    coins = []
    coin_size = 20
    max_attempts = 100  # Safety: max # times to try finding a valid spot

    for _ in range(num):
        attempts = 0
        while attempts < max_attempts:
            x = random.randint(0, SCREEN_WIDTH - coin_size)
            y = random.randint(0, SCREEN_HEIGHT - coin_size)
            new_coin_rect = pygame.Rect(x, y, coin_size, coin_size)

            # Check overlap with existing coins
            if not any(new_coin_rect.colliderect(c["rect"]) for c in coins):
                coins.append({"rect": new_coin_rect, "color": GREEN})
                break
            attempts += 1

def add_enemy():
    """
    Spawn ONE enemy (size=40). Speed is random within min/max, random direction.
    """
    global enemies
    x = random.randint(0, SCREEN_WIDTH - enemy_size)
    y = random.randint(0, SCREEN_HEIGHT - enemy_size)
    speed_x = random.randint(ENEMY_MIN_SPEED, ENEMY_MAX_SPEED) * random.choice([-1, 1])
    speed_y = random.randint(ENEMY_MIN_SPEED, ENEMY_MAX_SPEED) * random.choice([-1, 1])
    enemies.append({
        "rect": pygame.Rect(x, y, enemy_size, enemy_size),
        "speed_x": speed_x,
        "speed_y": speed_y,
        "color": BLACK
    })

def spawn_powerup():
    """
    Spawn a power-up (blue square), ensuring it doesn't overlap coins or enemies.
    """
    global powerup
    size = 30
    max_attempts = 100

    for _ in range(max_attempts):
        x = random.randint(0, SCREEN_WIDTH - size)
        y = random.randint(0, SCREEN_HEIGHT - size)
        new_rect = pygame.Rect(x, y, size, size)

        # Check overlap with coins or enemies
        if any(new_rect.colliderect(c["rect"]) for c in coins):
            continue
        if any(new_rect.colliderect(e["rect"]) for e in enemies):
            continue

        powerup = {"rect": new_rect, "color": BLUE}
        return
    powerup = None

def save_high_score(new_high_score):
    """Write the new high score to file."""
    with open(high_score_file, "w") as f:
        f.write(str(new_high_score))

# ------------------------
# MENU & GAME OVER SCREENS
# ------------------------
def handle_menu():
    """Handle the main menu: wait for SPACE to start or Q to quit."""
    global game_state

    screen.fill(LIGHTGRAY)
    draw_centered_text("ADVANCED GAME", SCREEN_HEIGHT // 2 - 50, big_font, BLUE)
    draw_centered_text("Press SPACE to START or Q to QUIT", SCREEN_HEIGHT // 2 + 30, font, BLACK)
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Reset the player and game variables
                reset_player()

                # Spawn coins (5) and 1 enemy for level 1
                spawn_coins(num_coins)
                add_enemy()  # level 1 => 1 enemy

                # Optionally spawn a powerup
                spawn_powerup()

                game_state = STATE_PLAY
            elif event.key == pygame.K_q:
                pygame.quit()
                sys.exit()

def handle_game_over():
    """Handle the Game Over screen: show final score and let player restart or quit."""
    global game_state, score

    screen.fill(LIGHTGRAY)
    draw_centered_text("GAME OVER", SCREEN_HEIGHT // 2 - 100, big_font, RED)
    draw_centered_text(f"Your Score: {score}", SCREEN_HEIGHT // 2, font, BLACK)
    draw_centered_text("Press R to RESTART or Q to QUIT", SCREEN_HEIGHT // 2 + 50, font, BLACK)
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                game_state = STATE_MENU
            elif event.key == pygame.K_q:
                pygame.quit()
                sys.exit()

def handle_pause():
    """
    Handle the Pause screen: wait for P to resume or Q to quit.
    """
    global game_state

    screen.fill(GRAY)
    draw_centered_text("PAUSED", SCREEN_HEIGHT // 2 - 50, big_font, YELLOW)
    draw_centered_text("Press P to RESUME or Q to QUIT", SCREEN_HEIGHT // 2 + 30, font, BLACK)
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                game_state = STATE_PLAY
            elif event.key == pygame.K_q:
                pygame.quit()
                sys.exit()

# ------------------------
# GAMEPLAY
# ------------------------
def handle_gameplay():
    """
    Handle the main game state: movement, collisions, UI, leveling, etc.
    """
    global player_x, player_y, score, high_score, game_state
    global invincible, invincible_end_time
    global coins_collected_this_level, level, powerup

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            # Toggle pause
            if event.key == pygame.K_p:
                game_state = STATE_PAUSE

    # Movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        player_y -= player_speed
    if keys[pygame.K_DOWN]:
        player_y += player_speed
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_x += player_speed

    # Keep player in screen bounds
    if player_x < 0:
        player_x = 0
    if player_x > SCREEN_WIDTH - player_size:
        player_x = SCREEN_WIDTH - player_size
    if player_y < 0:
        player_y = 0
    if player_y > SCREEN_HEIGHT - player_size:
        player_y = SCREEN_HEIGHT - player_size

    # Invincibility check: turn off if time is up
    if invincible and time.time() > invincible_end_time:
        invincible = False

    # Update enemies (move, bounce)
    for enemy in enemies:
        e_rect = enemy["rect"]
        e_rect.x += enemy["speed_x"]
        e_rect.y += enemy["speed_y"]

        # Bounce off edges
        if e_rect.left < 0 or e_rect.right > SCREEN_WIDTH:
            enemy["speed_x"] = -enemy["speed_x"]
        if e_rect.top < 0 or e_rect.bottom > SCREEN_HEIGHT:
            enemy["speed_y"] = -enemy["speed_y"]

    # Collision checks
    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)

    # Check coin collisions
    for coin in coins:
        if player_rect.colliderect(coin["rect"]):
            score += 1
            coins_collected_this_level += 1
            if coin_sound:
                coin_sound.play()

            # Respawn this coin in a new random spot
            coin_size = coin["rect"].width
            attempts = 0
            max_attempts = 50
            while attempts < max_attempts:
                x = random.randint(0, SCREEN_WIDTH - coin_size)
                y = random.randint(0, SCREEN_HEIGHT - coin_size)
                new_rect = pygame.Rect(x, y, coin_size, coin_size)
                # Check coin overlap and powerup overlap
                if not any(new_rect.colliderect(c["rect"]) for c in coins if c is not coin):
                    if not (powerup and new_rect.colliderect(powerup["rect"])):
                        coin["rect"] = new_rect
                        break
                attempts += 1

            # Level up if enough coins collected
            if coins_collected_this_level >= COINS_PER_LEVEL:
                level += 1
                coins_collected_this_level = 0

                if level <= 5:
                    # Add 1 new enemy, so total enemies = level
                    add_enemy()
                else:
                    # Already at max enemies (5). Increase enemy speed instead
                    for e in enemies:
                        e["speed_x"] *= 1.1
                        e["speed_y"] *= 1.1

                # Optionally spawn a powerup again
                if not powerup and random.random() < 0.15:  # 15% chance
                    spawn_powerup()

    # Power-up collision
    if powerup:
        if player_rect.colliderect(powerup["rect"]):
            # Player becomes invincible for 5 seconds
            invincible = True
            invincible_end_time = time.time() + 5
            powerup = None

    # Enemy collision => Game Over if NOT invincible
    if not invincible:
        for enemy in enemies:
            if player_rect.colliderect(enemy["rect"]):
                # Update high score if needed
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)

                game_state = STATE_GAME_OVER
                break

    # --- Draw everything ---
    screen.fill(WHITE)

    # Draw coins
    for coin in coins:
        pygame.draw.rect(screen, coin["color"], coin["rect"], border_radius=5)

    # Draw enemies
    for enemy in enemies:
        pygame.draw.rect(screen, enemy["color"], enemy["rect"], border_radius=5)

    # Draw power-up (if exists)
    if powerup:
        pygame.draw.rect(screen, powerup["color"], powerup["rect"], border_radius=5)

    # Draw player
    if invincible:
        pygame.draw.rect(screen, YELLOW, player_rect, border_radius=5)
    else:
        pygame.draw.rect(screen, RED, player_rect, border_radius=5)

    # Display HUD
    score_text = font.render(f"Score: {score}", True, BLACK)
    high_score_text = font.render(f"High Score: {high_score}", True, BLACK)
    level_text = font.render(f"Level: {level}", True, BLACK)
    screen.blit(score_text, (10, 10))
    screen.blit(high_score_text, (10, 50))
    screen.blit(level_text, (10, 90))

    # If invincible, show a small timer
    if invincible:
        remaining = int(invincible_end_time - time.time())
        inv_text = font.render(f"Invincible: {remaining}s", True, BLACK)
        screen.blit(inv_text, (SCREEN_WIDTH - 200, 10))

    pygame.display.flip()
    clock.tick(60)

# ------------------------
# MAIN GAME LOOP
# ------------------------
while True:
    if game_state == STATE_MENU:
        handle_menu()
    elif game_state == STATE_PLAY:
        handle_gameplay()
    elif game_state == STATE_PAUSE:
        handle_pause()
    elif game_state == STATE_GAME_OVER:
        handle_game_over()
