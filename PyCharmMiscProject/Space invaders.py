import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders")

# Clock for controlling game speed
clock = pygame.time.Clock()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 30))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 20
        self.speed = 8

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1
        self.speed = 2

    def update(self):
        self.rect.x += self.speed * self.direction

        # Random chance to shoot
        if random.randint(0, 1000) < 5:
            enemy_bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
            all_sprites.add(enemy_bullet)
            enemy_bullets.add(enemy_bullet)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 15))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = 10

    def update(self):
        self.rect.y -= self.speed
        # Remove bullet if it goes off the top of the screen
        if self.rect.bottom < 0:
            self.kill()


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 15))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed = 7

    def update(self):
        self.rect.y += self.speed
        # Remove bullet if it goes off the bottom of the screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


# Create sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()

# Create player
player = Player()
all_sprites.add(player)

# Create enemies
for row in range(5):
    for column in range(8):
        enemy = Enemy(100 + column * 70, 50 + row * 60)
        all_sprites.add(enemy)
        enemies.add(enemy)

# Score counter
score = 0
font = pygame.font.SysFont(None, 36)

# Game loop
running = True
game_over = False

while running:
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                player.shoot()
            if event.key == pygame.K_r and game_over:
                # Reset the game
                game_over = False
                all_sprites = pygame.sprite.Group()
                enemies = pygame.sprite.Group()
                bullets = pygame.sprite.Group()
                enemy_bullets = pygame.sprite.Group()
                player = Player()
                all_sprites.add(player)
                for row in range(5):
                    for column in range(8):
                        enemy = Enemy(100 + column * 70, 50 + row * 60)
                        all_sprites.add(enemy)
                        enemies.add(enemy)
                score = 0

    if not game_over:
        # Update
        all_sprites.update()

        # Check if enemies reach the edge of the screen
        change_direction = False
        for enemy in enemies:
            if enemy.rect.right >= SCREEN_WIDTH or enemy.rect.left <= 0:
                change_direction = True
                break

        if change_direction:
            for enemy in enemies:
                enemy.direction *= -1
                enemy.rect.y += 20

        # Check for collisions between bullets and enemies
        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for hit in hits:
            score += 10

        # Check for collisions between player and enemy bullets
        player_hit = pygame.sprite.spritecollide(player, enemy_bullets, True)
        if player_hit:
            game_over = True

        # Check if player collides with enemies
        enemy_collision = pygame.sprite.spritecollide(player, enemies, False)
        if enemy_collision:
            game_over = True

        # Check if enemies reached the bottom
        for enemy in enemies:
            if enemy.rect.bottom >= SCREEN_HEIGHT - 50:
                game_over = True
                break

        # Check if all enemies are defeated
        if len(enemies) == 0:
            # Create a new wave of enemies
            for row in range(5):
                for column in range(8):
                    enemy = Enemy(100 + column * 70, 50 + row * 60)
                    all_sprites.add(enemy)
                    enemies.add(enemy)

    # Draw
    screen.fill(BLACK)
    all_sprites.draw(screen)

    # Display score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Display game over message
    if game_over:
        game_over_text = font.render("GAME OVER! Press R to restart", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2))

    # Update display
    pygame.display.flip()

    # Control the game speed
    clock.tick(60)

# Quit the game
pygame.quit()
sys.exit()