import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pygame


CELL_SIZE = 28
GRID_MARGIN_X = 40
GRID_MARGIN_Y = 80
BACKGROUND_COLOR = (20, 20, 20)
GRID_COLOR = (70, 70, 70)
PIXEL_COLOR = (240, 240, 240)
PIXEL_BG = (35, 35, 35)
TEXT_COLOR = (220, 220, 220)
PREVIEW_COLOR = (200, 60, 60)

PATTERNS: Dict[str, Tuple[int, int]] = {
    "8x8": (8, 8),
    "8x16": (8, 16),
    "16x8": (16, 8),
    "16x16": (16, 16),
}


def bresenham_line(x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int]]:
    points: List[Tuple[int, int]] = []
    dx = abs(x1 - x0)
    sx = 1 if x0 < x1 else -1
    dy = -abs(y1 - y0)
    sy = 1 if y0 < y1 else -1
    error = dx + dy
    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        twice_error = 2 * error
        if twice_error >= dy:
            error += dy
            x0 += sx
        if twice_error <= dx:
            error += dx
            y0 += sy
    return points


class CharEditor:
    def __init__(self, output_path: Optional[Path]) -> None:
        pygame.init()
        self.output_path = output_path
        self.pattern_names = list(PATTERNS.keys())
        self.current_pattern = self.pattern_names[0]
        self.grid_width, self.grid_height = PATTERNS[self.current_pattern]
        self.grid: List[List[int]] = []
        self._build_grid()
        self.line_mode = False
        self.line_start: Optional[Tuple[int, int]] = None
        self.line_preview_end: Optional[Tuple[int, int]] = None
        self.drag_value: Optional[int] = None

        max_grid_width = max(width for width, _ in PATTERNS.values())
        max_grid_height = max(height for _, height in PATTERNS.values())
        window_width = max_grid_width * CELL_SIZE + GRID_MARGIN_X * 2
        window_height = max_grid_height * CELL_SIZE + GRID_MARGIN_Y * 2
        self.screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("JR-100 Character Editor")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Consolas", 18)
        self.small_font = pygame.font.SysFont("Consolas", 14)

    def _build_grid(self) -> None:
        width, height = PATTERNS[self.current_pattern]
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        self.grid_width = width
        self.grid_height = height
        self.line_start = None
        self.line_preview_end = None
        self.drag_value = None

    def run(self) -> None:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    running = self._handle_keydown(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_mouse_down(event)
                elif event.type == pygame.MOUSEMOTION:
                    self._handle_mouse_motion(event)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self._handle_mouse_up(event)

            self._draw()
            self.clock.tick(60)
        pygame.quit()

    def _handle_keydown(self, event: pygame.event.Event) -> bool:
        if event.key == pygame.K_ESCAPE:
            return False
        if event.key == pygame.K_r:
            self._build_grid()
        elif event.key == pygame.K_l:
            self.line_mode = not self.line_mode
            self.line_start = None
            self.line_preview_end = None
            self.drag_value = None
        elif event.key == pygame.K_s:
            self._export_json()
        elif pygame.K_1 <= event.key <= pygame.K_4:
            index = event.key - pygame.K_1
            if index < len(self.pattern_names):
                self._set_pattern(self.pattern_names[index])
        return True

    def _handle_mouse_down(self, event: pygame.event.Event) -> None:
        if event.button == 3 and self.line_mode:
            self.line_start = None
            self.line_preview_end = None
            return
        if event.button != 1:
            return
        cell = self._screen_to_cell(event.pos)
        if cell is None:
            return
        x, y = cell
        if self.line_mode:
            if self.line_start is None:
                self.line_start = (x, y)
                self.line_preview_end = (x, y)
            else:
                self._draw_line_to((x, y))
                self.line_preview_end = None
            return
        new_value = 0 if self.grid[y][x] else 1
        self._set_cell(x, y, new_value)
        self.drag_value = new_value

    def _handle_mouse_motion(self, event: pygame.event.Event) -> None:
        if self.line_mode:
            if self.line_start is None:
                self.line_preview_end = None
                return
            cell = self._screen_to_cell(event.pos)
            self.line_preview_end = cell
            return
        pressed = pygame.mouse.get_pressed()
        if not pressed[0] or self.drag_value is None:
            return
        cell = self._screen_to_cell(event.pos)
        if cell is None:
            return
        x, y = cell
        self._set_cell(x, y, self.drag_value)

    def _handle_mouse_up(self, event: pygame.event.Event) -> None:
        if event.button != 1:
            return
        if self.line_mode:
            return
        self.drag_value = None

    def _set_pattern(self, name: str) -> None:
        if name not in PATTERNS:
            return
        if self.current_pattern != name:
            self.current_pattern = name
            self._build_grid()

    def _set_cell(self, x: int, y: int, value: int) -> None:
        if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
            self.grid[y][x] = 1 if value else 0


    def _draw_line_to(self, end: Tuple[int, int]) -> None:
        if self.line_start is None:
            return
        sx, sy = self.line_start
        ex, ey = end
        for x, y in bresenham_line(sx, sy, ex, ey):
            self._set_cell(x, y, 1)
        self.line_start = None
        self.line_preview_end = None

    def _screen_to_cell(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        px, py = pos
        grid_left = GRID_MARGIN_X
        grid_top = GRID_MARGIN_Y
        width_px = self.grid_width * CELL_SIZE
        height_px = self.grid_height * CELL_SIZE
        if not (grid_left <= px < grid_left + width_px and grid_top <= py < grid_top + height_px):
            return None
        x = (px - grid_left) // CELL_SIZE
        y = (py - grid_top) // CELL_SIZE
        return int(x), int(y)

    def _draw(self) -> None:
        self.screen.fill(BACKGROUND_COLOR)
        self._draw_grid()
        self._draw_ui()
        pygame.display.flip()

    def _draw_grid(self) -> None:
        grid_top = GRID_MARGIN_Y
        grid_left = GRID_MARGIN_X
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                rect = pygame.Rect(
                    grid_left + x * CELL_SIZE,
                    grid_top + y * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE,
                )
                pygame.draw.rect(self.screen, PIXEL_BG, rect)
                if self.grid[y][x]:
                    inner = rect.inflate(-4, -4)
                    pygame.draw.rect(self.screen, PIXEL_COLOR, inner)
                pygame.draw.rect(self.screen, GRID_COLOR, rect, 1)
        if self.line_mode and self.line_start and self.line_preview_end:
            for px, py in bresenham_line(*self.line_start, *self.line_preview_end):
                if 0 <= px < self.grid_width and 0 <= py < self.grid_height:
                    rect = pygame.Rect(
                        grid_left + px * CELL_SIZE,
                        grid_top + py * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE,
                    )
                    outline = rect.inflate(-8, -8)
                    pygame.draw.rect(self.screen, PREVIEW_COLOR, outline, 2)

    def _draw_ui(self) -> None:
        line_mode_text = f"Line mode: {'ON' if self.line_mode else 'OFF'}"
        pattern_text = f"Pattern: {self.current_pattern}"
        combined = f"{pattern_text}    {line_mode_text}"
        hint_lines = [
            "1-4: pattern  L: line  R: clear  S: export  Esc: quit",
            "Left click: toggle / drag paints",
            "Line mode: right click cancels / preview shows in red",
        ]
        line_height = self.small_font.get_linesize()
        base_y = max(10, GRID_MARGIN_Y - line_height * (len(hint_lines) + 1) - 12)
        combined_surface = self.small_font.render(combined, True, TEXT_COLOR)
        self.screen.blit(combined_surface, (20, base_y))
        for idx, text in enumerate(hint_lines, start=1):
            surface = self.small_font.render(text, True, TEXT_COLOR)
            self.screen.blit(surface, (20, base_y + idx * line_height))

    def _export_json(self) -> None:
        hex_string = self._grid_to_hex()
        payload = {
            "pattern": self.current_pattern,
            "width": self.grid_width,
            "height": self.grid_height,
            "hex": hex_string,
        }
        text = json.dumps(payload, indent=2)
        print(text)
        if self.output_path:
            try:
                self.output_path.write_text(text)
                print(f"JSON written to {self.output_path}")
            except OSError as error:
                print(f"Failed to write JSON: {error}")

    def _grid_to_hex(self) -> str:
        bytes_out: List[int] = []
        for row in self.grid:
            byte_value = 0
            bit_index = 0
            for bit in row:
                byte_value = (byte_value << 1) | (1 if bit else 0)
                bit_index += 1
                if bit_index == 8:
                    bytes_out.append(byte_value)
                    byte_value = 0
                    bit_index = 0
            if bit_index != 0:
                byte_value <<= 8 - bit_index
                bytes_out.append(byte_value)
        return "".join(f"{value:02X}" for value in bytes_out)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="JR-100 character editor")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to write the exported JSON payload.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    editor = CharEditor(args.output)
    editor.run()


if __name__ == "__main__":
    main()
