"""UI components for the PCP game."""

import pygame
from config import *

class Button:
    def __init__(self, x, y, w, h, lbl, col=None, icon=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = lbl
        self.col = col or ACCENT
        self.icon = icon
        self._hov = False
        self.active = False  # for toggle/selected state

    def draw(self, surf, font):
        base = tuple(min(v + 30, 255) for v in self.col) if self._hov else self.col
        if self.active:
            base = tuple(min(v + 55, 255) for v in self.col)
        pygame.draw.rect(surf, base, self.rect, border_radius=7)
        border_col = WHITE if self.active else (*(min(v+60,255) for v in self.col),)
        pygame.draw.rect(surf, border_col[:3], self.rect, 1 if not self.active else 2, border_radius=7)
        lbl = (self.icon + ' ' if self.icon else '') + self.label
        t = font.render(lbl, True, WHITE)
        surf.blit(t, t.get_rect(center=self.rect.center))

    def update(self, mx, my):
        self._hov = self.rect.collidepoint(mx, my)

    def clicked(self, ev):
        return ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 \
               and self.rect.collidepoint(ev.pos)

def draw_domino_tile(surf, top, bot, x, y, highlighted=False, ghost=False, hint_score=0.0):
    """Draw a single domino tile."""
    w = domino_w(top, bot)
    h = D_H
    a = 120 if ghost else 255
    bg  = (80, 75, 10) if (highlighted and hint_score >= 80) else \
          (HINT_BG if highlighted else (38, 46, 68) if ghost else DARK_GRAY)
    bdr = GOLD if highlighted else (ACCENT if not ghost else GRAY)
    if not ghost:
        sdw = pygame.Surface((w, h), pygame.SRCALPHA)
        sdw.fill((0, 0, 0, 50))
        surf.blit(sdw, (x + 3, y + 3))
    tile = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(tile, (*bg, a), (0, 0, w, h), border_radius=8)
    pygame.draw.rect(tile, (*bdr, a), (0, 0, w, h), 2, border_radius=8)
    mid = D_PAD + SQ_SZ + D_PAD // 2 + 2
    pygame.draw.line(tile, (*bdr, a), (4, mid), (w - 4, mid), 2)
    def row(s, ry):
        for ci, ch in enumerate(s):
            col = SQ_COLORS.get(ch, (150, 150, 150))
            rx = D_PAD + ci * (SQ_SZ + SQ_GAP)
            pygame.draw.rect(tile, (*col, a), (rx, ry, SQ_SZ, SQ_SZ), border_radius=4)
            pygame.draw.rect(tile, (255, 255, 255, 40), (rx, ry, SQ_SZ, SQ_SZ), 1, border_radius=4)
    row(top, D_PAD)
    row(bot, mid + D_PAD // 2 + 2)
    surf.blit(tile, (x, y))
    if highlighted and hint_score > 0:
        glow = pygame.Surface((w + 8, h + 8), pygame.SRCALPHA)
        intensity = min(185, int(hint_score * 1.7))
        pygame.draw.rect(glow, (255, 225, 45, intensity), (0, 0, w + 8, h + 8), 3, border_radius=10)
        surf.blit(glow, (x - 4, y - 4))