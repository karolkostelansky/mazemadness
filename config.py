"""This module is used for configuration and for sharing variables throughout different files."""

MAXIMAL_NAME_LENGTH = 8

client = ""
users_names = set()
scores = {}
challenges_received = set()
challenges_send = set()

public_messages = []

CLIENT_NAME = ""
AUTOMATIC_TESTING = False

window_width = 1200
window_height = 700

scene_manager = ""

# Colors for Pygame
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GOLD = (255, 215, 0)
RED = (255, 0, 0)
BORDER = (171, 104, 87)


def center_text(render_text, want_x, want_y):
    """Helper function that calculates correct coordinates for text rendering."""

    text_width = render_text.get_width()
    text_height = render_text.get_height()

    return want_x - text_width // 2, want_y - text_height // 2
