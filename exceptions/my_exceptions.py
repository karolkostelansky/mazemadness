class CommunicationError(Exception):
    """
        Simple exception, idea is that whenever error with communication rises,
        this exception will be raised, so it is easy to catch it, because I use only
        one type of exception
    """
    def __init__(self, text=""):
        self.text = text
