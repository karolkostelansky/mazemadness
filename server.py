"""
    This module implements the server.
    When client connects to a server, new thread is created which
    communicates with him.
"""

import random
import time
import socket
import atexit
import threading

import sys
import signal

from communication import communication, server_utils, message

import maze.maze_generator
from exceptions.my_exceptions import CommunicationError

HOST = server_utils.get_local_ip()
PORT = 65432
MAX_CLIENTS = 20

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))

server_socket.listen(MAX_CLIENTS)

clients = []
clients_lock = threading.Lock()

clients_name = set()
client_to_name = {}
names_to_client = {}

last_heartbeat = {}
HEARTBEAT_TIMEOUT = 10

client_threads = {}
games = {}
scores = {}

public_messages = []

shutdown_event = threading.Event()


def handler(_, __):
    """Called when program receives SIGINT"""
    shutdown_event.set()
    server_socket.close()
    sys.exit(0)


signal.signal(signal.SIGINT, handler)


def safe_send_object(object_to_send, receiver):
    """
        Safely sends an object using the given receiver socket.
        Removes the receiver from clients and stops its thread if an error occurs.
    """
    try:
        communication.send_object(object_to_send, receiver)
    except CommunicationError as e:
        print(f"Communication error with receiver {receiver}: {e}")
        with clients_lock:
            if receiver in clients:
                clients.remove(receiver)

            if receiver in client_threads:
                stop_client_thread(receiver)


def client_login(name, sender):
    """
        Called when client tries to connect to the server.
        Checks whether name of the clients is unique.
    """

    answer = message.Message()

    answer.info = "login_successful" if name not in clients_name else "wrong_login_name"
    if name not in clients_name:
        clients_name.add(name)
    answer.data = [clients_name,
                   [tuple(players) for players in games.keys() if games[players] != []], scores,
                   public_messages]
    client_to_name[sender] = name
    names_to_client[name] = sender
    scores[name] = 0

    safe_send_object(answer, sender)

    answer.info = "user_count_change"
    answer.data = [clients_name, scores]
    for client in clients:
        if client != sender:
            safe_send_object(answer, client)


def find_player_games(name):
    """
        Helper function, finds all games which player with given name is playing.
        Player should be able to play maximally 1 game, this is just paranoia.
    """
    ans = []
    for (first, second) in games.keys():
        if name == first:
            ans.append((name, second))

        elif name == second:
            ans.append((name, first))

    return ans


def client_logout(name, sender):
    """
        When player sends message he logged_out, this functions sends
        this information to all other players.
    """

    if name not in clients_name:
        return

    clients_name.remove(name)
    if sender in clients:
        clients.remove(sender)

    del scores[name]

    left_message = message.Message()
    left_message.info = "left_game"
    player_games = find_player_games(name)
    for game in player_games:
        left_message.data = game
        safe_send_object(left_message, names_to_client[game[1]])

    info_message = message.Message()
    info_message.info = "user_count_change"
    info_message.data = [clients_name, scores]

    for client in clients:
        if client == sender:
            continue

        safe_send_object(info_message, client)


def stop_client_thread(client_connection):
    """Stops the thread handling the client and removes the client from the list."""

    if client_connection in client_threads:
        client_threads[client_connection].set()
        client_threads.pop(client_connection, None)

    else:
        return

    if client_connection in clients:
        clients.remove(client_connection)

    if client_connection in client_to_name:
        client_logout(client_to_name[client_connection], client_connection)
        try:
            del names_to_client[client_to_name[client_connection]]
            del client_to_name[client_connection]
        except KeyError:
            ...

    client_connection.close()


def create_challenge(loaded_message, sender):
    """Sends info to the player who was challenged by other player."""

    player1 = client_to_name[sender]
    player2 = loaded_message.data

    answer = message.Message()
    answer.info = "received_challenge"
    answer.data = player1

    opponent = None
    for opponent_connection, name in client_to_name.items():
        if name == player2:
            opponent = opponent_connection
            break

    safe_send_object(answer, opponent)


def delete_challenge(loaded_message, sender):
    """
        Sends info that the opponent was too scared and changed
        his mind to play against given player.
    """
    player1 = client_to_name[sender]
    player2 = loaded_message.data

    answer = message.Message()
    answer.info = "delete_challenge"
    answer.data = player1

    opponent = None
    for opponent_connection, name in client_to_name.items():
        if name == player2:
            opponent = opponent_connection
            break

    safe_send_object(answer, opponent)


def accept_challenge(loaded_message, sender):
    """Inform given player that his challenge was accepted."""

    player1 = client_to_name[sender]
    player2 = loaded_message.data

    players = frozenset([player1, player2])

    maze_size = random.randrange(21, 31, 2)
    generated_maze = maze.maze_generator.bfs_maze(maze_size)

    generated_maze[player1] = generated_maze["player1_start"]
    generated_maze[player2] = generated_maze["player2_start"]

    answer = message.Message()
    answer.info = "accepted_challenge"
    answer.data = [player1, generated_maze]

    opponent = None
    for opponent_connection, name in client_to_name.items():
        if name == player2:
            opponent = opponent_connection
            break

    safe_send_object(answer, opponent)

    challenge_no_longer_valid = message.Message()
    challenge_no_longer_valid.info = "challenge_no_longer_valid"
    challenge_no_longer_valid.data = (player1, player2)

    answer.data[0] = player2

    safe_send_object(answer, sender)

    for client in clients:
        try:
            if client_to_name[client] not in (player1, player2):
                safe_send_object(challenge_no_longer_valid, client)
        except KeyError:
            ...

    games[players] = generated_maze


def name_to_client(find_name):
    """Helper function"""
    for conn, name in client_to_name.items():
        if name == find_name:
            return conn

    return None


def notify_change_position(loaded_message, sender):
    """Sends information that opponent has made a move in game."""

    player1, opponent = find_player_games(client_to_name[sender])[0]
    players = frozenset([player1, opponent])

    answer = message.Message()
    answer.info = "opponent_changed_position"
    answer.data = loaded_message.data

    safe_send_object(answer, name_to_client(opponent))

    game_played = games.get(players)

    game_played[player1] = loaded_message.data
    answer.data = (loaded_message.data, player1)
    games[players] = game_played


def left_game(loaded_message, sender):
    """Notify all players that layer has left the game."""

    player1 = client_to_name[sender]
    player2 = loaded_message.data

    players = frozenset([player1, player2])

    answer = message.Message()
    answer.info = "left_game"
    answer.data = player1

    opponent = None
    for opponent_connection, name in client_to_name.items():
        if name == player2:
            opponent = opponent_connection
            break

    safe_send_object(answer, opponent)

    '''
    answer.data = (player1, player2)
    for conn, name in client_to_name.items():
        if name in (player1, player2):
            continue

        safe_send_object(answer, conn)
    '''

    games[players] = []


def player_has_won_a_game(sender):
    """Gives a point up for player who has won and informs other about this fact."""

    player_name = client_to_name[sender]
    scores[player_name] += 1

    answer = message.Message()
    answer.info = "player_has_won_a_game"
    answer.data = player_name

    for client in clients:
        safe_send_object(answer, client)


def send_public_message(loaded_object, sender):
    """Resending message from one client to all others."""

    public_messages.append(loaded_object.data)

    for client in clients:
        if client != sender:
            safe_send_object(loaded_object, client)


def send_private_message(loaded_object, sender):
    """Resending a private message from one player to another player."""

    player_name, opponent = find_player_games(client_to_name[sender])[0]
    safe_send_object(loaded_object, names_to_client[opponent])


def send_heartbeat(sender):
    """
        Respond to the heartbeat.
    """

    last_heartbeat[sender] = time.time()

    heartbeat_message = message.Message()
    heartbeat_message.info = "heartbeat"
    safe_send_object(heartbeat_message, sender)


def monitor_heartbeats():
    """
        Periodically checks if clients have sent a heartbeat within the timeout.
        Disconnects clients that exceed the timeout.
    """
    try:
        while True:
            current_time = time.time()
            for client, last_time in list(last_heartbeat.items()):
                if current_time - last_time > HEARTBEAT_TIMEOUT:
                    stop_client_thread(client)
                    client.close()
            time.sleep(1)
    except Exception as e:
        print(f"Exception in monitor_heartbeats: {e}")


def handle_loaded_object(loaded_object, sender):
    """Each time the server receives a message, this function decides what to do with it."""

    match loaded_object.info:
        case "login_attempt":
            client_login(loaded_object.data, sender)

        case "disconnect":
            client_logout(loaded_object.data, sender)
            stop_client_thread(sender)

        case "create_challenge":
            create_challenge(loaded_object, sender)

        case "delete_challenge":
            delete_challenge(loaded_object, sender)

        case "accept_challenge":
            accept_challenge(loaded_object, sender)

        case "change_position":
            notify_change_position(loaded_object, sender)

        case "leaving_game":
            left_game(loaded_object, sender)

        case "player_have_won_a_game":
            player_has_won_a_game(sender)

        case "public_message":
            send_public_message(loaded_object, sender)

        case "private_message":
            send_private_message(loaded_object, sender)

        case "heartbeat":
            send_heartbeat(sender)


def handle_client(client_connection):
    """Function that communicate with the client."""
    should_stop = client_threads[client_connection]

    try:

        while not should_stop.is_set():
            try:
                client_message = communication.load_object(client_connection)
            except CommunicationError:

                break

            if client_message:
                handle_loaded_object(client_message, client_connection)

            else:
                break
    finally:
        with clients_lock:
            if client_connection in client_to_name:
                client_name = client_to_name[client_connection]
                client_logout(client_name, client_connection)
                stop_client_thread(client_connection)
            try:

                clients.remove(client_connection)
            except ValueError:
                pass


def main():
    """Main function to  start the server"""
    server_utils.register_server()
    atexit.register(server_utils.unregister_server)

    heartbeat_monitor_thread = threading.Thread(target=monitor_heartbeats, daemon=True)
    heartbeat_monitor_thread.start()

    while not shutdown_event.is_set():
        with clients_lock:
            if len(clients) < MAX_CLIENTS:
                connection, client_address = server_socket.accept()
                clients.append(connection)

                stop_event = threading.Event()

                client_thread = threading.Thread(target=handle_client,
                                                 args=(connection,), daemon=True)
                client_threads[connection] = stop_event
                client_thread.start()
            else:
                print("Max clients reached, waiting for space.")


if __name__ == "__main__":
    main()
