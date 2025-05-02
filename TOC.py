import pygame
import math
import random

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Police vs Thief")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLUE = (50, 50, 255)     # Thief
RED = (255, 50, 50)      # Police
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
FONT = pygame.font.SysFont(None, 24)
SMALL_FONT = pygame.font.SysFont(None, 20)

# Thief class
class Thief:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.speed = 5
        self.radius = 50
        self.health = 10
        self.state = 'Idle'

    def move(self, keys):
        moved = False
        if self.health > 0:
            if keys[pygame.K_LEFT]:
                self.x -= self.speed
                moved = True
            if keys[pygame.K_RIGHT]:
                self.x += self.speed
                moved = True
            if keys[pygame.K_UP]:
                self.y -= self.speed
                moved = True
            if keys[pygame.K_DOWN]:
                self.y += self.speed
                moved = True

        if self.health <= 0:
            self.state = "Dead"
        elif moved:
            self.state = "Running"
        else:
            self.state = "Idle"

    def draw(self):
        pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), self.radius)
        # Draw name inside circle
        name_text = SMALL_FONT.render("Without Helmet", True, WHITE)
        screen.blit(name_text, (self.x - name_text.get_width() // 2, self.y - name_text.get_height() // 2))
        # Draw state above circle
        state_text = FONT.render(self.state, True, BLACK)
        screen.blit(state_text, (self.x - state_text.get_width() // 2, self.y - self.radius - 25))

# Police class (FSM NPC)
class Police:
    def __init__(self):
        self.x = random.randint(100, 700)
        self.y = random.randint(100, 500)   
        self.radius = 50
        self.speed = 2
        self.state = 'Idle'
        self.patrol_target = self.random_position()

    def random_position(self):
        return random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)

    def draw(self, thief_alive):
        color = RED if self.state != 'Dead' else GRAY
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
        # Draw name inside circle
        name_text = SMALL_FONT.render("Traffic Police", True, WHITE)
        screen.blit(name_text, (self.x - name_text.get_width() // 2, self.y - name_text.get_height() // 2))
        # Draw state above circle
        state_text = FONT.render(self.state, True, BLACK)
        screen.blit(state_text, (self.x - state_text.get_width() // 2, self.y - self.radius - 25))

    def update(self, thief):
        if thief.health <= 0:
            self.state = 'Dead'
            return

        distance = math.hypot(thief.x - self.x, thief.y - self.y)

        if self.state == 'Idle':
            if random.random() < 0.01:
                self.state = 'Patrolling'

        elif self.state == 'Patrolling':
            self.move_towards(self.patrol_target)
            if self.reached_target(self.patrol_target):
                self.patrol_target = self.random_position()
            if distance < 150:
                self.state = 'Chasing'

        elif self.state == 'Chasing':
            self.move_towards((thief.x, thief.y))
            if distance < 40:
                self.state = 'Attacking'
            elif distance > 200:
                self.state = 'Patrolling'

        elif self.state == 'Attacking':
            if distance > 40:
                self.state = 'Chasing'
            else:
                thief.health -= 0.05
                if thief.health <= 0:
                    thief.health = 0
                    thief.state = 'Caught'
                    self.state = 'Dead'
                else:
                    thief.state = 'Under Attack'

    def move_towards(self, target):
        tx, ty = target
        angle = math.atan2(ty - self.y, tx - self.x)
        self.x += self.speed * math.cos(angle)
        self.y += self.speed * math.sin(angle)

    def reached_target(self, target):
        return math.hypot(self.x - target[0], self.y - target[1]) < 10

# Game loop
def game():
    thief = Thief()
    police = Police()
    running = True
    end_reason = ""

    while running:
        screen.fill(WHITE)
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        thief.move(keys)
        police.update(thief)

        thief.draw()
        police.draw(thief.health > 0)

        # HUD
        hud_text = FONT.render(f"Thief Health: {int(thief.health)}", True, BLACK)
        screen.blit(hud_text, (10, 10))

        if thief.health <= 0:
            end_reason = "Police caught the Thief!"
            running = False

        pygame.display.flip()

    # End screen
    screen.fill(WHITE)
    message = pygame.font.SysFont(None, 48).render(end_reason, True, RED)
    screen.blit(message, (WIDTH // 2 - message.get_width() // 2, HEIGHT // 2 - 20))
    pygame.display.flip()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    game()
