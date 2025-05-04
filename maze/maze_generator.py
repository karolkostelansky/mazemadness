"""
    This module contains algorithms for generating a maze using BFS
    and finding start positions for players.
"""

import math
import random
import collections


def bfs_maze(size):
    """Generates a maze and finds the start positions for two players."""
    ans = {}

    array = [[0 for _ in range(size)] for _ in range(size)]
    ans["array"] = array

    start_x, start_y = random.randrange(1, size, 2), random.randrange(1, size, 2)
    end_x, end_y = random.randrange(1, size, 2), random.randrange(1, size, 2)

    array[start_y][start_x] = 1

    queue = collections.deque()
    queue.append((start_x, start_y))

    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    while queue:
        current_x, current_y = queue.pop()
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = current_x + dx * 2, current_y + dy * 2
            wall_x, wall_y = current_x + dx, current_y + dy

            if 0 < nx < size and 0 < ny < size and array[ny][nx] == 0:
                array[ny][nx] = 1
                array[wall_y][wall_x] = 1
                end_x, end_y = nx, ny
                queue.append((nx, ny))

    ans["end_tile"] = (end_x, end_y)
    standard_bfs(end_x, end_y, ans, size)
    return ans


def standard_bfs(x, y, ans, size):
    """Finds possible start positions for players using BFS."""

    queue = collections.deque()
    queue.append((x, y, 1))

    seen = set()
    seen.add((x, y))

    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    wanted_distance = int(size * 2)
    possible_ends = []

    while queue:
        current_x, current_y, distance = queue.popleft()
        if wanted_distance - size // 2 <= distance <= wanted_distance + size // 2:
            possible_ends.append((current_x, current_y))

        for dx, dy in directions:
            new_x, new_y = current_x + dx, current_y + dy

            if new_x < 0 or new_x >= size or new_y < 0 or new_y >= size \
                    or (new_x, new_y) in seen:
                continue

            if ans["array"][new_y][new_x] == 0:
                continue

            queue.append((new_x, new_y, distance + 1))
            seen.add((new_x, new_y))

    end1, end2 = find_best_ends(possible_ends)
    ans["player1_start"] = end1
    ans["player2_start"] = end2


def find_best_ends(array):
    """Finds the two furthest points in the maze."""

    max_distance = 0
    best_pair = None

    array_length = len(array)
    for i, _ in enumerate(array):
        for j in range(i + 1, array_length):
            x1, y1 = array[i]
            x2, y2 = array[j]

            distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

            if distance > max_distance:
                max_distance = distance
                best_pair = ((x1, y1), (x2, y2))

    return best_pair[0], best_pair[1]
