import pygame
import sys
import os

# ── Constants ────────────────────────────────────────────────────────────────
NATIVE_W, NATIVE_H = 1920, 1080   # internal render resolution (matches bg art)
TILE_SIZE           = 90           
FPS                 = 60
GRAVITY             = 0.7
JUMP_FORCE          = -22
MOVE_SPEED          = 9
CAMERA_LERP         = 0.08         # lower = more lag bwteen input and camera movement

# Colours these are placeholders
SKY_COLOR       = (30, 30, 46)
WALL_COLOR      = (80, 80, 110)
WALL_EDGE_COLOR = (110, 110, 150)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def asset(name):
    return os.path.join(BASE_DIR, name)

# ── Level grid  (0 = empty, 1 = wall) 
# 12 rows × 106 columns  →  world = 9600 × 1080 px
# Each row = 90 px tall, each col = 90 px wide.
# Add/remove columns but every row must stay the same length.
GRID = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,0,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,0,0,0,0,1,1,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,0,0,0,0,0,1,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,1,1,1,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

GRID_ROWS = len(GRID)
GRID_COLS = max(len(row) for row in GRID)
WORLD_W   = GRID_COLS * TILE_SIZE   # 9600
WORLD_H   = GRID_ROWS * TILE_SIZE   # 1080

# ── Background zones 
# Each zone covers a horizontal slice of the world.
# Zones are checked left-to-right; first match wins.
# For now they all fall back to a solid colour placeholder
ZONES = [
    {"x_start": 0,    "x_end": 3840,  "bg": "bg_1.jpg",  "fallback": (20,  40,  20)},
    {"x_start": 3840, "x_end": 6720,  "bg": "bg_2.jpg",    "fallback": (20,  20,  40)},
    {"x_start": 6720, "x_end": 9600,  "bg": "bg_3.jpg",  "fallback": (40,  20,  20)},
]

def load_bg_images():
    #Try to load each zone's background store None if file missing
    for zone in ZONES:
        try:
            img = pygame.image.load(asset(zone["bg"])).convert()
            zone["surface"] = pygame.transform.scale(img, (NATIVE_W, NATIVE_H))
        except FileNotFoundError:
            zone["surface"] = None

def build_wall_rects():
    rects = []
    for r, row in enumerate(GRID):
        for c, cell in enumerate(row):
            if cell == 1:
                rects.append(pygame.Rect(c * TILE_SIZE, r * TILE_SIZE,
                                         TILE_SIZE, TILE_SIZE))
    return rects
def build_enemy_spawns():
    spawns = []
    for r, row in enumerate(GRID):
        for c, cell in enumerate(row):
            if cell == 2:
                spawns.append((c * TILE_SIZE, r * TILE_SIZE))
    return spawns
def lerp(a, b, t):
    return a + (b - a) * t


# Camera 
class Camera:
    #Renders to a NATIVE_W *NATIVE_H surface; that surface is then scaled to the actual monitor resolution so the game always looks correct

    def __init__(self):
        self.x = 0.0
        self.y = 0.0

    def update(self, target_rect):
        tx = target_rect.centerx - NATIVE_W / 2
        ty = target_rect.centery - NATIVE_H / 2
        self.x = lerp(self.x, tx, CAMERA_LERP)
        self.y = lerp(self.y, ty, CAMERA_LERP)
        # Clamp to world edges
        self.x = max(0, min(self.x, WORLD_W - NATIVE_W))
        self.y = max(0, min(self.y, WORLD_H - NATIVE_H))

    def apply(self, rect):
        return rect.move(-int(self.x), -int(self.y))


# Player 
class Player:
    def __init__(self, x, y, image):
        self.rect      = pygame.Rect(x, y, TILE_SIZE - 10, TILE_SIZE - 6)
        self.vel_x     = 0.0
        self.vel_y     = 0.0
        self.on_ground = False
        self.flip      = False
        self.image     = pygame.transform.scale(image, (self.rect.w, self.rect.h))

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]:
            self.vel_x = -MOVE_SPEED
            self.flip  = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = MOVE_SPEED
            self.flip  = False
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) \
                and self.on_ground:
            self.vel_y     = JUMP_FORCE
            self.on_ground = False

    def apply_gravity(self):
        self.vel_y = min(self.vel_y + GRAVITY, 22)

    def move_and_collide(self, walls):
        self.rect.x += int(self.vel_x)
        for w in walls:
            if self.rect.colliderect(w):
                if self.vel_x > 0: self.rect.right = w.left
                else:              self.rect.left  = w.right

        self.rect.y   += int(self.vel_y)
        self.on_ground = False
        for w in walls:
            if self.rect.colliderect(w):
                if self.vel_y > 0:
                    self.rect.bottom = w.top
                    self.on_ground   = True
                    self.vel_y       = 0
                else:
                    self.rect.top    = w.bottom
                    self.vel_y       = 0

        self.rect.clamp_ip(pygame.Rect(0, 0, WORLD_W, WORLD_H))

    def update(self, walls):
        self.handle_input()
        self.apply_gravity()
        self.move_and_collide(walls)

    def draw(self, surface, camera):
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img, camera.apply(self.rect))

# Enemy
class Enemy:
    def __init__(self, x, y, image, speed=2):
        w, h = TILE_SIZE - 10, TILE_SIZE - 6
        # y passed in is the TOP of the spawn tile; snap rect bottom to the
        # bottom of that tile (= top of the platform tile below it)
        self.rect      = pygame.Rect(x, y + (TILE_SIZE - h), w, h)
        self.speed     = speed
        self.direction = 1   # 1 = right, -1 = left
        self.image     = pygame.transform.scale(image, (w, h))

    def update(self, walls):
        move_x = self.speed * self.direction
        next_rect = self.rect.move(move_x, 0)

        hit_wall = any(next_rect.colliderect(w) for w in walls)

        foot_x = next_rect.right - 1 if self.direction > 0 else next_rect.left
        probe = pygame.Rect(foot_x, self.rect.bottom + 2, 2, 4)
        ground_ahead = any(probe.colliderect(w) for w in walls)

        if hit_wall or not ground_ahead:
            self.direction *= -1
        else:
            self.rect.x += move_x

    def draw(self, surface, camera):
        img = pygame.transform.flip(self.image, self.direction < 0, False)
        surface.blit(img, camera.apply(self.rect))
def draw_background(surface, camera):
    #Draw the zone background that the camera is currently in
    cam_center_x = camera.x + NATIVE_W / 2
    for zone in ZONES:
        if zone["x_start"] <= cam_center_x < zone["x_end"]:
            if zone["surface"]:
                surface.blit(zone["surface"], (0, 0))
            else:
                surface.fill(zone["fallback"])
            return
    surface.fill(SKY_COLOR)

def draw_world(surface, wall_rects, camera):
    vis = pygame.Rect(camera.x, camera.y, NATIVE_W, NATIVE_H)
    for rect in wall_rects:
        if rect.colliderect(vis):
            sr = camera.apply(rect)
            pygame.draw.rect(surface, WALL_COLOR, sr)
            pygame.draw.rect(surface, WALL_EDGE_COLOR, sr, 2)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    pygame.init()

    # Fullscreen at native monitor resolution
    screen      = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    info        = pygame.display.Info()
    MONITOR_W   = info.current_w
    MONITOR_H   = info.current_h
    pygame.display.set_caption("Platformer")

    # All game rendering happens on this fixed surface, then scaled to screen
    canvas = pygame.Surface((NATIVE_W, NATIVE_H))

    clock = pygame.time.Clock()

    # Load assets
    load_bg_images()
    try:
        raw_image = pygame.image.load(asset("test.png")).convert_alpha()
    except FileNotFoundError:
        raw_image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        raw_image.fill((220, 60, 220))
        print("test.png not found using placeholder sprite.")

    wall_rects = build_wall_rects()
    enemy_spawns = build_enemy_spawns()
    enemies = [Enemy(x, y, raw_image) for x, y in enemy_spawns]

    spawn_col = 1
    spawn_row = GRID_ROWS - 2
    player    = Player(spawn_col * TILE_SIZE + 4,
                       spawn_row * TILE_SIZE - TILE_SIZE,
                       raw_image)

    camera = Camera()
    camera.x = player.rect.centerx - NATIVE_W / 2
    camera.y = player.rect.centery - NATIVE_H / 2

    font = pygame.font.SysFont("monospace", 20)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

        player.update(wall_rects)
        for enemy in enemies:
            enemy.update(wall_rects)
        camera.update(player.rect)

        # ── Render to canvas ─────────────────────────────────────────────────
        draw_background(canvas, camera)
        draw_world(canvas, wall_rects, camera)
        player.draw(canvas, camera)
        for enemy in enemies:
            enemy.draw(canvas, camera)

        # HUD
        hud = font.render(
            f"pos: ({player.rect.x}, {player.rect.y})   zone x: {int(camera.x)}",
            True, (220, 220, 220))
        canvas.blit(hud, (12, 12))

        # ── Scale canvas → fullscreen monitor
        scaled = pygame.transform.scale(canvas, (MONITOR_W, MONITOR_H))
        screen.blit(scaled, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    
    main()