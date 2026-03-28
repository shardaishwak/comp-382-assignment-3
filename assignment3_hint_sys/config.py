"""Configuration constants for the PCP game."""

import pygame

# ── Screen / layout ────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1280, 860
FPS = 60

# Layout zones (recalculated after toolbar)
TOOLBAR_H   = 100          # top bar height (title + two button rows)
SIDEBAR_W   = 380          # left domino pool
GAP         = 10
CONTENT_Y   = TOOLBAR_H + GAP
CONTENT_H   = SCREEN_H - CONTENT_Y - GAP

POOL_RECT   = pygame.Rect(GAP, CONTENT_Y, SIDEBAR_W, CONTENT_H)
MAIN_X      = GAP + SIDEBAR_W + GAP
MAIN_W      = SCREEN_W - MAIN_X - GAP
WORK_RECT   = pygame.Rect(MAIN_X, CONTENT_Y, MAIN_W, 220)

# ── Colour palette ─────────────────────────────────────────────────────────────
BG          = (14,  18,  32)
TOOLBAR_BG  = (20,  25,  45)
PANEL_BG    = (24,  30,  52)
PANEL_WORK  = (18,  34,  54)
ACCENT      = (72,  98, 175)
ACCENT2     = (50, 160, 200)
WHITE       = (235, 238, 252)
GRAY        = (108, 122, 145)
DARK_GRAY   = (40,  48,  70)
GOLD        = (255, 200,  50)
GREEN_OK    = (50,  190,  90)
RED_ERR     = (210,  60,  60)
ORANGE      = (235, 145,  38)
PURPLE      = (150, 108, 225)
HINT_BG     = (48,  45,  18)
CYAN        = (45,  205, 205)
DIVIDER     = (38,  46,  72)

SQ_COLORS   = {'0': (210, 68, 68), '1': (55, 180, 82), '2': (62, 120, 220)}
SQ_KEYS     = ['0', '1', '2']
MIN_MOVES   = 3

SQ_SZ, SQ_GAP, D_PAD = 20, 3, 7
D_H = 2 * SQ_SZ + 3 * D_PAD + 4

def domino_w(top: str, bot: str) -> int:
    return max(len(top), len(bot), 1) * (SQ_SZ + SQ_GAP) + 2 * D_PAD