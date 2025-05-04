import time
import pygame

from communication import communication, message
import config

from widgets.button import Button
from widgets.chatlog import Chatlog
from maze.player_maze import Maze

from .scene import Scene


class GameScene(Scene):
    def __init__(self, switch_scene_callback):
        """
        Initializes the GameScene with the given callback function for switching scenes.
        """
        super().__init__()
        self.switch_scene_callback = switch_scene_callback
        self.font = pygame.font.Font(None, 36)
        self.opponent = None
        self.maze = None

        self.last_time = None
        self.max_speed = 8

        self.button = None
        self.chatlog = None

        self.my_name = ""

    def init_button(self):
        """
        Initializes the button and chatlog for the game scene.
        """
        self.button = Button(x=self.calculate_mid(), y=config.window_height - 30,
                             command=self.go_back_to_menu, text="Leave game")

        self.chatlog = Chatlog(10, 10, self.maze.OFFSET_X, config.window_height,
                               background_color=(230, 255, 230), is_independent=True)

    def calculate_mid(self):
        """
        Calculates the horizontal center position of the maze.
        """
        return self.maze.OFFSET_X + (config.window_width - self.maze.OFFSET_X) // 2

    def handle_loaded_object(self, loaded_message):
        """
        Handles the loaded message and processes different types of server responses.
        """
        match loaded_message.info:
            case "user_count_change":
                self.user_count_change(loaded_message.data)

            case "left_game":
                config.scene_manager.switch_scene("MenuScene")

            case "opponent_changed_position":
                self.maze.move_opponent(loaded_message.data)

            case "player_has_won_a_game":
                config.scores[loaded_message.data] += 1

            case "public_message":
                self.chatlog.add_message(loaded_message.data)

            case "private_message":
                self.chatlog.add_message(loaded_message.data, True)

            case "challenge_no_longer_valid":
                self.remove_challenges(loaded_message.data)

            case _:
                ...

    def remove_challenges(self, players):
        """When challenge becomes invalid - the player started playing other game,
           function removes those two players from received challenges."""
        config.challenges_received = config.challenges_received - set(players)

    def update(self, dt):
        """
        Updates the game scene, including the maze and chatlog, based on the elapsed time.
        """
        self.chatlog.update(dt)

        if self.maze.win:
            return

        key_to_function = {
            pygame.K_w: self.maze.move_up,
            pygame.K_a: self.maze.move_left,
            pygame.K_s: self.maze.move_down,
            pygame.K_d: self.maze.move_right,
        }

        keys = pygame.key.get_pressed()

        for key, action in key_to_function.items():
            if keys[key]:
                if self.last_time is None:
                    self.last_time = time.time()

                elif time.time() - self.last_time < 1 / self.max_speed:
                    return

                self.last_time = time.time()
                action()

    def set_opponent(self, opponent):
        """
        Sets the opponent's name for the game.
        """
        self.opponent = opponent

    def set_names(self, names):
        """
        Sets the names of the player and the opponent.
        """
        self.my_name, self.opponent = names

    def set_maze(self, generated_maze):
        """
        Sets the maze for the game and initializes the button and chatlog.
        """
        self.maze = Maze(generated_maze, self.opponent, self.send_winning_message)
        self.init_button()

    def on_enter(self):
        """
        Called when the scene is entered. Sets the player's name.
        """
        self.my_name = config.CLIENT_NAME

    def send_winning_message(self):
        """
        Sends a message to the server when the player wins the game.
        """
        win_message = message.Message()
        win_message.info = "player_have_won_a_game"
        win_message.data = self.my_name

        communication.send_object(win_message, config.client)

    def go_back_to_menu(self):
        """
        Sends a message to the server indicating that the player is leaving the game.
        Switches to the MenuScene.
        """
        left_message = message.Message()
        left_message.info = "leaving_game"
        left_message.data = self.opponent

        communication.send_object(left_message, config.client)
        config.scene_manager.switch_scene("MenuScene")

    def handle_event(self, event):
        """
        Handles events for the game scene, including chatlog events.
        """
        self.chatlog.handle_event(event)

    def draw(self, screen):
        """
        Draws the game scene, including the maze, chatlog, and player information.
        """
        if self.maze is None:
            return

        screen.fill((250, 250, 250))
        self.chatlog.draw(screen)

        text = f"You are playing against: {self.opponent}"
        color = config.RED

        opponent_text = self.font.render(text, True, color)
        playing_against_text_x, playing_against_text_y = config.center_text(opponent_text,
                                                                            self.calculate_mid(),
                                                                            30)
        screen.blit(opponent_text, (playing_against_text_x, playing_against_text_y))

        self.button.draw(screen)
        self.maze.draw(screen)

        if self.maze.win is None:
            return

        winner_name = self.opponent if self.maze.win == "opponent" else self.my_name
        color = config.GREEN if self.maze.win == "me" else config.RED

        render_text = self.font.render(f"{winner_name} has won!", True, color)

        text_width = render_text.get_width()
        text_height = render_text.get_height()

        x, y = config.center_text(render_text, self.calculate_mid(), config.window_height // 2)

        border = 5
        border_width = 4
        pygame.draw.rect(screen, config.GOLD, (x - border - border_width, y - border - border_width,
                                               text_width + 2 * border + 2 * border_width,
                                               text_height + 2 * border + 2 * border_width))

        pygame.draw.rect(screen, config.BLACK,
                         (
                             x - border, y - border, text_width + 2 * border,
                             text_height + 2 * border))

        screen.blit(render_text, (x, y))
