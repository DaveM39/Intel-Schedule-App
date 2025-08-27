import pygame
import sys
import random
import math

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 100
BALL_SIZE = 15
SQUARE_SIZE = 50
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
PADDLE_SPEED = 7
BALL_SPEED_X = 5
BALL_SPEED_Y = 5
SQUARE_SPEED = 2
FPS = 60

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong with Chasing Square")
clock = pygame.time.Clock()

# Font for score display
font = pygame.font.SysFont('Arial', 32)


# Game objects
class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.score = 0
        self.velocity = 0

    def move(self):
        self.rect.y += self.velocity
        # Keep paddle on screen
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)


class Ball:
    def __init__(self):
        self.reset()

    def reset(self):
        self.rect = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
        self.velocity_x = BALL_SPEED_X * random.choice((1, -1))
        self.velocity_y = BALL_SPEED_Y * random.choice((1, -1))

    def move(self, left_paddle, right_paddle, chasing_square):
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        # Top and bottom collisions
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.velocity_y *= -1

        # Paddle collisions
        if self.rect.colliderect(left_paddle.rect) or self.rect.colliderect(right_paddle.rect):
            self.velocity_x *= -1
            # Add some randomness to the y velocity
            self.velocity_y = random.uniform(0.8, 1.2) * self.velocity_y

        # Chasing square collision
        if self.rect.colliderect(chasing_square.rect):
            # Determine which side of the square was hit
            dx = self.rect.centerx - chasing_square.rect.centerx
            dy = self.rect.centery - chasing_square.rect.centery

            if abs(dx) > abs(dy):
                self.velocity_x *= -1.1  # Increase speed slightly on bounce
            else:
                self.velocity_y *= -1.1  # Increase speed slightly on bounce

        # Scoring
        if self.rect.left <= 0:
            right_paddle.score += 1
            self.reset()
        if self.rect.right >= WIDTH:
            left_paddle.score += 1
            self.reset()

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)


class ChasingSquare:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - SQUARE_SIZE // 2, HEIGHT // 2 - SQUARE_SIZE // 2, SQUARE_SIZE, SQUARE_SIZE)
        self.speed = SQUARE_SPEED

    def move(self, ball):
        # Calculate direction to the ball
        dx = ball.rect.centerx - self.rect.centerx
        dy = ball.rect.centery - self.rect.centery

        # Normalize the direction
        distance = max(1, math.sqrt(dx * dx + dy * dy))  # Avoid division by zero
        dx = dx / distance
        dy = dy / distance

        # Move toward the ball
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

        # Keep square in the middle area of the screen
        margin = WIDTH // 4
        if self.rect.left < margin:
            self.rect.left = margin
        if self.rect.right > WIDTH - margin:
            self.rect.right = WIDTH - margin
        if self.rect.top < margin:
            self.rect.top = margin
        if self.rect.bottom > HEIGHT - margin:
            self.rect.bottom = HEIGHT - margin

    def draw(self):
        pygame.draw.rect(screen, RED, self.rect)


# Create game objects
left_paddle = Paddle(20, HEIGHT // 2 - PADDLE_HEIGHT // 2)
right_paddle = Paddle(WIDTH - 20 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2)
ball = Ball()
chasing_square = ChasingSquare()

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Paddle controls
        if event.type == pygame.KEYDOWN:
            # Left paddle controls
            if event.key == pygame.K_w:
                left_paddle.velocity = -PADDLE_SPEED
            if event.key == pygame.K_s:
                left_paddle.velocity = PADDLE_SPEED

            # Right paddle controls
            if event.key == pygame.K_UP:
                right_paddle.velocity = -PADDLE_SPEED
            if event.key == pygame.K_DOWN:
                right_paddle.velocity = PADDLE_SPEED

        if event.type == pygame.KEYUP:
            # Left paddle controls
            if event.key in (pygame.K_w, pygame.K_s):
                left_paddle.velocity = 0

            # Right paddle controls
            if event.key in (pygame.K_UP, pygame.K_DOWN):
                right_paddle.velocity = 0

    # Move objects
    left_paddle.move()
    right_paddle.move()
    chasing_square.move(ball)
    ball.move(left_paddle, right_paddle, chasing_square)

    # Draw everything
    screen.fill(BLACK)

    # Draw center line
    pygame.draw.aaline(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))

    # Draw middle area boundary (optional, for visualization)
    margin = WIDTH // 4
    pygame.draw.rect(screen, (30, 30, 30), pygame.Rect(margin, margin, WIDTH - 2 * margin, HEIGHT - 2 * margin), 1)

    # Draw game objects
    left_paddle.draw()
    right_paddle.draw()
    chasing_square.draw()
    ball.draw()

    # Draw scores
    left_score_surface = font.render(str(left_paddle.score), True, WHITE)
    right_score_surface = font.render(str(right_paddle.score), True, WHITE)
    screen.blit(left_score_surface, (WIDTH // 4, 20))
    screen.blit(right_score_surface, (3 * WIDTH // 4, 20))

    # Update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
