import pygame

from communication import communication, message
import config
from .entry import Entry


class Chatlog:
    def __init__(self, start_x, start_y, end_x, end_y, background_color=(255, 255, 255),
                 is_independent=False):
        """
        Initializes the Chatlog with the given position, dimensions, background color, and other settings.
        """
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y

        self.background_color = background_color
        self.is_independent = is_independent

        self.width = self.end_x - self.start_x
        self.height = self.end_y - self.start_y

        self.mid_x = self.start_x + (self.end_x - self.start_x) // 2

        self.font = pygame.font.SysFont("Arial", 20)
        self.title_font = pygame.font.SysFont("Arial", 24)
        self.entry = Entry(self.mid_x, self.end_y - 25, self.width * (2 / 3), 30, font_size=20,
                           enter_callback=self.send_message)

        self.max_number_messages = int(self.height * (8 / 10) / (23 + 5))
        self.messages = []

        self.private_messages = []

        self.set_messages(config.public_messages)

    def set_messages(self, mess):
        """
        Sets the messages for the chatlog, limiting the number of messages to max_number_messages.
        """
        self.messages = mess[-self.max_number_messages:] if self.max_number_messages <= len(
            config.public_messages) else mess

    def draw(self, screen):
        """
        Draws the chatlog and its messages on the screen.
        """
        pygame.draw.rect(screen, self.background_color,
                         (self.start_x, self.start_y, self.end_x - self.start_x,
                          self.end_y - self.start_y))
        if self.is_independent:
            pygame.draw.rect(screen, config.BORDER, (self.start_x, self.start_y, self.end_x -
                                                     self.start_x, self.end_y - self.start_y),
                             width=3)

        messages_to_draw = self.messages
        if self.is_independent:
            messages_to_draw = self.private_messages
            title_text = self.title_font.render("Chat", True, (0, 0, 0))
            screen.blit(title_text, (
                self.start_x + (self.end_x - self.start_x) // 2 - title_text.get_width() // 2,
                self.start_y + 10))

        message_y = self.start_y + 50 if self.is_independent else self.start_y
        for line in messages_to_draw:
            message_text = self.font.render(line, True, (0, 0, 0))
            screen.blit(message_text, (self.start_x + 10, message_y))
            message_y += message_text.get_height() + 5

        self.entry.draw(screen)

    def handle_event(self, event):
        """
        Handles events such as mouse clicks and key presses for the chatlog and entry.
        """
        self.entry.handle_event(event)

    def add_message(self, received_message, private=False):
        """
        Adds a received message to the chatlog, either as a public or private message.
        """
        if not received_message:
            return

        wrapped_message = self.wrap_text(received_message)

        if private:
            for line in wrapped_message:
                self.private_messages.append(line)
            while len(self.private_messages) > self.max_number_messages:
                self.private_messages.pop(0)
        else:
            for line in wrapped_message:
                self.messages.append(line)

            while len(self.messages) > self.max_number_messages:
                self.messages.pop(0)

    def send_message(self):
        """
            Sends the message that was entered in the entry field.
        """
        body = self.entry.text
        if not body:
            return

        self.add_message(f"{config.CLIENT_NAME} - {body}", self.is_independent)
        self.entry.text = ""

        message_to_send = message.Message()
        message_to_send.info = "public_message" if not self.is_independent else "private_message"
        message_to_send.data = f"{config.CLIENT_NAME} - {body}"

        communication.send_object(message_to_send, config.client)

    def update(self, dt):
        """
        Updates the cursor in the entry field based on the elapsed time.
        """
        self.entry.update_cursor(dt)

    def wrap_text(self, text):
        """
        Splits the given text into multiple lines so that each line fits within max_width.
        The algorithm adds one letter at a time to the current line until it exceeds max_width.
        """
        lines = []
        current_line = ""

        for char in text:
            test_line = current_line + char
            if self.font.size(test_line)[0] <= self.width - 20:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = char

        if current_line:
            lines.append(current_line)

        return lines
