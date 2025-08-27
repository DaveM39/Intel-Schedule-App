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
YELLOW = (255, 255, 0)

# Create window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroid Dodge")
clock = pygame.time.Clock()

# Font
font = pygame.font.SysFont('Arial', 26)


class Player:
    def __init__(self):
        self.radius = 15
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.speed = 5
        self.color = YELLOW
        self.trail = []
        self.max_trail = 20

    def move(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed

        # Keep player on screen
        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))

        # Add current position to trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)

    def draw(self):
        # Draw trail
        for i, pos in enumerate(self.trail):
            # Scale opacity based on position in trail
            alpha = int(255 * (i / len(self.trail)))
            color = (min(255, self.color[0]), min(255, self.color[1]), min(255, self.color[2]))
            size = int(self.radius * (i / len(self.trail)))
            if size > 0:
                pygame.draw.circle(screen, color, (int(pos[0]), int(pos[1])), size)

        # Draw player
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def collides_with(self, asteroid):
        distance = math.sqrt((self.x - asteroid.x) ** 2 + (self.y - asteroid.y) ** 2)
        return distance < self.radius + asteroid.radius


class Asteroid:
    def __init__(self):
        self.radius = random.randint(10, 30)

        # Spawn asteroids from the edges
        side = random.randint(0, 3)
        if side == 0:  # Top
            self.x = random.randint(0, WIDTH)
            self.y = -self.radius
            self.vx = random.uniform(-2, 2)
            self.vy = random.uniform(1, 3)
        elif side == 1:  # Right
            self.x = WIDTH + self.radius
            self.y = random.randint(0, HEIGHT)
            self.vx = random.uniform(-3, -1)
            self.vy = random.uniform(-2, 2)
        elif side == 2:  # Bottom
            self.x = random.randint(0, WIDTH)
            self.y = HEIGHT + self.radius
            self.vx = random.uniform(-2, 2)
            self.vy = random.uniform(-3, -1)
        else:  # Left
            self.x = -self.radius
            self.y = random.randint(0, HEIGHT)
            self.vx = random.uniform(1, 3)
            self.vy = random.uniform(-2, 2)

        self.color = (random.randint(150, 200), random.randint(100, 150), random.randint(100, 150))
        self.rotation = 0
        self.rotation_speed = random.uniform(-2, 2)

        # Create a random polygon shape
        self.vertices = []
        num_vertices = random.randint(5, 8)
        for i in range(num_vertices):
            angle = 2 * math.pi * i / num_vertices
            distance = self.radius * random.uniform(0.8, 1.2)
            self.vertices.append((distance * math.cos(angle), distance * math.sin(angle)))

    def move(self):
        self.x += self.vx
        self.y += self.vy
        self.rotation += self.rotation_speed

        # Check if asteroid is off-screen
        if (self.x < -self.radius * 2 or self.x > WIDTH + self.radius * 2 or
                self.y < -self.radius * 2 or self.y > HEIGHT + self.radius * 2):
            return True  # Asteroid should be removed
        return False

    def draw(self):
        # Draw the asteroid as a polygon
        points = []
        for vx, vy in self.vertices:
            # Rotate and translate the vertices
            rot_x = vx * math.cos(self.rotation) - vy * math.sin(self.rotation)
            rot_y = vx * math.sin(self.rotation) + vy * math.cos(self.rotation)
            points.append((self.x + rot_x, self.y + rot_y))

        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.polygon(screen, WHITE, points, 1)  # Outline


def display_game_over(score):
    screen.fill(BLACK)

    # Game Over text
    game_over_font = pygame.font.SysFont('Arial', 64)
    game_over_text = game_over_font.render("GAME OVER", True, RED)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))

    # Score text
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 30))

    # Restart instruction
    restart_text = font.render("Press SPACE to restart or ESC to quit", True, WHITE)
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 70))

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


def game_loop():
    player = Player()
    asteroids = []
    score = 0
    asteroid_timer = 0
    asteroid_spawn_rate = 1000  # milliseconds
    game_time = 0
    difficulty_increase_rate = 10000  # increase difficulty every 10 seconds

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

        # Get keyboard state for continuous movement
        keys = pygame.key.get_pressed()
        player.move(keys)

        # Spawn new asteroids
        if current_time - asteroid_timer > asteroid_spawn_rate:
            asteroids.append(Asteroid())
            asteroid_timer = current_time

            # Increase score just for surviving
            score += 1

        # Update asteroid positions and check collisions
        asteroids_to_remove = []
        for i, asteroid in enumerate(asteroids):
            if asteroid.move():  # Returns True if asteroid is off-screen
                asteroids_to_remove.append(i)
            elif player.collides_with(asteroid):
                display_game_over(score)
                return  # End the game

        # Remove off-screen asteroids
        for i in sorted(asteroids_to_remove, reverse=True):
            asteroids.pop(i)

        # Increase difficulty over time
        game_time += clock.get_time()
        if game_time > difficulty_increase_rate:
            game_time = 0
            asteroid_spawn_rate = max(200, asteroid_spawn_rate - 50)  # Increase spawn rate

        # Draw everything
        screen.fill(BLACK)

        # Draw stars in background
        for i in range(100):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            brightness = random.randint(100, 255)
            size = random.randint(1, 2)
            pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), size)

        for asteroid in asteroids:
            asteroid.draw()
        player.draw()

        # Draw score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)


# Main game loop
while True:
    game_loop()