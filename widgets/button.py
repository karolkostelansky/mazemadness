import pygame
import config


class Button:
    def __init__(self, x, y, width=None, height=None, command=None, text=""):
        """
        Initializes the Button with the given position, dimensions, command, and text.
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.command = command
        self.text = text

        self.font = pygame.font.Font(None, 45)
        self.render_text = self.font.render(self.text, True, config.WHITE)

        self.mouse_pressed = False
        self.default_color = (0, 120, 255)
        self.hover_color = (0, 150, 255)
        self.border_color = (0, 90, 200)

        self.border_offset = 15

        self.real_x, self.real_y = config.center_text(self.render_text, x, y)
        self.real_x -= self.border_offset
        self.real_y -= self.border_offset

        if self.width is None:
            self.width = self.render_text.get_width() + 2 * self.border_offset

        if self.height is None:
            self.height = self.render_text.get_height() + 2 * self.border_offset

    def draw(self, canvas):
        """
        Draws the button on the canvas, changes its appearance when hovered or clicked.
        """
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        if self.real_x <= mouse_pos[0] <= self.real_x + self.width and self.real_y <= mouse_pos[1] \
                <= self.real_y + self.height:

            self.draw_button(canvas, self.hover_color)

            if mouse_click[0]:
                if not self.mouse_pressed:
                    self.mouse_pressed = True
                    self.command()
        else:
            self.draw_button(canvas, self.default_color)

        self.draw_text(canvas)

        if not mouse_click[0]:
            self.mouse_pressed = False

    def draw_button(self, canvas, color):
        """
        Draws the button with rounded corners and a solid color.
        """
        pygame.draw.rect(canvas, color, (self.real_x, self.real_y, self.width, self.height),
                         border_radius=10)

        pygame.draw.rect(canvas, self.border_color,
                         (self.real_x, self.real_y, self.width, self.height), 3,
                         border_radius=10)

    def draw_text(self, canvas):
        """
        Draws the text on the button, centered within the button's area.
        """
        canvas.blit(self.render_text,
                    (self.real_x + self.border_offset, self.real_y + self.border_offset))
