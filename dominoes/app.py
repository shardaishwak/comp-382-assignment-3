
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

CONTROL_LEFT_PADDING = 20
CONTROL_TOP_PADDING = 62
CONTROL_ROW_HEIGHT = 86
CONTROL_LABEL_X = SET_AREA_X + CONTROL_LEFT_PADDING
CONTROL_VALUE_X = SET_AREA_X + 180
CONTROL_BUTTON_MINUS_X = SET_AREA_X + 250
CONTROL_BUTTON_PLUS_X = SET_AREA_X + 310
CONTROL_BUTTON_Y_OFFSET = 34
CONTROL_BUTTON_WIDTH = 44
CONTROL_BUTTON_HEIGHT = 34

ACTION_BUTTON_WIDTH = 140
ACTION_BUTTON_HEIGHT = 44
ACTION_BUTTON_GAP = 16

WORK_TEXT_X = WORK_AREA_X + 20
WORK_TEXT_Y = WORK_AREA_Y + 56
WORK_LINE_HEIGHT = 28

DOMINO_VIEW_MARGIN_X = 20
DOMINO_VIEW_MARGIN_TOP = 56
DOMINO_VIEW_MARGIN_BOTTOM = 20
DOMINO_SCROLL_STEP = DOMINO_HEIGHT + DOMINO_GAP

DOMINO_TEXT_COLOR = (60, 42, 30)
BUTTON_FILL = (94, 67, 47)
BUTTON_FILL_HOVER = (118, 84, 57)
BUTTON_TEXT_COLOR = TEXT_COLOR
CLEAR_BUTTON_FILL = (110, 55, 45)
GENERATE_BUTTON_FILL = (52, 102, 62)


def run_game() -> None:
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    font_title = pygame.font.SysFont("cooperblack", 32)
    font_label = pygame.font.SysFont("cooperblack", 22)
    font_text = pygame.font.SysFont("cooperblack", 18)
    font_button = pygame.font.SysFont("cooperblack", 20)

    state = GameState()
    domino_scroll_offset = 0

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        control_rects = _get_control_rects()
        action_rects = _get_action_rects()

        running, domino_scroll_offset = _handle_events(
            state=state,
            domino_scroll_offset=domino_scroll_offset,
            control_rects=control_rects,
            action_rects=action_rects,
        )
        domino_scroll_offset = _clamp_domino_scroll(state, domino_scroll_offset)

        _draw(
            screen=screen,
            state=state,
            font_title=font_title,
            font_label=font_label,
            font_text=font_text,
            font_button=font_button,
            mouse_pos=mouse_pos,
            control_rects=control_rects,
            action_rects=action_rects,
            domino_scroll_offset=domino_scroll_offset,
        )

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


def _handle_events(
    *,
    state: GameState,
    domino_scroll_offset: int,
    control_rects: dict[str, pygame.Rect],
    action_rects: dict[str, pygame.Rect],
) -> tuple[bool, int]:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False, domino_scroll_offset

        if event.type == pygame.MOUSEWHEEL:
            if _domino_viewport_rect().collidepoint(pygame.mouse.get_pos()):
                domino_scroll_offset -= event.y * DOMINO_SCROLL_STEP

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4 and _domino_viewport_rect().collidepoint(event.pos):
                domino_scroll_offset -= DOMINO_SCROLL_STEP
                continue

            if event.button == 5 and _domino_viewport_rect().collidepoint(event.pos):
                domino_scroll_offset += DOMINO_SCROLL_STEP
                continue

            if event.button != 1:
                continue

            if control_rects["string_length_minus"].collidepoint(event.pos):
                state.adjust_string_length(-1)
                continue

            if control_rects["string_length_plus"].collidepoint(event.pos):
                state.adjust_string_length(1)
                continue

            if control_rects["min_segment_minus"].collidepoint(event.pos):
                state.adjust_min_segment_length(-1)
                continue

            if control_rects["min_segment_plus"].collidepoint(event.pos):
                state.adjust_min_segment_length(1)
                continue

            if control_rects["max_segment_minus"].collidepoint(event.pos):
                state.adjust_max_segment_length(-1)
                continue

            if control_rects["max_segment_plus"].collidepoint(event.pos):
                state.adjust_max_segment_length(1)
                continue

            if control_rects["array_length_minus"].collidepoint(event.pos):
                state.adjust_array_length(-1)
                continue

            if control_rects["array_length_plus"].collidepoint(event.pos):
                state.adjust_array_length(1)
                continue

            if action_rects["generate"].collidepoint(event.pos):
                state.generate()
                domino_scroll_offset = 0
                continue

            if action_rects["clear"].collidepoint(event.pos):
                state.clear_output()
                domino_scroll_offset = 0
                continue

    return True, domino_scroll_offset


def _draw(
    *,
    screen: pygame.Surface,
    state: GameState,
    font_title: pygame.font.Font,
    font_label: pygame.font.Font,
    font_text: pygame.font.Font,
    font_button: pygame.font.Font,
    mouse_pos: tuple[int, int],
    control_rects: dict[str, pygame.Rect],
    action_rects: dict[str, pygame.Rect],
    domino_scroll_offset: int,
) -> None:
    screen.fill(BG_COLOR)

    _draw_header(screen, font_title, font_text)
    _draw_panel(screen, SET_AREA_X, SET_AREA_Y, SET_AREA_WIDTH, SET_AREA_HEIGHT, "Generator Controls", font_label)
    _draw_panel(screen, WORK_AREA_X, WORK_AREA_Y, WORK_AREA_WIDTH, WORK_AREA_HEIGHT, "Generation Output", font_label)
    _draw_panel(screen, INFO_AREA_X, INFO_AREA_Y, INFO_AREA_WIDTH, INFO_AREA_HEIGHT, "Generated Dominoes", font_label)

    _draw_controls(screen, state, font_text, font_button, mouse_pos, control_rects, action_rects)
    _draw_generation_output(screen, state, font_text)
    _draw_domino_panel(screen, state, font_text, mouse_pos, domino_scroll_offset)


def _draw_header(
    screen: pygame.Surface,
    font_title: pygame.font.Font,
    font_text: pygame.font.Font,
) -> None:
    title_surface = font_title.render("PCP GENERATOR TESTER", True, ACCENT_RED)
    screen.blit(title_surface, (40, 28))

    subtitle_surface = font_text.render(
        "Click the controls to set values, then click Generate.",
        True,
        TEXT_COLOR,
    )
    screen.blit(subtitle_surface, (40, 70))


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


def _draw_controls(
    screen: pygame.Surface,
    state: GameState,
    font_text: pygame.font.Font,
    font_button: pygame.font.Font,
    mouse_pos: tuple[int, int],
    control_rects: dict[str, pygame.Rect],
    action_rects: dict[str, pygame.Rect],
) -> None:
    control_rows = [
        ("String Length", str(state.string_length), "string_length_minus", "string_length_plus"),
        ("Min Segment", str(state.min_segment_length), "min_segment_minus", "min_segment_plus"),
        ("Max Segment", str(state.max_segment_length), "max_segment_minus", "max_segment_plus"),
        ("Array Length", str(state.array_length), "array_length_minus", "array_length_plus"),
    ]

    y = SET_AREA_Y + CONTROL_TOP_PADDING

    for label, value, minus_key, plus_key in control_rows:
        label_surface = font_text.render(label, True, TEXT_COLOR)
        value_surface = font_text.render(value, True, ACCENT_GREEN)

        screen.blit(label_surface, (CONTROL_LABEL_X, y))
        screen.blit(value_surface, (CONTROL_VALUE_X, y + 2))

        _draw_button(
            screen=screen,
            rect=control_rects[minus_key],
            text="-",
            font=font_button,
            mouse_pos=mouse_pos,
            fill_color=BUTTON_FILL,
        )
        _draw_button(
            screen=screen,
            rect=control_rects[plus_key],
            text="+",
            font=font_button,
            mouse_pos=mouse_pos,
            fill_color=BUTTON_FILL,
        )

        y += CONTROL_ROW_HEIGHT

    _draw_button(
        screen=screen,
        rect=action_rects["generate"],
        text="Generate",
        font=font_button,
        mouse_pos=mouse_pos,
        fill_color=GENERATE_BUTTON_FILL,
    )
    _draw_button(
        screen=screen,
        rect=action_rects["clear"],
        text="Clear",
        font=font_button,
        mouse_pos=mouse_pos,
        fill_color=CLEAR_BUTTON_FILL,
    )

    validity_text = "Valid range" if state.can_generate() else "Invalid range"
    validity_color = ACCENT_GREEN if state.can_generate() else ACCENT_RED
    validity_surface = font_text.render(validity_text, True, validity_color)
    screen.blit(validity_surface, (SET_AREA_X + 20, SET_AREA_Y + SET_AREA_HEIGHT - 120))

    rule_lines = [
        f"Min total: {state.array_length * state.min_segment_length}",
        f"Max total: {state.array_length * state.max_segment_length}",
    ]

    y = SET_AREA_Y + SET_AREA_HEIGHT - 88
    for line in rule_lines:
        surface = font_text.render(line, True, TEXT_COLOR)
        screen.blit(surface, (SET_AREA_X + 20, y))
        y += 26


def _draw_generation_output(
    screen: pygame.Surface,
    state: GameState,
    font_text: pygame.font.Font,
) -> None:
    x = WORK_TEXT_X
    y = WORK_TEXT_Y

    if state.error_message:
        _draw_wrapped_text(
            screen=screen,
            text=f"Error: {state.error_message}",
            font=font_text,
            color=ACCENT_RED,
            x=x,
            y=y,
            max_width=WORK_AREA_WIDTH - 40,
            line_height=WORK_LINE_HEIGHT,
        )
        return

    if not state.has_generated:
        placeholder = "No output yet. Click Generate to build an instance."
        surface = font_text.render(placeholder, True, TEXT_COLOR)
        screen.blit(surface, (x, y))
        return

    lines = [
        f"Source String: {state.source_string}",
        f"Top Array: {state.top_lengths}",
        f"Bottom Array: {state.bottom_lengths}",
        "",
        f"Top Segments: {' | '.join(state.top_segments)}",
        f"Bottom Segments: {' | '.join(state.bottom_segments)}",
    ]

    for line in lines:
        if line == "":
            y += 10
            continue

        y = _draw_wrapped_text(
            screen=screen,
            text=line,
            font=font_text,
            color=TEXT_COLOR,
            x=x,
            y=y,
            max_width=WORK_AREA_WIDTH - 40,
            line_height=WORK_LINE_HEIGHT,
        )
        y += 2


def _draw_domino_panel(
    screen: pygame.Surface,
    state: GameState,
    font_text: pygame.font.Font,
    mouse_pos: tuple[int, int],
    domino_scroll_offset: int,
) -> None:
    viewport_rect = _domino_viewport_rect()
    pygame.draw.rect(screen, BORDER_COLOR, viewport_rect, width=1, border_radius=6)

    if not state.has_generated:
        placeholder = font_text.render("No dominoes yet.", True, TEXT_COLOR)
        screen.blit(placeholder, (viewport_rect.x + 12, viewport_rect.y + 12))
        return

    previous_clip = screen.get_clip()
    screen.set_clip(viewport_rect)

    for index, domino in enumerate(state.dominoes):
        rect = _get_domino_rect(index, domino_scroll_offset)
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

    if _get_domino_content_height(len(state.dominoes)) > viewport_rect.height:
        _draw_domino_scrollbar(screen, state, mouse_pos, domino_scroll_offset, viewport_rect)


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


def _draw_domino_scrollbar(
    screen: pygame.Surface,
    state: GameState,
    mouse_pos: tuple[int, int],
    domino_scroll_offset: int,
    viewport_rect: pygame.Rect,
) -> None:
    content_height = _get_domino_content_height(len(state.dominoes))
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
    scroll_ratio = 0 if max_scroll == 0 else domino_scroll_offset / max_scroll
    thumb_y = track_rect.y + int((track_rect.height - thumb_height) * scroll_ratio)

    thumb_rect = pygame.Rect(track_rect.x + 1, thumb_y, track_rect.width - 2, thumb_height)
    thumb_color = BUTTON_FILL_HOVER if thumb_rect.collidepoint(mouse_pos) else TEXT_COLOR
    pygame.draw.rect(screen, thumb_color, thumb_rect, border_radius=5)


def _draw_button(
    *,
    screen: pygame.Surface,
    rect: pygame.Rect,
    text: str,
    font: pygame.font.Font,
    mouse_pos: tuple[int, int],
    fill_color: tuple[int, int, int],
) -> None:
    color = BUTTON_FILL_HOVER if rect.collidepoint(mouse_pos) else fill_color
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, BORDER_COLOR, rect, width=2, border_radius=8)

    text_surface = font.render(text, True, BUTTON_TEXT_COLOR)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)


def _draw_wrapped_text(
    *,
    screen: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: tuple[int, int, int],
    x: int,
    y: int,
    max_width: int,
    line_height: int,
) -> int:
    words = text.split(" ")
    current_line = ""

    for word in words:
        candidate = word if not current_line else f"{current_line} {word}"
        candidate_surface = font.render(candidate, True, color)

        if candidate_surface.get_width() <= max_width:
            current_line = candidate
            continue

        if current_line:
            line_surface = font.render(current_line, True, color)
            screen.blit(line_surface, (x, y))
            y += line_height

        current_line = word

    if current_line:
        line_surface = font.render(current_line, True, color)
        screen.blit(line_surface, (x, y))
        y += line_height

    return y


def _get_control_rects() -> dict[str, pygame.Rect]:
    top_y = SET_AREA_Y + CONTROL_TOP_PADDING + CONTROL_BUTTON_Y_OFFSET
    row_step = CONTROL_ROW_HEIGHT

    return {
        "string_length_minus": pygame.Rect(
            CONTROL_BUTTON_MINUS_X,
            top_y + row_step * 0,
            CONTROL_BUTTON_WIDTH,
            CONTROL_BUTTON_HEIGHT,
        ),
        "string_length_plus": pygame.Rect(
            CONTROL_BUTTON_PLUS_X,
            top_y + row_step * 0,
            CONTROL_BUTTON_WIDTH,
            CONTROL_BUTTON_HEIGHT,
        ),
        "min_segment_minus": pygame.Rect(
            CONTROL_BUTTON_MINUS_X,
            top_y + row_step * 1,
            CONTROL_BUTTON_WIDTH,
            CONTROL_BUTTON_HEIGHT,
        ),
        "min_segment_plus": pygame.Rect(
            CONTROL_BUTTON_PLUS_X,
            top_y + row_step * 1,
            CONTROL_BUTTON_WIDTH,
            CONTROL_BUTTON_HEIGHT,
        ),
        "max_segment_minus": pygame.Rect(
            CONTROL_BUTTON_MINUS_X,
            top_y + row_step * 2,
            CONTROL_BUTTON_WIDTH,
            CONTROL_BUTTON_HEIGHT,
        ),
        "max_segment_plus": pygame.Rect(
            CONTROL_BUTTON_PLUS_X,
            top_y + row_step * 2,
            CONTROL_BUTTON_WIDTH,
            CONTROL_BUTTON_HEIGHT,
        ),
        "array_length_minus": pygame.Rect(
            CONTROL_BUTTON_MINUS_X,
            top_y + row_step * 3,
            CONTROL_BUTTON_WIDTH,
            CONTROL_BUTTON_HEIGHT,
        ),
        "array_length_plus": pygame.Rect(
            CONTROL_BUTTON_PLUS_X,
            top_y + row_step * 3,
            CONTROL_BUTTON_WIDTH,
            CONTROL_BUTTON_HEIGHT,
        ),
    }


def _get_action_rects() -> dict[str, pygame.Rect]:
    action_y = SET_AREA_Y + CONTROL_TOP_PADDING + CONTROL_ROW_HEIGHT * 4 + 24
    generate_x = SET_AREA_X + 20
    clear_x = generate_x + ACTION_BUTTON_WIDTH + ACTION_BUTTON_GAP

    return {
        "generate": pygame.Rect(
            generate_x,
            action_y,
            ACTION_BUTTON_WIDTH,
            ACTION_BUTTON_HEIGHT,
        ),
        "clear": pygame.Rect(
            clear_x,
            action_y,
            ACTION_BUTTON_WIDTH,
            ACTION_BUTTON_HEIGHT,
        ),
    }


def _domino_viewport_rect() -> pygame.Rect:
    return pygame.Rect(
        INFO_AREA_X + DOMINO_VIEW_MARGIN_X,
        INFO_AREA_Y + DOMINO_VIEW_MARGIN_TOP,
        INFO_AREA_WIDTH - (DOMINO_VIEW_MARGIN_X * 2),
        INFO_AREA_HEIGHT - DOMINO_VIEW_MARGIN_TOP - DOMINO_VIEW_MARGIN_BOTTOM,
    )


def _get_domino_rect(index: int, domino_scroll_offset: int) -> pygame.Rect:
    return pygame.Rect(
        INFO_AREA_X + DOMINO_VIEW_MARGIN_X,
        INFO_AREA_Y + DOMINO_VIEW_MARGIN_TOP + index * (DOMINO_HEIGHT + DOMINO_GAP) - domino_scroll_offset,
        DOMINO_WIDTH,
        DOMINO_HEIGHT,
    )


def _get_domino_content_height(domino_count: int) -> int:
    if domino_count <= 0:
        return 0

    return domino_count * DOMINO_HEIGHT + (domino_count - 1) * DOMINO_GAP


def _clamp_domino_scroll(state: GameState, domino_scroll_offset: int) -> int:
    viewport_rect = _domino_viewport_rect()
    max_scroll = max(0, _get_domino_content_height(len(state.dominoes)) - viewport_rect.height)

    if domino_scroll_offset < 0:
        return 0

    if domino_scroll_offset > max_scroll:
        return max_scroll

    return domino_scroll_offset