import pickle

from exceptions.my_exceptions import CommunicationError


def send_object(object_to_send, connection):
    """
        Serializes and sends an object using the given socket connection.
    """
    if connection is None:
        return

    try:
        serialized_data = pickle.dumps(object_to_send)
    except Exception:
        ...

    try:

        data_length = len(serialized_data)
        connection.sendall(data_length.to_bytes(4, 'big'))

        connection.sendall(serialized_data)
    except (OSError, ConnectionError):
        ...


def load_object(connection):
    """
        Receives and deserializes an object using the given socket connection.
        Raises a CommunicationError if any error occurs.
    """
    if connection is None:
        return None

    try:

        data_length = int.from_bytes(connection.recv(4), 'big')
        if data_length <= 0:
            raise CommunicationError("Invalid data length received.")

        serialized_data = b''
        while len(serialized_data) < data_length:
            chunk = connection.recv(min(1024, data_length - len(serialized_data)))
            if not chunk:
                raise CommunicationError("Connection lost during object reception.")
            serialized_data += chunk

        return pickle.loads(serialized_data)
    except (OSError, ConnectionError) as e:
        raise CommunicationError(f"Error receiving data: {e}")
    except pickle.UnpicklingError as e:
        raise CommunicationError(f"Deserialization error: {e}")
