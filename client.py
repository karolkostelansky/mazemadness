"""
    Created by Karol Kostelanský.
    This module implements client code.
"""

import threading
import sys

import time
import socket
import atexit
import signal
import pygame

from communication import communication, connect_to_server, message

from scenes.login_scene import LoginScene
from scenes.menu_scene import MenuScene
from scenes.game_scene import GameScene
from scenes.scene import SceneManager

from exceptions.my_exceptions import CommunicationError

import config


def handler(_, __):
    """Called when program received SIGINT"""
    log_out()
    sys.exit(0)


signal.signal(signal.SIGINT, handler)

pygame.init()
RUNNING = True

PORT = 65432
SERVER_ADDRESS = connect_to_server.check_server_status()
if not SERVER_ADDRESS:
    print("Server is not running")
    sys.exit(1)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_ADDRESS, PORT))

config.client = client

screen_info = pygame.display.Info()
config.window_width = screen_info.current_w // 2
config.window_height = int(screen_info.current_h / 1.8)

screen = pygame.display.set_mode((config.window_width, config.window_height))
pygame.display.set_caption('Maze madness')

config.scene_manager = SceneManager()

config.scene_manager.add_scene("LoginScene", LoginScene(config.scene_manager.switch_scene))
config.scene_manager.add_scene("MenuScene", MenuScene(config.scene_manager.switch_scene))
config.scene_manager.add_scene("GameScene", GameScene(config.scene_manager.switch_scene))

config.scene_manager.switch_scene("LoginScene")

if len(sys.argv) > 1:
    config.AUTOMATIC_TESTING = True
    config.CLIENT_NAME = sys.argv[1]
    config.scene_manager.current_scene.log_in()


def listen_for_messages():
    """
        Listens for incoming messages from the server and handles them.
    """
    global RUNNING

    while not stop_event.is_set():
        try:
            server_message = communication.load_object(client)
            config.scene_manager.current_scene.handle_loaded_object(server_message)
        except CommunicationError:
            print("Server closed the connection")
            RUNNING = False
            break


def log_out():
    """
        Function that is called at the end of the program to tell
        the server client has disconnected.
    """

    mess = message.Message()
    mess.info = "disconnect"
    mess.data = config.CLIENT_NAME
    communication.send_object(mess, client)


def user_count_change(data):
    """
        Function that is called when some player has left or joined.
    """
    config.users_names = data
    config.users_names.add(config.CLIENT_NAME)


def send_heartbeat():
    """
        Sends heartbeat messages to the server every 10 seconds.
        If no acknowledgment is received, disconnects the client.
    """
    global RUNNING

    while RUNNING:
        try:
            heartbeat_message = message.Message()
            heartbeat_message.info = "heartbeat"
            communication.send_object(heartbeat_message, client)

            if stop_event.wait(timeout=1):
                break
        except CommunicationError:
            print("Heartbeat failed. Server not responding.")
            RUNNING = False
            break


atexit.register(log_out)
stop_event = threading.Event()

listen_thread = threading.Thread(target=listen_for_messages, daemon=True)
listen_thread.start()

heartbeat_thread = threading.Thread(target=send_heartbeat, daemon=True)
heartbeat_thread.start()

last_time = time.time()
while RUNNING:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUNNING = False
        config.scene_manager.handle_event(event)

    dt = time.time() - last_time
    last_time = time.time()

    config.scene_manager.update(dt)

    config.scene_manager.draw(screen)
    pygame.display.update()

pygame.quit()
sys.exit(0)
