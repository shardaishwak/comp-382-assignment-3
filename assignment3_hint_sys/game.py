"""Main game class with UI and game logic."""

import pygame
import sys
from typing import Optional, List, Dict, Tuple
from config import *
from state import Hint, HintType
from domino import generate_dominos
from hint_system import compute_hints
from ui import Button, draw_domino_tile

class PCPGame:
    DIFFICULTIES = {
        'Easy':   dict(num_dominos=6,  min_string_len=1, max_string_len=2, min_solution_moves=3),
        'Medium': dict(num_dominos=8,  min_string_len=1, max_string_len=3, min_solution_moves=4),
        'Hard':   dict(num_dominos=10, min_string_len=2, max_string_len=4, min_solution_moves=5),
        'Expert': dict(num_dominos=12, min_string_len=2, max_string_len=5, min_solution_moves=6),
    }

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
        pygame.display.set_caption("Post Correspondence Problem — PCP Puzzle")
        self.clock = pygame.time.Clock()

        # Fonts
        self.f_title = pygame.font.SysFont('segoeui', 22, bold=True)
        self.f_label = pygame.font.SysFont('segoeui', 15, bold=True)
        self.f_body  = pygame.font.SysFont('segoeui', 14)
        self.f_small = pygame.font.SysFont('segoeui', 12)

        self.current_diff = 'Medium'
        self._apply_difficulty('Medium')
        self._build_ui()
        self.new_game()

    def _apply_difficulty(self, name):
        self.current_diff = name
        cfg = self.DIFFICULTIES[name]
        self.num_dominos       = cfg['num_dominos']
        self.min_string_len    = cfg['min_string_len']
        self.max_string_len    = cfg['max_string_len']
        self.min_solution_moves = cfg['min_solution_moves']

    def _build_ui(self):
        """Build all UI buttons with clean non-overlapping layout."""
        # Row 1 (y=8): Difficulty tabs — shifted left of centre
        diff_labels = list(self.DIFFICULTIES.keys())
        diff_colors = {
            'Easy':   (38, 120, 78),
            'Medium': (120, 115, 38),
            'Hard':   (150, 65, 40),
            'Expert': (125, 48, 140),
        }
        bw, bh = 90, 30
        # Anchor from 200px instead of centre — shifts tabs left
        start_x = 200
        self.diff_btns = {}
        for i, name in enumerate(diff_labels):
            x = start_x + i * (bw + 6)
            btn = Button(x, 8, bw, bh, name, diff_colors[name])
            self.diff_btns[name] = btn

        # Row 1 right: Action buttons — same row as diff tabs, right-aligned
        aw, ah = 105, 30
        ax = SCREEN_W - 4 * (aw + 6) - 8
        self.btn_new   = Button(ax,             8, aw, ah, "New Game",  (38, 118, 78),  '↺')
        self.btn_clear = Button(ax + aw + 6,    8, aw, ah, "Clear",     (155, 62, 40),  '⌫')
        self.btn_undo  = Button(ax + 2*(aw+6),  8, aw, ah, "Undo",      (55, 75, 135),  '←')
        self.btn_hint  = Button(ax + 3*(aw+6),  8, aw, ah, "Hints: ON", (88, 50, 145),  '💡')

    def new_game(self):
        self.dominos, self.solution = generate_dominos(
            num_dominos=self.num_dominos,
            min_string_len=self.min_string_len,
            max_string_len=self.max_string_len,
            min_solution_moves=self.min_solution_moves
        )
        self.work_seq: List[int]       = []
        self.show_hints: bool          = True
        self.hints: List[Hint]         = []
        self.best_hint: Optional[Hint] = None
        self.hint_scores: Dict[int, float] = {}
        self.hint_top3: List[int]      = []
        self.game_won = False
        self.pool_scroll = 0
        self.dragging = None
        self.drag_x = self.drag_y = 0
        self.drag_off = (0, 0)
        # Sync active state on diff buttons
        for name, btn in self.diff_btns.items():
            btn.active = (name == self.current_diff)
        self._refresh()

    def _refresh(self):
        if self.show_hints:
            self.hints, self.best_hint = compute_hints(self.dominos, self.work_seq)
            self.hint_scores = {h.idx: h.score for h in self.hints}
            self.hint_top3   = [h.idx for h in self.hints[:3]]
        else:
            self.hints = []; self.best_hint = None
            self.hint_scores = {}; self.hint_top3 = []

    def toggle_hints(self):
        self.show_hints = not self.show_hints
        self.btn_hint.label = f"Hints: {'ON' if self.show_hints else 'OFF'}"
        self._refresh()

    def _check_win(self):
        if len(self.work_seq) < MIN_MOVES:
            return False
        t = ''.join(self.dominos[i]['top'] for i in self.work_seq)
        b = ''.join(self.dominos[i]['bot'] for i in self.work_seq)
        return t == b

    # Layout helpers
    def _pool_pos(self):
        cols = 3
        cw = (POOL_RECT.width - 16) // cols
        out = []
        for i, d in enumerate(self.dominos):
            r, c = divmod(i, cols)
            w = domino_w(d['top'], d['bot'])
            x = POOL_RECT.x + 8 + c * cw + (cw - w) // 2
            y = POOL_RECT.y + 50 + r * (D_H + 14) - self.pool_scroll
            out.append((x, y, i))
        return out

    def _work_pos(self):
        x = WORK_RECT.x + 10
        y = WORK_RECT.y + 50
        out = []
        for sp, di in enumerate(self.work_seq):
            d = self.dominos[di]
            out.append((x, y, di, sp))
            x += domino_w(d['top'], d['bot']) + 10
        return out

    def _pool_hit(self, mx, my):
        for x, y, i in self._pool_pos():
            d = self.dominos[i]
            if x <= mx <= x + domino_w(d['top'], d['bot']) and y <= my <= y + D_H:
                return i, x, y
        return None, 0, 0

    def _work_hit(self, mx, my):
        for x, y, di, sp in self._work_pos():
            d = self.dominos[di]
            if x <= mx <= x + domino_w(d['top'], d['bot']) and y <= my <= y + D_H:
                return sp, x, y
        return None, 0, 0

    def _insert_pos(self, drop_x):
        for x, y, di, sp in self._work_pos():
            if drop_x < x + domino_w(self.dominos[di]['top'], self.dominos[di]['bot']) // 2:
                return sp
        return len(self.work_seq)

    # Drawing methods
    def draw(self):
        W, H = self.screen.get_size()
        surf = self.screen
        surf.fill(BG)
        mx, my = pygame.mouse.get_pos()

        self._draw_toolbar(surf, W, mx, my)
        self._draw_pool(surf, mx, my)
        self._draw_work_area(surf, mx, my)
        self._draw_hint_panel(surf)
        self._draw_drag_ghost(surf)
        self._draw_win_overlay(surf, W, H)

        pygame.display.flip()

    def _draw_toolbar(self, surf, W, mx, my):
        toolbar = pygame.Rect(0, 0, W, TOOLBAR_H)
        pygame.draw.rect(surf, TOOLBAR_BG, toolbar)
        pygame.draw.line(surf, DIVIDER, (0, TOOLBAR_H), (W, TOOLBAR_H), 2)

        # Title — top left
        title_surf = self.f_title.render("POST CORRESPONDENCE PROBLEM", True, WHITE)
        surf.blit(title_surf, (12, 8))
        subtitle = self.f_small.render("Match top & bottom strings", True, GRAY)
        surf.blit(subtitle, (14, 30))

        # Row 1: diff tabs + action buttons (all at y=8, handled by _build_ui)
        all_btns = list(self.diff_btns.values()) + [self.btn_new, self.btn_clear, self.btn_undo, self.btn_hint]
        for btn in all_btns:
            btn.update(mx, my)
            btn.draw(surf, self.f_body)

        # Row 2 (y=46): info strip left, colour legend right — no overlap
        cfg = self.DIFFICULTIES[self.current_diff]
        info = (f"  {self.current_diff.upper()}:  {cfg['num_dominos']} dominos  •  "
                f"string {cfg['min_string_len']}–{cfg['max_string_len']}  •  "
                f"min {cfg['min_solution_moves']} moves   |   N=new  C=clear  Z=undo  H=hints")
        surf.blit(self.f_small.render(info, True, GRAY), (10, 50))

        # Colour legend — row 2, right side (no longer near action buttons)
        lx = SCREEN_W - 180
        surf.blit(self.f_small.render("Squares:", True, GRAY), (lx, 50))
        for ci, (nm, k) in enumerate([("Red", '0'), ("Green", '1'), ("Blue", '2')]):
            px = lx + 62 + ci * 52
            pygame.draw.rect(surf, SQ_COLORS[k], (px, 51, 11, 11), border_radius=2)
            surf.blit(self.f_small.render(nm, True, GRAY), (px + 14, 50))

        pygame.draw.line(surf, DIVIDER, (0, TOOLBAR_H), (W, TOOLBAR_H), 2)

    def _draw_pool(self, surf, mx, my):
        pygame.draw.rect(surf, PANEL_BG, POOL_RECT, border_radius=10)
        pygame.draw.rect(surf, ACCENT, POOL_RECT, 1, border_radius=10)

        pool_header = pygame.Rect(POOL_RECT.x, POOL_RECT.y, POOL_RECT.width, 36)
        pygame.draw.rect(surf, (30, 38, 65), pool_header,
                         border_top_left_radius=10, border_top_right_radius=10)
        surf.blit(self.f_label.render("DOMINO POOL", True, ACCENT2), (POOL_RECT.x + 12, POOL_RECT.y + 10))
        cnt = self.f_small.render(f"{len(self.dominos)} tiles", True, GRAY)
        surf.blit(cnt, (POOL_RECT.right - cnt.get_width() - 10, POOL_RECT.y + 12))

        clip = pygame.Rect(POOL_RECT.x + 4, POOL_RECT.y + 40,
                           POOL_RECT.width - 8, POOL_RECT.height - 44)
        surf.set_clip(clip)
        for x, y, i in self._pool_pos():
            if y + D_H < clip.top or y > clip.bottom:
                continue
            d = self.dominos[i]
            ghost = (self.dragging and not self.dragging['from_work']
                     and self.dragging['domino_idx'] == i)
            hl = i in self.hint_top3 and self.show_hints
            sc = self.hint_scores.get(i, 0.0)
            draw_domino_tile(surf, d['top'], d['bot'], x, y,
                             highlighted=hl, ghost=ghost, hint_score=sc if hl else 0)
            if hl and not ghost:
                w = domino_w(d['top'], d['bot'])
                badge = self.f_small.render(f"{int(sc)}", True, GOLD)
                surf.blit(badge, (x + w - badge.get_width() - 3, y + 2))
            # Index label
            idx_lbl = self.f_small.render(f"#{i}", True, GRAY)
            surf.blit(idx_lbl, (x, y + D_H + 1))
        surf.set_clip(None)

        # Scroll arrows
        rows = (len(self.dominos) + 2) // 3
        max_sc = max(0, rows * (D_H + 14) - (POOL_RECT.height - 50))
        cx = POOL_RECT.centerx
        if self.pool_scroll > 0:
            pygame.draw.polygon(surf, GRAY,
                [(cx, POOL_RECT.y+42), (cx-8, POOL_RECT.y+54), (cx+8, POOL_RECT.y+54)])
        if self.pool_scroll < max_sc:
            pygame.draw.polygon(surf, GRAY,
                [(cx, POOL_RECT.bottom-4), (cx-8, POOL_RECT.bottom-16), (cx+8, POOL_RECT.bottom-16)])

    def _draw_work_area(self, surf, mx, my):
        pygame.draw.rect(surf, PANEL_WORK, WORK_RECT, border_radius=10)
        pygame.draw.rect(surf, ACCENT, WORK_RECT, 1, border_radius=10)

        work_header = pygame.Rect(WORK_RECT.x, WORK_RECT.y, WORK_RECT.width, 36)
        pygame.draw.rect(surf, (22, 42, 65), work_header,
                         border_top_left_radius=10, border_top_right_radius=10)
        surf.blit(self.f_label.render("WORK AREA", True, ACCENT2), (WORK_RECT.x + 12, WORK_RECT.y + 10))
        mc = GREEN_OK if len(self.work_seq) >= MIN_MOVES else ORANGE
        ml = self.f_label.render(f"Moves: {len(self.work_seq)} / {MIN_MOVES}+", True, mc)
        surf.blit(ml, (WORK_RECT.right - ml.get_width() - 12, WORK_RECT.y + 10))

        # Drop zone
        dz = pygame.Rect(WORK_RECT.x + 8, WORK_RECT.y + 42, WORK_RECT.width - 16, D_H + 16)
        pygame.draw.rect(surf, DARK_GRAY, dz, border_radius=6)
        pygame.draw.rect(surf, ACCENT, dz, 1, border_radius=6)
        if not self.work_seq:
            ph = self.f_body.render("← Drag dominos here to build your sequence", True, GRAY)
            surf.blit(ph, (dz.x + 12, dz.y + (dz.height - ph.get_height()) // 2))

        for x, y, di, sp in self._work_pos():
            ghost = (self.dragging and self.dragging.get('from_work')
                     and self.dragging['work_pos'] == sp)
            d = self.dominos[di]
            draw_domino_tile(surf, d['top'], d['bot'], x, y, ghost=ghost)

        # String comparison bars
        bar_y = WORK_RECT.y + 42 + D_H + 24
        if self.work_seq:
            top_c = ''.join(self.dominos[i]['top'] for i in self.work_seq)
            bot_c = ''.join(self.dominos[i]['bot'] for i in self.work_seq)
            self._draw_bars(surf, top_c, bot_c, WORK_RECT.x + 10, bar_y)

        # Status line
        sy = WORK_RECT.bottom + 8
        if self.work_seq:
            tc = ''.join(self.dominos[i]['top'] for i in self.work_seq)
            bc = ''.join(self.dominos[i]['bot'] for i in self.work_seq)
            if tc == bc and len(self.work_seq) >= MIN_MOVES:
                st, sc2 = "✓  PERFECT MATCH — Puzzle Solved!", GREEN_OK
            elif tc == bc:
                st, sc2 = f"⚠  Strings match — need {MIN_MOVES - len(self.work_seq)} more domino(s)", ORANGE
            else:
                mn = min(len(tc), len(bc))
                if tc[:mn] == bc[:mn]:
                    st, sc2 = "Prefix matches — keep building!", GOLD
                else:
                    st, sc2 = "Mismatch — try a different domino", RED_ERR
        else:
            st, sc2 = "Goal: make top string equal bottom string using at least 3 dominos.", GRAY
        surf.blit(self.f_label.render(st, True, sc2), (WORK_RECT.x, sy))

    def _draw_bars(self, surf, top, bot, x, y):
        sq, gap = 15, 3
        for li, (lbl, s) in enumerate([("Top:", top), ("Bot:", bot)]):
            ly = y + li * (sq + 8)
            surf.blit(self.f_small.render(lbl, True, GRAY), (x, ly))
            for ci, ch in enumerate(s):
                col = SQ_COLORS.get(ch, (130, 130, 130))
                rx = x + 34 + ci * (sq + gap)
                bdr = (GREEN_OK if ci < len(top) and ci < len(bot) and top[ci] == bot[ci]
                       else RED_ERR if ci < len(top) and ci < len(bot) else GRAY)
                pygame.draw.rect(surf, col, (rx, ly, sq, sq), border_radius=3)
                pygame.draw.rect(surf, bdr, (rx, ly, sq, sq), 2, border_radius=3)
        diff = abs(len(top) - len(bot))
        col_diff = GREEN_OK if diff == 0 else ORANGE if diff < 3 else RED_ERR
        surf.blit(self.f_small.render(
            f"Top: {len(top)} chars  •  Bot: {len(bot)} chars  •  Δ = {diff}",
            True, col_diff), (x, y + 2 * (sq + 8) + 4))

    def _draw_hint_panel(self, surf):
        x = WORK_RECT.x
        y = WORK_RECT.bottom + 36
        w = WORK_RECT.width
        h = SCREEN_H - y - GAP
        
        panel = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surf, PANEL_BG, panel, border_radius=10)
        pygame.draw.rect(surf, PURPLE, panel, 1, border_radius=10)

        ph_rect = pygame.Rect(x, y, w, 34)
        pygame.draw.rect(surf, (30, 25, 52), ph_rect,
                         border_top_left_radius=10, border_top_right_radius=10)
        surf.blit(self.f_label.render("💡  HINT PANEL", True, PURPLE), (x + 12, y + 9))

        if not self.show_hints:
            surf.blit(self.f_body.render("Hints disabled — click the Hints button to enable.", True, GRAY),
                      (x + 12, y + 44))
            return
        if not self.best_hint:
            surf.blit(self.f_body.render("No valid next move found — try clearing and restarting.", True, GRAY),
                      (x + 12, y + 44))
            return

        bh = self.best_hint
        d  = self.dominos[bh.idx]
        pw = domino_w(d['top'], d['bot'])
        draw_domino_tile(surf, d['top'], d['bot'], x + 12, y + 40, highlighted=True, hint_score=bh.score)

        type_col = {
            HintType.PERFECT_MATCH:  GREEN_OK,
            HintType.EXACT_PREFIX:   CYAN,
            HintType.PARTIAL_PREFIX: GOLD,
            HintType.BALANCING:      ORANGE,
            HintType.EXPLORATORY:    GRAY
        }.get(bh.htype, GRAY)

        tx = x + 22 + pw
        surf.blit(self.f_label.render(f"#{bh.idx}  {bh.htype.name.replace('_', ' ')}", True, type_col),
                  (tx, y + 40))

        bw = min(300, w - pw - 55)
        filled = int(bw * min(bh.score, 100) / 100)
        pygame.draw.rect(surf, DARK_GRAY, (tx, y + 58, bw, 10), border_radius=4)
        pygame.draw.rect(surf, type_col,  (tx, y + 58, filled, 10), border_radius=4)
        surf.blit(self.f_small.render(f"Score: {int(bh.score)}/100", True, GRAY),
                  (tx + bw + 8, y + 57))

        ey = y + 72
        for line in self._wrap(bh.explanation, w - pw - 55):
            surf.blit(self.f_body.render(line, True, WHITE), (tx, ey))
            ey += 16

        others = self.hints[1:3]
        if others:
            ot = "Also try: " + ",  ".join(f"#{h.idx} (score {int(h.score)})" for h in others)
            surf.blit(self.f_small.render(ot, True, GRAY), (x + 12, y + h - 18))

    def _wrap(self, text, max_px):
        words, lines, cur, cw = text.split(), [], [], 0
        for wrd in words:
            ww = self.f_body.size(wrd + ' ')[0]
            if cw + ww > max_px and cur:
                lines.append(' '.join(cur)); cur, cw = [wrd], ww
            else:
                cur.append(wrd); cw += ww
        if cur: lines.append(' '.join(cur))
        return lines[:3]

    def _draw_drag_ghost(self, surf):
        if self.dragging:
            ox, oy = self.drag_off
            d = self.dominos[self.dragging['domino_idx']]
            draw_domino_tile(surf, d['top'], d['bot'],
                             self.drag_x - ox, self.drag_y - oy, highlighted=True, hint_score=80)

    def _draw_win_overlay(self, surf, W, H):
        if self.game_won:
            ov = pygame.Surface((W, H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 150))
            surf.blit(ov, (0, 0))
            m = self.f_title.render("🎉  MATCH FOUND!  Puzzle Solved!", True, GOLD)
            surf.blit(m, m.get_rect(center=(W // 2, H // 2 - 28)))
            s = self.f_label.render(
                f"Solved in {len(self.work_seq)} moves  •  Press N for a new game", True, WHITE)
            surf.blit(s, s.get_rect(center=(W // 2, H // 2 + 16)))

    # Event handling
    def handle_events(self):
        mx, my = pygame.mouse.get_pos()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_n:   self.new_game()
                elif ev.key in (pygame.K_c, pygame.K_r):
                    self.work_seq.clear(); self.game_won = False; self._refresh()
                elif ev.key == pygame.K_z:
                    if self.work_seq: self.work_seq.pop(); self.game_won = False; self._refresh()
                elif ev.key == pygame.K_h: self.toggle_hints()

            if ev.type == pygame.MOUSEWHEEL and POOL_RECT.collidepoint(mx, my):
                rows = (len(self.dominos) + 2) // 3
                ms = max(0, rows * (D_H + 14) - (POOL_RECT.height - 50))
                self.pool_scroll = max(0, min(ms, self.pool_scroll - ev.y * 25))

            # Difficulty buttons
            for name, btn in self.diff_btns.items():
                if btn.clicked(ev):
                    self._apply_difficulty(name)
                    self.new_game()

            # Action buttons
            if self.btn_new.clicked(ev):   self.new_game()
            if self.btn_clear.clicked(ev):
                self.work_seq.clear(); self.game_won = False; self._refresh()
            if self.btn_undo.clicked(ev):
                if self.work_seq: self.work_seq.pop(); self.game_won = False; self._refresh()
            if self.btn_hint.clicked(ev):  self.toggle_hints()

            # Right-click remove from work
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 3:
                sp, _, _ = self._work_hit(mx, my)
                if sp is not None:
                    self.work_seq.pop(sp); self.game_won = False; self._refresh()

            # Drag start
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and not self.game_won:
                di, dx, dy = self._pool_hit(mx, my)
                if di is not None:
                    self.dragging = {'domino_idx': di, 'from_work': False}
                    self.drag_x, self.drag_y = mx, my
                    self.drag_off = (mx - dx, my - dy)
                    continue
                sp, wx, wy = self._work_hit(mx, my)
                if sp is not None:
                    di = self.work_seq[sp]
                    self.dragging = {'domino_idx': di, 'from_work': True, 'work_pos': sp}
                    self.drag_x, self.drag_y = mx, my
                    self.drag_off = (mx - wx, my - wy)
                    continue

            if ev.type == pygame.MOUSEMOTION and self.dragging:
                self.drag_x, self.drag_y = mx, my

            if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1 and self.dragging:
                self._drop(mx, my)

    def _drop(self, mx, my):
        ox, oy = self.drag_off
        drop_x = self.drag_x - ox
        di = self.dragging['domino_idx']
        in_work = WORK_RECT.collidepoint(mx, my)
        if self.dragging['from_work']:
            self.work_seq.pop(self.dragging['work_pos'])
            if in_work:
                self.work_seq.insert(self._insert_pos(drop_x), di)
        else:
            if in_work:
                self.work_seq.insert(self._insert_pos(drop_x), di)
        self.dragging = None
        if self._check_win(): self.game_won = True
        self._refresh()

    def run(self):
        while True:
            self.handle_events()
            self.draw()
            self.clock.tick(FPS)