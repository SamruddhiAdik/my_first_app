import pygame
import random
import sys

# -----------------------------
# Settings
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60
LANES = 3
LANE_WIDTH = SCREEN_WIDTH // LANES

# Colors
BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (50,50,255)
RED = (255,50,50)
GREEN = (0,200,0)
YELLOW = (255,215,0)
CYAN = (0,255,255)
ORANGE = (255,140,0)
GRAY = (180,180,180)
DARK_GRAY = (100,100,100)

# Player
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
JUMP_HEIGHT = 120
GRAVITY = 6
DUCK_HEIGHT = 30

# Entity
OBSTACLE_WIDTH = 40
OBSTACLE_HEIGHT = 60
COIN_WIDTH = 20
POWER_WIDTH = 25

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Doraemon Subway Surfer")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

# -----------------------------
# Player Class
class Player:
    def __init__(self):
        self.lane = 1
        self.x = self.lane * LANE_WIDTH + (LANE_WIDTH - PLAYER_WIDTH) // 2
        self.y = SCREEN_HEIGHT - PLAYER_HEIGHT - 10
        self.vel_y = 0
        self.is_jumping = False
        self.is_ducking = False
        self.rect = pygame.Rect(self.x, self.y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.color = ORANGE
        self.power = None
        self.power_timer = 0

    def update(self):
        if self.is_jumping:
            self.y += self.vel_y
            self.vel_y += GRAVITY
            if self.y >= SCREEN_HEIGHT - PLAYER_HEIGHT - 10:
                self.y = SCREEN_HEIGHT - PLAYER_HEIGHT - 10
                self.is_jumping = False
                self.vel_y = 0

        self.rect.topleft = (self.x, self.y)

        if self.power_timer > 0:
            self.power_timer -= 1
        else:
            self.power = None

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.vel_y = -JUMP_HEIGHT // 10

    def duck(self):
        if not self.is_jumping:
            self.is_ducking = True
            self.rect.height = DUCK_HEIGHT
            self.rect.y = SCREEN_HEIGHT - DUCK_HEIGHT - 10

    def stand_up(self):
        self.is_ducking = False
        self.rect.height = PLAYER_HEIGHT
        self.rect.y = SCREEN_HEIGHT - PLAYER_HEIGHT - 10

    def move_lane(self, direction):
        new_lane = self.lane + direction
        if 0 <= new_lane < LANES:
            self.lane = new_lane
            self.x = self.lane * LANE_WIDTH + (LANE_WIDTH - PLAYER_WIDTH) // 2

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

# -----------------------------
class Entity:
    def __init__(self, lane, kind='obstacle', size='normal', power_type=None):
        self.kind = kind
        self.size = size
        self.power_type = power_type
        self.x = lane * LANE_WIDTH + (LANE_WIDTH - OBSTACLE_WIDTH) // 2
        self.y = -OBSTACLE_HEIGHT
        self.speed = 8
        self.rect = pygame.Rect(self.x, self.y, OBSTACLE_WIDTH, OBSTACLE_HEIGHT)

    def update(self):
        self.y += self.speed
        self.rect.y = self.y

    def draw(self, surface):
        if self.kind == "coin":
            pygame.draw.circle(surface, YELLOW, self.rect.center, COIN_WIDTH // 2)
        elif self.kind == "power":
            color = CYAN if self.power_type == "shield" else BLUE
            pygame.draw.rect(surface, color, self.rect)
        else:
            if self.size == "low":
                pygame.draw.rect(surface, DARK_GRAY, (self.x, self.y, OBSTACLE_WIDTH, 30))
            elif self.size == "high":
                pygame.draw.rect(surface, BLUE, (self.x, self.y, OBSTACLE_WIDTH, 80))
            else:
                pygame.draw.rect(surface, RED, self.rect)

# -----------------------------
player = Player()
entities = []
score = 0
distance = 0
frame_count = 0
SPAWN_RATE = 50
game_over = False

def spawn_entity():
    lane = random.randint(0, LANES - 1)
    chance = random.randint(0, 100)

    if chance < 60:
        entities.append(Entity(lane, "obstacle", random.choice(["low", "normal", "high"])))
    elif chance < 90:
        entities.append(Entity(lane, "coin"))
    else:
        entities.append(Entity(lane, "power", "normal", random.choice(["shield", "boost"])))

def reset_game():
    global score, distance, frame_count, game_over
    player.__init__()
    entities.clear()
    score = 0
    distance = 0
    frame_count = 0
    game_over = False

# -----------------------------
# Game Loop
while True:
    clock.tick(FPS)
    frame_count += 1

    if not game_over:
        distance += 1

    # Event Control
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if game_over and event.type == pygame.KEYDOWN:
            reset_game()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.move_lane(-1)
    if keys[pygame.K_RIGHT]:
        player.move_lane(1)
    if keys[pygame.K_UP]:
        player.jump()
    if keys[pygame.K_DOWN]:
        player.duck()
    else:
        player.stand_up()

    # Spawn Entities
    if frame_count % SPAWN_RATE == 0 and not game_over:
        spawn_entity()

    # Update
    if not game_over:
        player.update()
        for ent in entities:
            ent.update()

    # Collisions
    for ent in entities[:]:
        if player.rect.colliderect(ent.rect):
            if ent.kind == "obstacle":
                if player.power != "shield":
                    game_over = True
            elif ent.kind == "coin":
                score += 10
            elif ent.kind == "power":
                player.power = ent.power_type
                player.power_timer = 250

            entities.remove(ent)

    # Remove off-screen
    entities = [e for e in entities if e.rect.y < SCREEN_HEIGHT]

    # Draw Screen
    screen.fill(WHITE)
    for i in range(1, LANES):
        pygame.draw.line(screen, GRAY, (i * LANE_WIDTH, 0), (i * LANE_WIDTH, SCREEN_HEIGHT), 2)

    for ent in entities:
        ent.draw(screen)

    player.draw(screen)

    # HUD
    info = font.render(f"Score: {score}  Distance: {distance}  Power: {player.power or 'None'}", True, BLACK)
    screen.blit(info, (10, 10))

    if game_over:
        over_text = font.render("GAME OVER! Press any key to restart", True, RED)
        screen.blit(over_text, (30, SCREEN_HEIGHT//2))

    pygame.display.update()
