import sys
import os

import pygame

from communication import communication, message

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config


class Maze:
    """
    Manages the maze, player movement, win conditions, and drawing of the maze.
    """

    def __init__(self, generated_maze, opponent, win_callback):
        """
        Initializes the maze with the generated maze data and opponent.
        """
        self.opponent = opponent
        self.array = generated_maze["array"]
        self.win_callback = win_callback

        self.my_position_x, self.my_position_y = generated_maze[config.CLIENT_NAME]
        self.opponent_position_x, self.opponent_position_y = generated_maze[self.opponent]

        self.end_x, self.end_y = generated_maze["end_tile"]

        self.NUMBER_OF_TILES = len(self.array)

        self.OFFSET_Y = 70
        self.TILE_SIZE = (config.window_height - 2 * self.OFFSET_Y) // self.NUMBER_OF_TILES
        self.OFFSET_X = (config.window_width - self.NUMBER_OF_TILES * self.TILE_SIZE) - 20

        self.win = None

    def change_position(self):
        """
        Updates the player's position and checks if they have reached the end tile.
        """
        if (self.my_position_x, self.my_position_y) == (self.end_x, self.end_y):
            self.win = "me"
            self.win_callback()

        info_to_server = message.Message()
        info_to_server.info = "change_position"
        info_to_server.data = (self.my_position_x, self.my_position_y)

        communication.send_object(info_to_server, config.client)

    def move_opponent(self, new_position):
        """
        Updates the opponent's position and checks if they have reached the end tile.
        """
        self.opponent_position_x, self.opponent_position_y = new_position

        if (self.opponent_position_x, self.opponent_position_y) == (self.end_x, self.end_y):
            self.win = "opponent"

    def move_up(self):
        """Moves the player up if the tile is walkable."""
        new_y = max(0, self.my_position_y - 1)
        if self.array[new_y][self.my_position_x] == 1:
            self.my_position_y = new_y
            self.change_position()

    def move_down(self):
        """Moves the player down if the tile is walkable."""
        new_y = min(self.NUMBER_OF_TILES - 1, self.my_position_y + 1)
        if self.array[new_y][self.my_position_x] == 1:
            self.my_position_y = new_y
            self.change_position()

    def move_left(self):
        """Moves the player left if the tile is walkable."""
        new_x = max(0, self.my_position_x - 1)
        if self.array[self.my_position_y][new_x] == 1:
            self.my_position_x = new_x
            self.change_position()

    def move_right(self):
        """Moves the player right if the tile is walkable."""
        new_x = min(self.NUMBER_OF_TILES - 1, self.my_position_x + 1)
        if self.array[self.my_position_y][new_x] == 1:
            self.my_position_x = new_x
            self.change_position()

    def draw(self, screen):
        """
        Draws the maze and the player positions on the screen.
        """
        for y, row in enumerate(self.array):
            for x, number in enumerate(row):
                color = config.WHITE if number == 1 else config.BLACK
                pygame.draw.rect(screen, color, (
                    self.OFFSET_X + x * self.TILE_SIZE, self.OFFSET_Y + y * self.TILE_SIZE,
                    self.TILE_SIZE, self.TILE_SIZE))

        self.draw_tile(screen, self.my_position_x, self.my_position_y, config.GREEN)
        self.draw_tile(screen, self.opponent_position_x, self.opponent_position_y, config.RED)
        self.draw_tile(screen, self.end_x, self.end_y, config.GOLD)

    def draw_tile(self, screen, x, y, color=config.WHITE):
        """
        Draws a single tile on the screen.
        """
        pygame.draw.rect(screen, color,
                         (self.OFFSET_X + x * self.TILE_SIZE, self.OFFSET_Y + y * self.TILE_SIZE,
                          self.TILE_SIZE, self.TILE_SIZE))
