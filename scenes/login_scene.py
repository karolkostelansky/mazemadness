import pygame

import config
from communication import communication, message
from widgets.entry import Entry
from widgets.button import Button

from .scene import Scene


class LoginScene(Scene):
    """
    Represents the login scene where players can enter their name and connect to the server.
    Handles user input, server responses, and transitions to the next scene upon successful login.
    """

    def __init__(self, switch_scene_callback):
        """
        Initializes the login scene with entry field and button.
        """
        super().__init__()
        self.entry = Entry(x=config.window_width // 2, y=config.window_height // 2 - 50, width=400,
                           height=50, enter_callback=self.log_in)
        self.button = Button(x=config.window_width // 2, y=config.window_height // 2 + 50,
                             command=self.log_in, text="Connect")
        self.switch_scene_callback = switch_scene_callback

        self.error_message = ""
        self.error_timer = 0

    def handle_loaded_object(self, loaded_message):
        """
        Handles the server response based on the message received.
        """
        match loaded_message.info:
            case "login_successful":
                config.users_names = loaded_message.data[0]
                config.live_games = set(loaded_message.data[1])
                config.scores = loaded_message.data[2]
                config.public_messages = loaded_message.data[3]

                config.scene_manager.switch_scene("MenuScene")
                config.scene_manager.scenes["MenuScene"].set_players(loaded_message.data)

            case "wrong_login_name":
                self.error_message = "Name is already taken."
                self.error_timer = 3

            case "user_count_change":
                self.user_count_change(loaded_message.data)

            case _:
                pass

    def log_in(self):
        """
        Sends a login attempt message to the server with the entered name.
        Displays an error message if the name is invalid or too long.
        """
        if not self.entry.text and not config.AUTOMATIC_TESTING:
            return

        if len(self.entry.text) > config.MAXIMAL_NAME_LENGTH:
            self.error_message = "Name is too long"
            self.error_timer = 3
            return

        config.CLIENT_NAME = self.entry.text if not config.AUTOMATIC_TESTING else config.CLIENT_NAME
        init = message.Message("login_attempt", config.CLIENT_NAME)
        communication.send_object(init, config.client)

    def handle_event(self, event):
        """
        Handles events like keyboard input or mouse clicks.
        """
        self.entry.handle_event(event)

    def update(self, dt):
        """
        Updates the scene state, including cursor position and error message timer.
        """
        self.entry.update_cursor(dt)

        if self.error_timer > 0:
            self.error_timer -= dt
            if self.error_timer <= 0:
                self.error_message = ""

    def draw(self, screen):
        """
        Draws the scene, including the entry field, button, and error messages.
        """
        screen.fill(config.WHITE)
        self.entry.draw(screen)
        self.button.draw(screen)

        if self.error_message:
            font = pygame.font.Font(None, 36)
            error_surface = font.render(self.error_message, True, (255, 0, 0))
            screen.blit(error_surface, (200, 150))

    def on_enter(self):
        """
        Called when the scene becomes active.
        """
        self.entry.active = True
