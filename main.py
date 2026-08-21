import pygame
import sys
from enum import Enum, auto
from button import Button
from input_box import InputBox
from grid import create_grid, draw_grid_lines, draw_solution_edges
from solver import solve_atoms


class ScreenState(Enum):
    MENU = auto()
    DESIGN = auto()
    SOLVE = auto()


MIN_GRID_SIZE = 4
MAX_GRID_SIZE = 15


def main():
    pygame.init()

    WINDOW_WIDTH = 700
    WINDOW_HEIGHT = 700
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Atoms")

    BG_COLOR = (18, 36, 29)
    TITLE_COLOR = (255, 255, 255)
    SUBTITLE_COLOR = (180, 190, 200)
    ERROR_COLOR = (224, 122, 122)
    GRID_LINE_COLOR = (66, 71, 77)
    SOLUTION_LINE_COLOR = (220, 20, 60)

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

    solved_prompt_surface = subtitle_font.render(
        "Solved! Click Next to move on", True, SUBTITLE_COLOR
    )
    solved_prompt = solved_prompt_surface.get_rect(center=(WINDOW_WIDTH // 2, SUBTITLE_Y))

    unsolved_prompt_surface = subtitle_font.render(
        "Cannot be solved! Click Next to move on", True, SUBTITLE_COLOR
    )
    unsolved_prompt = unsolved_prompt_surface.get_rect(center=(WINDOW_WIDTH // 2, SUBTITLE_Y))

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

    # eraser and solve sit side by side along the same row the Mambo
    # solve/next button used to occupy on its own
    ACTION_BUTTON_WIDTH = 220
    ACTION_BUTTON_HEIGHT = 70
    ACTION_BUTTON_GAP = 20
    ACTION_BUTTON_Y = 610

    eraser_button = Button(
        WINDOW_WIDTH // 2 - ACTION_BUTTON_WIDTH - ACTION_BUTTON_GAP // 2,
        ACTION_BUTTON_Y,
        ACTION_BUTTON_WIDTH,
        ACTION_BUTTON_HEIGHT,
        "ERASER",
        small_button_font,
        (73, 80, 88),
    )
    ERASER_COLOR_ACTIVE = (224, 122, 122)
    ERASER_COLOR_INACTIVE = (73, 80, 88)

    solve_button = Button(
        WINDOW_WIDTH // 2 + ACTION_BUTTON_GAP // 2,
        ACTION_BUTTON_Y,
        ACTION_BUTTON_WIDTH,
        ACTION_BUTTON_HEIGHT,
        "SOLVE",
        small_button_font,
        (110, 200, 150),
    )

    NEXT_BUTTON_WIDTH = 300
    NEXT_BUTTON_HEIGHT = 70

    next_button = Button(
        WINDOW_WIDTH // 2 - NEXT_BUTTON_WIDTH // 2,
        ACTION_BUTTON_Y,
        NEXT_BUTTON_WIDTH,
        NEXT_BUTTON_HEIGHT,
        "NEXT",
        button_font,
        (120, 170, 230),
    )

    state = ScreenState.MENU
    error_message = None
    eraser_active = False

    rows = None
    cols = None
    atoms = []
    grid_rect = None
    cell_size = None

    solved = None
    solve_error = None
    solution_edges = []

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
                        # w/h are the number of vertical/horizontal LINES the
                        # user wants; the grid is built in terms of boxes
                        # (rows/cols), and a grid of N lines has N-1 boxes
                        cols, rows = w - 1, h - 1
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

                if solve_button.handle_event(event):
                    solved, solve_error, solution_edges = solve_atoms(atoms, rows, cols)
                    state = ScreenState.SOLVE

            elif state == ScreenState.SOLVE:
                if next_button.handle_event(event):
                    state = ScreenState.MENU

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
            solve_button.display(screen)

        elif state == ScreenState.SOLVE:
            if solved:
                screen.blit(solved_prompt_surface, solved_prompt)
            else:
                screen.blit(unsolved_prompt_surface, unsolved_prompt)

                if solve_error:
                    error_surface = error_font.render(solve_error, True, ERROR_COLOR)
                    error_rect = error_surface.get_rect(center=(WINDOW_WIDTH // 2, ERROR_Y))
                    screen.blit(error_surface, error_rect)

            draw_grid_lines(screen, grid_rect, rows, cols, cell_size, GRID_LINE_COLOR)
            draw_solution_edges(screen, solution_edges, SOLUTION_LINE_COLOR)

            for atom_row in atoms:
                for atom in atom_row:
                    atom.display(screen, eraser_active=False)

            next_button.display(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


main()
