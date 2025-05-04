import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import socket
import threading

from server import main as server_main
from communication import connect_to_server, communication, message

CLIENT_PORT = 65432


@pytest.fixture(scope="module")
def start_server():
    """Fixture to start the server before each test."""
    server_thread = threading.Thread(target=server_main, daemon=True)
    server_thread.start()
    time.sleep(2)

    SERVER_ADDRESS = connect_to_server.check_server_status()

    yield SERVER_ADDRESS


def create_and_connect_client(server_address, username):
    """Helper function to create a client, connect to the server, and send a login attempt."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_address, CLIENT_PORT))

    login_message = message.Message()
    login_message.info = "login_attempt"
    login_message.data = username

    time.sleep(1)

    communication.send_object(login_message, client)

    time.sleep(1)

    return client


def get_response(client):
    """Helper function to get the response from the server."""
    return communication.load_object(client)


def send_logout(client, username):
    """Helper function to send a logout message."""
    logout_message = message.Message()
    logout_message.info = "disconnect"
    logout_message.data = username

    communication.send_object(logout_message, client)

    time.sleep(1)


def test_client_connection(start_server):
    """Test that the client connects to the server successfully."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((start_server, CLIENT_PORT))
        client.close()
    except Exception as e:
        pytest.fail(f"Client failed to connect to the server: {e}")


def test_client_login(start_server):
    """Test if the client can log in with a valid username."""

    client = create_and_connect_client(start_server, "John")
    response = get_response(client)
    assert response.info == "login_successful"

    send_logout(client, "John")
    client.close()


def test_login_with_duplicate_names(start_server):
    """Test that client cannot have the same username as someone already logged in."""

    client1 = create_and_connect_client(start_server, "test")
    response1 = get_response(client1)
    assert response1.info == "login_successful"

    time.sleep(0.1)
    client2 = create_and_connect_client(start_server, "test")
    response2 = get_response(client2)
    assert response2.info == "wrong_login_name"

    send_logout(client1, "test")
    client1.close()
    client2.close()


def test_login_with_non_duplicate_names(start_server):
    """Test that two clients can log in with different usernames."""

    client1 = create_and_connect_client(start_server, "test")
    response1 = get_response(client1)
    assert response1.info == "login_successful"

    time.sleep(0.1)
    client2 = create_and_connect_client(start_server, "test2")
    response2 = get_response(client2)
    assert response2.info == "login_successful"

    time.sleep(0.1)
    send_logout(client1, "test")
    client1.close()

    send_logout(client2, "test2")
    client2.close()


def test_user_count_change_delivery(start_server):
    client1 = create_and_connect_client(start_server, "John")
    response1 = get_response(client1)
    assert response1.info == "login_successful"

    time.sleep(0.1)
    client2 = create_and_connect_client(start_server, "Mary")
    response2 = get_response(client2)
    assert response2.info == "login_successful"

    time.sleep(0.1)
    listened1 = communication.load_object(client1)
    assert listened1.info == "user_count_change"

    time.sleep(0.1)
    client3 = create_and_connect_client(start_server, "Doe")
    response3 = get_response(client3)
    assert response3.info == "login_successful"

    time.sleep(0.1)
    listened1 = communication.load_object(client1)
    assert listened1.info == "user_count_change"

    time.sleep(0.1)
    listened2 = communication.load_object(client2)
    assert listened2.info == "user_count_change"

    send_logout(client1, "John")
    client1.close()

    send_logout(client2, "Mary")
    client2.close()

    send_logout(client3, "Doe")
    client3.close()


def test_public_message_delivery(start_server):
    client1 = create_and_connect_client(start_server, "John")
    response1 = get_response(client1)
    assert response1.info == "login_successful"

    time.sleep(0.1)
    client2 = create_and_connect_client(start_server, "Mary")
    response2 = get_response(client2)
    assert response2.info == "login_successful"

    time.sleep(0.1)
    listened1 = communication.load_object(client1)
    assert listened1.info == "user_count_change"

    time.sleep(0.1)
    client3 = create_and_connect_client(start_server, "Doe")
    response3 = get_response(client3)
    assert response3.info == "login_successful"

    time.sleep(0.1)
    listened1 = communication.load_object(client1)
    assert listened1.info == "user_count_change"

    time.sleep(0.1)
    listened2 = communication.load_object(client2)
    assert listened2.info == "user_count_change"

    public_message = message.Message()
    public_message.info = "public_message"
    public_message.data = "Hello everybody"

    time.sleep(0.1)
    communication.send_object(public_message, client1)

    time.sleep(0.1)
    listened2 = communication.load_object(client2)
    assert listened2.data == "Hello everybody"

    time.sleep(0.1)
    listened3 = communication.load_object(client3)
    assert listened3.data == "Hello everybody"

    send_logout(client1, "John")
    client1.close()

    send_logout(client2, "Mary")
    client2.close()

    send_logout(client3, "Doe")
    client3.close()


def test_challenge_delivery(start_server):
    time.sleep(3)
    client1 = create_and_connect_client(start_server, "John")
    response1 = get_response(client1)
    assert response1.info == "login_successful"

    time.sleep(0.1)
    client2 = create_and_connect_client(start_server, "Mary")
    response2 = get_response(client2)
    assert response2.info == "login_successful"

    time.sleep(0.1)
    listened1 = communication.load_object(client1)
    assert listened1.info == "user_count_change"

    challenge_message = message.Message()
    time.sleep(0.1)
    challenge_message.info = "create_challenge"
    time.sleep(0.1)
    challenge_message.data = "Mary"

    time.sleep(0.1)
    communication.send_object(challenge_message, client1)

    time.sleep(0.1)
    listened2 = communication.load_object(client2)
    assert listened2.info == "received_challenge"
    assert listened2.data == "John"

    time.sleep(0.1)
    challenge_message.info = "delete_challenge"
    communication.send_object(challenge_message, client1)

    time.sleep(0.1)
    listened2 = communication.load_object(client2)
    assert listened2.info == "delete_challenge"
    assert listened2.data == "John"

    send_logout(client1, "John")
    client1.close()

    send_logout(client2, "Mary")
    client2.close()


def test_challenge_is_not_valid_after_opponent_started_another_game(start_server):
    client1 = create_and_connect_client(start_server, "John")
    response1 = get_response(client1)
    assert response1.info == "login_successful"

    time.sleep(0.1)
    client2 = create_and_connect_client(start_server, "Mary")
    response2 = get_response(client2)
    assert response2.info == "login_successful"

    time.sleep(0.1)
    listened1 = communication.load_object(client1)
    assert listened1.info == "user_count_change"

    time.sleep(0.1)
    client3 = create_and_connect_client(start_server, "Doe")
    response3 = get_response(client3)
    assert response3.info == "login_successful"

    time.sleep(0.1)
    listened1 = communication.load_object(client1)
    assert listened1.info == "user_count_change"

    time.sleep(0.1)
    listened2 = communication.load_object(client2)
    assert listened2.info == "user_count_change"

    challenge_message = message.Message()
    challenge_message.info = "create_challenge"
    challenge_message.data = "Mary"

    time.sleep(0.1)
    communication.send_object(challenge_message, client1)

    time.sleep(0.1)
    listened2 = communication.load_object(client2)
    assert listened2.info == "received_challenge"
    assert listened2.data == "John"

    time.sleep(0.1)
    challenge_message.data = "Doe"
    communication.send_object(challenge_message, client2)

    time.sleep(0.1)
    listened3 = communication.load_object(client3)
    assert listened3.info == "received_challenge"
    assert listened3.data == "Mary"

    time.sleep(0.1)
    challenge_message.info = "accept_challenge"
    challenge_message.data = "John"
    communication.send_object(challenge_message, client2)

    time.sleep(0.1)
    listened1 = communication.load_object(client1)
    assert listened1.info == "accepted_challenge"

    time.sleep(0.1)
    listened3 = communication.load_object(client3)

    assert listened3.info == "challenge_no_longer_valid"

    send_logout(client1, "John")
    client1.close()

    send_logout(client2, "Mary")
    client2.close()

    send_logout(client3, "Doe")
    client3.close()
