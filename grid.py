import pygame
from atom import Atom


def create_grid(rows, cols, window_width, atom_font):
    AVAILABLE_SPACE = 440
    TOP_MARGIN = 150

    cell_size = AVAILABLE_SPACE // max(rows, cols)
    total_width = cols * cell_size
    total_height = rows * cell_size

    start_x = (window_width - total_width) // 2
    start_y = TOP_MARGIN

    atom_radius = max(10, min(16, round(cell_size * 0.32)))

    atoms = []
    for row in range(rows + 1):
        atom_row = []
        for col in range(cols + 1):
            x = start_x + col * cell_size
            y = start_y + row * cell_size
            atom_row.append(Atom(x, y, atom_radius, atom_font, row, col))
        atoms.append(atom_row)

    grid_rect = pygame.Rect(start_x, start_y, total_width, total_height)

    return atoms, grid_rect, cell_size


def draw_grid_lines(screen, grid_rect, rows, cols, cell_size, color):
    for row in range(rows + 1):
        y = grid_rect.top + row * cell_size
        pygame.draw.line(screen, color, (grid_rect.left, y), (grid_rect.right, y), 2)

    for col in range(cols + 1):
        x = grid_rect.left + col * cell_size
        pygame.draw.line(screen, color, (x, grid_rect.top), (x, grid_rect.bottom), 2)


def draw_solution_edges(screen, solution_edges, color):
    LINE_THICKNESS = 4
    DOUBLE_LINE_GAP = 4

    for atom1, atom2, orientation, line_count in solution_edges:
        x1, y1 = atom1.center
        x2, y2 = atom2.center

        if line_count == 1:
            pygame.draw.line(screen, color, (x1, y1), (x2, y2), LINE_THICKNESS)
        else:
            if orientation == "H":
                pygame.draw.line(
                    screen, color, (x1, y1 - DOUBLE_LINE_GAP), (x2, y2 - DOUBLE_LINE_GAP), LINE_THICKNESS
                )
                pygame.draw.line(
                    screen, color, (x1, y1 + DOUBLE_LINE_GAP), (x2, y2 + DOUBLE_LINE_GAP), LINE_THICKNESS
                )
            else:
                pygame.draw.line(
                    screen, color, (x1 - DOUBLE_LINE_GAP, y1), (x2 - DOUBLE_LINE_GAP, y2), LINE_THICKNESS
                )
                pygame.draw.line(
                    screen, color, (x1 + DOUBLE_LINE_GAP, y1), (x2 + DOUBLE_LINE_GAP, y2), LINE_THICKNESS
                )
