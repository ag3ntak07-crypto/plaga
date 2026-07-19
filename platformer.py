import pygame
import sys

# Constants 
SCREEN_W, SCREEN_H = 1280, 720
TILE_SIZE          = 64
FPS                = 60
GRAVITY            = 0.6
JUMP_FORCE         = -18
MOVE_SPEED         = 5
CAMERA_LERP        = 0.08          # 0 = instant, lower = smoother lag. gng it makes the camera move slightly after the player moves. saw it in hollow knight so i did it to

# Colours
SKY_COLOR          = (30, 30, 46)
WALL_COLOR         = (80, 80, 110)
WALL_EDGE_COLOR    = (110, 110, 150)
DEBUG_GRID_COLOR   = (50, 50, 70)

# ── Level grid  (0 = empty, 1 = wall) ────────────────────────────────────────
# Edit this freely – add rows / columns, change 1s and 0s.
# Row 0 is the TOP of the world. Each cell = TILE_SIZE pixels.
GRID = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,1],
    [1,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

GRID_ROWS = len(GRID)
GRID_COLS = max(len(row) for row in GRID)

# World dimensions in pixels
WORLD_W = GRID_COLS * TILE_SIZE
WORLD_H = GRID_ROWS * TILE_SIZE


# ── Helpers ───────────────────────────────────────────────────────────────────
def build_wall_rects():
    """Return a list of pygame.Rect for every tile == 1."""
    rects = []
    for r, row in enumerate(GRID):
        for c, cell in enumerate(row):
            if cell == 1:
                rects.append(pygame.Rect(c * TILE_SIZE, r * TILE_SIZE,
                                         TILE_SIZE, TILE_SIZE))
    return rects


def lerp(a, b, t):
    return a + (b - a) * t


# ── Camera ────────────────────────────────────────────────────────────────────
class Camera:
    """camera keeps the player centred.
    Call update(player) every frame, then use offset to translate world objects."""

    def __init__(self):
        self.x = 0.0
        self.y = 0.0

    def update(self, target_rect):
        # Desired position: target centred on screen
        target_x = target_rect.centerx - SCREEN_W / 2
        target_y = target_rect.centery - SCREEN_H / 2

        # Smooth lerp (Hollow-Knight-style lag)
        self.x = lerp(self.x, target_x, CAMERA_LERP)
        self.y = lerp(self.y, target_y, CAMERA_LERP)

        # Clamp so we don't show outside the world
        self.x = max(0, min(self.x, WORLD_W - SCREEN_W))
        self.y = max(0, min(self.y, WORLD_H - SCREEN_H))

    @property
    def offset(self):
        return pygame.Vector2(self.x, self.y)

    def apply(self, rect):
        """Return a screen-space Rect for a world-space Rect."""
        return rect.move(-int(self.x), -int(self.y))


# Player 
class Player:
    def __init__(self, x, y, image):
        self.rect   = pygame.Rect(x, y, TILE_SIZE - 8, TILE_SIZE - 4)
        self.vel_x  = 0.0
        self.vel_y  = 0.0
        self.on_ground = False
        self.image  = pygame.transform.scale(image, (self.rect.w, self.rect.h))
        self.flip   = False          # face left / right

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
        self.vel_y += GRAVITY
        if self.vel_y > 20:          # terminal velocity
            self.vel_y = 20

    def move_and_collide(self, walls):
        # ── Horizontal ──────────────────────────────────────────────────────
        self.rect.x += int(self.vel_x)
        for wall in walls:
            if self.rect.colliderect(wall):
                if self.vel_x > 0:
                    self.rect.right = wall.left
                elif self.vel_x < 0:
                    self.rect.left  = wall.right

        # ── Vertical ────────────────────────────────────────────────────────
        self.rect.y += int(self.vel_y)
        self.on_ground = False
        for wall in walls:
            if self.rect.colliderect(wall):
                if self.vel_y > 0:
                    self.rect.bottom = wall.top
                    self.on_ground   = True
                    self.vel_y       = 0
                elif self.vel_y < 0:
                    self.rect.top    = wall.bottom
                    self.vel_y       = 0

        # Clamp inside world
        self.rect.clamp_ip(pygame.Rect(0, 0, WORLD_W, WORLD_H))

    def update(self, walls):
        self.handle_input()
        self.apply_gravity()
        self.move_and_collide(walls)

    def draw(self, surface, camera):
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img, camera.apply(self.rect))


# ── Tile rendering ────────────────────────────────────────────────────────────
def draw_world(surface, wall_rects, camera):
    # Only draw tiles visible on screen (culling)
    screen_rect = pygame.Rect(camera.x, camera.y, SCREEN_W, SCREEN_H)
    for rect in wall_rects:
        if rect.colliderect(screen_rect):
            screen_pos = camera.apply(rect)
            pygame.draw.rect(surface, WALL_COLOR, screen_pos)
            pygame.draw.rect(surface, WALL_EDGE_COLOR, screen_pos, 2)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Platformer Base")
    clock  = pygame.time.Clock()

    # Load character sprite
    try:
        raw_image = pygame.image.load("test.png").convert_alpha()
    except FileNotFoundError:
        # Fallback: magenta rectangle if test.png is missing
        raw_image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        raw_image.fill((220, 60, 220))
        print("⚠  test.png not found – using placeholder sprite.")

    wall_rects = build_wall_rects()

    # Spawn player on top of the floor (row 11 is last empty row)
    spawn_col = 2
    spawn_row = GRID_ROWS - 2          # one row above the bottom wall
    player    = Player(spawn_col * TILE_SIZE + 4,
                       spawn_row * TILE_SIZE - TILE_SIZE,
                       raw_image)

    camera = Camera()
    # Snap camera to player immediately on first frame
    camera.x = player.rect.centerx - SCREEN_W / 2
    camera.y = player.rect.centery - SCREEN_H / 2

    font = pygame.font.SysFont("monospace", 18)

    while True:
        # ── Events ──────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        # ── Update ──────────────────────────────────────────────────────────
        player.update(wall_rects)
        camera.update(player.rect)

        # ── Draw ────────────────────────────────────────────────────────────
        screen.fill(SKY_COLOR)
        draw_world(screen, wall_rects, camera)
        player.draw(screen, camera)

        # HUD
        hud = font.render(
            f"pos: ({player.rect.x}, {player.rect.y})  "
            f"vel: ({player.vel_x:.1f}, {player.vel_y:.1f})  "
            f"grounded: {player.on_ground}",
            True, (200, 200, 200))
        screen.blit(hud, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()