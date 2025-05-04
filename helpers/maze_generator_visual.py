"""
    This module was used for visualizing the maze generation algorithm.
"""


import math
import random
import threading
import time
import collections
import pygame

pygame.init()

SIZE = 41
TILE_SIZE = 20
maze_array = [[0 for _ in range(SIZE)] for _ in range(SIZE)]

WINDOW_WIDTH, WINDOW_HEIGHT = TILE_SIZE * SIZE + 20, TILE_SIZE * SIZE + 20

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GOLD = (255, 215, 0)

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Maze Madness')


def bfs_maze():
    start_x, start_y = random.randrange(1, SIZE, 2), random.randrange(1, SIZE, 2)
    end_x, end_y = random.randrange(1, SIZE, 2), random.randrange(1, SIZE, 2)

    maze_array[start_y][start_x] = 1
    draw_tile(start_x, start_y, WHITE)

    queue = collections.deque()
    queue.append((start_x, start_y))

    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    while queue:
        current_x, current_y = queue.pop()

        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = current_x + dx * 2, current_y + dy * 2
            wall_x, wall_y = current_x + dx, current_y + dy

            if 0 < nx < SIZE and 0 < ny < SIZE and maze_array[ny][nx] == 0:
                time.sleep(0.01)
                maze_array[ny][nx] = 1
                maze_array[wall_y][wall_x] = 1
                draw_tile(nx, ny, GREEN)
                draw_tile(wall_x, wall_y, GREEN)

                end_x, end_y = nx, ny

                queue.append((nx, ny))

    draw_tile(end_x, end_y, GREEN)
    standard_bfs(end_x, end_y)


def standard_bfs(x, y):
    queue = collections.deque()
    queue.append((x, y, 1))

    seen = set()
    seen.add((x, y))

    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    wanted_distance = int(SIZE * 2)
    possible_ends = []

    while queue:
        current_x, current_y, distance = queue.popleft()
        if wanted_distance - SIZE <= distance <= wanted_distance + SIZE:
            possible_ends.append((current_x, current_y))
            draw_tile(current_x, current_y, BLUE)

        for dx, dy in directions:
            new_x, new_y = current_x + dx, current_y + dy

            if new_x < 0 or new_x >= SIZE or new_y < 0 or new_y >= SIZE \
                    or (new_x, new_y) in seen:
                continue

            if maze_array[new_y][new_x] == 0:
                continue

            queue.append((new_x, new_y, distance + 1))
            draw_tile(new_x, new_y, WHITE)
            seen.add((new_x, new_y))
            time.sleep(0.001)

    for pos in possible_ends:
        draw_tile(pos[0], pos[1], WHITE)

    end1, end2 = find_best_ends(possible_ends)
    draw(maze_array)
    draw_tile(end1[0], end1[1], GREEN)
    draw_tile(end2[0], end2[1], GREEN)
    draw_tile(x, y, GOLD)

    time.sleep(5)

    start_again()


def start_again():
    global maze_array

    maze_array = [[0 for _ in range(SIZE)] for _ in range(SIZE)]
    draw(maze_array)
    bfs_maze()


def find_best_ends(array):
    max_distance = 0
    best_pair = None

    for i in range(len(array)):
        for j in range(i + 1, len(array)):
            x1, y1 = array[i]
            x2, y2 = array[j]

            distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

            if distance > max_distance:
                max_distance = distance
                best_pair = ((x1, y1), (x2, y2))

    return best_pair[0], best_pair[1]


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


thread = threading.Thread(target=bfs_maze, daemon=True)
thread.start()

RUNNING = True
while RUNNING:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUNNING = False

    pygame.display.update()

pygame.quit()
