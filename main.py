import pygame
import sys
from enum import Enum, auto
from button import Button
from input_box import InputBox
from grid import create_grid, draw_grid_lines


class ScreenState(Enum):
    MENU = auto()
    DESIGN = auto()


MIN_GRID_SIZE = 4
MAX_GRID_SIZE = 15


def main():
    pygame.init()

    WINDOW_WIDTH = 700
    WINDOW_HEIGHT = 700
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Atoms")

    BG_COLOR = (20, 27, 35)
    TITLE_COLOR = (255, 255, 255)
    SUBTITLE_COLOR = (180, 190, 200)
    ERROR_COLOR = (224, 122, 122)
    GRID_LINE_COLOR = (90, 97, 105)

    TITLE_SIZE = 60
    SUBTITLE_SIZE = 22
    ERROR_SIZE = 18
    TITLE_Y = 60
    SUBTITLE_Y = 108
    ERROR_Y = 134

    title_font = pygame.font.SysFont("franklingothicdemi", TITLE_SIZE)
    title_surface = title_font.render("ATOMS", True, TITLE_COLOR)
    title = title_surface.get_rect(center=(WINDOW_WIDTH // 2, TITLE_Y))

    subtitle_font = pygame.font.SysFont("franklingothicdemi", SUBTITLE_SIZE)
    subtitle_surface = subtitle_font.render(
        "Enter a grid size between 4 and 15", True, SUBTITLE_COLOR
    )
    subtitle = subtitle_surface.get_rect(center=(WINDOW_WIDTH // 2, SUBTITLE_Y))

    design_prompt_surface = subtitle_font.render(
        "Click on an intersection to place an atom", True, SUBTITLE_COLOR
    )
    design_prompt = design_prompt_surface.get_rect(center=(WINDOW_WIDTH // 2, SUBTITLE_Y))

    error_font = pygame.font.SysFont("franklingothicdemi", ERROR_SIZE)

    input_font = pygame.font.SysFont("franklingothicdemi", 28)
    button_font = pygame.font.SysFont("franklingothicdemi", 34)
    small_button_font = pygame.font.SysFont("franklingothicdemi", 24)

    BOX_WIDTH = 120
    BOX_HEIGHT = 60
    BOX_GAP = 40

    width_box = InputBox(
        WINDOW_WIDTH // 2 - BOX_WIDTH - BOX_GAP // 2,
        220,
        BOX_WIDTH,
        BOX_HEIGHT,
        input_font,
        "WIDTH",
    )

    height_box = InputBox(
        WINDOW_WIDTH // 2 + BOX_GAP // 2,
        220,
        BOX_WIDTH,
        BOX_HEIGHT,
        input_font,
        "HEIGHT",
    )

    START_BUTTON_WIDTH = 220
    START_BUTTON_HEIGHT = 70

    start_button = Button(
        WINDOW_WIDTH // 2 - START_BUTTON_WIDTH // 2,
        360,
        START_BUTTON_WIDTH,
        START_BUTTON_HEIGHT,
        "START",
        button_font,
        (110, 200, 150),
    )

    ERASER_BUTTON_WIDTH = 300
    ERASER_BUTTON_HEIGHT = 70

    eraser_button = Button(
        WINDOW_WIDTH // 2 - ERASER_BUTTON_WIDTH // 2,
        610,
        ERASER_BUTTON_WIDTH,
        ERASER_BUTTON_HEIGHT,
        "ERASER",
        small_button_font,
        (73, 80, 88),
    )
    ERASER_COLOR_ACTIVE = (224, 122, 122)
    ERASER_COLOR_INACTIVE = (73, 80, 88)

    state = ScreenState.MENU
    error_message = None
    eraser_active = False

    rows = None
    cols = None
    atoms = []
    grid_rect = None
    cell_size = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if state == ScreenState.MENU:
                width_box.handle_event(event)
                height_box.handle_event(event)

                if start_button.handle_event(event):
                    w = width_box.get_value()
                    h = height_box.get_value()

                    if w is None or h is None:
                        error_message = "Please enter both a width and a height"
                    elif not (MIN_GRID_SIZE <= w <= MAX_GRID_SIZE) or not (
                        MIN_GRID_SIZE <= h <= MAX_GRID_SIZE
                    ):
                        error_message = f"Grid size must be between {MIN_GRID_SIZE} and {MAX_GRID_SIZE}"
                    else:
                        error_message = None
                        cols, rows = w, h
                        atom_font = pygame.font.SysFont(
                            "franklingothicdemi", max(14, min(22, round(400 / max(rows, cols))))
                        )
                        atoms, grid_rect, cell_size = create_grid(
                            rows, cols, WINDOW_WIDTH, atom_font
                        )
                        eraser_active = False
                        state = ScreenState.DESIGN

            elif state == ScreenState.DESIGN:
                for atom_row in atoms:
                    for atom in atom_row:
                        atom.handle_event(event, eraser_active)

                if eraser_button.handle_event(event):
                    eraser_active = not eraser_active

        screen.fill(BG_COLOR)
        screen.blit(title_surface, title)

        if state == ScreenState.MENU:
            screen.blit(subtitle_surface, subtitle)

            width_box.display(screen)
            height_box.display(screen)
            start_button.display(screen)

            if error_message:
                error_surface = error_font.render(error_message, True, ERROR_COLOR)
                error_rect = error_surface.get_rect(center=(WINDOW_WIDTH // 2, ERROR_Y))
                screen.blit(error_surface, error_rect)

        elif state == ScreenState.DESIGN:
            screen.blit(design_prompt_surface, design_prompt)

            draw_grid_lines(screen, grid_rect, rows, cols, cell_size, GRID_LINE_COLOR)

            for atom_row in atoms:
                for atom in atom_row:
                    atom.display(screen, eraser_active)

            eraser_button.color = ERASER_COLOR_ACTIVE if eraser_active else ERASER_COLOR_INACTIVE
            eraser_button.display(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


main()
