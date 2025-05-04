import requests

WORDPRESS_API_URL = "https://webtesting.sk/wp-json/server-status/v1/status"


def check_server_status():
    try:
        response = requests.get(WORDPRESS_API_URL)
        response.raise_for_status()
        data = response.json()
        if "ip" in data and data["ip"]:
            return data['ip']
        else:
            return False

    except requests.RequestException as e:
        print(f"Failed to check server status: {e}")
