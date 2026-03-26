
from __future__ import annotations

import sys

import pygame

from config import (
    ACCENT_GREEN,
    ACCENT_RED,
    BG_COLOR,
    BORDER_COLOR,
    DOMINO_COLOR,
    DOMINO_EDGE,
    DOMINO_GAP,
    DOMINO_HEIGHT,
    DOMINO_WIDTH,
    FPS,
    INFO_AREA_HEIGHT,
    INFO_AREA_WIDTH,
    INFO_AREA_X,
    INFO_AREA_Y,
    PANEL_COLOR,
    SET_AREA_HEIGHT,
    SET_AREA_WIDTH,
    SET_AREA_X,
    SET_AREA_Y,
    TEXT_COLOR,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
    WORK_AREA_HEIGHT,
    WORK_AREA_WIDTH,
    WORK_AREA_X,
    WORK_AREA_Y,
)
from domino import Domino
from state import GameState

AVAILABLE_MARGIN_X = 20
AVAILABLE_MARGIN_TOP = 52
AVAILABLE_MARGIN_BOTTOM = 20
AVAILABLE_SCROLL_STEP = DOMINO_HEIGHT + DOMINO_GAP

WORKING_MARGIN_X = 20
WORKING_MARGIN_TOP = 70
WORKING_MARGIN_BOTTOM = 20
WORKING_TILE_GAP_X = 10
WORKING_TILE_GAP_Y = 12

DOMINO_TEXT_COLOR = (60, 42, 30)


def run_game() -> None:
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    font_title = pygame.font.SysFont("cooperblack", 32)
    font_label = pygame.font.SysFont("cooperblack", 22)
    font_text = pygame.font.SysFont("cooperblack", 18)

    state = GameState()
    state.reset_with_random_dominoes(count=8)

    available_scroll_offset = 0

    running = True
    while running:
        running, available_scroll_offset = _handle_events(state, available_scroll_offset)
        available_scroll_offset = _clamp_available_scroll(state, available_scroll_offset)
        _draw(screen, state, font_title, font_label, font_text, available_scroll_offset)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


def _handle_events(state: GameState, available_scroll_offset: int) -> tuple[bool, int]:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False, available_scroll_offset

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False, available_scroll_offset

            if event.key == pygame.K_r:
                state.reset_with_random_dominoes(count=8)
                available_scroll_offset = 0

        if event.type == pygame.MOUSEWHEEL:
            if _available_viewport_rect().collidepoint(pygame.mouse.get_pos()):
                available_scroll_offset -= event.y * AVAILABLE_SCROLL_STEP

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4 and _available_viewport_rect().collidepoint(event.pos):
                available_scroll_offset -= AVAILABLE_SCROLL_STEP
            elif event.button == 5 and _available_viewport_rect().collidepoint(event.pos):
                available_scroll_offset += AVAILABLE_SCROLL_STEP
            elif event.button == 1:
                clicked_domino = _get_clicked_available_domino(state.available_dominoes, event.pos, available_scroll_offset)
                if clicked_domino is not None:
                    state.append_to_working_sequence(clicked_domino)
                    available_scroll_offset = _clamp_available_scroll(state, available_scroll_offset)
                    continue

                clicked_working_index = _get_clicked_working_domino_index(state.working_sequence, event.pos)
                if clicked_working_index is not None:
                    state.remove_from_working_sequence(clicked_working_index)
                    available_scroll_offset = _clamp_available_scroll(state, available_scroll_offset)

    return True, available_scroll_offset


def _draw(
    screen: pygame.Surface,
    state: GameState,
    font_title: pygame.font.Font,
    font_label: pygame.font.Font,
    font_text: pygame.font.Font,
    available_scroll_offset: int,
) -> None:
    screen.fill(BG_COLOR)

    _draw_header(screen, state, font_title, font_text)

    _draw_panel(
        screen=screen,
        x=SET_AREA_X,
        y=SET_AREA_Y,
        width=SET_AREA_WIDTH,
        height=SET_AREA_HEIGHT,
        title="Available Dominoes",
        font=font_label,
    )
    _draw_panel(
        screen=screen,
        x=WORK_AREA_X,
        y=WORK_AREA_Y,
        width=WORK_AREA_WIDTH,
        height=WORK_AREA_HEIGHT,
        title="Active Area",
        font=font_label,
    )
    _draw_panel(
        screen=screen,
        x=INFO_AREA_X,
        y=INFO_AREA_Y,
        width=INFO_AREA_WIDTH,
        height=INFO_AREA_HEIGHT,
        title="Sequence Info",
        font=font_label,
    )

    _draw_available_dominoes(screen, state.available_dominoes, font_text, available_scroll_offset)
    _draw_working_sequence(screen, state.working_sequence, font_text)
    _draw_info(screen, state, font_text)


def _draw_header(
    screen: pygame.Surface,
    state: GameState,
    font_title: pygame.font.Font,
    font_text: pygame.font.Font,
) -> None:
    title_surface = font_title.render("PCP CASINO", True, ACCENT_RED)
    screen.blit(title_surface, (40, 28))

    controls_text = "Left click available domino to place | Click active domino to return | Mouse wheel scrolls supply | R = regenerate | Esc = quit"
    controls_surface = font_text.render(controls_text, True, TEXT_COLOR)
    screen.blit(controls_surface, (40, 68))

    count_text = f"Available: {len(state.available_dominoes)} | Active: {len(state.working_sequence)}"
    count_surface = font_text.render(count_text, True, ACCENT_GREEN)
    screen.blit(count_surface, (40, 96))


def _draw_panel(
    screen: pygame.Surface,
    x: int,
    y: int,
    width: int,
    height: int,
    title: str,
    font: pygame.font.Font,
) -> None:
    panel_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, PANEL_COLOR, panel_rect, border_radius=10)
    pygame.draw.rect(screen, BORDER_COLOR, panel_rect, width=2, border_radius=10)

    title_surface = font.render(title, True, TEXT_COLOR)
    screen.blit(title_surface, (x + 16, y + 12))


def _draw_available_dominoes(
    screen: pygame.Surface,
    available_dominoes: list[Domino],
    font_text: pygame.font.Font,
    available_scroll_offset: int,
) -> None:
    viewport_rect = _available_viewport_rect()
    previous_clip = screen.get_clip()
    screen.set_clip(viewport_rect)

    for index, domino in enumerate(available_dominoes):
        rect = _get_available_domino_rect(index, available_scroll_offset)
        if rect.bottom < viewport_rect.top or rect.top > viewport_rect.bottom:
            continue

        _draw_domino(
            screen=screen,
            rect=rect,
            domino=domino,
            font_text=font_text,
            label=str(index + 1),
        )

    screen.set_clip(previous_clip)
    pygame.draw.rect(screen, BORDER_COLOR, viewport_rect, width=1, border_radius=6)

    if _get_available_content_height(len(available_dominoes)) > viewport_rect.height:
        _draw_available_scrollbar(screen, available_dominoes, available_scroll_offset, viewport_rect)


def _draw_available_scrollbar(
    screen: pygame.Surface,
    available_dominoes: list[Domino],
    available_scroll_offset: int,
    viewport_rect: pygame.Rect,
) -> None:
    content_height = _get_available_content_height(len(available_dominoes))
    if content_height <= viewport_rect.height:
        return

    track_width = 10
    track_rect = pygame.Rect(
        viewport_rect.right - track_width - 6,
        viewport_rect.top + 6,
        track_width,
        viewport_rect.height - 12,
    )
    pygame.draw.rect(screen, DOMINO_EDGE, track_rect, width=1, border_radius=5)

    thumb_height = max(40, int(track_rect.height * (viewport_rect.height / content_height)))
    max_scroll = max(0, content_height - viewport_rect.height)
    scroll_ratio = 0 if max_scroll == 0 else available_scroll_offset / max_scroll
    thumb_y = track_rect.y + int((track_rect.height - thumb_height) * scroll_ratio)

    thumb_rect = pygame.Rect(track_rect.x + 1, thumb_y, track_rect.width - 2, thumb_height)
    pygame.draw.rect(screen, TEXT_COLOR, thumb_rect, border_radius=5)


def _draw_working_sequence(
    screen: pygame.Surface,
    working_sequence: list[Domino],
    font_text: pygame.font.Font,
) -> None:
    for index, domino in enumerate(working_sequence):
        rect = _get_working_domino_rect(index)
        _draw_domino(
            screen=screen,
            rect=rect,
            domino=domino,
            font_text=font_text,
            label=str(index + 1),
        )


def _draw_domino(
    screen: pygame.Surface,
    rect: pygame.Rect,
    domino: Domino,
    font_text: pygame.font.Font,
    label: str,
) -> None:
    pygame.draw.rect(screen, DOMINO_COLOR, rect, border_radius=8)
    pygame.draw.rect(screen, DOMINO_EDGE, rect, width=2, border_radius=8)

    divider_y = rect.y + rect.height // 2
    pygame.draw.line(screen, DOMINO_EDGE, (rect.x, divider_y), (rect.x + rect.width, divider_y), 2)

    label_surface = font_text.render(label, True, ACCENT_RED)
    screen.blit(label_surface, (rect.x + 8, rect.y + 6))

    top_surface = font_text.render(domino.top, True, DOMINO_TEXT_COLOR)
    bottom_surface = font_text.render(domino.bottom, True, DOMINO_TEXT_COLOR)

    screen.blit(top_surface, (rect.x + 40, rect.y + 10))
    screen.blit(bottom_surface, (rect.x + 40, rect.y + rect.height // 2 + 8))


def _draw_info(
    screen: pygame.Surface,
    state: GameState,
    font_text: pygame.font.Font,
) -> None:
    lines = [
        f"Top string:    {state.top_string if state.top_string else '-'}",
        f"Bottom string: {state.bottom_string if state.bottom_string else '-'}",
        "",
        
    ]

    x = INFO_AREA_X + 20
    y = INFO_AREA_Y + 55

    for line in lines:
        surface = font_text.render(line, True, TEXT_COLOR)
        screen.blit(surface, (x, y))
        y += 28


def _available_viewport_rect() -> pygame.Rect:
    return pygame.Rect(
        SET_AREA_X + AVAILABLE_MARGIN_X,
        SET_AREA_Y + AVAILABLE_MARGIN_TOP,
        SET_AREA_WIDTH - (AVAILABLE_MARGIN_X * 2),
        SET_AREA_HEIGHT - AVAILABLE_MARGIN_TOP - AVAILABLE_MARGIN_BOTTOM,
    )


def _get_available_content_height(domino_count: int) -> int:
    if domino_count <= 0:
        return 0

    return domino_count * DOMINO_HEIGHT + (domino_count - 1) * DOMINO_GAP


def _clamp_available_scroll(state: GameState, available_scroll_offset: int) -> int:
    viewport_rect = _available_viewport_rect()
    max_scroll = max(0, _get_available_content_height(len(state.available_dominoes)) - viewport_rect.height)

    if available_scroll_offset < 0:
        return 0

    if available_scroll_offset > max_scroll:
        return max_scroll

    return available_scroll_offset


def _get_available_domino_rect(index: int, available_scroll_offset: int) -> pygame.Rect:
    return pygame.Rect(
        SET_AREA_X + AVAILABLE_MARGIN_X,
        SET_AREA_Y + AVAILABLE_MARGIN_TOP + index * (DOMINO_HEIGHT + DOMINO_GAP) - available_scroll_offset,
        DOMINO_WIDTH,
        DOMINO_HEIGHT,
    )


def _get_working_domino_rect(index: int) -> pygame.Rect:
    usable_width = WORK_AREA_WIDTH - (WORKING_MARGIN_X * 2)
    tile_full_width = DOMINO_WIDTH + WORKING_TILE_GAP_X
    columns = max(1, (usable_width + WORKING_TILE_GAP_X) // tile_full_width)

    row = index // columns
    column = index % columns

    x = WORK_AREA_X + WORKING_MARGIN_X + column * tile_full_width
    y = WORK_AREA_Y + WORKING_MARGIN_TOP + row * (DOMINO_HEIGHT + WORKING_TILE_GAP_Y)

    return pygame.Rect(x, y, DOMINO_WIDTH, DOMINO_HEIGHT)


def _get_clicked_available_domino(
    available_dominoes: list[Domino],
    mouse_pos: tuple[int, int],
    available_scroll_offset: int,
) -> Domino | None:
    viewport_rect = _available_viewport_rect()
    if not viewport_rect.collidepoint(mouse_pos):
        return None

    for index, domino in enumerate(available_dominoes):
        rect = _get_available_domino_rect(index, available_scroll_offset)
        if rect.collidepoint(mouse_pos):
            return domino

    return None


def _get_clicked_working_domino_index(
    working_sequence: list[Domino],
    mouse_pos: tuple[int, int],
) -> int | None:
    for index in range(len(working_sequence)):
        rect = _get_working_domino_rect(index)
        if rect.collidepoint(mouse_pos):
            return index

    return None