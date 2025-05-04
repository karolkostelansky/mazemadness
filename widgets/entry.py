import pygame

import config


class Entry:
    def __init__(self, x, y, width, height, text='', font_size=32, enter_callback=None):
        """
        Initializes the Entry field with the given position, dimensions, text, font size, and callback.
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.font_size = font_size

        self.real_x = self.x - self.width / 2
        self.real_y = self.y - self.height / 2

        self.text = text
        self.font = pygame.font.SysFont('Arial', self.font_size)
        self.active = False
        self.color_inactive = (200, 200, 200)
        self.color_active = (240, 240, 255)
        self.color_border = (0, 90, 200)
        self.cursor_pos = len(text)
        self.cursor_visible = True
        self.cursor_timer = 0
        self.enter_callback = enter_callback
        self.offset = 0
        self.backspace_active = False
        self.backspace_timer = 0

    def handle_event(self, event):
        """
        Handles events such as mouse clicks and key presses for the Entry field.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.real_x <= event.pos[0] <= self.real_x + self.width and self.real_y <= event.pos[
                1] <= self.real_y + self.height:
                self.active = True
            else:
                self.active = False

        if self.active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.backspace_active = True
                    self.delete_character()
                elif event.key == pygame.K_RETURN and self.enter_callback:
                    if config.scene_manager.current_scene != config.scene_manager.scenes[
                        "LoginScene"]:
                        self.offset = 0
                    self.enter_callback()
                elif len(self.text) < 100:
                    self.text = self.text[:self.cursor_pos] + event.unicode + self.text[
                                                                              self.cursor_pos:]
                    self.cursor_pos += 1
                    self.adjust_offset()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_BACKSPACE:
                    self.backspace_active = False

    def delete_character(self):
        """
        Deletes a character and adjusts cursor/offset.
        """
        if len(self.text) > 0:
            self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
            self.cursor_pos -= 1
            self.cursor_pos = max(self.cursor_pos, 0)
            self.offset = max(self.offset - 1, 0)
            self.adjust_offset()

    def adjust_offset(self):
        """
        Adjusts the text offset to ensure the cursor is visible.
        """
        text_width = self.font.size(self.text[self.offset:self.cursor_pos])[0]
        if text_width > self.width - 20:
            self.offset += 1

    def draw(self, canvas):
        """
        Draws the Entry field and its text on the canvas.
        """
        border_color = self.color_active if self.active else self.color_inactive
        pygame.draw.rect(canvas, border_color, (self.real_x, self.real_y, self.width, self.height),
                         border_radius=10)

        visible_text = self.text[self.offset:]
        text_surface = self.font.render(visible_text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(
            topleft=(self.real_x + 5, self.real_y + (self.height - text_surface.get_height()) // 2))
        canvas.blit(text_surface, text_rect)

        if self.active and self.cursor_visible:
            cursor_x = self.real_x + 5 + self.font.size(self.text[self.offset:self.cursor_pos])[0]
            cursor_rect = pygame.Rect(cursor_x, self.real_y + 10, 2, self.height - 20)
            pygame.draw.rect(canvas, (0, 0, 0), cursor_rect)

    def update_cursor(self, dt):
        """
        Updates the cursor visibility and handles backspace behavior.
        """
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

        if self.active and self.backspace_active:
            self.backspace_timer += dt
            if self.backspace_timer >= 0.1:
                self.delete_character()
                self.backspace_timer = 0
        else:
            self.backspace_timer = 0
