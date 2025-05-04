import sys
import os
import threading
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pygame
from maze import maze_generator

pygame.init()

SIZE = 41
TILE_SIZE = 20
WINDOW_WIDTH, WINDOW_HEIGHT = TILE_SIZE * SIZE + 20, TILE_SIZE * SIZE + 20

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GOLD = (255, 215, 0)

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Maze Madness')


def test_maze_generator():
    maze = maze_generator.bfs_maze(SIZE)
    draw(maze["array"])
    draw_tile(maze["end_tile"][0], maze["end_tile"][1], GOLD)
    draw_tile(maze["player1_start"][0], maze["player1_start"][1], GREEN)
    draw_tile(maze["player2_start"][0], maze["player2_start"][1], GREEN)

    time.sleep(0.05)
    test_maze_generator()


def draw_tile(x, y, color=WHITE):
    start_x = 10
    start_y = 10

    pygame.draw.rect(screen, color, (start_x + x * TILE_SIZE, start_y + y * TILE_SIZE,
                                     TILE_SIZE, TILE_SIZE))


def draw(array):
    start_x = 10
    start_y = 10

    for y, row in enumerate(array):
        for x, number in enumerate(row):
            color = WHITE if number == 1 else BLACK
            pygame.draw.rect(screen, color, (start_x + x * TILE_SIZE, start_y + y * TILE_SIZE,
                                             TILE_SIZE, TILE_SIZE))


thread = threading.Thread(target=test_maze_generator, daemon=True)
thread.start()

RUNNING = True
while RUNNING:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUNNING = False

    pygame.display.update()

pygame.quit()
