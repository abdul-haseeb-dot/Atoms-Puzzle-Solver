import pygame


class Atom:
    def __init__(self, center_x, center_y, radius, font, row, col):
        self.center = (center_x, center_y)
        self.radius = radius
        self.font = font
        self.row = row
        self.col = col

        self.state = 0  # 0 = empty, 1-8 = atom value

        self.FILL_COLOR = (46, 52, 60)
        self.FILL_COLOR_HOVER = (58, 65, 74)
        self.BORDER_COLOR = (255, 255, 255)
        self.BORDER_COLOR_ERASE = (224, 122, 122)
        self.TEXT_COLOR = (255, 255, 255)
        self.HOVER_EMPTY_COLOR = (255, 255, 255, 35)

        self.is_hovered = False

    def handle_event(self, event, eraser_active):
        if event.type == pygame.MOUSEMOTION:
            dx = event.pos[0] - self.center[0]
            dy = event.pos[1] - self.center[1]
            self.is_hovered = (dx * dx + dy * dy) <= (self.radius * self.radius)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            dx = event.pos[0] - self.center[0]
            dy = event.pos[1] - self.center[1]
            if (dx * dx + dy * dy) <= (self.radius * self.radius):
                if eraser_active:
                    self.state = 0
                else:
                    self.state = (self.state + 1) % 9
                return True
        return False

    def display(self, screen, eraser_active):
        if self.state == 0:
            if self.is_hovered:
                overlay = pygame.Surface(
                    (self.radius * 2, self.radius * 2), pygame.SRCALPHA
                )
                pygame.draw.circle(
                    overlay, self.HOVER_EMPTY_COLOR, (self.radius, self.radius), self.radius
                )
                screen.blit(
                    overlay, (self.center[0] - self.radius, self.center[1] - self.radius)
                )
            return

        fill_color = self.FILL_COLOR_HOVER if self.is_hovered else self.FILL_COLOR
        border_color = self.BORDER_COLOR_ERASE if (self.is_hovered and eraser_active) else self.BORDER_COLOR

        pygame.draw.circle(screen, fill_color, self.center, self.radius)
        pygame.draw.circle(screen, border_color, self.center, self.radius, width=2)

        text_surface = self.font.render(str(self.state), True, self.TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.center)
        screen.blit(text_surface, text_rect)
