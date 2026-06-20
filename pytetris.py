import pygame
import random
import math
import time
from collections import deque
import json

# =========================================================
# PERFECT 2 PLAYER TETRIS
# PART 1: FOUNDATION ENGINE
# =========================================================

pygame.init()

# =========================================================
# CONFIG
# =========================================================
SCREEN_SHAKE_POWER = 12
FLASH_TIME = 0.15

ENABLE_EFFECTS = True

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900

FPS = 60

BOARD_WIDTH = 10
BOARD_HEIGHT = 22
VISIBLE_HEIGHT = 20

CELL_SIZE = 32

PLAYER1_OFFSET_X = 180
PLAYER2_OFFSET_X = 980
BOARD_OFFSET_Y = 100

GRAVITY = 1 / 60

LOCK_DELAY = 0

DAS = 0.15
ARR = 0.03

MAX_PARTICLES = 400

MAX_LOCK_RESETS = 15

LINE_CLEAR_DELAY = 0.12
SPAWN_DELAY = 0.08

ENABLE_AI = False

AI_MOVE_DELAY = 0.04

FULLSCREEN = False

STATE_PAUSED = 3

# =========================================================
# COLORS
# =========================================================

BLACK = (10, 10, 10)
WHITE = (240, 240, 240)
GRAY = (60, 60, 60)

CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
PURPLE = (160, 0, 240)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 120, 255)
ORANGE = (255, 140, 0)

#GHOST = (120, 120, 120)

COLORS = {
    "I": CYAN,
    "O": YELLOW,
    "T": PURPLE,
    "S": GREEN,
    "Z": RED,
    "J": BLUE,
    "L": ORANGE
}

P1_KEYS = {
    "left": pygame.K_a,
    "right": pygame.K_d,
    "rotate": pygame.K_w,
    "soft": pygame.K_s,
    "hard": pygame.K_SPACE,
    "hold": pygame.K_LSHIFT
}

P2_KEYS = {
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "rotate": pygame.K_UP,
    "soft": pygame.K_DOWN,
    "hard": pygame.K_END,
    "hold": pygame.K_RSHIFT
}

CONTROL_RECTS = []

# =========================================================
# TETROMINOS
# =========================================================

TETROMINOS = {

    "I": [
        [
            [0,0,0,0],
            [1,1,1,1],
            [0,0,0,0],
            [0,0,0,0]
        ],
        [
            [0,0,1,0],
            [0,0,1,0],
            [0,0,1,0],
            [0,0,1,0]
        ],
        [
            [0,0,0,0],
            [0,0,0,0],
            [1,1,1,1],
            [0,0,0,0]
        ],
        [
            [0,1,0,0],
            [0,1,0,0],
            [0,1,0,0],
            [0,1,0,0]
        ]
    ],

    "O": [
        [
            [1,1],
            [1,1]
        ]
    ] * 4,

    "T": [
        [
            [0,1,0],
            [1,1,1],
            [0,0,0]
        ],
        [
            [0,1,0],
            [0,1,1],
            [0,1,0]
        ],
        [
            [0,0,0],
            [1,1,1],
            [0,1,0]
        ],
        [
            [0,1,0],
            [1,1,0],
            [0,1,0]
        ]
    ],

    "S": [
        [
            [0,1,1],
            [1,1,0],
            [0,0,0]
        ],
        [
            [0,1,0],
            [0,1,1],
            [0,0,1]
        ],
        [
            [0,0,0],
            [0,1,1],
            [1,1,0]
        ],
        [
            [1,0,0],
            [1,1,0],
            [0,1,0]
        ]
    ],

    "Z": [
        [
            [1,1,0],
            [0,1,1],
            [0,0,0]
        ],
        [
            [0,0,1],
            [0,1,1],
            [0,1,0]
        ],
        [
            [0,0,0],
            [1,1,0],
            [0,1,1]
        ],
        [
            [0,1,0],
            [1,1,0],
            [1,0,0]
        ]
    ],

    "J": [
        [
            [1,0,0],
            [1,1,1],
            [0,0,0]
        ],
        [
            [0,1,1],
            [0,1,0],
            [0,1,0]
        ],
        [
            [0,0,0],
            [1,1,1],
            [0,0,1]
        ],
        [
            [0,1,0],
            [0,1,0],
            [1,1,0]
        ]
    ],

    "L": [
        [
            [0,0,1],
            [1,1,1],
            [0,0,0]
        ],
        [
            [0,1,0],
            [0,1,0],
            [0,1,1]
        ],
        [
            [0,0,0],
            [1,1,1],
            [1,0,0]
        ],
        [
            [1,1,0],
            [0,1,0],
            [0,1,0]
        ]
    ]
}

# =========================================================
# SRS WALL KICKS
# =========================================================

JLSTZ_KICKS = {

    (0,1): [(0,0),(-1,0),(-1,1),(0,-2),(-1,-2)],
    (1,0): [(0,0),(1,0),(1,-1),(0,2),(1,2)],

    (1,2): [(0,0),(1,0),(1,-1),(0,2),(1,2)],
    (2,1): [(0,0),(-1,0),(-1,1),(0,-2),(-1,-2)],

    (2,3): [(0,0),(1,0),(1,1),(0,-2),(1,-2)],
    (3,2): [(0,0),(-1,0),(-1,-1),(0,2),(-1,2)],

    (3,0): [(0,0),(-1,0),(-1,-1),(0,2),(-1,2)],
    (0,3): [(0,0),(1,0),(1,1),(0,-2),(1,-2)]
}

I_KICKS = {

    (0,1): [(0,0),(-2,0),(1,0),(-2,-1),(1,2)],
    (1,0): [(0,0),(2,0),(-1,0),(2,1),(-1,-2)],

    (1,2): [(0,0),(-1,0),(2,0),(-1,2),(2,-1)],
    (2,1): [(0,0),(1,0),(-2,0),(1,-2),(-2,1)],

    (2,3): [(0,0),(2,0),(-1,0),(2,1),(-1,-2)],
    (3,2): [(0,0),(-2,0),(1,0),(-2,-1),(1,2)],

    (3,0): [(0,0),(1,0),(-2,0),(1,-2),(-2,1)],
    (0,3): [(0,0),(-1,0),(2,0),(-1,2),(2,-1)]
}

# =========================================================
# WINDOW
# =========================================================

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Perfect 2P Tetris")

clock = pygame.time.Clock()

# =========================================================
# FONTS
# =========================================================

font_small = pygame.font.SysFont("consolas", 22)
font_medium = pygame.font.SysFont("consolas", 32)
font_big = pygame.font.SysFont("consolas", 56)


# =========================================================
# FX GLOBALS
# =========================================================

screen_shake = 0
flash_timer = 0

# =========================================================
# HELPERS
# =========================================================

def draw_text(text, font, color, x, y):

    img = font.render(text, True, color)
    screen.blit(img, (x, y))

# =========================================================
# SCREEN SHAKE
# =========================================================

def add_screen_shake(power):

    global screen_shake

    screen_shake = max(
        screen_shake,
        power
    )

# =========================================================
# FLASH
# =========================================================

def trigger_flash():

    global flash_timer

    flash_timer = FLASH_TIME

# =========================================================
# BAG RANDOMIZER
# =========================================================

class BagRandomizer:

    def __init__(self):

        self.queue = deque()
        self.fill()

    def fill(self):

        pieces = ["I","O","T","S","Z","J","L"]
        random.shuffle(pieces)

        for p in pieces:
            self.queue.append(p)

    def next_piece(self):

        if len(self.queue) <= 7:
            self.fill()

        return self.queue.popleft()

# =========================================================
# PARTICLES
# =========================================================

class Particle:

    def __init__(self, x, y, color):

        self.x = x
        self.y = y

        self.dx = random.uniform(-4, 4)
        self.dy = random.uniform(-8, -2)

        self.life = random.randint(20, 40)

        self.color = color

    def update(self):

        self.x += self.dx
        self.y += self.dy

        self.dy += 0.22

        self.dx *= 0.985

        self.life -= 1

    def draw(self):

        radius = max(
            1,
            int(self.life / 8)
        )

        pygame.draw.circle(
            screen,
            self.color,
            (int(self.x), int(self.y)),
            radius
        )

# =========================================================
# END OF PART 1
# =========================================================
# NEXT:
# Part 2:
# - Tetromino Class
# - Board Class
# - Collision System
# - Locking
# - Ghost Piece
# =========================================================
# =========================================================
# PART 2
# TETROMINO + BOARD SYSTEM
# =========================================================

class Tetromino:

    def __init__(self, piece_type):

        self.type = piece_type

        self.rotation = 0

        self.matrix = TETROMINOS[piece_type][0]

        self.x = 3
        self.y = 0

        if piece_type == "O":
            self.x = 4

        self.color = COLORS[piece_type]

        self.lock_timer = 0
        self.lock_resets = 0

        self.grounded = False

        self.last_move_rotate = False
        self.was_kick = False

    def get_cells(self):

        cells = []

        for row in range(len(self.matrix)):
            for col in range(len(self.matrix[row])):

                if self.matrix[row][col]:

                    cells.append(
                        (
                            self.x + col,
                            self.y + row
                        )
                    )

        return cells

    def rotate(self, direction):

        old_rotation = self.rotation

        if direction == 1:
            self.rotation = (self.rotation + 1) % 4
        else:
            self.rotation = (self.rotation - 1) % 4

        self.matrix = TETROMINOS[self.type][self.rotation]

        return old_rotation

# =========================================================
# BOARD
# =========================================================

class Board:

    def __init__(self, player_id):

        self.player_id = player_id

        self.grid = []
        self.pending_garbage = 0
        self.garbage_anim = 0
        self.garbage_delay = 0

        self.attack_effects = []

        for _ in range(BOARD_HEIGHT):

            row = [None for _ in range(BOARD_WIDTH)]
            self.grid.append(row)

        self.randomizer = BagRandomizer()

        self.current = None

        self.hold_piece = None
        self.can_hold = True

        self.next_queue = deque()

        for _ in range(5):
            self.next_queue.append(
                self.randomizer.next_piece()
            )

        self.score = 0
        self.lines = 0
        self.level = 1

        self.back_to_back = False

        self.game_over = False
        # Garbage
        self.pending_garbage = 0
        self.garbage_flash = 0

        # Attack tracking
        self.last_clear_was_tetris = False
        self.last_attack = 0
        self.last_clear_text = ""
        self.clear_text_timer = 0
        self.flash_color = WHITE

        # Statistics
        self.total_pieces = 0
        self.total_attacks = 0

        self.start_time = time.time()

        self.pps = 0
        self.apm = 0

        # Replay
        self.replay_frames = []

        self.gravity_timer = 0
        self.line_clear_delay = 0
        self.spawn_delay = 0

        self.waiting_for_spawn = False

        self.particles = []

        # Apply garbage after lock
        self.apply_garbage()

        self.spawn_piece()

    # =====================================================
    # SPAWN
    # =====================================================

    def spawn_piece(self):

        piece_type = self.next_queue.popleft()

        self.next_queue.append(
            self.randomizer.next_piece()
        )

        self.current = Tetromino(piece_type)

        self.can_hold = True

        if self.collision(
            self.current,
            self.current.x,
            self.current.y
        ):
            self.game_over = True
        self.total_pieces += 1

    # =====================================================
    # HOLD
    # =====================================================

    def hold(self):

        if not self.can_hold:
            return

        self.can_hold = False

        current_type = self.current.type

        if self.hold_piece is None:

            self.hold_piece = current_type

            self.spawn_piece()

        else:

            swap = self.hold_piece

            self.hold_piece = current_type

            self.current = Tetromino(swap)

    # =====================================================
    # COLLISION
    # =====================================================

    def collision(self, piece, x, y, matrix=None):

        if matrix is None:
            matrix = piece.matrix

        for row in range(len(matrix)):
            for col in range(len(matrix[row])):

                if not matrix[row][col]:
                    continue

                board_x = x + col
                board_y = y + row

                if board_x < 0:
                    return True

                if board_x >= BOARD_WIDTH:
                    return True

                if board_y >= BOARD_HEIGHT:
                    return True

                if board_y >= 0:

                    if self.grid[board_y][board_x]:
                        return True

        return False

    # =====================================================
    # MOVE
    # =====================================================

    def move(self, dx):

        new_x = self.current.x + dx

        if not self.collision(
            self.current,
            new_x,
            self.current.y
        ):

            self.current.x = new_x

            # Reset lock delay if grounded
            if self.grounded():

                if self.current.lock_resets < MAX_LOCK_RESETS:

                    self.current.lock_timer = 0
                    self.current.lock_resets += 1

            return True

        return False

    # =====================================================
    # SOFT DROP
    # =====================================================

    def soft_drop(self):

        new_y = self.current.y + 1

        if not self.collision(
            self.current,
            self.current.x,
            new_y
        ):

            self.current.y = new_y

            self.score += 1

            return True

        return False
    
    # =====================================================
    # GROUNDED CHECK
    # =====================================================

    def grounded(self):

        return self.collision(
            self.current,
            self.current.x,
            self.current.y + 1
        )

    # =====================================================
    # HARD DROP
    # =====================================================

   # =====================================================
    # HARD DROP
    # =====================================================

    def hard_drop(self):

        distance = 0

        while not self.collision(
            self.current,
            self.current.x,
            self.current.y + 1
        ):

            self.current.y += 1
            distance += 1

        self.score += distance * 2

        self.lock_piece()

        self.waiting_for_spawn = True
        self.spawn_delay = SPAWN_DELAY

    # =====================================================
    # ROTATION
    # =====================================================

    def rotate(self, direction):

        piece = self.current

        old_rotation = piece.rotation

        piece.rotate(direction)

        new_rotation = piece.rotation

        kicks = []

        if piece.type == "I":
            kicks = I_KICKS.get(
                (old_rotation, new_rotation),
                [(0,0)]
            )

        elif piece.type == "O":
            kicks = [(0,0)]

        else:
            kicks = JLSTZ_KICKS.get(
                (old_rotation, new_rotation),
                [(0,0)]
            )

        for kick_x, kick_y in kicks:

            new_x = piece.x + kick_x
            new_y = piece.y - kick_y

            if not self.collision(
                piece,
                new_x,
                new_y
            ):

                piece.x = new_x
                piece.y = new_y

                piece.last_move_rotate = True
                piece.was_kick = (kick_x != 0 or kick_y != 0)

                return True

        piece.rotation = old_rotation
        piece.matrix = TETROMINOS[piece.type][old_rotation]

        return False

    # =====================================================
    # GHOST PIECE
    # =====================================================

    """def ghost_y(self):

        ghost = self.current.y

        while not self.collision(
            self.current,
            self.current.x,
            ghost + 1
        ):
            ghost += 1

        return ghost"""

    # =====================================================
    # LOCK PIECE
    # =====================================================

    # =====================================================
    # LOCK PIECE
    # =====================================================

    def lock_piece(self):

        tspin = self.detect_tspin()

        for x, y in self.current.get_cells():

            if y >= 0:

                self.grid[y][x] = self.current.color

                if len(self.particles) < MAX_PARTICLES:

                    px = (
                        self.get_offset_x()
                        + x * CELL_SIZE
                        + CELL_SIZE // 2
                    )

                    py = (
                        BOARD_OFFSET_Y
                        + (y - 2) * CELL_SIZE
                        + CELL_SIZE // 2
                    )

                    for _ in range(3):

                        self.particles.append(
                            Particle(px, py, self.current.color)
                        )

        cleared = self.clear_lines()
        if cleared <= 1:
            self.last_attack = 0 
        else: 
            self.last_attack = cleared
        
        #print("ATTACK =", self.last_attack)

        perfect_clear = self.detect_perfect_clear()

        # ============================================
        # GUIDELINE SCORING
        # ============================================

        score_gain = 0
        clear_power = 0

        # ============================================
        # T-SPINS
        # ============================================

        if tspin:
     
            if cleared == 1:
                score_gain += 800 * self.level

            elif cleared == 2:
                score_gain += 1200 * self.level

            elif cleared == 3:
                score_gain += 1600 * self.level

            elif cleared == 4:
                score_gain += 2000 * self.level
                
            else:
                score_gain = 0
            self.score += score_gain
        

        # ============================================
        # NORMAL CLEARS
        # ============================================

        else:

            if cleared == 1:
                score_gain += 100 * self.level

            elif cleared == 2:
                score_gain += 300 * self.level

            elif cleared == 3:
                score_gain += 500 * self.level

            elif cleared == 4:
                score_gain += 800 * self.level

                clear_power = 1


        difficult = (
            tspin or cleared == 4
        )

        if difficult:

            if self.back_to_back:

                score_gain = int(score_gain * 1.5)



            self.back_to_back = True

        else:

            if cleared > 0:

                self.back_to_back = False

        self.score += score_gain

        # ============================================
        # VISUAL FX
        # ============================================

        if ENABLE_EFFECTS:

            if clear_power > 0:

                add_screen_shake(
                    SCREEN_SHAKE_POWER * clear_power
                )

                trigger_flash()

                if clear_power == 1:

                    self.flash_color = CYAN

                elif clear_power == 2:

                    self.flash_color = PURPLE

                else:

                    self.flash_color = WHITE
        # ============================================
        # CLEAR TEXT
        # ============================================

        if tspin:

            if cleared > 0:
                self.last_clear_text = f"T-SPIN {cleared}"
            else:
                self.last_clear_text = "T-SPIN"

        elif cleared == 4:

            self.last_clear_text = "TETRIS"

        elif perfect_clear:

            self.last_clear_text = "PERFECT CLEAR"

        else:

            self.last_clear_text = ""

        self.clear_text_timer = 2.0

        # ============================================
        # RESET ROTATION FLAGS
        # ============================================

        self.current.last_move_rotate = False
        self.current.was_kick = False

        # ============================================
        # APPLY GARBAGE
        # ============================================

        self.apply_garbage()

        self.waiting_for_spawn = True

        self.spawn_delay = SPAWN_DELAY

    # =====================================================
    # CLEAR LINES
    # =====================================================

    # =====================================================
    # CLEAR LINES + ATTACKS
    # =====================================================

    def clear_lines(self):

        cleared = 0

        new_grid = []

        for row in self.grid:

            full = True

            for cell in row:

                if cell is None:
                    full = False
                    break

            if full:

                cleared += 1

            else:

                new_grid.append(row)

        while len(new_grid) < BOARD_HEIGHT:

            new_grid.insert(
                0,
                [None for _ in range(BOARD_WIDTH)]
            )

        self.grid = new_grid

        self.lines += cleared

        self.level = 1 + self.lines // 10

        # ============================================
        # ATTACK CALCULATION
        # ============================================

        attack = 0

        # Single
        if cleared == 1:
            attack = 0

        # Double
        elif cleared == 2:
            attack = 1

        # Triple
        elif cleared == 3:
            attack = 2

        # Tetris
        elif cleared == 4:
            attack = 4

    

        # Back-to-back
        if cleared == 4:

            if self.back_to_back:

                attack += 1

            self.back_to_back = True

        else:

            if cleared > 0:
                self.back_to_back = False

        self.last_attack = attack

        return cleared
    # =====================================================
    # RECEIVE GARBAGE
    # =====================================================

    def receive_garbage(self, amount):

        self.garbage_flash = 1.0
        self.current = None
        self.spawn_piece()   

        self.pending_garbage += amount

        self.garbage_delay = 0.25

        self.garbage_anim = amount * CELL_SIZE

        if self.current:

            self.current.y -= amount

    # =====================================================
    # APPLY GARBAGE
    # =====================================================

    def apply_garbage(self):

        if self.pending_garbage <= 0:
            return

        holes = []

        for _ in range(self.pending_garbage):

            hole = random.randint(
                0,
                BOARD_WIDTH - 1
            )

            holes.append(hole)

        for hole in holes:

            # Push upward
            self.grid.pop(0)

            garbage_row = []

            for x in range(BOARD_WIDTH):

                if x == hole:
                    garbage_row.append(None)
                else:
                    garbage_row.append((90,90,90))

            self.grid.append(garbage_row)

        self.pending_garbage = 0
    
    # =====================================================
    # T-SPIN DETECTION
    # =====================================================

    def detect_tspin(self):

        piece = self.current

        if piece.type != "T":
            return False

        if not piece.last_move_rotate:
            return False

        center_x = piece.x + 1
        center_y = piece.y + 1

        corners = [

            (center_x - 1, center_y - 1),
            (center_x + 1, center_y - 1),
            (center_x - 1, center_y + 1),
            (center_x + 1, center_y + 1)

        ]

        filled = 0

        for x, y in corners:

            if x < 0 or x >= BOARD_WIDTH:
                filled += 1
                continue

            if y >= BOARD_HEIGHT:
                filled += 1
                continue

            if y >= 0:

                if self.grid[y][x]:
                    filled += 1

        return filled >= 3

    # =====================================================
    # PERFECT CLEAR
    # =====================================================

    def detect_perfect_clear(self):

        for row in self.grid:

            for cell in row:

                if cell is not None:
                    return False

        return True
    def add_one_garbage_line(self):

            hole = random.randint(
                0,
                BOARD_WIDTH - 1
            )

            self.grid.pop(0)

            garbage_row = []

            for x in range(BOARD_WIDTH):

                if x == hole:

                    garbage_row.append(None)

                else:

                    garbage_row.append((120,120,120))

            self.grid.append(garbage_row)
    # =====================================================
    # UPDATE
    # =====================================================

    def update(self, dt):

        if self.game_over:
            return

        # ============================================
        # DELAY BEFORE NEXT PIECE
        # ============================================

        if self.waiting_for_spawn:

            self.spawn_delay -= dt

            if self.spawn_delay <= 0:

                self.waiting_for_spawn = False

                self.spawn_piece()

            return

        # ============================================
        # GRAVITY CURVE
        # ============================================

        gravity_speed = max(
            0.03,
            0.8 - ((self.level - 1) * 0.007)
        )

        self.gravity_timer += dt

        if self.gravity_timer >= gravity_speed:

            self.gravity_timer = 0

            moved = self.soft_drop()

            # ========================================
            # LOCK DELAY
            # ========================================

            if not moved:

                self.lock_piece()

            else:

                self.current.lock_timer = 0

        # ============================================
        # PARTICLES
        # ============================================

        for particle in self.particles[:]:

            particle.update()

            if particle.life <= 0:

                self.particles.remove(particle)

        # ============================================
        # CLEAR TEXT TIMER
        # ============================================

        if self.clear_text_timer > 0:

            self.clear_text_timer -= dt
        # ============================================
        # STATS
        # ============================================

        elapsed = max(
            1,
            time.time() - self.start_time
        )

        self.pps = round(
            self.total_pieces / elapsed,
            2
        )

        self.apm = round(
            (self.total_attacks / elapsed) * 60,
            2
        )
        # ============================================
        # GARBAGE FLASH
        # ============================================

        if self.garbage_flash > 0:

            self.garbage_flash -= dt * 3

            if self.garbage_flash < 0:

                self.garbage_flash = 0
               
        
        if self.garbage_delay > 0:

            self.garbage_delay -= dt

        elif self.pending_garbage > 0:

            if self.garbage_anim == 0:

                self.garbage_anim = (
                    self.pending_garbage * CELL_SIZE
                )

            self.garbage_anim -= 2

            if self.garbage_anim <= 0:

                self.garbage_anim = 0

                for _ in range(self.pending_garbage):

                    self.add_one_garbage_line()

                self.pending_garbage = 0

        for effect in self.attack_effects[:]:

            effect["x"] += (
                effect["target_x"]
                - effect["x"]
            ) * 0.2

            if abs(
                effect["target_x"]
                - effect["x"]
            ) < 5:

                self.attack_effects.remove(effect)

    # =====================================================
    # DRAW
    # =====================================================

    def get_offset_x(self):

        if self.player_id == 1:
            return PLAYER1_OFFSET_X

        return PLAYER2_OFFSET_X

    def draw_grid(self):

        ox = self.get_offset_x()

        # Background
        pygame.draw.rect(
            screen,
            (20,20,20),
            (
                ox,
                BOARD_OFFSET_Y,
                BOARD_WIDTH * CELL_SIZE,
                VISIBLE_HEIGHT * CELL_SIZE
            )
        )

        # Grid
        for y in range(2, BOARD_HEIGHT):

            for x in range(BOARD_WIDTH):

                rect = pygame.Rect(
                    ox + x * CELL_SIZE,
                    BOARD_OFFSET_Y
                    + (y - 2) * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )

                pygame.draw.rect(
                    screen,
                    (40,40,40),
                    rect,
                    1
                )

                cell = self.grid[y][x]

                if cell:

                    pygame.draw.rect(
                        screen,
                        cell,
                        rect.inflate(-2, -2)
                    )
        
        if self.pending_garbage > 0:

            for line in range(self.pending_garbage):

                y = (
                    BOARD_OFFSET_Y
                    + VISIBLE_HEIGHT * CELL_SIZE
                    + (self.pending_garbage * CELL_SIZE)
                    - self.garbage_anim
                    + line * CELL_SIZE
                )

                for x in range(BOARD_WIDTH):

                    rect = pygame.Rect(
                        ox + x * CELL_SIZE,
                        y,
                        CELL_SIZE,
                        CELL_SIZE
                    )

                    pygame.draw.rect(
                        screen,
                        (120,120,120),
                        rect.inflate(-2,-2)
                    )
        
        for effect in self.attack_effects:

            pygame.draw.rect(
                screen,
                (255,80,80),
                (
                    effect["x"],
                    effect["y"],
                    80,
                    20 * effect["lines"]
                )
            )

    # =====================================================
    # DRAW GHOST
    # =====================================================

    """def draw_ghost(self):

        ghost_y = self.ghost_y()

        ox = self.get_offset_x()

        for row in range(len(self.current.matrix)):
            for col in range(len(self.current.matrix[row])):

                if self.current.matrix[row][col]:

                    x = self.current.x + col
                    y = ghost_y + row

                    if y >= 2:

                        rect = pygame.Rect(
                            ox + x * CELL_SIZE,
                            BOARD_OFFSET_Y + (y - 2) * CELL_SIZE,
                            CELL_SIZE,
                            CELL_SIZE
                        )

                        pygame.draw.rect(
                            screen,
                            GHOST,
                            rect,
                            2
                        )"""

# =========================================================
# END OF PART 2
# NEXT:
# Part 3:
# - Rendering System
# - UI
# - Next Queue
# - Hold Display
# - Score Panels
# - Piece Rendering
# =========================================================
# =========================================================
# PART 3
# RENDERING + UI SYSTEM
# =========================================================

# =========================================================
# MINI PIECE DRAW
# =========================================================

def draw_mini_piece(piece_type, x, y):

    matrix = TETROMINOS[piece_type][0]

    color = COLORS[piece_type]

    mini = CELL_SIZE // 2

    for row in range(len(matrix)):
        for col in range(len(matrix[row])):

            if matrix[row][col]:

                rect = pygame.Rect(
                    x + col * mini,
                    y + row * mini,
                    mini,
                    mini
                )

                pygame.draw.rect(
                    screen,
                    color,
                    rect.inflate(-2, -2)
                )

# =========================================================
# CURRENT PIECE DRAW
# =========================================================

def draw_current_piece(board):

    piece = board.current

    ox = board.get_offset_x()

    for row in range(len(piece.matrix)):
        for col in range(len(piece.matrix[row])):

            if piece.matrix[row][col]:

                x = piece.x + col
                y = piece.y + row

                if y >= 0:

                    rect = pygame.Rect(
                        ox + x * CELL_SIZE,
                       BOARD_OFFSET_Y + (y - 2) * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE
                    )

                    pygame.draw.rect(
                        screen,
                        piece.color,
                        rect.inflate(-2, -2)
                    )

                    pygame.draw.rect(
                        screen,
                        WHITE,
                        rect,
                        1
                    )

# =========================================================
# HOLD PANEL
# =========================================================

def draw_hold(board):

    ox = board.get_offset_x()

    panel_x = ox - 130
    panel_y = BOARD_OFFSET_Y + 40

    pygame.draw.rect(
        screen,
        (25,25,25),
        (panel_x, panel_y, 100, 100)
    )

    pygame.draw.rect(
        screen,
        GRAY,
        (panel_x, panel_y, 100, 100),
        2
    )

    draw_text(
        "NEXT",
        font_small,
        WHITE,
        panel_x + 12,
        panel_y - 30
    )

    if len(board.next_queue) > 0:

        draw_mini_piece(
            board.next_queue[0],
            panel_x + 20,
            panel_y + 30
        )

# =========================================================
# NEXT QUEUE
# =========================================================

def draw_next(board):

    ox = board.get_offset_x()

    panel_x = ox + BOARD_WIDTH * CELL_SIZE + 30
    panel_y = BOARD_OFFSET_Y + 40

    pygame.draw.rect(
        screen,
        (25,25,25),
        (panel_x, panel_y, 130, 360)
    )

    pygame.draw.rect(
        screen,
        GRAY,
        (panel_x, panel_y, 130, 360),
        2
    )

    draw_text(
        "NEXT",
        font_small,
        WHITE,
        panel_x + 25,
        panel_y - 30
    )

    for i, piece_type in enumerate(board.next_queue):

        py = panel_y + 20 + i * 65

        draw_mini_piece(
            piece_type,
            panel_x + 25,
            py
        )

# =========================================================
# STATS PANEL
# =========================================================

def draw_stats(board):

    ox = board.get_offset_x()

    panel_x = ox - 130
    panel_y = BOARD_OFFSET_Y + 200

    pygame.draw.rect(
        screen,
        (25,25,25),
        (panel_x, panel_y, 120, 520)
    )

    pygame.draw.rect(
        screen,
        GRAY,
        (panel_x, panel_y, 120, 520),
        2
    )

    y = panel_y + 10

    stats = [

        ("SCORE", board.score, CYAN),
        ("LINES", board.lines, GREEN),
        ("LEVEL", board.level, ORANGE),
        ("GARB", board.pending_garbage, RED),
        ("LOCK", board.current.lock_resets, CYAN),
        ("PPS", board.pps, YELLOW),
        ("APM", board.apm, PURPLE),
        ("ATTACK", board.total_attacks, WHITE)

    ]

    for label, value, color in stats:

        draw_text(
            label,
            font_small,
            WHITE,
            panel_x + 10,
            y
        )

        draw_text(
            str(value),
            font_small,
            color,
            panel_x + 10,
            y + 30
        )

        y += 60

# =========================================================
# PARTICLES
# =========================================================

def draw_particles(board):

    for particle in board.particles:

        particle.draw()

# =========================================================
# BOARD FRAME
# =========================================================

def draw_board_frame(board):

    ox = board.get_offset_x()

    pygame.draw.rect(
        screen,
        WHITE,
        (
            ox - 4,
            BOARD_OFFSET_Y - 4,
            BOARD_WIDTH * CELL_SIZE + 8,
            VISIBLE_HEIGHT * CELL_SIZE + 8
        ),
        4
    )

# =========================================================
# PLAYER LABEL
# =========================================================

def draw_player_label(board):

    ox = board.get_offset_x()

    label = f"PLAYER {board.player_id}"

    draw_text(
        label,
        font_medium,
        WHITE,
        ox + 40,
        40
    )


def draw_clear_text(board):

    if board.clear_text_timer <= 0:
        return

    ox = board.get_offset_x()

    pulse = (
        math.sin(
            pygame.time.get_ticks() * 0.01
        ) * 6
    )

    size = int(32 + pulse)

    temp_font = pygame.font.SysFont(
        "consolas",
        size,
        bold=True
    )

    surf = temp_font.render(
        board.last_clear_text,
        True,
        CYAN
    )

    screen.blit(
        surf,
        (
            ox,
            760
        )
    )

# =========================================================
# GAME OVER
# =========================================================

def draw_game_over(board):

    if not board.game_over:
        return

    ox = board.get_offset_x()

    overlay = pygame.Surface(
        (
            BOARD_WIDTH * CELL_SIZE,
            VISIBLE_HEIGHT * CELL_SIZE
        )
    )

    overlay.set_alpha(180)
    overlay.fill((0,0,0))

    screen.blit(
        overlay,
        (ox, BOARD_OFFSET_Y)
    )

    draw_text(
        "GAME OVER",
        font_medium,
        RED,
        ox + 30,
        BOARD_OFFSET_Y + 250
    )

# =========================================================
# BACKGROUND
# =========================================================

# =========================================================
# FPS COUNTER
# =========================================================

def draw_fps():

    fps = int(clock.get_fps())

    draw_text(
        f"FPS: {fps}",
        font_small,
        GREEN,
        20,
        20
    )
# =========================================================
# MATCH TIMER
# =========================================================

def draw_match_timer(board):

    elapsed = int(
        time.time() - board.start_time
    )

    minutes = elapsed // 60
    seconds = elapsed % 60

    text = f"{minutes:02}:{seconds:02}"

    draw_text(
        text,
        font_medium,
        WHITE,
        SCREEN_WIDTH//2 - 50,
        20
    )

# =========================================================
# REPLAY PLAYBACK
# =========================================================

def playback_replay(filename="replay.json"):

    try:

        with open(filename, "r") as f:

            data = json.load(f)

        print(
            f"Loaded replay with "
            f"{len(data['frames'])} frames."
        )

    except:

        print("Replay load failed.")

# =========================================================
# PAUSE OVERLAY
# =========================================================

def draw_pause():

    overlay = pygame.Surface(
        (SCREEN_WIDTH, SCREEN_HEIGHT)
    )

    overlay.set_alpha(180)

    overlay.fill((0,0,0))

    screen.blit(overlay, (0,0))

    draw_center_message(
        "PAUSED",
        YELLOW
    )

# =========================================================
# ATTACK METER
# =========================================================

def draw_attack_meter(board):

    ox = board.get_offset_x()

    height = min(
        400,
        board.pending_garbage * 18
    )

    rect = pygame.Rect(
        ox + BOARD_WIDTH * CELL_SIZE + 8,
        BOARD_OFFSET_Y + (
            VISIBLE_HEIGHT * CELL_SIZE
            - height
        ),
        16,
        height
    )

    color = RED

    if board.garbage_flash > 0:

        pulse = int(
            255 * board.garbage_flash
        )

        color = (
            255,
            pulse,
            pulse
        )

    pygame.draw.rect(
        screen,
        color,
        rect
    )

    pygame.draw.rect(
        screen,
        WHITE,
        rect,
        2
    )

# =========================================================
# WIN COUNTER
# =========================================================

# =========================================================
# WIN ORBS
# =========================================================

# =========================================================
# STAR WIN COUNTER
# =========================================================

# =========================================================
# DRAW STAR
# =========================================================

# =========================================================
# ANIMATED STAR
# =========================================================

def draw_star(x, y, color, scale=0.2):

    size = 12 * scale

    points = [

        (x, y - size),
        (x + size * 0.35, y - size * 0.35),
        (x + size, y - size * 0.35),
        (x + size * 0.5, y + size * 0.15),
        (x + size * 0.7, y + size),
        (x, y + size * 0.5),
        (x - size * 0.7, y + size),
        (x - size * 0.5, y + size * 0.15),
        (x - size, y - size * 0.35),
        (x - size * 0.35, y - size * 0.35)

    ]

    pygame.draw.polygon(
        screen,
        color,
        points
    )

    pygame.draw.polygon(
        screen,
        WHITE,
        points,
        2
    )

    # Glow
    glow = pygame.Surface((80,80), pygame.SRCALPHA)

    pygame.draw.circle(
        glow,
        (255,255,120,80),
        (40,40),
        int(20 * scale)
    )

    screen.blit(
        glow,
        (x - 40, y - 40),
        special_flags=pygame.BLEND_RGBA_ADD
    )
# =========================================================
# RESET MATCH RESULTS
# =========================================================

def reset_match_results():

    global player1_wins
    global player2_wins

    player1_wins = 0
    player2_wins = 0

    print("Match results reset.")
# =========================================================
# STAR WIN COUNTER
# =========================================================

def draw_win_counter():

    p1_y = SCREEN_HEIGHT - 60
    p2_y = SCREEN_HEIGHT - 60

    # ============================================
    # PLAYER 1
    # ============================================

    draw_text(
        "P1",
        font_medium,
        CYAN,
        120,
        p1_y
    )

    for i in range(player1_wins):

        scale = 1.0

        if i == player1_wins - 1:

            scale += (
                math.sin(
                    pygame.time.get_ticks() * 0.02
                ) * 0.3 * p1_star_anim
            )

            scale += p1_star_anim

        """draw_star(
            190 + i * 40,
            p1_y + 12,
            YELLOW,
            scale
        )"""
        draw_text(
            str(player1_wins),
            font_big,
            YELLOW,
            180,
            p1_y-10
        )

    # ============================================
    # PLAYER 2
    # ============================================

    draw_text(
        "P2",
        font_medium,
        ORANGE,
        SCREEN_WIDTH - 320,
        p2_y
    )

    for i in range(player2_wins):

        scale = 1.0

        if i == player2_wins - 1:

            scale += (
                math.sin(
                    pygame.time.get_ticks() * 0.02
                ) * 0.3 * p2_star_anim
            )

            scale += p2_star_anim

        """draw_star(
            SCREEN_WIDTH - 240 + i * 40,
            p2_y + 12,
            YELLOW,
            scale
        )"""
        draw_text(
            str(player2_wins),
            font_big,
            YELLOW,
            SCREEN_WIDTH - 260,
            p2_y-10
        )

# =========================================================
# HUD
# =========================================================

def draw_hud():

    draw_text(
        "F5 SAVE REPLAY",
        font_small,
        GRAY,
        20,
        SCREEN_HEIGHT - 90
    )

    draw_text(
        "F9 LOAD REPLAY",
        font_small,
        GRAY,
        20,
        SCREEN_HEIGHT - 60
    )

    draw_text(
        "F11 FULLSCREEN",
        font_small,
        GRAY,
        20,
        SCREEN_HEIGHT - 30
    )

def draw_background():

    screen.fill((10,10,16))

    # Animated grid dots
    t = pygame.time.get_ticks() * 0.001

    for i in range(120):

        x = (i * 137) % SCREEN_WIDTH

        wave = math.sin(
            t * 2 + i
        ) * 20

        y = ((i * 67) % SCREEN_HEIGHT) + wave

        pygame.draw.circle(
            screen,
            (18,18,26),
            (int(x), int(y)),
            2
        )

def draw_attack_effects(board):

    for effect in board.attack_effects:

        pygame.draw.rect(
            screen,
            (255,0,0),
            (
                effect["x"],
                effect["y"],
                60,
                20
            )
        )
# =========================================================
# FLASH OVERLAY
# =========================================================

def draw_flash_overlay(color):

    global flash_timer

    if flash_timer <= 0:
        return

    alpha = int(
        255 * (
            flash_timer / FLASH_TIME
        )
    )

    overlay = pygame.Surface(
        (SCREEN_WIDTH, SCREEN_HEIGHT)
    )

    overlay.set_alpha(alpha)

    overlay.fill(color)

    screen.blit(overlay, (0,0))

# =========================================================
# FULL BOARD DRAW
# =========================================================

def draw_board(board):

    board.draw_grid()

    #board.draw_ghost()

    draw_current_piece(board)

    draw_board_frame(board)

    draw_hold(board)

    draw_next(board)
    
    draw_attack_meter(board)

    draw_attack_effects(board)

    draw_stats(board)

    draw_particles(board)

    draw_player_label(board)

    draw_clear_text(board)

    draw_game_over(board)

# =========================================================
# CENTER MESSAGE
# =========================================================


def draw_center_message(text, color=WHITE):

    surf = font_big.render(
        text,
        True,
        color
    )

    rect = surf.get_rect(
        center=(SCREEN_WIDTH//2, 100)
    )

    screen.blit(surf, rect)

# =========================================================
# TITLE SCREEN
# =========================================================

def draw_title_screen():

    screen.fill(BLACK)
    draw_center_message(
        "COOL TETRIS",
        CYAN
    )

    draw_text(
        "P1",
        font_medium,
        WHITE,
        320,
        250
    )

    draw_text(
        "A/D : MOVE",
        font_small,
        GRAY,
        320,
        300
    )

    draw_text(
        "S : ROTATE",
        font_small,
        GRAY,
        320,
        340
    )

    draw_text(
        "W : SOFT DROP",
        font_small,
        GRAY,
        320,
        380
    )

    draw_text(
        "SPACE : HARD DROP",
        font_small,
        GRAY,
        320,
        420
    )

    draw_text(
        "P2",
        font_medium,
        WHITE,
        920,
        250
    )

    draw_text(
        "LEFT/RIGHT : MOVE",
        font_small,
        GRAY,
        920,
        300
    )

    draw_text(
        "UP : ROTATE",
        font_small,
        GRAY,
        920,
        340
    )

    draw_text(
        "DOWN : SOFT DROP",
        font_small,
        GRAY,
        920,
        380
    )

    draw_text(
        "END : HARD DROP",
        font_small,
        GRAY,
        920,
        420
    )

    draw_text(
        "PRESS ENTER TO START",
        font_medium,
        GREEN,
        560,
        760
    )
    font_small_2 = pygame.font.Font("C:/Windows/Fonts/seguiemj.ttf", 24)  # Segoe UI Emoji
    
    draw_text(
        "(❁´◡`❁)By B2AST🥸(❁´◡`❁)",
        font_small_2,
        WHITE,
        1200,
        800
    )

# =========================================================
# WINNER SCREEN
# =========================================================

# =========================================================
# WINNER ALERT
# =========================================================

def draw_winner(winner):

    # Dark overlay
    overlay = pygame.Surface(
        (SCREEN_WIDTH, SCREEN_HEIGHT)
    )

    overlay.set_alpha(160)

    overlay.fill((0,0,0))

    screen.blit(overlay, (0,0))

    # Alert box
    box_width = 700
    box_height = 220

    box_x = (
        SCREEN_WIDTH // 2
        - box_width // 2
    )

    box_y = (
        SCREEN_HEIGHT // 2
        - box_height // 2
    )

    pygame.draw.rect(
        screen,
        (30,30,40),
        (
            box_x,
            box_y,
            box_width,
            box_height
        ),
        border_radius=18
    )

    pygame.draw.rect(
        screen,
        CYAN,
        (
            box_x,
            box_y,
            box_width,
            box_height
        ),
        4,
        border_radius=18
    )

    # Winner text
    if winner == 0:

        text = "DRAW GAME"

        color = YELLOW

    else:

        text = f"PLAYER {winner} WINS!"

        color = GREEN

    title_font = pygame.font.SysFont(
        "consolas",
        52,
        bold=True
    )

    text_surface = title_font.render(
        text,
        True,
        color
    )

    text_rect = text_surface.get_rect(
        center=(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 25
        )
    )

    screen.blit(
        text_surface,
        text_rect
    )

    # Subtitle
    sub_font = pygame.font.SysFont(
        "consolas",
        28
    )

    sub = sub_font.render(
        "Next round starts in 3 seconds...",
        True,
        WHITE
    )

    sub_rect = sub.get_rect(
        center=(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 45
        )
    )

    screen.blit(sub, sub_rect)

def draw_controls_menu():

    pygame.draw.rect(
        screen,
        (20,20,20),
        (150,100,700,500)
    )

    pygame.draw.rect(
        screen,
        WHITE,
        (150,100,700,500),
        3
    )

    draw_text(
        "KEY SETTINGS",
        font_small,
        WHITE,
        320,
        120
    )
    CONTROL_RECTS.clear()

    y1 = 220

    for action,key in P1_KEYS.items():

        text = f"P1 a{action} : {pygame.key.name(key)}"

        draw_text(
            text,
            font_small,
            WHITE,
            200,
            y1
        )

        rect = pygame.Rect(
            200,
            y1,
            250,
            30
        )

        CONTROL_RECTS.append(
            (rect, 1, action)
        )
        y1 += 35

    y2 = 220
    for action,key in P2_KEYS.items():

        text = f"P2 {action} : {pygame.key.name(key)}"

        draw_text(
            text,
            font_small,
            WHITE,
            500,
            y2
        )

        rect = pygame.Rect(
            500,
            y2,
            250,
            30
        )

        CONTROL_RECTS.append(
            (rect, 2, action)
        )

        y2 += 35
    if game.waiting_for_key:

        draw_text(
            "PRESS NEW KEY...",
            font_small,
            (255,255,0),
            250,
            550
        )


# =========================================================
# END OF PART 3
# NEXT:
# Part 4:
# - Input System
# - DAS
# - ARR
# - Key Repeat
# - Game States
# - Main Loop
# =========================================================
# =========================================================
# PART 4
# INPUT SYSTEM + DAS/ARR + MAIN LOOP
# =========================================================

# =========================================================
# GAME STATES
# =========================================================

STATE_TITLE = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2
round_end_timer = 0

game_state = STATE_TITLE

player1_wins = 0
player2_wins = 0

winner = None

p1_star_anim = 0
p2_star_anim = 0

# =========================================================
# ATTACK FX
# =========================================================

attack_animations = []

screen_shake = 0

class InputManager:

    def __init__(self):

        self.left_held = False
        self.right_held = False

        self.left_timer = 0
        self.right_timer = 0

        self.left_arr_timer = 0
        self.right_arr_timer = 0

    def reset(self):

        self.left_held = False
        self.right_held = False

        self.left_timer = 0
        self.right_timer = 0

        self.left_arr_timer = 0
        self.right_arr_timer = 0

# =========================================================
# ATTACK ANIMATION
# =========================================================

class AttackAnimation:

    def __init__(
        self,
        start_x,
        start_y,
        end_x,
        end_y
    ):

        self.x = start_x
        self.y = start_y

        self.end_x = end_x
        self.end_y = end_y

        self.life = 0.35

    def update(self, dt):

        speed = 14

        self.x += (
            self.end_x - self.x
        ) * speed * dt

        self.y += (
            self.end_y - self.y
        ) * speed * dt

        self.life -= dt

    def draw(self):

        if self.life <= 0:
            return

        pygame.draw.line(
            screen,
            YELLOW,
            (
                int(self.x),
                int(self.y)
            ),
            (
                int(self.end_x),
                int(self.end_y)
            ),
            6
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (
                int(self.x),
                int(self.y)
            ),
            8
        )

# =========================================================
# PLAYER CONTROLLER
# =========================================================

class PlayerController:

    def __init__(self, board, controls):

        self.board = board

        self.controls = controls

        self.input = InputManager()

    # =====================================================
    # KEYDOWN
    # =====================================================

    def keydown(self, key):

        if self.board.game_over:
            return

        if key == self.controls["left"]:

            self.board.move(-1)

            self.input.left_held = True
            self.input.left_timer = 0
            self.input.left_arr_timer = 0

        elif key == self.controls["right"]:

            self.board.move(1)

            self.input.right_held = True
            self.input.right_timer = 0
            self.input.right_arr_timer = 0

        elif key == self.controls["rotate"]:

            self.board.rotate(-1)

        elif key == self.controls["soft"]:

            self.board.soft_drop()

        elif key == self.controls["hard"]:

            self.board.hard_drop()

        

    # =====================================================
    # KEYUP
    # =====================================================

    def keyup(self, key):

        if key == self.controls["left"]:

            self.input.left_held = False

        elif key == self.controls["right"]:

            self.input.right_held = False

    # =====================================================
    # DAS + ARR
    # =====================================================

    def update(self, dt):

        if self.board.game_over:
            return

        # LEFT
        if self.input.left_held:

            self.input.left_timer += dt

            if self.input.left_timer >= DAS:

                self.input.left_arr_timer += dt

                if self.input.left_arr_timer >= ARR:

                    self.board.move(-1)

                    self.input.left_arr_timer = 0

        # RIGHT
        if self.input.right_held:

            self.input.right_timer += dt

            if self.input.right_timer >= DAS:

                self.input.right_arr_timer += dt

                if self.input.right_arr_timer >= ARR:

                    self.board.move(1)

                    self.input.right_arr_timer = 0

# =========================================================
# GAME CLASS
# =========================================================
# =========================================================
# REPLAY RECORDER
# =========================================================

class ReplayRecorder:

    def __init__(self):

        self.frames = []

        self.recording = True

    def record(self, frame_data):

        if not self.recording:
            return

        self.frames.append(frame_data)

    def save(self, filename="replay.json"):

        data = {
            "frames": self.frames
        }

        with open(filename, "w") as f:

            json.dump(data, f)

    def load(self, filename="replay.json"):

        with open(filename, "r") as f:

            data = json.load(f)

        self.frames = data["frames"]

# =========================================================
# SIMPLE TETRIS AI
# =========================================================

class SimpleAI:

    def __init__(self, board):

        self.board = board

        self.timer = 0

    # =====================================================
    # EVALUATE BOARD
    # =====================================================

    def evaluate(self, grid):

        heights = []

        holes = 0

        for x in range(BOARD_WIDTH):

            h = 0
            found = False

            for y in range(BOARD_HEIGHT):

                if grid[y][x]:

                    if not found:

                        h = BOARD_HEIGHT - y
                        found = True

                elif found:

                    holes += 1

            heights.append(h)

        bumpiness = 0

        for i in range(len(heights)-1):

            bumpiness += abs(
                heights[i] - heights[i+1]
            )

        aggregate = sum(heights)

        score = (
            -0.51 * aggregate
            -0.36 * holes
            -0.18 * bumpiness
        )

        return score

    # =====================================================
    # SIMULATE
    # =====================================================

    def simulate(self, piece, rotation, x_pos):

        matrix = TETROMINOS[piece.type][rotation]

        y = piece.y

        while not self.board.collision(
            piece,
            x_pos,
            y + 1,
            matrix
        ):
            y += 1

        temp = [
            row[:] for row in self.board.grid
        ]

        for row in range(len(matrix)):
            for col in range(len(matrix[row])):

                if matrix[row][col]:

                    gx = x_pos + col
                    gy = y + row

                    if 0 <= gy < BOARD_HEIGHT:

                        temp[gy][gx] = piece.color

        return self.evaluate(temp)

    # =====================================================
    # BEST MOVE
    # =====================================================

    def best_move(self):

        piece = self.board.current

        best_score = -999999
        best_rot = 0
        best_x = piece.x

        for rot in range(4):

            matrix = TETROMINOS[piece.type][rot]

            width = len(matrix[0])

            for x in range(-2, BOARD_WIDTH):

                collision = False

                for row in range(len(matrix)):
                    for col in range(len(matrix[row])):

                        if matrix[row][col]:

                            gx = x + col

                            if gx < 0 or gx >= BOARD_WIDTH:
                                collision = True

                if collision:
                    continue

                score = self.simulate(
                    piece,
                    rot,
                    x
                )

                if score > best_score:

                    best_score = score
                    best_rot = rot
                    best_x = x

        return best_rot, best_x

    # =====================================================
    # UPDATE
    # =====================================================

    def update(self, dt):

        self.timer += dt

        if self.timer < AI_MOVE_DELAY:
            return

        self.timer = 0

        piece = self.board.current

        target_rot, target_x = self.best_move()

        if piece.rotation != target_rot:

            self.board.rotate(1)

            return

        if piece.x < target_x:

            self.board.move(1)

            return

        elif piece.x > target_x:

            self.board.move(-1)

            return

        self.board.hard_drop()

class Game:

    def __init__(self):

        self.reset()
        self.replay = ReplayRecorder()
        self.show_controls = False
        self.waiting_for_key = None

    # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        global winner

        winner = None

        self.board1 = Board(1)
        self.board2 = Board(2)

        self.controller1 = PlayerController(
            self.board1,
            P1_KEYS
        )

        self.controller2 = PlayerController(
            self.board2,
            P2_KEYS
        )

        self.ai = None

        if ENABLE_AI:

            self.ai = SimpleAI(
                self.board2
            )

    # =====================================================
    # UPDATE
    # =====================================================

    def update(self, dt):

        global game_state
        global winner

        self.controller1.update(dt)
        self.controller2.update(dt)
        # AI
        if self.ai:

            self.ai.update(dt)

        self.board1.update(dt)
        self.board2.update(dt)
        # ============================================
        # SEND ATTACKS
        # ============================================

        if self.board1.last_attack > 0:
            
            attack_animations.append(

                AttackAnimation(

                    self.board1.get_offset_x()
                    + BOARD_WIDTH * CELL_SIZE,

                    BOARD_OFFSET_Y + 250,

                    self.board2.get_offset_x(),

                    BOARD_OFFSET_Y + 250
                )
            )

            self.board2.receive_garbage(
                self.board1.last_attack
            )

            self.board1.last_attack = 0

        if self.board2.last_attack > 0:
            
            attack_animations.append(

                AttackAnimation(

                    self.board2.get_offset_x(),

                    BOARD_OFFSET_Y + 250,

                    self.board1.get_offset_x()
                    + BOARD_WIDTH * CELL_SIZE,

                    BOARD_OFFSET_Y + 250
                )
            )

            self.board1.receive_garbage(
                self.board2.last_attack
            )

            self.board2.last_attack = 0

        # WINNER DETECTION
        # ============================================

        global round_end_timer

        if self.board1.game_over and not self.board2.game_over:

            winner = 2

            global player2_wins
            player2_wins += 1
            global p2_star_anim

            p2_star_anim = 1.0

            game_state = STATE_GAME_OVER

            round_end_timer = 3.0

        elif self.board2.game_over and not self.board1.game_over:

            winner = 1

            global player1_wins
            player1_wins += 1
            global p1_star_anim

            p1_star_anim = 1.0

            game_state = STATE_GAME_OVER

            round_end_timer = 3.0

        elif self.board1.game_over and self.board2.game_over:

            winner = 0

            game_state = STATE_GAME_OVER

            round_end_timer = 3.0
        # ============================================
        # REPLAY RECORD
        # ============================================

        self.replay.record({

            "time": time.time(),

            "p1_score": self.board1.score,
            "p2_score": self.board2.score,

            "p1_lines": self.board1.lines,
            "p2_lines": self.board2.lines,

            "p1_attack": self.board1.total_attacks,
            "p2_attack": self.board2.total_attacks
        })
        for anim in attack_animations[:]:

            anim.update(dt)

            if anim.life <= 0:

                attack_animations.remove(anim)
    # =====================================================
    # DRAW
    # =====================================================

    def draw(self):

        global screen_shake
        global flash_timer

        # ============================================
        # SHAKE OFFSET
        # ============================================
        shake_x = 0
        shake_y = 0
        if screen_shake > 0:

            shake_x = random.randint(
                -int(screen_shake),
                int(screen_shake)
            )

            shake_y = random.randint(
                -int(screen_shake),
                int(screen_shake)
            )

            screen_shake *= 0.9

            if screen_shake < 0.5:

                screen_shake = 0

        # ============================================
        # TEMP SURFACE
        # ============================================

        temp_surface = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )

        global screen
        original_screen = screen

        screen = temp_surface

        draw_background()

        draw_board(self.board1)
        draw_board(self.board2)

        pygame.draw.line(
            screen,
            (40,40,40),
            (SCREEN_WIDTH//2, 80),
            (SCREEN_WIDTH//2, SCREEN_HEIGHT-40),
            3
        )

        # ============================================
        # FLASH
        # ============================================

        if flash_timer > 0:

            flash_timer -= 1 / FPS

            flash_color = WHITE

            if self.board1.clear_text_timer > 0:

                flash_color = self.board1.flash_color

            if self.board2.clear_text_timer > 0:

                flash_color = self.board2.flash_color

            draw_flash_overlay(
                flash_color
            )

        # ============================================
        # RESTORE
        # ============================================

        screen = original_screen

        screen.blit(
            temp_surface,
            (shake_x, shake_y)
        )
        draw_fps()
        draw_match_timer(self.board1)
        draw_hud()
        draw_win_counter()
        for anim in attack_animations:
            anim.draw()
        
        if self.show_controls:

            draw_controls_menu()
        
        

# =========================================================
# GAME INSTANCE
# =========================================================

game = Game()

# =========================================================
# MAIN LOOP
# =========================================================

running = True

while running:

    dt = clock.tick(FPS) / 1000.0

    # =====================================================
    # EVENTS
    # =====================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False
        
        # =================================================
        # KEYDOWN
        # =================================================
        elif event.type == pygame.MOUSEBUTTONDOWN:

            if game.show_controls:

                mx, my = event.pos

                for rect, player, action in CONTROL_RECTS:

                    if rect.collidepoint(mx, my):

                        game.waiting_for_key = (
                            player,
                            action
                        )
        elif event.type == pygame.KEYDOWN:
            if game.waiting_for_key:
                player, action = game.waiting_for_key
                if player == 1:
                    P1_KEYS[action] = event.key
                else:
                    P2_KEYS[action] = event.key
                Game.controller1.controls = P1_KEYS
                Game.controller2.controls = P2_KEYS
                game.waiting_for_key = None
                continue
            if event.key == pygame.K_F1:
                game.show_controls = not game.show_controls

            # TITLE SCREEN
            if game_state == STATE_TITLE:

                if event.key == pygame.K_RETURN:

                    game.reset()

                    game_state = STATE_PLAYING

            # PLAYING
            elif game_state == STATE_PLAYING:

                game.controller1.keydown(event.key)
                game.controller2.keydown(event.key)
                # Reset win results
                # ====================================
                # FULL GAME RESET
                # ====================================
                   
                if event.key == pygame.K_F5:

                    player1_wins = 0
                    player2_wins = 0

                    winner = None

                    round_end_timer = 0

                    game.reset()

                    game_state = STATE_PLAYING

                    print("Full game reset.")
                # Pause / Reset
                if event.key == pygame.K_ESCAPE:

                    game_state = STATE_TITLE
               
                # Fullscreen
                if event.key == pygame.K_F11:

                    FULLSCREEN = not FULLSCREEN

                    if FULLSCREEN:

                        screen = pygame.display.set_mode(
                            (
                                SCREEN_WIDTH,
                                SCREEN_HEIGHT
                            ),
                            pygame.FULLSCREEN
                        )

                    else:

                        screen = pygame.display.set_mode(
                            (
                                SCREEN_WIDTH,
                                SCREEN_HEIGHT
                            )
                        )
                # Load replay
                if event.key == pygame.K_F9:

                    playback_replay() 
            
            elif game_state == STATE_PAUSED:

                if event.key == pygame.K_ESCAPE:

                    game_state = STATE_PLAYING
        # =================================================
        # KEYUP
        # =================================================

        elif event.type == pygame.KEYUP:

            if game_state == STATE_PLAYING:

                game.controller1.keyup(event.key)
                game.controller2.keyup(event.key)

    # =====================================================
    # UPDATE
    # =====================================================

    if game_state == STATE_PLAYING:

        game.update(dt)
    # ================================================
    # AUTO NEXT ROUND
    # ================================================
        # ================================================
    # STAR ANIMATION
    # ================================================

    if p1_star_anim > 0:

        p1_star_anim -= dt * 1.5

    if p2_star_anim > 0:

        p2_star_anim -= dt * 1.5

    if game_state == STATE_GAME_OVER:

        round_end_timer -= dt

        if round_end_timer <= 0:

            game.reset()

            game_state = STATE_PLAYING
    
    # =====================================================
    # DRAW
    # =====================================================

    if game_state == STATE_TITLE:

        draw_title_screen()

    elif game_state == STATE_PLAYING:

        game.draw()

    elif game_state == STATE_PAUSED:

        game.draw()

        draw_pause()

        game.draw()

        if winner == 0:

            draw_center_message(
                "DRAW",
                YELLOW
            )

       # else:

           # draw_winner(winner)

        draw_text(
            "PRESS ENTER TO RESTART",
            font_medium,
            WHITE,
            540,
            820
        )
    elif game_state == STATE_GAME_OVER:

        game.draw()

        if winner is not None:

            draw_winner(winner)

    pygame.display.flip()

# =========================================================
# CLEANUP
# =========================================================

pygame.quit()

# =========================================================
# END OF PART 4
# NEXT:
# Part 5:
# - Garbage System
# - Competitive Attacks
# - Tetris Bonus
# - Back-to-Back
# =========================================================