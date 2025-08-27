import pygame
import sys
import random
import math

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)

# Create window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Defenders")
clock = pygame.time.Clock()

# Font
font = pygame.font.SysFont('Arial', 26)


class Player:
    def __init__(self):
        self.width = 50
        self.height = 40
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - self.height - 20
        self.speed = 6
        self.color = GREEN
        self.cooldown = 0
        self.fire_rate = 300  # milliseconds
        self.lives = 3
        self.score = 0
        self.powerup = None
        self.powerup_time = 0
        self.powerup_duration = 5000  # 5 seconds

    def move(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed

        # Keep player on screen
        self.x = max(0, min(WIDTH - self.width, self.x))

    def draw(self):
        # Draw ship body
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

        # Draw ship details
        pygame.draw.polygon(screen, WHITE, [
            (self.x + self.width // 2, self.y - 10),
            (self.x + self.width // 4, self.y),
            (self.x + 3 * self.width // 4, self.y)
        ])

        # Draw engine flames
        flame_height = random.randint(5, 15)
        pygame.draw.polygon(screen, YELLOW, [
            (self.x + self.width // 3, self.y + self.height),
            (self.x + self.width // 3, self.y + self.height + flame_height),
            (self.x + self.width // 2, self.y + self.height + flame_height // 2)
        ])
        pygame.draw.polygon(screen, YELLOW, [
            (self.x + 2 * self.width // 3, self.y + self.height),
            (self.x + 2 * self.width // 3, self.y + self.height + flame_height),
            (self.x + self.width // 2, self.y + self.height + flame_height // 2)
        ])

    def shoot(self, current_time, bullets):
        if current_time - self.cooldown > self.fire_rate:
            bullet_x = self.x + self.width // 2 - 2
            bullet_y = self.y - 10

            # Normal fire
            if self.powerup != "triple":
                bullets.append(Bullet(bullet_x, bullet_y))
            # Triple shot powerup
            else:
                bullets.append(Bullet(bullet_x, bullet_y))
                bullets.append(Bullet(bullet_x - 10, bullet_y, -0.3))
                bullets.append(Bullet(bullet_x + 10, bullet_y, 0.3))

            self.cooldown = current_time

    def check_powerup_status(self, current_time):
        if self.powerup and current_time - self.powerup_time > self.powerup_duration:
            self.powerup = None
            self.fire_rate = 300  # Reset fire rate
            self.speed = 6  # Reset speed
            self.color = GREEN  # Reset color


class Enemy:
    def __init__(self, x, y, enemy_type):
        self.width = 40
        self.height = 30
        self.x = x
        self.y = y
        self.type = enemy_type
        self.health = 1

        if self.type == "zigzag":
            self.color = RED
            self.speed = 2
            self.direction = 1
            self.counter = 0
            self.amplitude = 100
            self.period = 120
            self.base_x = x
        elif self.type == "follower":
            self.color = BLUE
            self.speed = 1.5
            self.health = 2
        elif self.type == "shooter":
            self.color = PURPLE
            self.speed = 1
            self.shoot_timer = random.randint(1000, 3000)
            self.last_shot = 0
        else:  # "normal"
            self.color = RED
            self.speed = 2

    def move(self, player):
        if self.type == "normal":
            self.y += self.speed
        elif self.type == "zigzag":
            self.counter += 1
            self.x = self.base_x + self.amplitude * math.sin(2 * math.pi * self.counter / self.period)
            self.y += self.speed * 0.7
        elif self.type == "follower":
            # Move toward player
            dx = player.x + player.width // 2 - (self.x + self.width // 2)
            direction = 1 if dx > 0 else -1
            self.x += direction * self.speed
            self.y += self.speed
        elif self.type == "shooter":
            self.y += self.speed * 0.5

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

        # Draw details based on enemy type
        if self.type == "normal" or self.type == "zigzag":
            # Eyes
            pygame.draw.circle(screen, WHITE, (int(self.x + 10), int(self.y + 10)), 5)
            pygame.draw.circle(screen, WHITE, (int(self.x + self.width - 10), int(self.y + 10)), 5)
            # Pupils
            pygame.draw.circle(screen, BLACK, (int(self.x + 10), int(self.y + 10)), 2)
            pygame.draw.circle(screen, BLACK, (int(self.x + self.width - 10), int(self.y + 10)), 2)
            # Mouth
            pygame.draw.arc(screen, WHITE, (self.x + 10, self.y + 15, self.width - 20, 10), 0, math.pi, 2)
        elif self.type == "follower":
            # Angry eyes
            pygame.draw.line(screen, WHITE, (self.x + 5, self.y + 10), (self.x + 15, self.y + 5), 2)
            pygame.draw.line(screen, WHITE, (self.x + 5, self.y + 5), (self.x + 15, self.y + 10), 2)
            pygame.draw.line(screen, WHITE, (self.x + self.width - 5, self.y + 10),
                             (self.x + self.width - 15, self.y + 5), 2)
            pygame.draw.line(screen, WHITE, (self.x + self.width - 5, self.y + 5),
                             (self.x + self.width - 15, self.y + 10), 2)
            # Mouth
            pygame.draw.line(screen, WHITE, (self.x + 10, self.y + 20), (self.x + self.width - 10, self.y + 20), 2)
        elif self.type == "shooter":
            # Target eyes
            pygame.draw.circle(screen, WHITE, (int(self.x + 10), int(self.y + 10)), 6)
            pygame.draw.circle(screen, RED, (int(self.x + 10), int(self.y + 10)), 4)
            pygame.draw.circle(screen, WHITE, (int(self.x + self.width - 10), int(self.y + 10)), 6)
            pygame.draw.circle(screen, RED, (int(self.x + self.width - 10), int(self.y + 10)), 4)
            # Antennae
            pygame.draw.line(screen, self.color, (self.x + self.width // 2, self.y),
                             (self.x + self.width // 2, self.y - 10), 2)
            pygame.draw.circle(screen, RED, (int(self.x + self.width // 2), int(self.y - 10)), 3)

    def should_shoot(self, current_time):
        if self.type == "shooter" and current_time - self.last_shot > self.shoot_timer:
            self.last_shot = current_time
            self.shoot_timer = random.randint(1000, 3000)
            return True
        return False


class Bullet:
    def __init__(self, x, y, angle_offset=0):
        self.width = 4
        self.height = 10
        self.x = x
        self.y = y
        self.speed = 7
        self.angle_offset = angle_offset  # For spread shots

    def move(self):
        self.y -= self.speed
        self.x += self.speed * self.angle_offset
        return self.y < -self.height

    def draw(self):
        pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.width, self.height))


class EnemyBullet:
    def __init__(self, x, y):
        self.width = 4
        self.height = 10
        self.x = x
        self.y = y
        self.speed = 5

    def move(self):
        self.y += self.speed
        return self.y > HEIGHT

    def draw(self):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))


class PowerUp:
    def __init__(self, x, y):
        self.width = 20
        self.height = 20
        self.x = x
        self.y = y
        self.speed = 3

        powerup_types = ["rapid", "triple", "speed"]
        self.type = random.choice(powerup_types)

        if self.type == "rapid":
            self.color = YELLOW
        elif self.type == "triple":
            self.color = BLUE
        elif self.type == "speed":
            self.color = GREEN

    def move(self):
        self.y += self.speed
        return self.y > HEIGHT

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

        # Draw icon based on powerup type
        if self.type == "rapid":
            # Clock icon
            pygame.draw.circle(screen, WHITE, (int(self.x + self.width // 2), int(self.y + self.height // 2)), 6, 1)
            pygame.draw.line(screen, WHITE,
                             (self.x + self.width // 2, self.y + self.height // 2),
                             (self.x + self.width // 2, self.y + self.height // 2 - 4), 1)
            pygame.draw.line(screen, WHITE,
                             (self.x + self.width // 2, self.y + self.height // 2),
                             (self.x + self.width // 2 + 3, self.y + self.height // 2), 1)
        elif self.type == "triple":
            # Triple dot icon
            pygame.draw.circle(screen, WHITE, (int(self.x + self.width // 2), int(self.y + self.height // 2 - 3)), 2)
            pygame.draw.circle(screen, WHITE, (int(self.x + self.width // 2 - 4), int(self.y + self.height // 2 + 3)),
                               2)
            pygame.draw.circle(screen, WHITE, (int(self.x + self.width // 2 + 4), int(self.y + self.height // 2 + 3)),
                               2)
        elif self.type == "speed":
            # Lightning icon
            pygame.draw.line(screen, WHITE,
                             (self.x + self.width // 2 - 2, self.y + 5),
                             (self.x + self.width // 2 + 2, self.y + self.height - 5), 2)
            pygame.draw.line(screen, WHITE,
                             (self.x + self.width // 2 + 2, self.y + self.height // 2),
                             (self.x + self.width // 2 - 2, self.y + self.height - 5), 2)


class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 1
        self.max_radius = 20
        self.speed = 1.5
        self.color = YELLOW

    def update(self):
        self.radius += self.speed
        if self.radius >= self.max_radius:
            return True  # Explosion complete
        return False

    def draw(self):
        # Outer explosion
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.radius))
        # Inner explosion
        if self.radius > 5:
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), int(self.radius * 0.7))
        # Core
        if self.radius > 10:
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), int(self.radius * 0.3))


def spawn_enemies(wave):
    enemies = []
    rows = min(3 + wave // 2, 6)  # Increase rows with waves, max 6
    cols = min(5 + wave // 3, 8)  # Increase columns with waves, max 8

    spacing_x = WIDTH // (cols + 1)
    spacing_y = 60

    # Define enemy types distribution based on wave
    enemy_types = ["normal"] * 10  # Start with normal enemies
    if wave >= 2:
        enemy_types.extend(["zigzag"] * 4)  # Add zigzag in wave 2+
    if wave >= 3:
        enemy_types.extend(["follower"] * 3)  # Add followers in wave 3+
    if wave >= 4:
        enemy_types.extend(["shooter"] * 3)  # Add shooters in wave 4+

    for row in range(rows):
        for col in range(cols):
            x = spacing_x * (col + 1) - 20  # Center enemies
            y = spacing_y * (row + 1) - 30
            enemy_type = random.choice(enemy_types)
            enemies.append(Enemy(x, y, enemy_type))

    return enemies


def display_game_over(score, wave):
    screen.fill(BLACK)

    # Game Over text
    game_over_font = pygame.font.SysFont('Arial', 64)
    game_over_text = game_over_font.render("GAME OVER", True, RED)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 80))

    # Score text
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))

    # Wave text
    wave_text = font.render(f"Waves Cleared: {wave - 1}", True, WHITE)
    screen.blit(wave_text, (WIDTH // 2 - wave_text.get_width() // 2, HEIGHT // 2 + 40))

    # Restart instruction
    restart_text = font.render("Press SPACE to restart or ESC to quit", True, WHITE)
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 100))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        clock.tick(FPS)


def draw_starfield(stars, speed):
    for i, star in enumerate(stars):
        # Move star down
        star[1] += speed[i]

        # Reset star if it goes off screen
        if star[1] > HEIGHT:
            star[0] = random.randint(0, WIDTH)
            star[1] = 0
            speed[i] = random.uniform(0.5, 3)

        # Draw star with size based on speed
        size = 1 if speed[i] < 1.5 else 2
        brightness = int(min(255, 100 + speed[i] * 50))
        pygame.draw.circle(screen, (brightness, brightness, brightness), (int(star[0]), int(star[1])), size)

    return stars, speed


def game_loop():
    player = Player()
    bullets = []
    enemy_bullets = []
    enemies = spawn_enemies(1)
    powerups = []
    explosions = []
    wave = 1

    # Create starfield background
    stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT)] for _ in range(100)]
    star_speed = [random.uniform(0.5, 3) for _ in range(100)]

    enemy_spawn_timer = 0
    wave_cleared = False

    running = True
    while running:
        current_time = pygame.time.get_ticks()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE:
                    player.shoot(current_time, bullets)

        # Get keyboard state for continuous movement
        keys = pygame.key.get_pressed()
        player.move(keys)

        # Check for active power-ups
        player.check_powerup_status(current_time)

        # Move bullets and check for offscreen
        bullets = [b for b in bullets if not b.move()]
        enemy_bullets = [b for b in enemy_bullets if not b.move()]

        # Move enemies and check for player collision
        for enemy in enemies[:]:
            enemy.move(player)

            # Check if enemy reached bottom of screen
            if enemy.y > HEIGHT:
                enemies.remove(enemy)
                continue

            # Check for collision with player
            if (player.x < enemy.x + enemy.width and
                    player.x + player.width > enemy.x and
                    player.y < enemy.y + enemy.height and
                    player.y + player.height > enemy.y):

                # Create explosion
                explosions.append(Explosion(enemy.x + enemy.width // 2, enemy.y + enemy.height // 2))
                enemies.remove(enemy)
                player.lives -= 1

                if player.lives <= 0:
                    display_game_over(player.score, wave)
                    return

            # Enemy shooting
            if enemy.should_shoot(current_time):
                enemy_bullets.append(EnemyBullet(enemy.x + enemy.width // 2 - 2, enemy.y + enemy.height))

        # Check bullet collisions with enemies
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if (bullet.x < enemy.x + enemy.width and
                        bullet.x + bullet.width > enemy.x and
                        bullet.y < enemy.y + enemy.height and
                        bullet.y + bullet.height > enemy.y):

                    # Damage enemy
                    enemy.health -= 1

                    if enemy.health <= 0:
                        # Create explosion
                        explosions.append(Explosion(enemy.x + enemy.width // 2, enemy.y + enemy.height // 2))

                        # Chance to drop power-up
                        if random.random() < 0.1:  # 10% chance
                            powerups.append(PowerUp(enemy.x + enemy.width // 2 - 10, enemy.y + enemy.height))

                        enemies.remove(enemy)
                        player.score += 10

                    if bullet in bullets:
                        bullets.remove(bullet)
                    break

        # Check enemy bullet collisions with player
        for bullet in enemy_bullets[:]:
            if (bullet.x < player.x + player.width and
                    bullet.x + bullet.width > player.x and
                    bullet.y < player.y + player.height and
                    bullet.y + bullet.height > player.y):

                enemy_bullets.remove(bullet)
                player.lives -= 1

                # Create explosion
                explosions.append(Explosion(player.x + player.width // 2, player.y + player.height // 2))

                if player.lives <= 0:
                    display_game_over(player.score, wave)
                    return

        # Move power-ups and check for player collision
        for powerup in powerups[:]:
            if powerup.move():
                powerups.remove(powerup)
                continue

            if (player.x < powerup.x + powerup.width and
                    player.x + player.width > powerup.x and
                    player.y < powerup.y + powerup.height and
                    player.y + player.height > powerup.y):

                # Apply power-up effect
                player.powerup = powerup.type
                player.powerup_time = current_time

                if powerup.type == "rapid":
                    player.fire_rate = 150  # Faster firing
                    player.color = YELLOW
                elif powerup.type == "triple":
                    player.fire_rate = 300  # Normal firing, but triple shot
                    player.color = BLUE
                elif powerup.type == "speed":
                    player.speed = 10  # Faster movement
                    player.color = GREEN

                powerups.remove(powerup)

        # Update explosions
        explosions = [exp for exp in explosions if not exp.update()]

        # Check if wave is cleared
        if len(enemies) == 0 and not wave_cleared:
            wave_cleared = True
            enemy_spawn_timer = current_time

        # Spawn new wave after delay
        if wave_cleared and current_time - enemy_spawn_timer > 3000:  # 3 second delay
            wave += 1
            enemies = spawn_enemies(wave)
            wave_cleared = False

        # Draw everything
        screen.fill(BLACK)

        # Draw starfield
        stars, star_speed = draw_starfield(stars, star_speed)

        # Draw game objects
        for bullet in bullets:
            bullet.draw()

        for enemy_bullet in enemy_bullets:
            enemy_bullet.draw()

        for enemy in enemies:
            enemy.draw()

        for powerup in powerups:
            powerup.draw()

        for explosion in explosions:
            explosion.draw()

        player.draw()

        # Draw UI
        # Score
        score_text = font.render(f"Score: {player.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Lives
        lives_text = font.render(f"Lives: {player.lives}", True, WHITE)
        screen.blit(lives_text, (10, 40))

        # Wave
        wave_text = font.render(f"Wave: {wave}", True, WHITE)
        screen.blit(wave_text, (WIDTH - wave_text.get_width() - 10, 10))

        # Power-up status
        if player.powerup:
            powerup_time_left = (player.powerup_duration - (current_time - player.powerup_time)) // 1000
            powerup_text = font.render(f"{player.powerup.capitalize()}: {powerup_time_left}s", True, player.color)
            screen.blit(powerup_text, (WIDTH - powerup_text.get_width() - 10, 40))

        # New wave message
        if wave_cleared:
            time_to_next = 3 - (current_time - enemy_spawn_timer) // 1000
            wave_message = font.render(f"Wave {wave} Cleared! Next wave in {time_to_next}...", True, YELLOW)
            screen.blit(wave_message, (WIDTH // 2 - wave_message.get_width() // 2, HEIGHT // 2))

        pygame.display.flip()
        clock.tick(FPS)


# Main game loop
while True:
    game_loop()