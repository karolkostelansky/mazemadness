import socket
import requests

WORDPRESS_API_URL = "https://webtesting.sk/wp-json/server-status/v1/status"


def get_local_ip():
    """
    Returns the local IP address of the machine.
    Attempts to connect to a non-local IP address to determine the local IP.
    If the connection fails, returns the loopback address '127.0.0.1'.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('10.254.254.254', 1))
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = '127.0.0.1'
    finally:
        s.close()
    return ip_address


def register_server():
    """
        Registers the server with its local IP address by sending a POST
        request to the WORDPRESS_API_URL. The request contains the
        server's IP address and an action to start the server.
    """
    ip_address = get_local_ip()
    data = {"ip": ip_address, "action": "start"}
    try:
        response = requests.post(WORDPRESS_API_URL, json=data)
        response.raise_for_status()
        print(f"Server registered with IP {ip_address}.")
    except requests.RequestException as e:
        print(f"Failed to register server: {e}")


def unregister_server():
    """
        Unregisters the server by sending a POST request to the WORDPRESS_API_URL
        with an action to stop the server.
    """
    data = {"action": "stop"}
    try:
        response = requests.post(WORDPRESS_API_URL, json=data)
        response.raise_for_status()
        print("Server unregistered.")
    except requests.RequestException as e:
        print(f"Failed to unregister server: {e}")
