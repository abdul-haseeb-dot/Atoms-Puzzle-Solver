import pygame


class InputBox:
    def __init__(self, x, y, width, height, font, label, max_digits=2):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.label = label
        self.max_digits = max_digits
        self.text = ""

        self.BG_COLOR = (40, 45, 52)
        self.BG_COLOR_ACTIVE = (51, 57, 65)
        self.BORDER_COLOR = (73, 80, 88)
        self.BORDER_COLOR_ACTIVE = (255, 255, 255)
        self.TEXT_COLOR = (255, 255, 255)
        self.PLACEHOLDER_COLOR = (110, 118, 128)
        self.LABEL_COLOR = (180, 190, 200)
        self.BORDER_RADIUS = 10

        self.is_active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.is_active = self.rect.collidepoint(event.pos)

        elif event.type == pygame.KEYDOWN and self.is_active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key in (pygame.K_TAB, pygame.K_RETURN):
                pass
            elif event.unicode.isdigit() and len(self.text) < self.max_digits:
                self.text += event.unicode

    def display(self, screen):
        label_surface = self.font.render(self.label, True, self.LABEL_COLOR)
        label_rect = label_surface.get_rect(midbottom=(self.rect.centerx, self.rect.top - 10))
        screen.blit(label_surface, label_rect)

        bg_color = self.BG_COLOR_ACTIVE if self.is_active else self.BG_COLOR
        border_color = self.BORDER_COLOR_ACTIVE if self.is_active else self.BORDER_COLOR

        pygame.draw.rect(screen, bg_color, self.rect, border_radius=self.BORDER_RADIUS)
        pygame.draw.rect(
            screen, border_color, self.rect, width=2, border_radius=self.BORDER_RADIUS
        )

        if self.text:
            content_surface = self.font.render(self.text, True, self.TEXT_COLOR)
        else:
            content_surface = self.font.render("-", True, self.PLACEHOLDER_COLOR)

        content_rect = content_surface.get_rect(center=self.rect.center)
        screen.blit(content_surface, content_rect)

    def get_value(self):
        return int(self.text) if self.text else None
