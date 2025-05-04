class Message:
    """Simple class, which is transported through the network."""
    def __init__(self, info="", data=""):
        self.info = info
        self.data = data
