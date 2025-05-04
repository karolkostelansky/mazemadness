"""Module contains base scene class and scene manager"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config


class Scene:
    """
        Base class for all scenes in the game.

        A scene represents a single screen or stage in the game, such as a login screen, menu,
        or gameplay screen. This class provides methods for handling events, updating the scene,
        drawing the scene, and managing transitions between scenes.
    """

    def __init__(self):
        """Initializes the scene."""


    def handle_event(self, event):
        """Handles user events for the scene."""


    def user_count_change(self, data):
        """This method updates the list of players, scores,
            and challenges based on the provided data."""
        config.users_names = data[0]
        config.scores = data[1]
        config.users_names.add(config.CLIENT_NAME)

        config.challenges_received = {challenge for challenge in config.challenges_received if
                                      challenge in data}
        config.challenges_send = {challenge for challenge in config.challenges_send if
                                  challenge in data}

    def update(self, dt):
        """This method is called every frame to update the state of the scene."""


    def draw(self, screen):
        """This method is called every frame to render the scene to the screen."""


    def on_enter(self):
        """This method is called when the scene is switched to and becomes the active scene."""


    def on_exit(self):
        """This method is called when the scene is switched away from
            and is no longer the active scene."""


class SceneManager:
    """Manages the transitions and handling of scenes."""

    def __init__(self):
        """Initializes the SceneManager with an empty set of scenes and no active scene."""
        self.scenes = {}
        self.current_scene = None

    def add_scene(self, name, scene):
        """Adds a new scene to the manager.

        Args:
            name: The name of the scene to add.
            scene: The scene object to add.
        """
        self.scenes[name] = scene

    def switch_scene(self, name):
        """Switches to a new scene."""
        if self.current_scene:
            self.current_scene.on_exit()
        self.current_scene = self.scenes.get(name)
        if self.current_scene:
            self.current_scene.on_enter()

    def handle_event(self, event):
        """This method passes events to the current scene's `handle_event` method."""
        if self.current_scene:
            self.current_scene.handle_event(event)

    def update(self, dt):
        """This method calls the `update` method on the current scene."""
        if self.current_scene:
            self.current_scene.update(dt)

    def draw(self, screen):
        """This method calls the `draw` method on the current scene to render it to the screen."""
        if self.current_scene:
            self.current_scene.draw(screen)
